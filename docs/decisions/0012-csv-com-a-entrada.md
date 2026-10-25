# ADR-0012 — CSV com a format d'entrada

**Estat:** Acceptat. Substitueix l'ADR-0007.

## Context
L'ADR-0007 fixava l'Excel com a format d'entrada per al calendari i les inscripcions. L'Excel com a entrada presenta més inconvenients que el CSV.

## Decisió
- Hi ha dos formats d'entrada en CSV:
  - **CSV de calendari:** un per temporada, comú a tots els nedadors. Genera el catàleg de competicions.
  - **CSV d'inscripcions:** un per nedador i temporada. Genera les inscripcions del nedador.
- La importació converteix cada CSV a JSON. El sistema només llegeix JSON.
- El CSV és la font del catàleg i de les inscripcions. Quan el CSV canvia, es torna a importar i el JSON corresponent se substitueix.
- La importació no modifica mai els plans. Si un canvi afecta un pla existent, el sistema avisa.
- Els Excels de sortida (full de piscina, resum) continuen sent només sortida.

## Alternatives
- **Excel com a entrada (ADR-0007):** descartat, per tenir més inconvenients que el CSV.
- **Introduir les dades per CLI o editar el JSON a mà:** descartat, perquè és poc pràctic per al coach.

## Conseqüències
- La spec 002 defineix les columnes de cada CSV i les regles d'importació.
- Format del fitxer: codificació UTF-8, separador de camps `;` i coma decimal.
