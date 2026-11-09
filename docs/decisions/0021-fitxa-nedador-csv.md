# ADR-0021 — Fitxa del nedador en CSV

**Estat:** Acceptat. Amplia l'ADR-0013 (no el substitueix).

## Context
L'ADR-0013 fixa dos formats d'entrada en CSV: el calendari (catàleg) i les inscripcions. Les dades del nedador (contacte, estils preferents, dies d'entrenament, volum setmanal, tests CSS i millors marques) no tenien cap canal d'entrada, i l'ADR-0013 descarta la CLI i l'edició del JSON a mà.

## Decisió
- Hi ha un **tercer CSV d'entrada: la fitxa del nedador**, una per nedador.
- El coach omple la fitxa en un full de càlcul, a partir d'una plantilla d'**un sol full**, i l'exporta a CSV amb el format de l'ADR-0013 (UTF-8, separador `;`, coma decimal). El sistema llegeix el CSV, mai el full de càlcul.
- **Alta:** el sistema genera l'id i l'alias (RN-002, RN-003) i els comunica al coach.
- **Nedador existent:** s'identifica per l'alias. La importació torna a validar el nedador sencer i substitueix les dades modificables (spec 001, § Modificació). L'id, l'alias i `versio_esquema` no canvien. Els tests CSS i les millors marques només s'afegeixen: un test nou entra sense acceptar, i una marca només s'afegeix si millora la vigent (RN-007).
- Un ERROR no desa res; mai s'inventen valors.

## Alternatives
- **Llegir el full de càlcul (.xlsx) directament:** descartat pels mateixos inconvenients que van fer descartar l'Excel com a entrada (ADR-0013).
- **CLI per a les dades del nedador:** descartat per l'ADR-0013.
- **Una sola fitxa per a tots els nedadors:** descartat; una fitxa per nedador és coherent amb el CSV d'inscripcions i aïlla els errors.

## Conseqüències
- La spec 002 defineix la plantilla (camps, ordre i taules de tests i de marques), com es distingeix una alta d'una actualització i les regles d'importació.
- Un full de càlcul amb diversos fulls exportaria diversos CSV: per això la plantilla és d'un sol full.
