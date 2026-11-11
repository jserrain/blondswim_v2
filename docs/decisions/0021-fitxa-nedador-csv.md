# ADR-0021 — Fitxa del nedador en CSV

**Estat:** Acceptat. Amplia l'ADR-0013 (no el substitueix). Revisat (2026-11-11): format `clau;valor`, estat actual.

## Context
L'ADR-0013 fixa dos formats d'entrada en CSV: el calendari (catàleg) i les inscripcions. Les dades del nedador (contacte, estils preferents, dies d'entrenament, volum setmanal, test CSS i millors marques) no tenien cap canal d'entrada, i l'ADR-0013 descarta la CLI i l'edició del JSON a mà.

Una fitxa amb seccions (dades, taula de tests, taula de marques) obliga a un lector amb files de tipus diferents, que és la normalització que l'ADR-0013 revisat vol evitar.

## Decisió
- Hi ha un **tercer CSV d'entrada: la fitxa del nedador**, una per nedador, d'un sol full.
- **Format `clau;valor`:** cada fila és una clau i el seu valor; els valors compostos van separats per `|`. Un sol tipus de fila; cap secció. Claus i ordre els fixa la spec 002. Una clau desconeguda o repetida (fora de les repetibles) és error.
- **La fitxa descriu l'estat actual del nedador**, no un històric: un test CSS per piscina com a màxim, i la millor marca actual per prova i piscina. El que el sistema conserva ho diu la spec 001 (amb l'ADR-0022 per al test CSS).
- **Identitat:** la fila `alias`. Sense sufix → **alta** (és l'`alias_part`; el sistema genera id i alias, RN-002, RN-003, i els comunica al coach). Amb sufix que coincideix amb un nedador existent → **actualització**: es torna a validar el nedador sencer i se substitueixen els camps modificables (spec 001, § Modificació); id, alias i `versio_esquema` no canvien. Amb sufix sense coincidència → error.
- **Test CSS:** entrar-lo a la fitxa és acceptar-lo: s'aplica a la següent planificació (ADR-0022).
- **Marques:** una marca només s'afegeix si millora la vigent de la mateixa prova i piscina (RN-007); si no, no es fa res.
- Un ERROR no desa res; mai s'inventen valors.
- **Ubicació i ordre:** `data/entrada/nedadors/<nom lliure>.csv`; `blondswim importar fitxa <camí>`. Aquí la identitat sí que és dins del fitxer, perquè la fitxa *és* el nedador.

## Alternatives
- **Llegir el full de càlcul (.xlsx) directament:** descartat pels mateixos inconvenients que van fer descartar l'Excel com a entrada (ADR-0013).
- **CLI per a les dades del nedador:** descartat per l'ADR-0013.
- **Una sola fitxa per a tots els nedadors:** descartat; una fitxa per nedador és coherent amb el CSV d'inscripcions i aïlla els errors.
- **Fitxa amb seccions i taules (versió anterior d'aquest ADR):** descartat; files de tipus diferents compliquen el lector.
- **Fitxers plans separats per a tests i marques:** descartat; trenca «una fitxa per nedador».

## Conseqüències
- La spec 002 defineix les claus de la fitxa, quines són repetibles (`marca`, `test_css`) i les regles d'importació d'alta i d'actualització.
