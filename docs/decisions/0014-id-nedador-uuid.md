# ADR-0014 — L'id del nedador és un UUID

**Estat:** Acceptat. Esmena la spec 001 (RN-001, RN-002, RN-003).

## Context
La spec 001 fixava l'id del nedador com `n` + 4 dígits, assignat de manera seqüencial. Un id seqüencial es pot endevinar i revela quants nedadors hi ha. Si l'aplicació s'exposa algun dia a un endpoint, això facilita l'accés a dades d'altres nedadors quan falla l'autorització (IDOR). Ara no hi ha codi ni dades, i el canvi no té cost de migració.

## Decisió
- L'id del nedador és un UUID v4 en forma canònica en minúscules (`xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`, amb `y` entre `8` i `b`).
- L'id continua sent el nom de la carpeta (`nedadors/<id>/`) i no es repeteix dins del fitxer.
- L'id el genera el sistema en crear el nedador. No canvia mai i no es reutilitza.
- A la CLI, el nedador s'identifica per id o per `alias` (RN-003).

## Alternatives
- **Mantenir `n` + 4 dígits:** descartat, perquè l'id es pot endevinar.
- **Id intern seqüencial i UUID només a l'exterior:** descartat, perquè són dues fonts per a una sola identitat.

## Conseqüències
- L'UUID no substitueix l'autorització: qualsevol endpoint futur ha de comprovar que l'usuari té accés a cada nedador. Es decidirà en un ADR propi quan hi hagi un endpoint (`BACKLOG.md`).
- El format de l'id es valida abans de construir cap ruta de fitxer.
- L'alias és obligatori, immutable i porta com a sufix els 7 primers caràcters de l'id (RN-003). És la manera còmoda d'identificar el nedador a la CLI.
