# Quickstart: validar la importació

**Spec**: [spec.md](spec.md) · **Contractes**: [contracts/](contracts/)

Guia de validació de punta a punta. Les ordres les executa el coach o el desenvolupador; `AGENTS.md` prohibeix que Claude Code les executi.

## Prerequisits
- Fase 0 acabada: `bash scripts/verify.sh` en verd amb el model `test_css` (spec 001, ADR-0022).
- Fixtures a `tests/fixtures/entrada/` (plantilla per al coach).
- `data/` buit o amb dades de prova (no es versiona).

## 1. Calendari (US1)
```bash
cp -r tests/fixtures/entrada/<AAAA-AA> data/entrada/
uv run blondswim importar calendari --temporada <AAAA-AA>
```
Esperat, calendari sense incidències: codi `0`, estat `desat`, i `data/competicions/<AAAA-AA>.json` amb l'id de cada competició (slug del nom).
Amb una seu buida: codi `2`, `pendent de confirmar`; tornar-hi amb `--confirma` desa i registra l'avís a `data/avisos.jsonl`.

## 2. Fitxa del nedador (US3)
```bash
uv run blondswim importar fitxa data/entrada/nedadors/<nom>.csv --alta
uv run blondswim importar fitxa data/entrada/nedadors/<nom>.csv
```
Esperat, fitxa d'alta sense avisos que requereixin confirmació: codi `0` a la primera passada i `nedadors/<uuid>/nedador.json` amb l'alias de la fitxa. Si l'alias ja existia, l'avís RN-041 indica l'alias que s'assignaria (`…01`) i el codi és `2`: repeteix amb `--confirma` només si és un nedador nou.
Esperat, fitxa d'actualització (segona ordre, sense `--alta`, amb l'alias d'un nedador existent) sense incidències: codi `0`. Un alias que no existeix: codi `1` amb RN-003.
Una fitxa amb `canal_preferent` buit: codi `2` (RN-035) i, amb `--confirma`, es desa.

## 3. Inscripcions (US2)
```bash
uv run blondswim importar inscripcions --temporada <AAAA-AA> --alias <alias>
```
Esperat: codi `0` i `inscripcions.json` amb una participació per competició. Reimportant-ho amb una participació menys: codi `2` (RN-039) i, amb `--confirma`, el fitxer queda amb les participacions del CSV.

## 4. Errors
- Un CSV amb una columna de més o una data `31/12/2026`: codi `1`, no es desa res i l'informe llista totes les incidències amb `fila:columna`.
- Una fitxa sense cap fila, o amb una clau repetida: codi `1`.
- Reimportar un calendari que treu una competició amb inscripcions: codi `1` amb RN-010 i l'alias afectat; el catàleg no canvia.

## 5. Verificació completa
```bash
bash scripts/verify.sh
```
Inclou el contracte d'import-linter (`interfaces/*` → `application/`) i la traçabilitat dels CA.
