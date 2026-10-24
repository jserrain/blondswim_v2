# Estat del projecte

Fitxer de traspàs entre sessions. S'actualitza en tancar cada bloc. No és normatiu.

## On som
- Branca: `001-model-domini`. Spec 001 amb G1 i G2 passats; pla i tasques llestos (34 tasques, 46 CA amb test).
- Constitució 1.3.0 (G0 r2: passa amb condicions).
- Següent pas: implementar la spec 001, fase 1 (T001, T003–T010), amb `docs/prompts/001-fase1.md`.
- Durant la implementació, `verify.sh` mostra «Traçabilitat CA» com a AVÍS (CA sense test encara). Passa a bloquejant amb T002, al final.

## Decisions recents (detall als ADR i a la spec)
- Nedador identificat pel correu, únic; no es desen nom ni cognoms (RN-032).
- Temporada 1/10–30/09, derivada del nom de la carpeta (RN-031); proves oficials per piscina (RN-030).
- Tres tipus de camp: obligatori, informatiu (pot faltar) i opcional amb avís (spec 001, § Format JSON).
- Avisos a `data/avisos.jsonl`, que només creix.
- Pydantic v2 estricte, només a `infrastructure`; definicions de RN com a constants del domini (principi V).
- L'històric d'entrenaments no s'importa (ADR-0012).

## Pendents
- Esmena 1.4.0: ADR de dades cap a l'LLM, «canvis petits» (II), raons de II, IV, VI, VII i VIII, secció «Fora d'abast». Abans de la primera spec amb judici LLM.
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
