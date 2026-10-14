#!/usr/bin/env bash
# Verificació determinista del projecte. Sense LLM. No modifica res.
set -u
cd "$(git rev-parse --show-toplevel)"
fails=0

check() {
  local name="$1"; shift
  if out=$("$@" 2>&1); then
    printf "OK    %s\n" "$name"
  else
    printf "FAIL  %s\n%s\n" "$name" "$(echo "$out" | tail -n 15 | sed 's/^/      /')"
    fails=$((fails + 1))
  fi
}

# Entorn
check "uv.lock sincronitzat"   uv lock --check
check "Python 3.12"            uv run python -c "import sys; assert sys.version_info[:2] == (3, 12)"

# Estructura
check "Capes Clean Architecture" bash -c 'for l in domain application infrastructure interfaces; do test -f src/blondswim/$l/__init__.py || exit 1; done'
check "Carpetes del projecte"    bash -c 'for d in tests/unit tests/integration specs docs/decisions data; do test -d $d || exit 1; done'
check "Pre-commit instal·lat"    test -f .git/hooks/pre-commit

# Portes de qualitat (sense --fix: només lectura)
check "ruff lint"      uv run ruff check .
check "ruff format"    uv run ruff format --check .
check "mypy strict"    uv run mypy src
check "import-linter"  uv run lint-imports
check "pytest"         uv run pytest

# Seguretat
check ".gitignore (.venv, .env)" bash -c 'grep -qxE "\.venv/?" .gitignore && grep -qx ".env" .gitignore'
check ".env no versionat"        bash -c '[ -z "$(git ls-files .env)" ]'
check "Cap clau al repo"         bash -c '! git grep -q --untracked "sk-""ant-"'
check "Clau API llegible"        uv run python -c "from blondswim.infrastructure.secrets import anthropic_api_key as k; assert len(k()) > 50"

echo
if [ "$fails" -eq 0 ]; then
  echo "LLEST PER SEGUIR"
else
  echo "BLOQUEJAT: $fails comprovació(ns) fallida(es)"
  exit 1
fi