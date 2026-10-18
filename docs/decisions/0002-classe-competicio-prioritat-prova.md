# ADR-0002 — Classe per competició, prioritat per prova

**Estat:** Substituït per l'ADR-0006

## Context
Una competició té diverses proves (estil + distància), i el nedador en pot nedar diverses el mateix dia.
La jerarquia A/B/C s'inspira en la de TrainingPeaks: A = objectiu de temporada amb pic de forma; B = competició exigent sense taper complet; C = competició integrada en l'entrenament, sense descàrrega prèvia. El tractament concret de cada classe el fixa la spec 003.

## Decisió
- La classe (A/B/C) és un atribut de la competició.
- Cada prova on participa el nedador té una prioritat: principal o secundària.
- Les competicions A són els objectius. Les B i les C serveixen per avaluar la progressió.

## Alternatives
- Classe per prova: descartat. Barreja la importància de la competició amb la importància de la prova dins de la competició.

## Conseqüències
- La periodització es construeix a partir de les competicions A.
- El pes de l'entrenament específic depèn de la prioritat de cada prova.
