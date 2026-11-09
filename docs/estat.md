# Estat del projecte

Fitxer de traspàs entre sessions. S'actualitza en tancar cada bloc. No és normatiu.

## On som (2026-11-09)
- **Spec 001 tancada.** Implementada sencera (54 tasques), traçabilitat bloquejant, revisió independent del codi feta i corregida. Fusionada a `main` amb la PR #2 (`94e2e6b`). `main` és igual a GitHub, GitLab i el Mac.
- **Branca de treball: `002-importacio`** (surt de `main`). Únic commit fins ara: ADR-0021 (`2ff33e7`).
- Constitució 1.3.0 (G0 r2: passa amb condicions).
- CI a GitHub Actions: `verify.sh` a Linux a cada push i també a macOS a les PR.

## Següent pas: especificar la spec 002 (importació)
Al xat, abans de Spec Kit:
1. Analitzar el calendari real (`Calendari_26-27.xlsx`, al projecte) i `claude/fonts_dades.md` (irregularitats de les fonts).
2. Proposar les columnes del **CSV de calendari** (→ catàleg) i del **CSV d'inscripcions** (→ inscripcions del nedador).
3. Proposar la **plantilla de la fitxa del nedador** (un sol full; camps de contacte, estils, dies, volum, i taules de tests CSS i de millors marques) i com es distingeix una alta d'una actualització.
4. Decidir i preparar el bloc consolidat per a `/speckit-specify` de la 002.

Decisions ja preses per a la 002:
- Tres CSV d'entrada (ADR-0013 + ADR-0021): calendari (un per temporada), inscripcions (un per nedador i temporada) i fitxa del nedador (una per nedador). UTF-8, separador `;`, coma decimal. El sistema llegeix el CSV, mai el full de càlcul.
- Fitxa d'un nedador existent: s'identifica per l'alias; substitueix les dades modificables; tests CSS i millors marques només s'afegeixen (test nou sense acceptar; marca només si millora la vigent, RN-007). Alta: el sistema genera id i alias i els comunica.
- A la 002 hi van també: resum per nivells, codi de sortida, confirmació d'avisos a l'entrada (`decisio` confirmat/rebutjat) i els CA pendents de la 001 (CA-001-38, 58, 63, 64, 68, 72).
- Mai valors inventats; informe d'errors.

## Decisions vigents (detall als ADR i a les specs)
- Identitat: `IdNedador` UUID v4 (ADR-0014); alias obligatori i immutable `<part>_<sufix>` (RN-003).
- Contacte (ADR-0020): correu opcional, desat tal com s'entra, format mínim, únic sense distingir majúscules; mòbil obligatori, no únic; canal preferent amb avís (RN-035).
- Millor marca: llista de millores successives per prova i piscina, només de competició; `competicio` és un nom (RN-007). Tests CSS: es desen tots.
- Validació: ERROR exclou només el nedador (un error del catàleg fa fallar tota la càrrega); AVÍS no bloqueja. Avisos a `data/avisos.jsonl`, que només creix.
- Temporada 1/10–30/09 (RN-031); proves oficials per piscina (RN-030).
- Pydantic v2 estricte només a `infrastructure`.

## Pendents
- Spec de pagaments (Bizum): per decidir el model.
- Esmena de la constitució 1.4.0 (ADR de dades cap a l'LLM, etc.), abans de la primera spec amb judici LLM.
- ADR de dades personals (dret de supressió), quan un nedador ho demani.
- Spec 002b (biblioteca de tècnica) i la resta del mapa (`docs/mapa_specs.md`).

## Flux de treball
1. Xat nou per bloc, començant per aquest fitxer i la spec en curs.
2. Decisions de spec al xat; després un bloc consolidat per a Spec Kit / Claude Code.
3. Auditoria: Part A a consola (`bash scripts/auditar.sh spec|plan specs/<NNN>`); Part B per un agent independent.
4. Implementació: o bé Claude Code amb `docs/prompts/<spec>-<fase>.md` (abans, `bash scripts/preflight.sh <prompt>`), o bé directament al núvol amb `verify.sh` en verd a cada fase.
5. Verificació: `bash scripts/verify.sh | tail -3` ha d'acabar «LLEST PER SEGUIR».
6. Tancament: PR a `main` amb la CI verda; després `git push gitlab main`.
