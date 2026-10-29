# Estat del projecte

Fitxer de traspàs entre sessions. S'actualitza en tancar cada bloc. No és normatiu.

## On som
- Branca: `001-model-domini`. Spec 001 amb l'esmena del 2026-10-29 (ADR-0017, millor registre, correccions del G2) pendent de passar G1 i G2 de nou; 92 CA actius (83 amb test, 9 pendents), 3 retirats (CA-001-55, 56 i 77); 19 CA amb test als markers de `tests/`.
- Constitució 1.3.0 (G0 r2: passa amb condicions).
- `tasks.md` (54 tasques, 83 CA amb tasca; IDs fora d'ordre, vegeu la nota): fetes Setup (T001), Foundational (T003–T010) i US1 (T011–T016), contra la spec anterior. US1b (T035–T050), US3 (T051–T052) i US4 (T053–T054) amb tasques noves, pendents d'implementar. Decisions D1 i D2 confirmades (`plan.md`).
- Següent pas: fase US1b, començant per T048 i T049 (reescriure els tests fets), que modifica el codi fet (p. ex. `_RE_ID = n[0-9]{4}` a `valors.py`); després, US2 (T017–T019).
- Durant la implementació, `verify.sh` mostra «Traçabilitat CA» com a AVÍS (CA sense test encara). Passa a bloquejant amb T002, al final.

## Decisions recents (detall als ADR i a la spec)
- Identitat = `IdNedador`, UUID v4 (ADR-0014); alias obligatori i immutable `<part>_<sufix>` (RN-003). Contacte: ADR-0017 substitueix l'ADR-0016; correu obligatori, únic, normalitzat i amb format simple (RN-032); mòbil obligatori i no buit, sense cap altra validació (RN-033 i RN-034 retirades); canal preferent (RN-035). Pendent: G1 i G2 de l'esmena i implementació.
- Millor registre: un per prova i piscina, només de competició; un temps menor substitueix el desat (RN-007 reinstaurada, esmenada). Els tests CSS es desen tots.
- Nedador identificat pel correu, únic; no es desen nom ni cognoms (RN-032).
- Temporada 1/10–30/09, derivada del nom de la carpeta (RN-031); proves oficials per piscina (RN-030).
- Tres tipus de camp: obligatori, informatiu (pot faltar) i opcional amb avís (spec 001, § Format JSON).
- Avisos a `data/avisos.jsonl`, que només creix.
- Pydantic v2 estricte, només a `infrastructure`; definicions de RN com a constants del domini (principi V).
- L'històric d'entrenaments no s'importa (ADR-0012).

## Pendents
- Spec de pagaments (Bizum): pagador com a entitat pròpia amb nedadors associats. Per decidir: Bizum comerços o particular, rebuts, quotes mensuals o per sessió.
- Esmena 1.4.0: ADR de dades cap a l'LLM, «canvis petits» (II), raons de II, IV, VI, VII i VIII, secció «Fora d'abast». Abans de la primera spec amb judici LLM.
- ADR de dades personals: supressió (dret de supressió del RGPD davant la regla d'arxivar sense esborrar) a `nedador.json` (correu i mòbil) i al registre d'avisos (`avisos.jsonl`); es decidirà quan un nedador ho demani. També al `BACKLOG.md`.
- G1 i G2 de l'esmena del 2026-10-29 (ADR-0017, RN-007, tasques T048–T054).
- Spec 002: abast reduït (sense històric), àlies «lliure» → `Cr`, CSV o Excel.

## Flux de treball
1. Xat nou per bloc, començant per aquest fitxer i la spec en curs.
2. Spec, clarify, pla i tasques al xat, en format Spec Kit.
3. Auditoria: Part A a consola (`bash scripts/auditar.sh …`); Part B al xat, només sobre el que ha canviat.
4. Abans d'obrir Claude Code: `bash scripts/preflight.sh docs/prompts/<spec>-<fase>.md` ha d'acabar «LLEST».
5. Implementació a Claude Code: una sessió per fase, `/clear` entre fases, model econòmic i prompt de `docs/prompts/`.
6. Verificació a consola: `bash scripts/verify.sh 2>&1 | grep -E 'FAIL|AVÍS|LLEST|BLOQUEJAT' -A5`.
7. Patches: `bash scripts/aplicar.sh <fitxer.patch>`.
- Spec 000 (inventari 2026-10-29): CA-000-10 té tasca (T050); CA-000-01 és `[PENDENT spec 004]` i CA-000-02 a 09 i 11 a 24, `[PENDENT spec 006]`.
