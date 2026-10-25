# ADR-0013 — No s'importa l'històric d'entrenaments

**Estat:** Acceptat. Substitueix l'ADR-0003.

## Context
L'ADR-0003 preveia importar l'Excel d'entrenaments de temporades passades com a arxiu de consulta per al coach. L'històric disponible es va fer sense una metodologia explícita i està esbiaixat cap a les proves d'un sol nedador. Importar-lo no aporta valor a la planificació.

## Decisió
- No s'importa l'històric d'entrenaments de temporades passades.
- Les sessions noves es composen amb plantilla i metodologia (ADR-0004) i la tècnica de la biblioteca del coach (ADR-0005).
- L'històric no es passa mai a l'LLM com a referència.

## Alternatives
- **Importar-lo com a arxiu de consulta (ADR-0003):** descartat, perquè no aporta valor.
- **Reutilitzar sessions senceres:** descartat, per l'esbiaix d'estil i de proves.
- **Biblioteca de blocs etiquetats extreta de l'històric:** descartat, per la manca de metodologia de l'origen.

## Conseqüències
- La spec 002 no inclou la importació d'entrenaments.
- Deixa de bloquejar la spec 002 la conversió de la notació `c/` → `d/` de l'històric.
- El registre de l'execució real de la temporada en curs (spec 007) no queda afectat.
