# ADR-0011 — Sessió de test CSS sense tècnica

**Estat:** Acceptat. Esmena l'ADR-0004 en un sol punt.

## Context
Una sessió d'entrenament i un test CSS tenen objectius diferents. El test busca un resultat comparable d'un test a un altre. Un bloc de tècnica abans del test hi afegeix una variable que no serveix a aquest objectiu.

## Decisió
- La sessió de test CSS no té bloc de tècnica.
- La resta de l'estructura de l'ADR-0004 es manté: escalfament, principal I, recuperació a A0 entre principals, principal II i tornada a la calma.
- El contingut de cada part el fixa el protocol del test (spec 000, §9).

## Alternatives
- **Estructura completa amb una tècnica fixa:** descartat. La tècnica no serveix a l'objectiu del test i en fa variar les condicions.
- **Tipus de sessió propi, fora de l'ADR-0004:** descartat. L'estructura de l'ADR-0004 s'hi adapta, excepte la tècnica.

## Conseqüències
- La regla d'una sola part de tècnica (`docs/regles.md`) té una excepció per a la sessió de test CSS.
- La plantilla de la sessió de test és de la spec 006.
