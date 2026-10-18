# BlondSwim v2.0

Planificador d'entrenaments de natació multi-nedador.
Periodització per objectius A/B/C, mesocicles planificats cap enrere des de l'objectiu A.

## Arquitectura (Clean Architecture, verificada per import-linter)
- `domain/`: entitats i regles pures. Sense I/O, sense LLM, sense dependències externes.
- `application/`: casos d'ús i ports (Protocols).
- `infrastructure/`: JSON, Excel, clients LLM, secrets.
- `interfaces/`: CLI.
Una capa només importa capes inferiors.

## Decisions fixades (no les canviïs sense ADR a docs/decisions/)
- Una carpeta per nedador a `data/`; el nom de carpeta és l'ID.
- L'Excel de calendari i el d'inscripcions són entrades; la importació els converteix a JSON i el sistema només llegeix JSON. Els Excels que genera el sistema són només sortida (ADR-0007).
- Catàleg comú de competicions per temporada; inscripcions per nedador amb classe A/B/C per participació i prioritat principal/secundària per prova (ADR-0006).
- L'històric d'entrenaments és un arxiu de referència per al coach; no és font de sessions ni es passa a l'LLM (ADR-0003).
- Sessió: escalfament, tècnica, principal I, principal II (opcional), tornada a la calma (ADR-0004).
- Biblioteca d'exercicis de tècnica per estil, confeccionada pel coach; el sistema indica el bloc i els metres de tècnica (ADR-0005).
- LLM només en punts de judici; tota la resta és determinista.
- Sèries prescrites com a zona + descans (cada nedador aplica el seu ritme).

## Regles de treball
- Treballa sempre a partir d'una spec de `specs/`. Si no n'hi ha, atura't i demana-la.
- No inventis regles de negoci: si la spec no ho diu, pregunta.
- Specs, ADR i codi són genèrics: mai no anomenen un nedador, una competició ni una data concreta (només als tests i als exemples).
- Els documents i el codi de la v1 són només referència històrica. Una regla de la v1 no és vàlida fins que no queda recollida en un ADR o en una spec.
- Canvis petits, una spec per branca.
- Executa amb `uv run`. Dependències només amb `uv add`.
- Abans de donar una tasca per acabada: `bash scripts/verify.sh` en verd.

## Ordres
- Verificació completa: `bash scripts/verify.sh`
- Tests: `uv run pytest`
