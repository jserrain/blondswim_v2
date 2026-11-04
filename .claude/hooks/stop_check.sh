#!/usr/bin/env bash
# Hook Stop: ruff + mypy + lint-imports. Si fallen, retorna l'error a Claude (exit 2)
# com a màxim 2 vegades seguides per sessió; a la 3a deixa aturar i avisa.
input=$(cat)
camp() { printf '%s' "$input" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$1', ''))" 2>/dev/null; }
sid=$(camp session_id); actiu=$(camp stop_hook_active)
comptador="${TMPDIR:-/tmp}/blondswim-stop-${sid:-sense-sessio}"
# Una aturada nova (no provocada pel hook) torna a començar el compte
[[ "$actiu" == "True" ]] || rm -f "$comptador"

check="${BLONDSWIM_STOP_CHECK:-uv run ruff check . 2>&1 && uv run mypy src 2>&1 && uv run lint-imports 2>&1}"
if out=$(bash -c "$check"); then rm -f "$comptador"; exit 0; fi

n=$(( $(cat "$comptador" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$comptador"
if (( n > 2 )); then
  rm -f "$comptador"
  echo "Comprovacions encara en vermell després de 2 intents: m'aturo. Executa-les tu i decideix." 
  exit 0
fi
echo "$out" | tail -n 20 >&2
exit 2
