# ADR-0012 — Sense importació de l'històric d'entrenaments

**Estat:** Acceptat. Substitueix l'ADR-0003.

## Context
- L'històric d'entrenaments disponible no té planificació ni estructura definida, i està esbiaixat cap a les proves d'un sol nedador.
- L'ADR-0003 ja el descartava com a font de sessions i només el conservava com a arxiu de consulta per al coach. Aquest ús no aporta valor a l'objectiu de l'aplicació: el màxim rendiment a les proves de cada nedador.

## Decisió
- L'històric d'entrenaments no s'importa ni es desa al sistema.
- Les sessions es generen amb l'estructura de l'ADR-0004 (escalfament, tècnica, principal I, principal II opcional, tornada a la calma), la tècnica de la biblioteca del coach (ADR-0005) i la metodologia de les specs de planificació i composició.

## Alternatives
- Mantenir l'històric com a arxiu de consulta (ADR-0003): descartat, perquè no aporta valor i obliga a importar un format sense estructura.

## Conseqüències
- La spec 002 no tracta l'Excel d'entrenaments.
- Cap spec ni cap regla no pot fer servir l'històric com a referència.
