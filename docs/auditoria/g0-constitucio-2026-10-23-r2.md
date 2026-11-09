# Auditoria G0 — Constitució 1.3.0 · 2026-10-23 · revisió 2

Re-auditoria del canvi 1.2.1 → 1.3.0 (commit `8501ccb`) i de l'ADR-0012 (commit `631f828`). La resta de criteris no han canviat respecte de `g0-constitucio-2026-10-23.md`.

## 1. Resum executiu
- **Estat:** l'esmena del principi V és verificable, té raó i no contradiu cap altre principi ni cap ADR. La plantilla de pla ja la recull.
- **Risc principal:** el mateix que a la revisió 1. Falta l'ADR que fixa quines dades poden arribar a un LLM.
- **Veredicte proposat:** **Passa amb condicions.** Les condicions pendents de la revisió 1 passen a l'esmena 1.4.0.

## 2. Part A (consola)
`docs/auditoria/g0-mecanic-2026-10-23.txt`: versió 1.3.0, 0 FALLA. Hi ha 3 principis amb raó (abans 2).

## 3. Criteris afectats

| ID | Criteri | O/R | Estat | Evidència | Observació |
|---|---|---|---|---|---|
| G0-E03 | Versió i dates | O | ✅ | 1.3.0 · 2026-10-23 | |
| G0-E04 | Governança | O | ✅ | § Governance | El salt és MINOR i no MAJOR perquè el principi V no canvia d'objectiu (dades honestes): s'hi afegeix la distinció entre paràmetres ajustables i definicions |
| G0-Q01 | Principis verificables | O | ⚠️ | V: «en un sol lloc del codi, amb l'ID de la font citat i comprovades per un criteri d'acceptació» | V és verificable. Continua pendent «canvis petits» del principi II (revisió 1) |
| G0-Q02 | Raó per principi | R | ⚠️ | «Raó:» a I, III i V | En falten 5 (II, IV, VI, VII i VIII) |
| G0-Q03 | Sense contradiccions | O | ✅ | V i III; V i `domain/definicions.py` (pla 001); ADR-0012 i ADR-0004/0005 | La definició es manté a `regles.md` (III) i el codi la implementa. L'ADR-0012 no toca cap principi |
| G0-C01 | `AGENTS.md` coherent | O | ✅ | llista d'ADR amb el 0012 i sense el 0003 | |
| G0-C02 | Constitution Check alineat | R | ✅ | `overrides/plan-template.md`, punt V | Actualitzat al mateix commit |

## 4. Altres observacions
- `docs/mapa_specs.md` (no normatiu, línia 22) encara diu «mai constants al codi». Cal alinear-lo amb la redacció nova.

## 5. Accions

| Prioritat | Acció | Com |
|---|---|---|
| Alta | ADR de dades cap a l'LLM i línia al principi IV | Esmena 1.4.0, abans de la primera spec amb judici LLM |
| Mitjana | «Canvis petits» (II) i raó a II, IV, VI, VII i VIII | Esmena 1.4.0 |
| Baixa | «Fora d'abast» (MCP, aïllament, observabilitat, evals) | Esmena 1.4.0 |
| Baixa | Alinear `docs/mapa_specs.md` línia 22 amb el principi V | Editar el fitxer |

## Aprovació
- Veredicte: Passa amb condicions
- Aprovador: Josep M. Serrainat
- Data: 2026-10-23
- Falsos positius marcats: G0-P08
- Condicions i terminis: esmena 1.4.0 (dades LLM, Q01, raons, fora d'abast) abans de la primera spec amb judici LLM
