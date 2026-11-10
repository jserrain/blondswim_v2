# Instruccions del projecte BlondSwim v2

## Font de veritat
1. `AGENTS.md` i els ADR de `docs/decisions/` (repo blondswim_v2).
2. Les specs de `specs/`, un cop aprovades.

## Material de referència (no normatiu)
- `claude/mapa_specs.md`: requisits, principis, organització de dades i ordre de les specs.
- `claude/fonts_dades.md`: **referència històrica**. Descriu els Excels de la v1 i les seves irregularitats. Des de la revisió de l'ADR-0013 (format estricte) no genera cap regla: el CSV s'escriu segons la spec 002.
- `inventari/regles.md` i `inventari/auditoria.md`: inventari de la v1. Serveixen per saber quins errors no repetir; una regla de la v1 no és vàlida fins que no queda en un ADR o en una spec.
- `metodologia_ritmes.md`: coneixement de domini per a les zones. Es retira quan existeixi l'ADR de zones.
- Excels: casos de prova d'un nedador real, no regles.

## Regles de treball
- Regles, specs i ADR són genèrics: mai no anomenen un nedador, una competició ni una data concreta. Els casos concrets van als exemples i als tests.
- Els documents normatius descriuen l'estat actual; el perquè va a l'ADR i la història a git.
- Si una regla no està decidida en un ADR o en una spec, pregunta; no l'inventis.
- Prioritza el nucli mínim: el que queda fora d'abast s'aparca, no es resol.
- Respostes en català, directes i concises.
