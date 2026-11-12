# ADR-0023 — Alias llegible escrit pel coach

**Estat:** Acceptat (2026-11-11). Substitueix la forma de l'alias de RN-003 (ADR-0014). Matisa la decisió de no desar nom ni cognoms.

## Context
Fins ara l'alias era `<part>_<sufix>`, amb el sufix pres de l'UUID. Era únic però il·legible, aleatori (dues passades d'importació generaven alias diferents) i obligava a confirmar-lo. Amb la fitxa com a canal d'entrada (ADR-0021), el coach ja escriu la part de l'alias.

## Decisió
- **L'alias l'escriu el coach** a la fila `alias` de la fitxa, seguint la seva convenció (recomanada: inicial del nom + fins a 8 caràcters del cognom). El sistema **no rep ni desa nom ni cognoms**; només valida el format.
- **Format (RN-003):** `^[a-z0-9]{2,9}(\d{2})?$`. Minúscules, sense accents ni signes (mateixa normalització que el slug de competicions, sense guions). Únic entre tots els nedadors, arxivats inclosos. Immutable.
- **Alta explícita:** `blondswim importar fitxa <camí> --alta`. Amb `--alta`, l'alias de la fitxa és una proposta: si ja existeix, el sistema hi afegeix el primer sufix lliure de dos dígits (`01`…`99`) i ho mostra a l'informe. Sense `--alta`, l'alias ha d'existir (actualització); si no existeix, error.
- L'alias és determinista: la primera i la segona passada de la importació donen el mateix resultat. No cal confirmar-lo.
- L'alias és el nom del fitxer d'inscripcions (`inscripcions_<alias>.csv`), l'argument `--alias` i l'identificador als informes i al registre d'avisos. Pot contenir un cognom: és una dada personal com el correu, viu a `data/` (no versionat) i no arriba a cap LLM.
- L'UUID continua sent l'id i el nom de la carpeta (ADR-0014). Simplificació futura possible: carpeta = alias.

## Alternatives
- **Part + sufix UUID (fins ara):** descartat; aleatori, il·legible, obliga a confirmar.
- **Alias generat pel sistema a partir de nom i cognom entrats a la fitxa:** descartat; introdueix els noms al sistema.
- **Distingir alta i actualització pel contingut de la fitxa:** descartat; una col·lisió d'alias es confondria amb una actualització. El senyal és `--alta`.
- **Carpeta = alias (retirar l'UUID):** diferit; toca RN-001/002 i codi implementat.

## Conseqüències
- Spec 001: RN-003 reescrita; CA-001-46, 51, 52 i 61 reescrits; CA-001-68 retirat; § Modificació sense canvis (l'alias continua immutable).
- Spec 002: fila `alias` de la fitxa sense la distinció sufix/no sufix; ordre `--alta`; RN-041 es reformula (alias existent amb `--alta` → sufix numèric, avís informatiu).
- Pla 002, fase 0: migrar la generació d'alias al format nou.
- Dades existents a `data/`: cap nedador real desat encara; si n'hi hagués, caldria migració.
