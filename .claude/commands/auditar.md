---
description: Part B de l'auditoria — revisió semàntica de la constitució (G0) o d'una spec (G1)
argument-hint: constitution | spec specs/NNN-nom
allowed-tools: Read, Glob, Grep, Write(docs/auditoria/**), Edit(docs/auditoria/**)
---

Actua com a AUDITOR SEMÀNTIC. Només llegeixes; l'únic fitxer que escrius és l'informe de `docs/auditoria/`. No executis cap comanda de terminal ni modifiquis cap artefacte auditat.

Argument: `$ARGUMENTS`

## 1. Preparació
1. Llegeix `docs/auditoria/PROCEDIMENT.md`. Criteris, columna **Qui**, escala i veredicte són la referència única.
2. Determina el gate:
   - `constitution` → Gate 0 (secció 5). Fitxer de la Part A: `docs/auditoria/g0-mecanic-*.txt`.
   - `spec specs/NNN-nom` → Gate 1 (secció 6). Fitxer de la Part A: `docs/auditoria/g1-NNN-mecanic-*.txt`.
3. Pren el fitxer de la Part A amb la data més recent al nom.
   - Si no n'hi ha, atura't i indica: `bash scripts/auditar.sh $ARGUMENTS`.
   - Si l'última línia no és `Resultat: cap FALLA`, atura't i llista les `FALLA`.
   - Si el fitxer auditat ha canviat després de la data del fitxer de la Part A (mira `**Last Amended**` o la data indicada), avisa que cal repetir la Part A.

## 2. Fonts
- **G0**: `.specify/memory/constitution.md`, `CLAUDE.md` i els fitxers que importa amb `@` (p. ex. `AGENTS.md`), `.specify/templates/overrides/*.md` (si no hi són, `.specify/templates/*.md`), `.claude/settings.json`, `scripts/verify.sh`, la llista de `docs/decisions/` i, només si cal per a G0-Q03, els ADR acceptats.
- **G1**: la `spec.md` indicada, `checklists/`, la constitució, `AGENTS.md`, `specs/000-*` (glossari), les files de `docs/regles.md` de les RN que la spec referencia i els ADR que la spec cita.
- No llegeixis `.env`, `~/.secrets` ni la v1.

## 3. Repartiment de criteris
- **Qui = A**: no els tornis a avaluar. OK → ✅, AVÍS → ⚠️, FALLA → ❌.
- **Qui = A→B**: la línia de consola (`PISTA`, `INFO`, `AVÍS`) és el punt de partida, no el veredicte. Una `PISTA` només diu que s'ha trobat una paraula o un fitxer; comprova al text que el criteri es compleix de debò.
- **Qui = B**: avalua'ls completament.

## 4. Regles d'avaluació
- Escala ✅ / ⚠️ / ❌ / N/A·j / N/A. N/A·j només per a criteris **R** i amb la cita de la justificació escrita; si no n'hi ha, ⚠️.
- Cada valoració porta evidència: ruta + secció o cita breu (≤ 15 paraules), o «no trobat».
- Separa FETS (verificat) d'INFERÈNCIES (deduït). No inventis contingut: si no hi és, és ❌.
- La constitució mana en present indicatiu i en català; no ho consideris falta de formulació normativa.
- **G0**: per a cada principi I–VIII, indica: verificable (sí/no), raó (explícita / via ADR / no), mecanisme de compliment (eina o porta concreta) i pilars d'AprenIA relacionats.
- **G1**: per a cada CA, indica només els que són ambigus, no provables, barregen QUÈ i COM o no tenen cas límit associat; resumeix la resta. Comprova que la spec no repeteix el contingut de les RN.

## 5. Sortida
Escriu `docs/auditoria/g0-constitucio-<AAAA-MM-DD>.md` o `docs/auditoria/g1-<NNN>-<AAAA-MM-DD>.md` amb:

1. **Resum executiu** (màx. 5 línies): estat, risc principal i veredicte proposat segons la secció 4 del procediment.
2. **Part A**: nom del fitxer `*-mecanic-*.txt` i recompte OK / AVÍS / PISTA / FALLA.
3. **Taula de criteris**: ID | criteri | O/R | Qui | estat | evidència | observació. Tots els criteris del gate, en l'ordre del procediment.
4. **Anàlisi detallada**: principis (G0) o CA, RN i requisits (G1).
5. **Accions recomanades**, prioritzades (Alta/Mitjana/Baixa), cadascuna amb la comanda Spec Kit (`/speckit-constitution`, `/speckit-clarify`…) o el fitxer que la resol.
6. **Falsos positius de la Part A** detectats (per millorar `auditar.sh`).
7. Secció `## Aprovació` buida (Part C), amb el format de la secció 7 del procediment.

En acabar, mostra només el resum executiu i la ruta de l'informe.
