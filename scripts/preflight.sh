#!/usr/bin/env bash
# Comprovació prèvia abans d'obrir Claude Code per a una fase. Sense LLM, cost zero.
# Ús: bash scripts/preflight.sh docs/prompts/001-fase1.md
# Codi de sortida: 0 = llest, 1 = cal corregir alguna cosa.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
P="${1:-}"; [[ -f "$P" ]] || { echo "Ús: $0 docs/prompts/<spec>-<fase>.md"; exit 1; }
F=0
ok()    { echo "  OK     $1"; }
falla() { echo "  FALLA  $1"; F=$((F+1)); }
avis()  { echo "  AVÍS   $1"; }

nnn=$(basename "$P" | grep -oE '^[0-9]{3}')
S=$(ls -d specs/"$nnn"-*/ 2>/dev/null | head -1); S="${S%/}"
echo "== Preflight: $P (spec $nnn) =="

# 1. Git
b=$(git rev-parse --abbrev-ref HEAD)
[[ "$b" == "$(basename "$S")" ]] && ok "Branca $b" || falla "Branca $b ≠ $(basename "$S")"
[[ -z "$(git status --porcelain)" ]] && ok "Arbre net" || falla "Hi ha canvis sense commit (git status)"
git fetch -q 2>/dev/null
[[ "$(git rev-parse HEAD)" == "$(git rev-parse @{u} 2>/dev/null)" ]] && ok "Sincronitzat amb el remot" || avis "HEAD diferent del remot (falta push o pull)"

# 2. Gates
for g in "constitution" "spec $S" "plan $S"; do
  if bash scripts/auditar.sh $g >/dev/null 2>&1; then ok "Auditoria Part A ($g): cap FALLA"
  else falla "Auditoria Part A ($g) amb FALLA: bash scripts/auditar.sh $g"; fi
done
git checkout -q -- docs/auditoria 2>/dev/null; git clean -qf docs/auditoria 2>/dev/null
for g in "g1-$nnn" "g2-$nnn"; do
  # l'informe més recent: data més alta i, dins la data, la revisió -rN més alta
  last=$(ls docs/auditoria/$g-20*.md 2>/dev/null | awk '{k=$0; if (k !~ /-r[0-9]+\.md$/) sub(/\.md$/, "-r0.md", k); match(k, /-r[0-9]+\.md$/); printf "%s %04d %s\n", substr(k,1,RSTART-1), substr(k,RSTART+2,RLENGTH-5), $0}' | sort | tail -1 | cut -d' ' -f3)
  if [[ -z "$last" ]]; then falla "Sense informe $g"
  elif grep -qE '^- Veredicte: Passa' "$last"; then ok "$(basename "$last") signat: $(grep -m1 '^- Veredicte:' "$last" | cut -d: -f2-)"
  else falla "$(basename "$last") sense signar"; fi
done

# 3. Prompt i fitxers que cita
for f in $(grep -oE '[A-Za-z0-9_./-]+\.(md|json|py)' "$P" | sort -u); do
  [[ -e "$f" || -e "$S/$f" || -e "$S/contracts/$(basename "$f")" ]] && ok "Existeix $f" || falla "El prompt cita $f, que no existeix"
done
ids=$(grep -viE 'no facis|no executis' "$P" | grep -oE 'T[0-9]{3}' | sort -u)
rang=$(grep -viE 'no facis' "$P" | grep -oE 'T[0-9]{3}–T[0-9]{3}' | head -1)
if [[ -n "$rang" ]]; then
  # els números es treuen amb grep: cut -c compta caràcters o bytes segons el sistema (el guió – és multibyte)
  a=$(echo "$rang" | grep -oE '[0-9]{3}' | head -1); z=$(echo "$rang" | grep -oE '[0-9]{3}' | tail -1)
  i=$((10#$a)); while [[ "$i" -le "$((10#$z))" ]]; do ids="$ids $(printf 'T%03d' "$i")"; i=$((i+1)); done
fi
for t in $(echo $ids | tr ' ' '\n' | sort -u); do
  grep -qE "^- \[ \] $t " "$S/tasks.md" && ok "$t pendent a tasks.md" \
    || { grep -qE "^- \[[xX]\] $t " "$S/tasks.md" && avis "$t ja marcada com a feta" || falla "$t no existeix a tasks.md"; }
done

# 4. Dependències i entorn
if grep -q 'uv add' "$P" || grep -qi 'pydantic' "$S/plan.md"; then
  grep -qi 'pydantic' pyproject.toml && grep -qi 'name = "pydantic"' uv.lock \
    && ok "Pydantic a pyproject.toml i uv.lock" || falla "Falta Pydantic: uv add pydantic"
fi
uv lock --check >/dev/null 2>&1 && ok "uv.lock sincronitzat" || falla "uv.lock desincronitzat: uv lock"

# 5. Configuració de Claude Code
python3 -m json.tool .claude/settings.json >/dev/null 2>&1 && ok "settings.json vàlid" || falla "settings.json no és JSON vàlid"
for d in 'docs/auditoria' 'docs/inventari' 'ws_blondswim/'; do
  grep -q "Read(.*$d" .claude/settings.json && ok "deny de lectura: $d" || avis "Sense deny de lectura: $d"
done
c=$(cat CLAUDE.md AGENTS.md | wc -l | tr -d ' ')
[[ "$c" -le 80 ]] && ok "Context fix CLAUDE.md + AGENTS.md: $c línies" || avis "Context fix llarg: $c línies"
grep -q 'tracabilitat = "avis"' pyproject.toml && ok "Traçabilitat en mode avís (T002 al final)" || avis "Traçabilitat no és «avis»"

# 6. Base verda abans de començar
out=$(bash scripts/verify.sh 2>&1)
echo "$out" | grep -q 'LLEST PER SEGUIR' && ok "verify.sh en verd abans de començar" \
  || { falla "verify.sh no és verd:"; echo "$out" | grep -E '^FAIL' | sed 's/^/         /'; }

echo
[[ "$F" -eq 0 ]] && echo "LLEST: obre Claude Code amb «Segueix @$P»" || echo "NO LLEST: $F FALLA(ES)"
[[ "$F" -eq 0 ]]
