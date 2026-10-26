# ADR-0015 — Contacte del nedador: correu i mòbil obligatoris

**Estat:** Acceptat. Amplia la spec 001 (RN-032) amb RN-033, RN-034 i RN-035.

## Context
La spec 001 identifica la persona pel correu (RN-032) i no en desa ni el nom ni els cognoms. Cal un segon canal de contacte. Es va valorar fer el mòbil i el correu alternatius (almenys un), però això obliga a tractar quatre combinacions.

## Decisió
- Tot nedador té `correu` i `mobil`, tots dos obligatoris.
- El correu continua sent únic entre tots els nedadors, sense distingir majúscules (RN-032).
- El mòbil es desa en format E.164 (`+` i de 8 a 15 dígits) (RN-033). No ha de ser únic: si diversos nedadors el comparteixen (per exemple, el d'un pare o una mare), es genera un avís (RN-034).
- `canal_preferent` (`correu` o `mobil`) és informatiu: pot faltar sense avís. Un valor no admès és una incidència resoluble pel coach (RN-035).
- Cap identificador del sistema no deriva del correu ni del mòbil: l'id és l'UUID (ADR-0014).

## Alternatives
- **Correu i/o mòbil, almenys un:** descartat, per simplicitat.
- **Mòbil únic:** descartat, perquè germans i famílies poden compartir el mòbil d'un adult.
- **Id derivat del correu o del mòbil:** descartat, perquè canvien amb el temps i hi introduirien una dada personal (ADR-0014).

## Conseqüències
- Al fitxer només hi ha mòbils en E.164. Afegir `+34` a un número sense prefix és feina de l'entrada de dades (importació o CLI), no de la càrrega.
- La validació del format del correu i la verificació de tots dos canals queden fora d'abast d'aquesta versió.
- Quines dades de contacte poden arribar a un LLM ho fixa l'ADR pendent de dades cap a l'LLM.
