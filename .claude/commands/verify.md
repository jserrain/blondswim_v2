---
description: Executa la verificació i diagnostica els errors (només lectura)
allowed-tools: Bash(bash scripts/verify.sh), Read, Grep, Glob
---
Executa `bash scripts/verify.sh`.

- Si acaba en "LLEST PER SEGUIR": respon només això.
- Si hi ha FAIL: per a cada un, llegeix només els fitxers implicats i dona
  la causa i l'ordre o canvi exacte per corregir-ho. No modifiquis res.
- No llegeixis mai `.env` ni `~/.secrets`.


