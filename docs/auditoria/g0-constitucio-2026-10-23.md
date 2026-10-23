# Auditoria G0 — Constitució 1.2.1 · 2026-10-23

## 1. Resum executiu
- **Estat:** cap ❌. Un ⚠️ en criteri obligatori (G0-Q01) i set ⚠️ en criteris recomanats.
- **Risc principal:** la constitució no diu quines dades poden arribar a un LLM al núvol (P04, P05). `verify.sh` ja exigeix una clau API, i els fitxers dels nedadors contenen nom i cognoms de tercers.
- **Segon risc:** `.claude/settings.json` autoritza Claude Code a executar `verify.sh` i `uv run`, però `AGENTS.md` li prohibeix executar ordres.
- **Veredicte proposat:** **Passa amb condicions.** Esmena 1.3.0 abans de la primera spec amb judici LLM; el ⚠️ de Q01 es resol a la mateixa esmena.

## 2. Part A (consola)
Fitxer: `docs/auditoria/g0-mecanic-2026-10-23.txt` (executat a macOS, `exit=0`).
Recompte: 15 OK · 11 PISTA · 4 AVÍS · 0 FALLA.

## 3. Taula de criteris

| ID | Criteri | O/R | Qui | Estat | Evidència | Observació |
|---|---|---|---|---|---|---|
| G0-E01 | Existeix la constitució | O | A | ✅ | consola OK | |
| G0-E02 | Sense marcadors | O | A | ✅ | consola OK | |
| G0-E03 | Versió i dates | O | A | ✅ | 1.2.1 · 2026-10-18 · 2026-10-23 | |
| G0-E04 | Governança: esmena, versió, compliment | O | A→B | ✅ | § Governance: MAJOR/MINOR/PATCH; «El Constitution Check… verifica el compliment» | No diu qui aprova una esmena ni que cal sincronitzar `AGENTS.md` i plantilles (inferència: ho fa `/speckit-constitution`) |
| G0-E05 | Registre de canvis | R | A | ✅ | 6 commits a git | Coherent amb el principi VIII |
| G0-Q01 | Principis normatius i verificables | O | A→B | ⚠️ | II: «amb canvis petits» | «Canvis petits» no és verificable. La resta, sí (veure §4) |
| G0-Q02 | Raó per principi | R | A→B | ⚠️ | «Raó:» només a I i III | II, IV–VIII sense raó ni ADR citat |
| G0-Q03 | Sense contradiccions | O | B | ✅ | V («un valor derivat no es desa») coherent amb spec 001 § Valors derivats | Cap contradicció entre principis ni amb els ADR acceptats 0003–0008 i 0011 |
| G0-Q04 | Principis de projecte | R | B | ✅ | | VII inclou detall operatiu (sintaxi del marcador pytest); acceptable perquè és la convenció de traçabilitat |
| G0-Q05 | Mecanisme de compliment per principi | O | B | ✅ | Constitution Check a `overrides/plan-template.md` cobreix I–VIII | Només I i VII tenen comprovació automàtica (§4) |
| G0-C05 | Fonts normatives existeixen | O | A | ✅ | consola OK | |
| G0-C06 | Portes de `verify.sh` | O | A→B | ✅ | ruff, format, mypy, import-linter, pytest, traçabilitat; § Seguretat: `.gitignore`, `.env` no versionat, cap clau al repo | «Clau API llegible» fa fallar `verify.sh` sense clau real |
| G0-P01 | SDD | R | A→B | ✅ | II «Tota feina parteix d'una spec» | |
| G0-P02 | Sortides validades | R | A→B | ✅ | IV «comprovació determinista que valida la sortida» | |
| G0-P03 | MCP | R | A→B | ⚠️ | no trobat | Probablement no aplica, però falta justificació escrita (N/A·j) |
| G0-P04 | Dades local/núvol | R | A→B | ⚠️ | no trobat | Hi ha LLM al núvol (clau API a `verify.sh`) i no hi ha regla |
| G0-P05 | PII | R | A→B | ⚠️ | no trobat | L'id opac (n + 4 dígits) ho facilita, però cap principi ni ADR prohibeix enviar nom o cognoms a l'LLM |
| G0-P06 | HITL | R | A→B | ✅ | IV «El sistema avisa; el coach decideix» | |
| G0-P07 | Aïllament i VCS | R | A→B | ⚠️ | II «Cada branca porta una sola spec»; «La v1 només es pot llegir» | VCS cobert. Aïllament d'execució no tractat (justificable com a N/A·j en ús local) |
| G0-P08 | Observabilitat | R | A→B | ⚠️ | consola: «registren» | Fals positiu: es refereix als avisos (IV), no a temps, cost o tokens de l'LLM |
| G0-P09 | Avaluació | R | A→B | ⚠️ | no trobat | IV valida cada sortida, però no hi ha joc de referència per avaluar els judicis LLM |
| G0-P10 | Proves | R | A→B | ✅ | VII | |
| G0-C01 | `CLAUDE.md`/`AGENTS.md` coherents | O | A→B | ✅ | `AGENTS.md` § Principis i decisions | Coherent amb VII (mode avís de traçabilitat) |
| G0-C02 | Constitution Check alineat | R | A→B | ✅ | `overrides/plan-template.md`: un ítem per principi I–VIII | |
| G0-C03 | Plantilla de spec | R | B | ✅ | `overrides/spec-template.md`: Estat, CA-ID, Donat/quan/aleshores, Business Rules, referències normatives | La spec 001 no segueix aquesta plantilla (es tracta al G1) |
| G0-C04 | `settings.json` reforça la constitució | R | A→B | ⚠️ | `allow: Bash(bash scripts/verify.sh)`, `Bash(uv run:*)`; hook `Stop` executa ruff, mypy i lint-imports | Contradiu `AGENTS.md` («No executis… verify.sh, tests, git, uv»). No impedeix editar la v1 |

## 4. Anàlisi dels principis

| Principi | Verificable | Raó | Mecanisme | Pilars |
|---|---|---|---|---|
| I Capes | Sí | Explícita | import-linter (`verify.sh`, hook Stop) | P07 |
| II Primer la spec | Parcial: «canvis petits» no | No | Constitution Check; `AGENTS.md` | P01, P07 |
| III RN única font | Sí | Explícita | Constitution Check; G1-Q04 d'`auditar.sh` (existència de RN) | — |
| IV Avisa / coach decideix | Sí (tests) | No | Constitution Check; comprovació determinista per RN judici LLM | P02, P06, P09 parcial |
| V Dades honestes | Sí (tests, revisió) | No | Constitution Check | — |
| VI Pla versionat | Sí, quan hi hagi spec del pla | No | Constitution Check | — |
| VII Traçabilitat | Sí | No | `check_tracabilitat.py` a `verify.sh` | P10 |
| VIII Genèrics | Sí (cerca de dates i noms) | No | Constitution Check; G1-Q07 d'`auditar.sh` | — |

FETS: taula verificada als fitxers citats. INFERÈNCIA: la clau API de `verify.sh` és d'un LLM al núvol (Anthropic) que rebrà dades dels nedadors quan s'implementin els judicis LLM.

## 5. Accions recomanades

| Prioritat | Acció | Resol | Com |
|---|---|---|---|
| Alta | Regla de dades cap a l'LLM: només id opac i dades d'entrenament; mai nom ni cognoms; quines crides poden anar al núvol | P04, P05 | ADR nou + línia al principi IV (`/speckit-constitution`, MINOR → 1.3.0). Termini: abans de la primera spec amb judici LLM |
| Mitjana | Treure «amb canvis petits» o definir-ho | Q01 | Mateixa esmena 1.3.0 |
| Mitjana | Alinear `settings.json` amb `AGENTS.md`: treure els `allow` de `verify.sh` i `uv run`, decidir si el hook `Stop` es manté, afegir `deny` d'edició a `../ws_blondswim/**` | C04 | Editar `.claude/settings.json` |
| Mitjana | Afegir «Raó:» a II, IV, V, VI, VII i VIII (una línia o referència a ADR) | Q02 | Mateixa esmena 1.3.0 |
| Baixa | Secció «Fora d'abast» amb N/A·j per a MCP i aïllament d'execució; observabilitat (cost i tokens) i joc de referència dels judicis LLM, diferits a la spec que introdueixi l'LLM | P03, P07, P08, P09 | Mateixa esmena 1.3.0 |
| Baixa | Automatitzar III i VIII a `verify.sh` (RN referenciades existeixen; dates en documents normatius) | Q05 | `scripts/verify.sh` |

## 6. Falsos positius de la Part A
- **G0-P08:** «registren» correspon als avisos persistents, no a observabilitat. Treure la paraula del patró.
- **G0-P07:** «branca» només cobreix VCS, no aïllament. Correcte com a pista; deixar-ho.

## Aprovació
- Veredicte:
- Aprovador:
- Data:
- Falsos positius marcats:
- Condicions i terminis:
