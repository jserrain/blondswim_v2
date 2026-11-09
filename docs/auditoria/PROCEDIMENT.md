# Procediment d'auditoria de specs (Spec Kit + Claude Code)

> Versió 2.1 · 2026-10-23 · Document de suport, no normatiu (constitució, «Fonts normatives»).
> Referència de criteris: **constitució de BlondSwim v2** (obligatoris) + **pilars d'AprenIA** (recomanats, admeten N/A justificat).

---

## 1. Objectiu i abast

Verificar, abans de passar a la fase següent de Spec Kit, que els artefactes:
1. existeixen i segueixen la **seqüència** correcta,
2. compleixen la **constitució** i les convencions del projecte (CA, RN, Estat, fonts normatives),
3. cobreixen els **pilars d'AprenIA** que apliquen al projecte.

Flux: `constitution → specify → clarify → checklist → plan → tasks → analyze → implement`
(comandes instal·lades com a skills: `/speckit-constitution`, `/speckit-specify`, `/speckit-clarify`…).

| Gate | Quan | Què audita | Bloqueja |
|---|---|---|---|
| **G0 Constitució** | Després de `/speckit-constitution` o d'una esmena | `.specify/memory/constitution.md`, fonts normatives, plantilles, configuració | `/speckit-specify` |
| **G1 Spec** | Després de `specify` + `clarify` (+ `checklist`) | `specs/NNN-nom/spec.md` | `/speckit-plan` |
| **G2 Pla** | Després de `plan` + `tasks` (inclou l'anàlisi de `/speckit-analyze`) | `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `tasks.md` | `/speckit-implement` |

---

## 2. Separació de responsabilitats

| Part | On | Tipus | Fa | No fa |
|---|---|---|---|---|
| **A. Consola** | Terminal, `scripts/auditar.sh` | Determinista, sense LLM | Existència, formats, IDs, referències creuades, seqüència. Dona **pistes** per als A→B | Jutjar si un text és clar, coherent o adequat |
| **B. Claude Code** | Sessió nova, `/auditar` | Semàntica (LLM) | Jutja qualitat, coherència i cobertura; escriu l'informe | Repetir la Part A; modificar artefactes |
| **C. Humà** | — | Decisió | Valida l'informe i signa el veredicte | — |

**Regla:** si la Part A dona alguna `FALLA`, es corregeix abans de la Part B.

Estats de la Part A: `OK` (criteri A complert) · `FALLA` (bloqueja) · `AVÍS` (no bloqueja) · `PISTA` (s'ha trobat alguna cosa; **no** vol dir que el criteri es compleixi) · `INFO` (dada per a la Part B).

Columna **Qui**: **A** = consola sola · **A→B** = consola dona pista, Claude Code decideix · **B** = només Claude Code.

---

## 3. Passos

### Part A — Consola
```bash
bash scripts/auditar.sh constitution                  # → docs/auditoria/g0-mecanic-AAAA-MM-DD.txt
bash scripts/auditar.sh spec specs/001-model-domini   # → docs/auditoria/g1-001-mecanic-AAAA-MM-DD.txt
bash scripts/auditar.sh plan specs/001-model-domini   # → docs/auditoria/g2-001-mecanic-AAAA-MM-DD.txt
echo $?                                               # 0 = cap FALLA · 1 = alguna FALLA
```
L'script desa la sortida ell mateix (no cal `tee`) i conserva el codi de sortida. `BASE=<branca>` canvia la branca base de G1-S04 i G2-S05 (per defecte `main`).

### Part B — Claude Code
En una **sessió nova** (no la que ha generat l'artefacte), en mode normal (no *plan mode*: cal escriure l'informe):
```
/auditar constitution
/auditar spec specs/001-model-domini
/auditar plan specs/001-model-domini
```
La comanda només pot llegir i escriure a `docs/auditoria/`. Genera `docs/auditoria/g0-constitucio-AAAA-MM-DD.md`, `g1-NNN-AAAA-MM-DD.md` o `g2-NNN-AAAA-MM-DD.md`. Una re-auditoria afegeix el sufix `-rN`.

### Part C — Humà
1. Llegir l'informe i marcar falsos positius.
2. Signar la secció `## Aprovació`.
3. Corregir els `❌` amb la comanda Spec Kit corresponent (`/speckit-constitution`, `/speckit-clarify`…) o editant la font.
4. Re-auditar (A → B → C) fins que el gate passa. Es conserven tots els informes.

---

## 4. Escala i veredicte

| Valor | Significat |
|---|---|
| ✅ | Complet i amb evidència |
| ⚠️ | Parcial o ambigu |
| ❌ | Falta o contradiu |
| N/A·j | No aplica, **amb justificació escrita** a la constitució, un ADR o la spec (cal citar-la). Sense justificació escrita → ⚠️ |
| N/A | No aplica en aquest gate |

| Veredicte | Condició |
|---|---|
| **Passa** | Cap ❌ en criteris O; cap ⚠️ en O |
| **Passa amb condicions** | Cap ❌ en O; ⚠️ amb acció i termini |
| **No passa** | Algun ❌ en un criteri O |

Només els criteris **R** admeten N/A·j.

---

## 5. Criteris del Gate 0 — Constitució

### 5.1 Estructura

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G0-E01 | Existeix `.specify/memory/constitution.md` | O | A |
| G0-E02 | Sense marcadors de plantilla (`[PROJECT_NAME]`, `[PRINCIPLE_…]`, `TODO`) fora de comentaris HTML | O | A |
| G0-E03 | `**Version**` semver, `**Ratified**` i `**Last Amended**` en AAAA-MM-DD; esmena ≥ ratificació i no futura | O | A |
| G0-E04 | Secció de governança (A) que explica com s'esmena, es versiona i es comprova el compliment (B) | O | A→B |
| G0-E05 | Registre de canvis: *Sync Impact Report* **o** historial git del fitxer (el principi VIII envia la història a git) | R | A |

### 5.2 Qualitat dels principis

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G0-Q01 | Principis numerats (A); cadascun és normatiu i verificable. El present indicatiu normatiu («una capa només importa…») és vàlid (B) | O | A→B |
| G0-Q02 | Cada principi té raó explícita o l'aporta un ADR citat | R | A→B |
| G0-Q03 | No hi ha principis contradictoris entre si ni amb els ADR acceptats | O | B |
| G0-Q04 | Els principis són de projecte, no detalls d'una funcionalitat | R | B |
| G0-Q05 | Cada principi té un mecanisme de compliment identificable (eina de `verify.sh`, *Constitution Check*, revisió) | O | B |

### 5.3 Fonts normatives i portes de qualitat

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G0-C05 | Existeixen les fonts normatives que declara la constitució: `docs/regles.md`, ADR a `docs/decisions/`, spec 000 | O | A |
| G0-C06 | `scripts/verify.sh` inclou les portes que la constitució declara (ruff, format, mypy, import-linter, pytest, traçabilitat) (A) i les comprovacions de seguretat declarades (B) | O | A→B |

### 5.4 Pilars d'AprenIA (recomanats)

La consola mostra les paraules trobades (`PISTA`). Claude Code decideix si el pilar està recollit com a principi, si no aplica (N/A·j) o si falta.

| ID | Pilar | Tipus | Qui | Principi relacionat |
|---|---|---|---|---|
| G0-P01 | Spec-Driven: cap codi sense spec aprovada | R | A→B | II |
| G0-P02 | Sortides estructurades validades amb schema | R | A→B | IV (comprovació determinista) |
| G0-P03 | MCP com a estàndard d'integració d'eines | R | A→B | — |
| G0-P04 | Classificació de dades i regla local vs núvol | R | A→B | — |
| G0-P05 | Dades personals (PII) protegides abans d'enviar-les a APIs externes | R | A→B | — |
| G0-P06 | Accions sensibles i aprovació humana (HITL) | R | A→B | IV |
| G0-P07 | Entorn aïllat i control de versions | R | A→B | II (branca per spec) |
| G0-P08 | Observabilitat (temps, cost, tokens) | R | A→B | IV (registre d'avisos) |
| G0-P09 | Avaluació: criteris convertibles en evals / golden set | R | A→B | IV, VII |
| G0-P10 | Estratègia de proves | R | A→B | VII |

### 5.5 Coherència i propagació

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G0-C01 | `CLAUDE.md` o els fitxers que importa amb `@` (p. ex. `AGENTS.md`) remeten a la constitució (A) i no la contradiuen (B) | O | A→B |
| G0-C02 | La plantilla de pla efectiva (`overrides/` si existeix) té *Constitution Check* (A) alineat amb els principis I–VIII (B) | R | A→B |
| G0-C03 | La plantilla de spec efectiva inclou el que exigeix la constitució: CA-ID, Donat/quan/aleshores, RN, Estat | R | B |
| G0-C04 | `.claude/settings.json` és JSON vàlid (A) i els permisos i hooks reforcen la constitució (B) | R | A→B |

---

## 6. Criteris del Gate 1 — Spec

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G1-S01 | Carpeta `specs/NNN-nom/spec.md` i branca igual al nom de la carpeta | O | A |
| G1-S02 | Clarify registrat: secció `## Clarifications` (també si es va fer fora de la comanda) | O | A |
| G1-S03 | Checklist a `checklists/` (A); ítems pendents resolts o justificats (B) | R | A→B |
| G1-S04 | Sense `plan.md`, `tasks.md` ni canvis a `src/` o `tests/` respecte de la branca base. En re-auditoria (hi ha un informe G1 anterior), el pla, les tasques i el codi existent donen INFO; per comprovar que l'esmena no toca codi, `BASE=<commit previ a l'esmena>` | O | A |
| G1-S05 | Línia `**Estat:**` present (A); coherent amb el moment del gate (B) | O | A→B |
| G1-Q01 | Històries prioritzades P1, P2… provables de manera independent | R | A→B |
| G1-Q02 | Criteris `- **CA-NNN-nn**` amb Donat/quan/aleshores (A); escenaris complets i casos límit (B) | O | A→B |
| G1-Q03 | CA únics i amb el número de la spec | O | A |
| G1-Q04 | Totes les `RN-NNN` referenciades existeixen a `docs/regles.md` i no estan retirades (A); la spec no en repeteix el contingut (B, principi III) | O | A→B |
| G1-Q05 | Zero `[NEEDS CLARIFICATION]` (A, O) i secció `## Assumptions` (A, R) | O/R | A |
| G1-Q06 | Descriu QUÈ i PER QUÈ, no COM | O | B |
| G1-Q07 | Document genèric: no anomena nedadors, competicions ni dates concretes fora d'exemples (principi VIII) | O | A→B |
| G1-Q08 | Si hi ha `FR-NNN`/`SC-NNN`, són provables, mesurables i sense tecnologia | R | B |
| G1-A01 | Cap requisit contradiu la constitució, els ADR acceptats ni el glossari | O | B |
| G1-A02 | Dades personals i accions sensibles identificades | R | A→B |
| G1-A03 | Punts de judici LLM identificats com a RN de tipus judici LLM (principi IV) | R | B |

---

## 7. Criteris del Gate 2 — Pla i tasques

Inclou l'anàlisi de coherència de `/speckit-analyze` (duplicats, ambigüitats, buits de cobertura, inconsistències i alineació amb la constitució).

### 7.1 Estructura i seqüència

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G2-S01 | Existeixen `plan.md`, `tasks.md`, `research.md` i `data-model.md` (O); `quickstart.md` i `contracts/` (R) | O/R | A |
| G2-S02 | Zero `NEEDS CLARIFICATION` al pla, la recerca i el data model; spec `Aprovada` | O | A |
| G2-S03 | *Constitution Check* sense caselles buides i amb tots els principis (A); cada ✓ és cert segons el pla (B) | O | A→B |
| G2-S04 | Tota violació o compliment parcial està justificat a *Complexity Tracking* | O | A→B |
| G2-S05 | Sense canvis a `src/` ni `tests/` respecte de la branca base | O | A |

### 7.2 Tasques

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G2-T01 | Format `- [ ] TNNN [P?] [USn?] [capa] descripció`, amb una sola capa per tasca (principi VII) | O | A |
| G2-T02 | IDs únics (O) i consecutius (R) | O/R | A |
| G2-T03 | Cada tasca indica el fitxer o la comanda | R | A→B |
| G2-T04 | Ordre correcte: tests abans de la implementació; dependències entre blocs coherents | O | B |
| G2-T05 | Cada element del data model i de l'estructura del pla té almenys una tasca | R | A→B |

### 7.3 Traçabilitat i coherència

| ID | Criteri | Tipus | Qui |
|---|---|---|---|
| G2-Q01 | Cada CA no pendent té almenys una tasca de test | O | A |
| G2-Q02 | Cap tasca cita un CA inexistent o pendent | O | A |
| G2-Q03 | Les RN citades al pla, la recerca, el data model i les tasques existeixen | O | A |
| G2-Q04 | Les capes del pla tenen tasques | R | A |
| G2-Q05 | El pla no afegeix regles ni requisits que no siguin a la spec, a `regles.md` o als ADR (principi II) | O | B |
| G2-Q06 | El data model és coherent amb la spec: camps, obligatorietat, `null`, derivats | O | B |
| G2-Q07 | Cada decisió de `research.md` té raó i alternatives | R | B |
| G2-Q08 | Terminologia coherent entre spec, glossari, pla i tasques; sense duplicats ni contradiccions | R | B |

---

## 8. Registre

| Fitxer | Generat per |
|---|---|
| `docs/auditoria/g0-mecanic-AAAA-MM-DD.txt` · `g1-NNN-mecanic-AAAA-MM-DD.txt` · `g2-NNN-mecanic-AAAA-MM-DD.txt` | Part A |
| `docs/auditoria/g0-constitucio-AAAA-MM-DD.md` · `g1-NNN-AAAA-MM-DD.md` · `g2-NNN-AAAA-MM-DD.md` | Part B |
| Secció `## Aprovació` de l'informe | Part C |

```markdown
## Aprovació
- Veredicte: Passa / Passa amb condicions / No passa
- Aprovador: <nom>
- Data: AAAA-MM-DD
- Falsos positius marcats: …
- Condicions i terminis: …
```

---

## 9. Manteniment

- Quan la constitució s'esmeni, revisar 5.2–5.5, 6 i 7 perquè segueixin els principis vigents.
- Si un criteri **B** es pot comprovar amb una regla fixa, passar-lo a **A**.
- Si un criteri **A** dona falsos positius sovint, passar-lo a **A→B** (sortida `PISTA`).
- Provar `auditar.sh` a macOS (bash 3.2, grep BSD) després de cada canvi.
- Referents: NIST AI RMF (Govern/Map), NIST SSDF (PO.1), OWASP Top 10 LLM i Agentic, CRISP-ML(Q).

