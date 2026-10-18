# ADR-0006 — Catàleg comú de competicions i inscripcions per nedador

**Estat:** Acceptat. Substitueix l'ADR-0001 i l'ADR-0002.

## Context
- Diversos nedadors van a les mateixes competicions. Amb un calendari per nedador (ADR-0001), cada canvi de data o de seu s'havia de repetir a cada calendari.
- Una mateixa competició pot tenir una importància diferent per a cada nedador. Per això la classe no pot ser un atribut de la competició (ADR-0002).
- La jerarquia A/B/C s'inspira en TrainingPeaks:
  - A: objectiu de temporada, amb pic de forma;
  - B: competició exigent, amb taper breu;
  - C: entrenament de qualitat, sense descàrrega.

## Decisió
- Hi ha un **catàleg comú de competicions** per temporada. Cada competició hi té id, nom, dates, piscina i seu.
- Cada nedador té les seves **inscripcions** per temporada, dins del seu espai:
  - **Participació:** a quina competició del catàleg va el nedador i amb quina **classe** (A/B/C). La classe és de la participació del nedador.
  - **Proves:** dia, prova i **prioritat** (principal o secundària).
- Les participacions de classe A són els objectius. Les de classe B i C serveixen per avaluar la progressió.

## Alternatives
- **Calendari per nedador (ADR-0001):** descartat, perquè duplica les dades de les competicions.
- **Classe per competició (ADR-0002):** descartat, perquè impedeix que una competició tingui una importància diferent per a cada nedador.
- **Classe per prova:** descartat, perquè barreja la importància de la competició amb la importància de la prova.

## Conseqüències
- Un canvi de data o de seu es fa una sola vegada, al catàleg.
- Cada participació ha d'apuntar a una competició que existeixi al catàleg.
- No es pot esborrar una competició que tingui participacions.
- La periodització es construeix a partir de les participacions de classe A de cada nedador.
- El pes de l'entrenament específic depèn de la prioritat de cada prova.
