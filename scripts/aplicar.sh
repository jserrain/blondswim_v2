#!/usr/bin/env bash
# Aplica un patch amb comprovació prèvia. Ús: bash scripts/aplicar.sh <fitxer.patch> [...]
# Busca el fitxer tal com s'indica i, si no hi és, a ~/Downloads. S'atura al primer error.
set -u
[[ $# -gt 0 ]] || { echo "Ús: $0 <fitxer.patch> [...]"; exit 2; }
cd "$(git rev-parse --show-toplevel)" || exit 2
for p in "$@"; do
  f="$p"; [[ -f "$f" ]] || f="$HOME/Downloads/$(basename "$p")"
  [[ -f "$f" ]] || { echo "FALTA  $p (ni aquí ni a ~/Downloads)"; exit 1; }
  if ! git apply --check "$f" 2>/tmp/aplicar.err; then
    echo "NO APLICA  $f"; head -5 /tmp/aplicar.err; exit 1
  fi
  git apply "$f" && echo "APLICAT  $f"
done
git status --short
