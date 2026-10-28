# Estat del projecte

Fitxer de traspàs entre sessions. S'actualitza en tancar cada bloc. No és normatiu.

## On som
- Branca: `001-model-domini`. Spec 001 amb G1 i G2 passats; pla i tasques llestos (34 tasques; 84 CA, 9 pendents; 19 CA amb test als markers de `tests/`).
- Constitució 1.3.0 (G0 r2: passa amb condicions).
- `tasks.md` (47 tasques, 75 CA amb tasca): fetes Setup (T001), Foundational (T003–T010) i US1 (T011–T016), contra la spec anterior. Tasques de la fase US1b (T035–T047) afegides, pendents d'implementar. Decisions D1 i D2 confirmades (`plan.md`).
- Següent pas: fase US1b (UUID, alias, contacte i validació), que modifica el codi fet (p. ex. `_RE_ID = n[0-9]{4}` a `valors.py`); després, US2 (T017–T019).
- Durant la implementació, `verify.sh` mostra «Traçabilitat CA» com a AVÍS (CA sense test encara). Passa a bloquejant amb T002, al final.

## Decisions recents (detall als ADR i a la spec)
- Identitat = `IdNedador`, UUID v4 (ADR-0014); alias obligatori i immutable `<part>_<sufix>` (RN-003). Contacte: correu i mòbil obligatoris (ADR-0016, RN-032 a RN-035). Pendent: G1 de l'esmena, tasques US1b i implementació.
- Nedador identificat pel correu, únic; no es desen nom ni cognoms (RN-032).
- Temporada 1/10–30/09, derivada del nom de la carpeta (RN-031); proves oficials per piscina (RN-030).
- Tres tipus de camp: obligatori, informatiu (pot faltar) i opcional amb avís (spec 001, § Format JSON).
- Avisos a `data/avisos.jsonl`, que només creix.
- Pydantic v2 estricte, només a `infrastructure`; definicions de RN com a constants del domini (principi V).
- L'històric d'entrenaments no s'importa (ADR-0012).

## Pendents
- Spec de pagaments (Bizum): pagador com a entitat pròpia amb nedadors associats. Per decidir: Bizum comerços o particular, rebuts, quotes mensuals o per sessió.
- Esmena 1.4.0: ADR de dades cap a l'LLM, «canvis petits» (II), raons de II, IV, VI, VII i VIII, secció «Fora d'abast». Abans de la primera spec amb judici LLM.
- ADR de dades personals: supressió (dret de supressió del RGPD davant la regla d'arxivar sense esborrar) a `nedador.json` i al registre d'avisos (`avisos.jsonl`); es decidirà quan un nedador ho demani.
- Tasques per al bloc US1b de `tasks.md` (encara no afegides):
  - adaptar la càrrega al criteri per nedador;
  - camp «decisió» al registre d'avisos;
  - unicitat sobre els fitxers llegibles, vàlids o no;
  - RN-035 només avís; valor no admès com a error de format;
  - filtre de validació (un sol validador, tots els nedadors, resultat per camp, fitxer il·legible);
  - camps immutables (`id`, `alias`, `versio_esquema`) i modificables;
  - operacions de modificació (nedador sencer revalidat; tests i millors registres només s'afegeixen);
  - arxivar i desarxivar.
- Spec 002: abast reduït (sense històric), àlies «lliure» → `Cr`, CSV o Excel.

## Flux de treball
1. Xat nou per bloc, començant per aquest fitxer i la spec en curs.
2. Spec, clarify, pla i tasques al xat, en format Spec Kit.
3. Auditoria: Part A a consola (`bash scripts/auditar.sh …`); Part B al xat, només sobre el que ha canviat.
4. Abans d'obrir Claude Code: `bash scripts/preflight.sh docs/prompts/<spec>-<fase>.md` ha d'acabar «LLEST».
5. Implementació a Claude Code: una sessió per fase, `/clear` entre fases, model econòmic i prompt de `docs/prompts/`.
6. Verificació a consola: `bash scripts/verify.sh 2>&1 | grep -E 'FAIL|AVÍS|LLEST|BLOQUEJAT' -A5`.
7. Patches: `bash scripts/aplicar.sh <fitxer.patch>`.
- 24 CA de la spec 000 sense tasca: decidir si s'afegeix un bloc US7 a la 001 o es marquen com a pendents, abans de T002.
