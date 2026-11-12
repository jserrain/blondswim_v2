# Implementation Plan: Importació estricta

**Branch**: `002-importacio` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-importacio/spec.md`

## Summary

Tres casos d'ús d'entrada (`importar_fitxa`, `importar_calendari`, `importar_inscripcions`) a `application/` que reben el contingut d'un CSV com a text cru i retornen un `ResultatImportacio` amb una sola llista `incidencies[]` (constitució IX). Un lector CSV a `infrastructure/csv/` només obre el fitxer i retorna text. Una CLI a `interfaces/` només pinta el resultat i tradueix `ok/desat/pendent_confirmacio` a codi de sortida (constitució X). Els casos d'ús reutilitzen el validador únic de la spec 001 i només hi afegeixen els errors de format i les RN-036 a RN-042.

Abans de res (**fase 0**), el codi de la spec 001 migra a `test_css` per piscina sense `acceptat` (ADR-0022) i la generació d'alias passa al format de l'ADR-0023 (alias escrit pel coach, sufix numèric en col·lisió, sense sufix d'UUID). Es retiren els tests de CA-001-05, 30, 35, 68 i 82. Aquesta fase acaba quan `bash scripts/verify.sh` queda en verd.

Enfocament:
- Biblioteca estàndard per a CSV (`csv`, lectura `utf-8-sig`) i UUID. Cap dependència nova.
- Conversió text → valors de domini a `application`, amb incidències `FORMAT-<camp>`; el lector no conté regles.
- La fitxa es valida com un sol nedador sencer, sense desar a mig camí (research R6).
- El flux de dues passades i el registre d'avisos viuen en un sol mòdul (`flux.py`) compartit pels tres casos d'ús.
- Slug de l'id de competició: funció pura a `domain/definicions.py` (RN-008).
- Punt d'entrada fora de les quatre capes (`blondswim/arrel.py`) que només cabla (research R3).

Sense LLM. El rellotge s'injecta per al registre d'avisos.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: cap de nova. `csv`, `unicodedata`, `argparse` i `uuid` de la biblioteca estàndard. Pydantic continua només a `infrastructure` per al JSON; no s'usa als CSV

**Storage**: entrada `data/entrada/` (CSV, només lectura); sortida els JSON de la spec 001 i `data/avisos.jsonl`

**Testing**: pytest amb `@pytest.mark.ca`, mypy estricte, import-linter, ruff (`verify.sh`)

**Target Platform**: macOS local (Mac del coach)

**Project Type**: biblioteca amb casos d'ús i CLI (`blondswim importar …`)

**Performance Goals**: N/A. Fitxers de desenes de files

**Constraints**: `interfaces/*` només importa `application/`; `infrastructure/csv` no importa `domain`; `ResultatImportacio` només porta tipus primitius (cap tipus de domini arriba a la vista); un error no desa res del fitxer; escriptura estable byte a byte

**Scale/Scope**: 3 fitxers d'entrada; 64 CA (1 pendent de la spec 003); a la 001, 5 CA retirats (05, 30, 35, 68 i 82) i 9 de reescrits (04, 14, 31, 32, 46, 49, 51, 52 i 61)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Arquitectura per capes:** slug i `Alias` (format RN-003 i sufix numèric) a `domain`; casos d'ús, DTO, `ResultatImportacio` i el port `LectorCsv` a `application`; lector CSV a `infrastructure`; CLI a `interfaces`. El rellotge i el generador d'id arriben per ports existents. Cap import cap amunt.
- [x] **II. Primer la spec:** tot surt de la spec 002, de les RN i de l'ADR-0023. No queda cap punt obert. Les decisions de disseny no afegeixen regles de negoci.
- [x] **III. Regles de negoci identificades i amb una sola font:** RN-036 a RN-042 són a `docs/regles.md`; la derivació del slug és a RN-008. El codi cita les RN per ID.
- [x] **IV. El sistema avisa; el coach decideix:** avisos per fila i columna, registrats amb `decisio: confirmat` només en desar amb `--confirma`; cap guarda silenciosa (RN-039 per a la substitució d'inscripcions).
- [x] **V. Dades honestes:** cap valor per defecte; no es desa cap valor derivat. L'alias és una dada escrita pel coach (RN-003) i l'id el genera el sistema (RN-002). El slug és una definició (RN-008) en un sol lloc, amb CA-002-51.
- [x] **VI. El pla es persisteix i es versiona:** no aplica. La importació no modifica mai cap pla (RN-022). RN-040 queda per a la spec 003 (research R7).
- [x] **VII. Traçabilitat de la spec al test:** a `tasks.md`, cada tasca portarà capa i cada CA no pendent, un test amb `@pytest.mark.ca`.
- [x] **VIII. Documents genèrics i sense història:** els exemples i les fixtures viuen a `tests/fixtures/entrada/`.
- [x] **IX. Contracte dels casos d'ús d'entrada:** DTO d'entrada i resultat tipat amb `ok` i `incidencies[]` (origen, codi, nivell, missatge); nivells i codis al cas d'ús; les vistes només mapegen.
- [x] **X. Regla de capa per a les vistes:** contracte import-linter `interfaces` → només `application` (research R9).

**Re-check post-disseny:** compleix tots els principis. Les decisions D1–D6 de § Decisions de disseny no canvien cap principi.

## Project Structure

### Documentation (this feature)

```text
specs/002-importacio/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── casos-d-us.md       # DTO, ResultatImportacio i ports
│   └── cli.md              # ordres, codis de sortida, informe
├── checklists/
└── tasks.md                # /speckit-tasks
```

### Source Code (repository root)

```text
src/blondswim/
├── arrel.py                       # punt d'entrada: cabla infrastructure i application a la CLI (R3); fora de les quatre capes
├── domain/
│   ├── definicions.py             # + slug_competicio (RN-008)
│   ├── valors.py                  # fase 0: Alias amb el format de RN-003 (ADR-0023) i alias amb el primer sufix lliure
│   ├── nedador.py                 # fase 0: TestCss sense `acceptat`; Nedador.test_css per piscina
│   └── derivats.py                # fase 0: test_vigent(nedador, piscina) = test_css[piscina]
├── application/
│   ├── gestio.py                  # fase 0: substitueix_test (en lloc d'afegeix_test/accepta_test); alta amb l'alias proposat i sufix numèric en col·lisió, sense reintents d'id; prepara_alta separada de desar
│   ├── ports.py                   # + LectorCsv; docstring de `decisio` (confirmat | None)
│   └── importacio/
│       ├── resultat.py            # Incidencia, Origen, ResultatImportacio
│       ├── conversio.py           # text → valors de domini, amb incidències FORMAT-<camp>
│       ├── flux.py                # dues passades, codi d'estat, registre d'avisos
│       ├── calendari.py           # importar_calendari (RN-008, 009, 010, 038)
│       ├── inscripcions.py        # importar_inscripcions (RN-011, 015, 016, 019, 030, 036, 037, 039)
│       ├── fitxa.py               # importar_fitxa (RN-003, 005, 007, 032, 035, 041, 042)
│       └── serveis.py             # ServeisImportacio: llegeix amb el port i crida els tres casos d'ús
├── infrastructure/
│   ├── dto.py, mappers.py         # fase 0: clau JSON `test_css`
│   └── csv/
│       └── lector.py              # LectorCsvFitxer: codificació, capçalera, files; sense regles
└── interfaces/
    └── cli.py                     # argparse; pinta ResultatImportacio; codi de sortida

tests/
├── fixtures/entrada/              # CSV d'exemple que fan de plantilla per al coach
├── unit/                          # casos d'ús amb repositoris en memòria i lector fals
└── integration/                   # lector real, repositoris JSON i CLI amb tmp_path
```

**Structure Decision**: estructura existent de quatre capes (principi I) més un sol mòdul d'arrel per al cablatge (justificat a Complexity Tracking). `application/importacio/` és un paquet nou perquè agrupa tres casos d'ús que comparteixen resultat i flux.

## Fases

| Fase | Contingut | Sortida / porta |
|---|---|---|
| **0** | Migració de la spec 001 a `test_css` (ADR-0022) i a l'alias de l'ADR-0023: domini (`TestCss`, `Alias`), validació, gestió (alta), JSON, `data-model.md` i `contracts/fitxers-json.md` de la 001 (exemple d'alias) i tests; retirada dels tests de CA-001-05, 30, 35, 68 i 82; reescriptura dels de CA-001-04, 14, 31, 32, 46, 49, 51, 52 i 61 | `verify.sh` en verd abans de la fase 1 |
| **1** | Fonaments: slug, resultat i incidències, `conversio`, `flux`, port `LectorCsv`, lector CSV, contractes import-linter, fixtures | CA-002-02 a 10 (format i confirmació, amb fitxers de prova), 49, 51, 52, 59, 60, 62 |
| **2** | US1 — calendari | CA-002-30 a 37, 63 |
| **3** | US2 — inscripcions | CA-002-38 a 47, 55 (48 pendent) |
| **4** | US3 — fitxa (alta i actualització) | CA-002-11 a 29, 53, 54, 56 a 58, 61, 64 |
| **5** | CLI i arrel; informe | CA-002-50 |

`/speckit-tasks` ordena les tasques dins de cada fase amb els tests abans de la implementació (G2-T04).

## Decisions de disseny

Cap afegeix regles de negoci. D1, D4, D5 i D6 estan **confirmades** pel coach (2026-11-11). D2 i D3 continuen proposades.

- **D1 — Cablatge fora de les capes (confirmada).** `blondswim/arrel.py` crea els repositoris, el lector, el rellotge i el generador d'id, construeix `ServeisImportacio` i el passa a `interfaces.cli.executa`. És l'únic mòdul que importa `infrastructure` i `interfaces` alhora. `[project.scripts]` apunta a `blondswim.arrel:main` (ara apunta a `blondswim:main`). *Alternativa descartada:* cablar a `interfaces/` (viola X) o a `application/` (importaria `infrastructure`).
- **D2 — Lectura per un port (proposada).** `ServeisImportacio` rep un `LectorCsv` (Protocol a `application/ports.py`) i construeix el DTO; els casos d'ús no fan I/O. Els errors de lectura (no UTF-8, buit, capçalera, fitxer inexistent) es mapegen a incidències d'origen `fitxer`. *Alternativa descartada:* que la CLI cridi el lector (viola X).
- **D3 — Una sola llista d'incidències (decidida a la spec, § Contracte).** El validador de la 001 retorna `ErrorValidacio` i `Avis`; `resultat.py` els converteix a `Incidencia` amb `nivell` i `origen` (R4, R5).
- **D4 — Fitxa atòmica (confirmada).** L'alta i l'actualització construeixen el `Nedador` nou en memòria, el validen sencer (`valida_nedador` + `valida_unicitat`) i desen una sola vegada. Cal separar `prepara_alta` de `desar` a `gestio.py` i deixar que `NouNedador` porti `test_css` i `millors_registres` (R6).
- **D5 — `versio_esquema` no canvia a la fase 0 (confirmada).** No hi ha dades reals desades i la clau `tests_css` passa a `test_css`; les fixtures de test es regeneren. *Si ja hi ha fitxers desats, cal pujar la versió i una migració* (R8).
- **D6 — Comprovació contra els altres nedadors al calendari (confirmada).** Per a RN-010 i RN-038 es llegeixen les inscripcions de la temporada de tots els nedadors (arxivats inclosos). Un fitxer il·legible és una incidència bloquejant d'origen `fitxer`, perquè no es pot garantir RN-010 (R10).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| `blondswim/arrel.py` fora de les quatre capes (principi I: «quatre capes») | La CLI (`interfaces`) no pot importar `infrastructure` (X) i `application` tampoc; algú ha de cablar els ports | Cablar a `interfaces` viola X; cablar a `application` viola I. No és una capa de codi de negoci: només construeix objectes |
| Subpaquet `infrastructure/csv` amb el nom de la biblioteca estàndard | La spec l'anomena (CA-002-49) | Funciona amb imports absoluts; si causa confusió amb mypy o ruff, es reanomena a `lector_csv` i s'esmena CA-002-49 |

## Punts oberts

Cap. R2 (slug buit) i R11 (alias entre passades) estan resolts a la spec 002 (CA-002-63) i a l'ADR-0023.
