# ADR-0017 — Contacte del nedador

**Estat:** Acceptat. Substitueix l'ADR-0016. Esmena RN-032 i retira RN-033 i RN-034 (spec 001).

## Context
L'ADR-0016 demanava un mòbil en E.164 i avisava si es compartia. No s'ha vist cap ús per al format ni per a l'avís, i el correu continua sent la dada que identifica la persona (RN-032), sense format definit.

## Decisió
- `correu`: obligatori, únic entre tots els nedadors (arxivats inclosos) i intransferible: mentre un nedador el té, cap altre no el pot fer servir.
- Es normalitza (sense espais als extrems, en minúscules) abans de validar-lo i de desar-lo.
- Format (ERROR): exactament una «@», part local no buida, domini amb almenys un punt i un TLD de 2 lletres o més, sense espais, 254 caràcters com a màxim. És una regla simple al domini, sense llibreries externes.
- El correu es pot modificar: l'id no canvia (RN-002); el correu nou passa format i unicitat, i l'antic queda lliure.
- `mobil`: obligatori, no buit després de treure'n els espais als extrems. Cap altra validació: sense format, unicitat ni avís (RN-033 i RN-034 retirades).
- `canal_preferent` (`correu` o `mobil`): absent o `null` genera un avís (RN-035). Un valor no admès és un error de format.
- Cap identificador del sistema no deriva del correu ni del mòbil: l'id és l'UUID (ADR-0014).
- La unicitat només s'aplica a correu i alias.

## Alternatives
- **Llibreria de validació de correus:** descartada; afegiria una dependència per a una regla que cal que sigui simple i comprensible.
- **Només comprovar la «@»:** descartat; deixa passar correus evidentment incomplets.
- **Verificar la bústia o el domini:** fora d'abast d'aquesta versió (`BACKLOG.md`).
- **Mantenir el format E.164 i l'avís de mòbil compartit (ADR-0016):** descartat; no aporta cap decisió de planificació.
- **Id derivat del correu o del mòbil:** descartat, perquè canvien amb el temps i hi introduirien una dada personal (ADR-0014).

## Conseqüències
- RN-032 incorpora la normalització i el format; RN-033 i RN-034 queden retirades i `data/avisos.jsonl` ja no porta mòbils.
- El correu antic d'un nedador queda lliure en modificar-lo; mentre un nedador el tingui, ni tan sols un arxivat no el deixa lliure.
- La validació completa del domini i la verificació de la bústia queden al `BACKLOG.md`.
- Quines dades de contacte poden arribar a un LLM ho fixa l'ADR pendent de dades cap a l'LLM.
- La supressió de dades personals (correu i mòbil) és al pendent «ADR de dades personals: supressió» (`docs/estat.md`).
