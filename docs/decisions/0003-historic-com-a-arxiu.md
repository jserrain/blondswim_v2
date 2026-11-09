# ADR-0003 — Històric d'entrenaments com a arxiu de referència

**Estat:** Substituït per l'ADR-0012.

## Context
L'històric d'entrenaments disponible es va fer sense una metodologia explícita i està esbiaixat cap a les proves d'un sol nedador.

## Decisió
- L'històric és un arxiu de sessions passades. El consulta el coach per conèixer el tipus d'entrenament que s'ha fet.
- No és una font de sessions: les sessions noves es composen amb plantilla i metodologia.
- L'històric no es passa mai a l'LLM com a referència.

## Alternatives
- Reutilitzar sessions senceres: descartat, per l'esbiaix d'estil i de proves.
- Biblioteca de blocs etiquetats extreta de l'històric: descartat, per la manca de metodologia de l'origen.

## Conseqüències
- Cal definir plantilles de sessió (spec 006).
- La importació de l'Excel d'entrenaments (spec 002) només arxiva; no etiqueta.
- La spec 002b passa a tractar la biblioteca d'exercicis tècnics (ADR-0005).
