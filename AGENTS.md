# BlondSwim v2.0

Planificador d'entrenaments de natació multi-nedador.
Periodització per objectius A/B/C, mesocicles planificats cap enrere des de l'objectiu A.

## Arquitectura (Clean Architecture, verificada per import-linter)
- `domain/`: entitats i regles pures. Sense I/O, sense LLM, sense dependències externes.
- `application/`: casos d'ús i ports (Protocols).
- `infrastructure/`: JSON, Excel, clients LLM, secrets.
- `interfaces/`: CLI.
Una capa només importa capes inferiors.

## Principis i decisions
Els principis són a la constitució (`.specify/memory/constitution.md`). Les decisions
vigents són als ADR acceptats de `docs/decisions/`; no les canviïs sense un ADR nou.

- ADR-0003 — Històric d'entrenaments com a arxiu de referència
- ADR-0004 — Estructura de la sessió
- ADR-0005 — Biblioteca d'exercicis de tècnica, confeccionada pel coach
- ADR-0006 — Catàleg comú de competicions i inscripcions per nedador
- ADR-0007 — Excel com a format d'entrada
- ADR-0008 — Sèries prescrites com a zona + descans

## Regles de treball
- Treballa sempre a partir d'una spec de `specs/`. Si no n'hi ha, atura't i demana-la.
- No inventis regles de negoci: si la spec no ho diu, pregunta.
- Specs, ADR i codi són genèrics: mai no anomenen un nedador, una competició ni una data concreta (només als tests i als exemples).
- Els documents i el codi de la v1 són només referència històrica. Una regla de la v1 no és vàlida fins que no queda recollida en un ADR, en una spec o a `docs/regles.md`.
- Canvis petits, una spec per branca.
- Executa amb `uv run`. Dependències només amb `uv add`.
- Abans de donar una tasca per acabada: `bash scripts/verify.sh` en verd.

## Ordres
- Verificació completa: `bash scripts/verify.sh`
- Tests: `uv run pytest`
