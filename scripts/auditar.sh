#!/usr/bin/env bash
# PART A de l'auditoria (procediment v2): comprovacions mecàniques, sense LLM.
# Resol els criteris "A" i dona PISTES per als "A→B". El veredicte semàntic és de la Part B (/auditar).
#
# Ús (des de l'arrel del repo):
#   bash scripts/auditar.sh constitution            → docs/auditoria/g0-mecanic-AAAA-MM-DD.txt
#   bash scripts/auditar.sh spec specs/NNN-nom      → docs/auditoria/g1-NNN-mecanic-AAAA-MM-DD.txt
# L'script desa ell mateix la sortida (no cal tee) i conserva el codi de sortida:
#   0 = cap FALLA · 1 = alguna FALLA · 2 = ús incorrecte
# Variables: BASE (branca base per a G1-S04, per defecte main).
# Compatible amb bash 3.2 i eines BSD (macOS): sense \b, grep -P, mapfile ni bc.

set -u

FALLES=0
ok()    { echo "  OK     $1"; }
avis()  { echo "  AVÍS   $1"; }
falla() { echo "  FALLA  $1"; FALLES=$((FALLES+1)); }
info()  { echo "  INFO   $1"; }
pista() { echo "  PISTA  $1"; }   # només per a A→B: indica què s'ha trobat, no si es compleix

C=".specify/memory/constitution.md"
AVUI=$(date +%F)

# Treu els comentaris HTML (p. ex. el Sync Impact Report de Spec Kit).
sense_comentaris() { awk '/<!--/{c=1} !c{print} /-->/{c=0}' "$1"; }

# Mostra les paraules trobades (paraula sencera) perquè la Part B vegi d'on surt la pista.
check_pilar() {
  local id="$1" pat="$2" trobat
  trobat=$(grep -oiwE "$pat" "$C" | sort -u | tr '\n' ',' | sed 's/,$//')
  if [[ -n "$trobat" ]]; then pista "$id trobat: $trobat"; else avis "$id cap paraula clau"; fi
}

gate_constitution() {
  echo "== Gate 0: Constitució ($AVUI) =="
  if [[ ! -f "$C" ]]; then falla "G0-E01 No existeix $C"; return; fi
  ok "G0-E01 Existeix $C"

  # E02: marcadors fora de comentaris
  local tokens
  tokens=$(sense_comentaris "$C" | grep -oE '\[[A-Z][A-Z0-9_]+\]|TODO' | sort -u | tr '\n' ' ')
  [[ -n "$tokens" ]] && falla "G0-E02 Marcadors pendents: $tokens" || ok "G0-E02 Sense marcadors de plantilla"

  # E03: format de versió i dates
  local linia ver rat ame
  linia=$(grep -E '\*\*Version\*\*' "$C" | tail -1)
  ver=$(echo "$linia" | sed -nE 's/.*\*\*Version\*\*: *([0-9]+\.[0-9]+\.[0-9]+).*/\1/p')
  rat=$(echo "$linia" | sed -nE 's/.*\*\*Ratified\*\*: *([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/p')
  ame=$(echo "$linia" | sed -nE 's/.*\*\*Last Amended\*\*: *([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/p')
  [[ -n "$ver" ]] && ok "G0-E03 Versió semver: $ver" || falla "G0-E03 Sense **Version**: X.Y.Z"
  [[ -n "$rat" ]] && ok "G0-E03 Ratificació: $rat" || falla "G0-E03 Sense **Ratified**: AAAA-MM-DD"
  [[ -n "$ame" ]] && ok "G0-E03 Última esmena: $ame" || falla "G0-E03 Sense **Last Amended**: AAAA-MM-DD"
  if [[ -n "$rat" && -n "$ame" ]]; then
    [[ "$ame" < "$rat" ]] && falla "G0-E03 Última esmena ($ame) anterior a la ratificació ($rat)"
    [[ "$ame" > "$AVUI" ]] && falla "G0-E03 Última esmena ($ame) en el futur"
  fi

  # E04: governança (presència; el contingut el jutja B)
  grep -qiE '^#+ .*(governan|governance)' "$C" && pista "G0-E04 Hi ha secció de governança" \
                                                || falla "G0-E04 Sense secció de governança"

  # E05: registre de canvis = Sync Impact Report o historial git del fitxer
  local commits
  commits=$(git log --oneline -- "$C" 2>/dev/null | wc -l | tr -d ' ')
  if grep -qiE 'sync impact report' "$C"; then ok "G0-E05 Sync Impact Report present"
  elif [[ "$commits" -gt 0 ]]; then ok "G0-E05 Historial git del fitxer: $commits commits"
  else avis "G0-E05 Sense Sync Impact Report ni historial git"; fi

  # Q01/Q02/Q05: dades per a la Part B
  local np nr
  np=$(grep -cE '^### [IVXLC]+\.' "$C")
  nr=$(grep -ciE '^(Raó|Rationale):' "$C")
  info "Principis (### I., II., …): $np"
  info "Principis amb línia 'Raó:'/'Rationale:': $nr"
  [[ "$np" -eq 0 ]] && falla "G0-Q01 No s'identifica cap principi numerat"
  [[ "$np" -gt 0 && "$nr" -lt "$np" ]] && pista "G0-Q02 $((np-nr)) principi(s) sense raó explícita"

  echo "-- Fonts normatives (G0-C05) --"
  [[ -f docs/regles.md ]] && ok "G0-C05 docs/regles.md" || falla "G0-C05 Falta docs/regles.md"
  ls docs/decisions/*.md >/dev/null 2>&1 && ok "G0-C05 docs/decisions/ amb ADR" || falla "G0-C05 Sense ADR a docs/decisions/"
  { ls specs/000-*.md >/dev/null 2>&1 || ls specs/000-*/spec.md >/dev/null 2>&1; } \
    && ok "G0-C05 Glossari (spec 000)" || falla "G0-C05 Falta la spec 000"

  echo "-- Portes de qualitat (G0-C06): el que la constitució diu que comprova verify.sh --"
  if [[ -f scripts/verify.sh ]]; then
    local eina
    for eina in 'ruff check' 'ruff format' 'mypy' 'lint-imports' 'pytest' 'tracabilitat'; do
      grep -q "$eina" scripts/verify.sh && ok "G0-C06 verify.sh inclou: $eina" || avis "G0-C06 verify.sh no inclou: $eina"
    done
  else
    falla "G0-C06 Falta scripts/verify.sh"
  fi

  echo "-- Pilars d'AprenIA (pistes; decideix la Part B, admet N/A justificat) --"
  check_pilar "G0-P01 SDD"                 'spec|specs|spec-driven|SDD'
  check_pilar "G0-P02 Schemas"             'pydantic|schema|esquema|validació|comprovació determinista'
  check_pilar "G0-P03 MCP"                 'MCP|model context protocol'
  check_pilar "G0-P04 Dades local/núvol"   'núvol|cloud|classificació|dades sensibles|en local'
  check_pilar "G0-P05 PII"                 'PII|dades personals|personal data|anonimitz[a-z]*|pseudonim[a-z]*'
  check_pilar "G0-P06 HITL"                'HITL|human-in-the-loop|aprovació humana|coach decideix|avisa'
  check_pilar "G0-P07 Aïllament/VCS"       'sandbox|contenidor|container|docker|worktree|branca'
  check_pilar "G0-P08 Observabilitat"      'observabilitat|observability|langfuse|traces|cost|tokens|registren'
  check_pilar "G0-P09 Avaluació"           'evals|golden|LLM-as-judge|avaluació'
  check_pilar "G0-P10 Proves"              'test|tests|pytest|prova|proves'

  echo "-- Coherència --"
  # C01: CLAUDE.md o els fitxers que importa amb @
  if [[ -f CLAUDE.md ]]; then
    local fonts f trobat=""
    fonts="CLAUDE.md $(grep -oE '^@[^ ]+' CLAUDE.md | sed 's/^@//' | tr '\n' ' ')"
    for f in $fonts; do [[ -f "$f" ]] && grep -qiE 'constitu' "$f" && trobat="$trobat $f"; done
    [[ -n "$trobat" ]] && pista "G0-C01 Remet a la constitució:$trobat" || avis "G0-C01 Ni CLAUDE.md ni els seus @imports citen la constitució"
  else
    avis "G0-C01 No hi ha CLAUDE.md"
  fi
  # C02: la plantilla efectiva és la d'overrides si existeix
  local pt=.specify/templates/plan-template.md
  [[ -f .specify/templates/overrides/plan-template.md ]] && pt=.specify/templates/overrides/plan-template.md
  grep -qi 'constitution check' "$pt" 2>/dev/null && pista "G0-C02 $pt té Constitution Check" || avis "G0-C02 Sense Constitution Check a $pt"
  # C04: settings.json existeix i és JSON vàlid
  if [[ -f .claude/settings.json ]]; then
    if command -v python3 >/dev/null 2>&1; then
      python3 -m json.tool .claude/settings.json >/dev/null 2>&1 && pista "G0-C04 .claude/settings.json vàlid" || falla "G0-C04 .claude/settings.json no és JSON vàlid"
    else
      pista "G0-C04 .claude/settings.json existeix (JSON no validat: falta python3)"
    fi
  else
    avis "G0-C04 No hi ha .claude/settings.json"
  fi
}

gate_spec() {
  local F="${1%/}" S nom nnn
  nom=$(basename "$F"); nnn="${nom%%-*}"; S="$F/spec.md"
  echo "== Gate 1: Spec $nom ($AVUI) =="

  # S01: carpeta i branca
  [[ "$nnn" =~ ^[0-9]{3}$ ]] || { falla "G1-S01 La carpeta no té format NNN-nom: $nom"; return; }
  [[ -f "$S" ]] || { falla "G1-S01 No existeix $S"; return; }
  ok "G1-S01 Carpeta $F amb spec.md"
  local branca
  branca=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  if [[ "$branca" == "$nom" ]]; then ok "G1-S01 Branca = carpeta: $branca"
  elif [[ "$branca" == "$nnn"-* ]]; then avis "G1-S01 Branca $branca no coincideix amb la carpeta $nom"
  else falla "G1-S01 Branca $branca no és de la spec $nnn"; fi

  # S02, S03
  grep -qE '^## Clarifications' "$S" && ok "G1-S02 ## Clarifications" || falla "G1-S02 Sense ## Clarifications"
  if ls "$F"/checklists/*.md >/dev/null 2>&1; then
    local pend; pend=$(cat "$F"/checklists/*.md | grep -cE '^[[:space:]]*- \[ \]')
    pista "G1-S03 Checklist present; ítems pendents: $pend"
  else
    avis "G1-S03 Sense checklist"
  fi

  # S04: res de plan/tasks ni codi
  [[ -e "$F/plan.md" || -e "$F/tasks.md" ]] && falla "G1-S04 Ja existeix plan.md o tasks.md" || ok "G1-S04 Sense plan/tasks"
  local base="${BASE:-main}" canvis
  if git rev-parse --verify -q "$base" >/dev/null; then
    canvis=$(git diff --name-only "$base"...HEAD -- src tests 2>/dev/null | wc -l | tr -d ' ')
    [[ "$canvis" -gt 0 ]] && falla "G1-S04 $canvis fitxer(s) de src/ o tests/ canviats respecte de $base" || ok "G1-S04 Sense codi nou respecte de $base"
  else
    avis "G1-S04 No existeix la branca base $base: no es comprova el codi"
  fi

  # S05: estat
  local estat; estat=$(sed -nE 's/^\*\*Estat:\*\* *([A-Za-zÀ-ú]+).*/\1/p' "$S" | head -1)
  [[ -n "$estat" ]] && info "G1-S05 Estat: $estat" || falla "G1-S05 Sense línia **Estat:**"

  # Q02/Q03: criteris d'acceptació CA-NNN[x]-nn
  local defs ids nca dup mal sense
  defs=$(grep -oE '^[[:space:]]*- \*\*CA-[0-9]{3}[a-z]?-[0-9]{2}\*\*' "$S" | grep -oE 'CA-[0-9]{3}[a-z]?-[0-9]{2}')
  nca=$(echo "$defs" | grep -c 'CA-')
  [[ "$nca" -gt 0 ]] && ok "G1-Q02 Criteris d'acceptació definits: $nca" || falla "G1-Q02 Cap criteri - **CA-$nnn-nn**"
  dup=$(echo "$defs" | sort | uniq -d | tr '\n' ' ')
  [[ -n "$dup" ]] && falla "G1-Q03 CA duplicats: $dup" || ok "G1-Q03 CA únics"
  mal=$(echo "$defs" | grep -vE "^CA-$nnn[a-z]?-" | grep 'CA-' | tr '\n' ' ')
  [[ -n "$mal" ]] && falla "G1-Q03 CA amb número de spec incorrecte: $mal" || ok "G1-Q03 Tots els CA són de la spec $nnn"
  sense=$(grep -E '^[[:space:]]*- \*\*CA-[0-9]{3}' "$S" | grep -viE 'dona[td][a-z]*.*quan.*aleshores' \
          | grep -oE 'CA-[0-9]{3}[a-z]?-[0-9]{2}' | tr '\n' ' ')
  [[ -n "$sense" ]] && avis "G1-Q02 CA sense Donat(s/da/des)/quan/aleshores: $sense" || ok "G1-Q02 Tots els CA en format Donat/quan/aleshores"
  info "G1-Q02 CA marcats [PENDENT spec NNN]: $(grep -cE '^[[:space:]]*- \*\*CA-.*\[PENDENT spec' "$S")"

  # Q04: RN referenciades existeixen a docs/regles.md
  local rns falten="" ret="" r
  rns=$(grep -oE 'RN-[0-9]{3}' "$S" | sort -u)
  if [[ -z "$rns" ]]; then
    info "G1-Q04 La spec no referencia cap RN"
  elif [[ ! -f docs/regles.md ]]; then
    falla "G1-Q04 Falta docs/regles.md"
  else
    for r in $rns; do
      grep -qE "^\| *$r *\|" docs/regles.md || falten="$falten $r"
      grep -E "^\| *$r *\|" docs/regles.md | grep -qi 'retirada' && ret="$ret $r"
    done
    [[ -n "$falten" ]] && falla "G1-Q04 RN no definides a docs/regles.md:$falten" || ok "G1-Q04 $(echo "$rns" | wc -l | tr -d ' ') RN referenciades, totes definides"
    [[ -n "$ret" ]] && avis "G1-Q04 RN retirades referenciades:$ret"
  fi

  # Q05
  local nc; nc=$(grep -c 'NEEDS CLARIFICATION' "$S")
  [[ "$nc" -eq 0 ]] && ok "G1-Q05 Zero [NEEDS CLARIFICATION]" || falla "G1-Q05 [NEEDS CLARIFICATION] pendents: $nc"
  grep -qE '^## Assumptions' "$S" && ok "G1-Q05 ## Assumptions" || avis "G1-Q05 Sense ## Assumptions"

  # Q07: document genèric (principi VIII) — dates concretes com a pista
  local dates; dates=$(grep -oE '20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$S" | sort -u | tr '\n' ' ')
  [[ -n "$dates" ]] && pista "G1-Q07 Dates concretes a revisar: $dates" || ok "G1-Q07 Sense dates concretes"

  # Q01, Q08, A02, A03: pistes per a la Part B
  grep -qE 'Priority: P1|Prioritat: P1|\(P1\)' "$S" && pista "G1-Q01 Hi ha històries prioritzades" || avis "G1-Q01 Sense històries P1/P2"
  info "G1-Q08 FR-NNN: $(grep -oE 'FR-[0-9]{3}' "$S" | sort -u | wc -l | tr -d ' ') · SC-NNN: $(grep -oE 'SC-[0-9]{3}' "$S" | sort -u | wc -l | tr -d ' ')"
  grep -qiE 'accions sensibles|sensitive actions|dades personals' "$S" && pista "G1-A02 Esmenta dades o accions sensibles" || avis "G1-A02 Sense secció de dades/accions sensibles"
  grep -qiE 'judici LLM' "$S" && pista "G1-A03 Esmenta punts de judici LLM" || info "G1-A03 Sense punts de judici LLM"
}

case "${1:-}" in
  constitution) OUT="docs/auditoria/g0-mecanic-$AVUI.txt" ;;
  spec)
    [[ -n "${2:-}" ]] || { echo "Ús: $0 spec specs/NNN-nom"; exit 2; }
    n=$(basename "${2%/}"); OUT="docs/auditoria/g1-${n%%-*}-mecanic-$AVUI.txt" ;;
  *) echo "Ús: $0 constitution | spec specs/NNN-nom"; exit 2 ;;
esac
[[ -d .git || -f .git ]] || { echo "Executa'l des de l'arrel del repo"; exit 2; }
mkdir -p docs/auditoria

{
  case "$1" in
    constitution) gate_constitution ;;
    spec)         gate_spec "$2" ;;
  esac
  echo
  [[ "$FALLES" -eq 0 ]] && echo "Resultat: cap FALLA" || echo "Resultat: $FALLES FALLA(ES)"
  echo "$FALLES" > "$OUT.falles"
} | tee "$OUT"

FALLES=$(cat "$OUT.falles"); rm -f "$OUT.falles"
echo "Desat a $OUT"
[[ "$FALLES" -eq 0 ]]
