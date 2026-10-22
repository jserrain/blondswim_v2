# ADR-0004 — Estructura de la sessió

**Estat:** Acceptat. Substitueix l'estructura fixa de 4 parts. Esmenat per l'ADR-0011 (sessió de test CSS sense tècnica).

## Context
Un nedador pot tenir més d'una prova objectiu, i l'estructura amb un sol nucli no permet entrenar-ne dues amb qualitat a la mateixa sessió.

## Decisió
La sessió segueix aquest ordre:
1. Escalfament
2. Tècnica
3. Principal I
4. Principal II (opcional)
5. Tornada a la calma

- Quan hi ha dues proves objectiu, cada principal es pot dedicar a una prova.
- En sessions de qualitat amb principal II, entre els dos principals hi va una recuperació a A0 prou llarga per afrontar el segon bloc amb força.

## Alternatives
- Estructura de 4 parts amb un sol nucli: descartat, pel motiu exposat al context.

## Conseqüències
- La plantilla de sessió (spec 006) determina quan s'activa el principal II i la durada de la recuperació entre principals.
