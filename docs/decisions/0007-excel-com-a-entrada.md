# ADR-0007 — Excel com a format d'entrada

**Estat:** Substituït per l'ADR-0013.

## Context
El coach manté el calendari i les inscripcions en fulls de càlcul. AGENTS.md deia «Excel = només sortida».

## Decisió
- Hi ha dos formats d'entrada en Excel:
  - **Excel de calendari:** un per temporada, comú a tots els nedadors. Genera el catàleg de competicions.
  - **Excel d'inscripcions:** un per nedador i temporada. Genera les inscripcions del nedador.
- La importació converteix cada Excel a JSON. El sistema només llegeix JSON.
- L'Excel és la font del catàleg i de les inscripcions. Quan l'Excel canvia, es torna a importar i el JSON corresponent se substitueix.
- La importació no modifica mai els plans. Si un canvi afecta un pla existent, el sistema avisa.
- Els Excels de sortida (full de piscina, resum) continuen sent només sortida.

## Alternatives
- **Introduir les dades per CLI o editar el JSON a mà:** descartat, perquè és poc pràctic per al coach.

## Conseqüències
- La spec 002 defineix el format de cada Excel i les regles d'importació.
