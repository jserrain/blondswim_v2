# ADR-0001 — Calendari de competicions per nedador

**Estat:** Substituït per l'ADR-0006

## Context
El producte és multi-nedador. Cada nedador participa en competicions diferents, amb classes i proves diferents.

## Decisió
Cada nedador té el seu calendari per temporada, dins del seu espai. No hi ha catàleg comú de competicions.

## Alternatives
- Catàleg comú amb inscripcions per nedador: descartat. Crea dependències entre nedadors i un model més complex del que cal al nucli mínim.

## Conseqüències
- Si dos nedadors van a la mateixa competició, cadascun la té al seu calendari.
- Un canvi de data s'actualitza a cada calendari. Cost acceptat.
