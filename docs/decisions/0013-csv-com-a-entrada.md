# ADR-0013 — CSV com a format d'entrada

**Estat:** Acceptat. Substitueix l'ADR-0007. Revisat: format estricte i CSV de nedadors.

## Context
L'ADR-0007 fixava l'Excel com a format d'entrada per al calendari i les inscripcions. L'Excel com a entrada presenta més inconvenients que el CSV.

La part cara de la importació no és validar sinó normalitzar dades heretades (dates en diversos formats, valors marcadors, files compostes). Una interfície web resoldria el mateix problema, però amb cost d'interfície i tria de framework prematura. Es difereix a una spec posterior (009).

La spec 001 deixa a la spec 002 el format d'entrada dels nedadors.

## Decisió
- Hi ha tres formats d'entrada en CSV:
  - **CSV de nedadors:** un, sense temporada. Dona d'alta nedadors nous (id i alias els genera el sistema, RN-003). No modifica, arxiva ni esborra cap nedador existent; les altres operacions sobre el nedador (modificar, arxivar, tests CSS, millors registres) són ordres de CLI pròpies.
  - **CSV de calendari:** un per temporada, comú a tots els nedadors. Genera el catàleg de competicions.
  - **CSV d'inscripcions:** un per nedador i temporada. Genera les inscripcions del nedador.
- **Format estricte.** El CSV s'escriu segons la spec 002: un sol format per camp, dada desconeguda = camp buit (`null`). No hi ha cap normalització de dades heretades: tot el que no s'ajusta al format és un error, no una heurística.
- **Ubicació:** `data/entrada/nedadors.csv`, `data/entrada/<AAAA-AA>/calendari.csv` i `data/entrada/<AAAA-AA>/inscripcions_<alias>.csv`. `data/entrada/` no es versiona, com la resta de `data/`.
- **Identificació del nedador en importar inscripcions:** l'alias és un argument de l'ordre; el nom del fitxer se'n deriva. L'alias no es llegeix mai de dins del CSV (una sola font).
- La importació converteix cada CSV a JSON. El sistema només llegeix JSON.
- El CSV és la font del catàleg i de les inscripcions. Quan el CSV canvia, es torna a importar i el JSON corresponent se substitueix.
- La importació no modifica mai els plans. Si un canvi afecta un pla existent, el sistema avisa.
- La importació és un cas d'ús d'`application/` amb DTO d'entrada i resultat tipat (errors amb origen, codi, nivell i missatge). El lector CSV i la CLI són vistes: mapegen fitxer → DTO i resultat → text, sense lògica pròpia (constitució IX, X). Una futura interfície web reutilitza el mateix cas d'ús.
- Els Excels de sortida (full de piscina, resum) continuen sent només sortida.

## Alternatives
- **Excel com a entrada (ADR-0007):** descartat, per tenir més inconvenients que el CSV.
- **Introduir les dades per CLI o editar el JSON a mà:** descartat per a calendari, inscripcions i alta de nedadors, perquè és poc pràctic per al coach. La CLI queda per a les operacions puntuals sobre un nedador.
- **Interfície web local com a únic camí d'entrada:** diferit (spec 009). Elimina la normalització igual que el format estricte, però afegeix una dependència, tests d'interfície i obliga a triar framework abans d'hora.
- **CSV amb normalització d'irregularitats heretades:** descartat, és la part cara i no aporta valor un cop el CSV l'escriu el coach segons la spec.

## Conseqüències
- La spec 002 defineix les columnes, tipus i format de cada camp dels tres CSV, el catàleg de codis d'error amb nivell (bloquejant / avís), el resultat del cas d'ús i la confirmació d'avisos i d'alias.
- `claude/fonts_dades.md` passa a referència històrica: les seves irregularitats no generen regles.
- Format del fitxer: codificació UTF-8, separador de camps `;`, coma decimal, llistes dins d'un camp separades per `|`.
- Regla de capa (constitució): `interfaces/*` només importa `application/`.
