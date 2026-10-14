# BlondSwim v2.0

Planificador d'entrenaments de natació per a 4 nedadors (Jep, Lou, Cris, Pere).
Periodització per objectius A/B/C, mesocicles planificats cap enrere des de l'objectiu A.

## Arquitectura (Clean Architecture, verificada per import-linter)
- `domain/`: entitats i regles pures. Sense I/O, sense LLM, sense dependències externes.
- `application/`: casos d'ús i ports (Protocols).
- `infrastructure/`: JSON, Excel, clients LLM, secrets.
- `interfaces/`: CLI.
Una capa només importa capes inferiors.

## Decisions fixades (no les canviïs sense ADR a docs/decisions/)
- Una carpeta per nedador a `data/`; el nom de carpeta és l'ID.
- JSON = font de veritat; Excel = només sortida.
- Catàleg de competicions compartit; calendari A/B/C per nedador.
- LLM només en punts de judici; tota la resta és determinista.
- Sèries prescrites com a zona + descans (cada nedador aplica el seu ritme).
- Sessió amb estructura fixa: escalfament, tècnica, nucli, tornada a la calma.

## Regles de treball
- Treballa sempre a partir d'una spec de `specs/`. Si no n'hi ha, atura't i demana-la.
- No inventis regles de negoci: si la spec no ho diu, pregunta.
- Canvis petits, una spec per branca.
- Executa amb `uv run`. Dependències només amb `uv add`.
- Abans de donar una tasca per acabada: `bash scripts/verify.sh` en verd.

## Ordres
- Verificació completa: `bash scripts/verify.sh`
- Tests: `uv run pytest`