# Implementation Plan: Model de domini

**Branch**: `001-model-domini` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-model-domini/spec.md`

## Summary

Implementar les entitats, els invariants i el format JSON de la spec 001: nedador (identificat per correu), tests CSS, millors registres, catàleg de competicions i inscripcions per temporada. També les operacions de gestió que els CA exigeixen i les dues validacions: model vàlid i aptitud per planificar.

Enfocament:
- Domini pur amb objectes de valor immutables.
- Mappers JSON explícits a `infrastructure`, amb biblioteca estàndard.
- Definicions de RN-030 i RN-031 com a constants del domini (principi V, 1.3.0).
- Lectura JSON amb Pydantic estricte a `infrastructure`.
- Registre d'avisos a `data/avisos.jsonl`.
- Escriptura determinista.

Sense LLM. El rellotge només s'injecta per registrar avisos.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Pydantic v2, només a `infrastructure` i en mode estricte (research R1)

**Storage**: fitxers JSON a `data/` i registre `data/avisos.jsonl` (no versionats)

**Testing**: pytest amb `@pytest.mark.ca`, mypy estricte, import-linter, ruff (`verify.sh`)

**Target Platform**: macOS local (Mac del coach)

**Project Type**: biblioteca amb casos d'ús. La CLI queda fora d'abast

**Performance Goals**: N/A. Escala petita

**Constraints**: domini sense I/O, LLM, rellotge ni dependències externes; escriptura estable byte a byte (CA-001-36); errors en català amb fitxer, camp i valor

**Scale/Scope**: desenes de nedadors i de competicions per temporada; 48 CA, 3 dels quals pendents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Arquitectura per capes:** objectes de valor, entitats i validació a `domain`; casos d'ús i ports a `application`; JSON i paràmetres a `infrastructure`. Sense imports cap amunt. El domini no té cap dependència externa.
- [x] **II. Primer la spec:** totes les regles surten de la spec 001 i de `docs/regles.md`. No queda cap `NEEDS CLARIFICATION`.
- [x] **III. Regles de negoci identificades i amb una sola font:** el codi cita les RN per ID. RN-030 i RN-031 s'implementen a `domain/definicions.py`; la font és `docs/regles.md` (research R2).
- [x] **IV. El sistema avisa; el coach decideix:** errors i avisos acumulats amb motiu; avisos registrats a `data/avisos.jsonl` (research R5; CA-001-47, 48).
- [x] **V. Dades honestes:** temporada, setmana, test vigent i proves objectiu es deriven. No hi ha valors per defecte en carregar. Només hi ha constants per a definicions (RN-030, RN-031), com permet la versió 1.3.0.
- [x] **VI. El pla es persisteix i es versiona:** no aplica. La 001 no genera plans.
- [x] **VII. Traçabilitat de la spec al test:** cada tasca porta capa; cada CA no pendent té test amb `@pytest.mark.ca`. La traçabilitat passa a «bloquejant» al primer commit d'implementació.
- [x] **VIII. Documents genèrics i sense història:** els exemples de contracte fan servir valors fictius.

**Re-check post-disseny:** compleix tots els principis.

## Project Structure

### Documentation (this feature)

```text
specs/001-model-domini/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── fitxers-json.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
src/blondswim/
├── domain/
│   ├── valors.py              # IdNedador, Correu, Alias, Estil, Dia, Piscina, Temps, Prova, Classe, Prioritat, CodiTemporada
│   ├── definicions.py         # RN-030 proves oficials, RN-031 inici de temporada
│   ├── nedador.py             # Nedador, TestCss, DetallProva, MillorRegistre
│   ├── cataleg.py             # Competicio, Cataleg
│   ├── inscripcions.py        # Participacio, Inscripcio
│   ├── derivats.py            # temporada, setmana ISO, test vigent, proves objectiu
│   └── validacio.py           # Resultat, ErrorValidacio, Avis; model vàlid i aptitud
├── application/
│   ├── ports.py               # RepositoriNedadors, RepositoriCataleg, RegistreAvisos, Rellotge (Protocols)
│   ├── carrega.py             # carregar i registrar els avisos
│   └── gestio.py              # crear, arxivar, esborrar, canviar correu, registrar/acceptar test, esborrar competició
└── infrastructure/
    ├── json_io.py             # escriptura estable (R3)
    ├── dto.py                 # models Pydantic estrictes (R1)
    ├── mappers.py             # DTO ↔ domini; errors en català amb fitxer/camp/valor
    ├── repositoris.py         # implementació dels ports sobre data/
    ├── registre_avisos.py     # data/avisos.jsonl, només afegir
    └── rellotge.py            # Rellotge del sistema

tests/
├── unit/                      # domini i casos d'ús amb repositoris en memòria
└── integration/               # fitxers reals amb tmp_path
```

**Structure Decision**: estructura existent de quatre capes (principi I). `interfaces` no es toca en aquesta spec.

## Complexity Tracking

Cap violació per justificar.
