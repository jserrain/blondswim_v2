# ADR-0019 — Contacte del nedador

**Estat:** Substituït per ADR-0020. Substituïa sencer l'ADR-0017. Esmena RN-032 i manté RN-033 i RN-034 retirades (spec 001).

## Context
El correu identifica la persona (RN-032) i el mòbil és només una dada de contacte. Calia un format de correu precís i comprovable, i fixar en un sol ADR tot el contacte del nedador.

## Decisió
- `correu`: obligatori, únic entre tots els nedadors (arxivats inclosos) i intransferible: mentre un nedador el té, cap altre no el pot fer servir.
- Es normalitza (sense espais en blanc als extrems —espais, tabuladors i salts de línia— i en minúscules) abans de validar-lo i de desar-lo.
- Un cop normalitzat, ha de complir l'expressió regular de RN-032, aplicada a tot el text; si no, és un ERROR.
- El correu es pot modificar: l'id no canvia (RN-002); el correu nou passa format i unicitat, i l'antic queda lliure.
- `mobil`: obligatori, no buit després de treure'n els espais als extrems. És informatiu: no intervé en cap regla, no és únic i no té format ni avís.
- `canal_preferent` (`correu` o `mobil`): sense canvis. Absent o `null` genera un avís (RN-035); un valor no admès és un error de format.
- Verificar que el correu existeix i és actiu: ADR-0018.
- Cap identificador del sistema no deriva del correu ni del mòbil: l'id és l'UUID (ADR-0014).
- La unicitat només s'aplica a correu i alias.

## Alternatives
- **Llibreria de validació de correus:** descartada; afegiria una dependència per a una regla que cal que sigui explícita i comprovable.
- **Només comprovar la «@»:** descartat; deixa passar correus evidentment incomplets.
- **Mòbil en E.164 amb avís si es comparteix (ADR-0016):** descartat; no aporta cap decisió de planificació.
- **Id derivat del correu o del mòbil:** descartat, perquè canvien amb el temps i hi introduirien una dada personal (ADR-0014).

## Conseqüències
- RN-032 porta la normalització i l'expressió regular; RN-033 i RN-034 continuen retirades i `data/avisos.jsonl` no porta mòbils.
- El correu antic d'un nedador queda lliure en modificar-lo; mentre un nedador el tingui, ni tan sols un arxivat no el deixa lliure.
- Quines dades de contacte poden arribar a un LLM ho fixa l'ADR pendent de dades cap a l'LLM.
- La supressió de dades personals (correu i mòbil) és al pendent «ADR de dades personals: supressió» (`docs/estat.md`).
