# Tasks: Importació estricta

**Input**: `specs/002-importacio/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md) i constitució 1.4.1
**Tests**: obligatoris (constitució VII): cada CA no pendent té un test amb `@pytest.mark.ca("CA-002-NN")`. Els tests van abans de la implementació (G2-T04).
**Format**: `- [ ] T### [P?] [Història?] [capa] Descripció amb camí`
- **[P]**: fitxers diferents, sense dependència d'una tasca incompleta.
- **[capa]**: `domain`, `application`, `infrastructure`, `interfaces` o `project` (constitució VII).
- Ordre de les històries: US1 (P1), US3 (P1), US2 (P2, depèn d'US1 i US3, spec § Històries). El pla les llista US2 abans d'US3; aquí s'inverteixen per respectar la dependència.
- Ordres de consola: les executa l'usuari (AGENTS.md). Les tasques `checkpoint` indiquen l'ordre exacta.

---

## Phase 1: Setup

- [ ] T001 [project] Crea els paquets buits `src/blondswim/application/importacio/__init__.py` i `src/blondswim/infrastructure/csv/__init__.py` (imports absoluts; si `csv` causa confusió amb mypy o ruff, vegeu Complexity Tracking del pla).
- [ ] T002 [P] [project] Fixtures vàlides de fitxa a `tests/fixtures/entrada/nedadors/alta.csv` i `actualitzacio.csv`: files `clau;valor` amb totes les claus obligatòries de la spec (`alias`, `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament`, `volum_setmanal`) més un `test_css` i una `marca`; noms i alias fictius (R12).
- [ ] T003 [P] [project] Fixtures vàlides `tests/fixtures/entrada/<AAAA-AA>/calendari.csv` (capçalera `nom;dates;piscina;seu`, tres competicions) i `inscripcions_<alias>.csv` (capçalera `competicio;classe;dia;distancia;estil;prioritat`, tres files de dues competicions del calendari). Plantilla per al coach (R12).

---

## Phase 2: Foundational (bloqueja totes les històries)

### Fase 0 del pla — migració de la spec 001 (ADR-0022, ADR-0023)

**Tests primer**

- [ ] T004 [domain] Retira els tests i els marcadors de CA-001-05, 30, 35, 51, 68 i 82 (CA retirats) a `tests/`; localitza'ls amb `grep -rn 'CA-001-05\|CA-001-30\|CA-001-35\|CA-001-51\|CA-001-68\|CA-001-82' tests/`.
- [ ] T005 [P] [domain] Tests a Reescriu els tests de CA-001-04 i CA-001-14 segons el text vigent a `specs/001-*/spec.md`: `Nedador.test_css` és un test o `None` per piscina, sense `acceptat`; `test_vigent(nedador, piscina)` = `test_css[piscina]`. A `tests/unit/domain/`.
- [ ] T006 [P] [domain] Tests de l'alias a `tests/unit/domain/test_valors.py` (CA-001-46, 52): format `^[a-z0-9]{2,9}(\d{2})?$` (RN-003); funció que, donats l'alias proposat i els existents, retorna el primer sufix `01`…`99` lliure; error si ja en té un de dos dígits o els 99 sufixos són ocupats (base de CA-002-64).
- [ ] T007 [P] [application] Tests a Reescriu els tests de `gestio` de CA-001-31, 32, 46, 49 i 61 segons el text vigent de la spec 001: `substitueix_test` (en lloc d'`afegeix_test`/`accepta_test`), alta amb alias proposat i sufix numèric en col·lisió, sense reintents d'id. A `tests/unit/application/`.
- [ ] T008 [P] [infrastructure] Test d'ida i volta del JSON del nedador amb la clau `test_css` (`"25"`, `"50"`; valor o `null`) a `tests/integration/`; `versio_esquema` es manté a 1 (D5).

**Implementació**

- [ ] T009 [domain] `src/blondswim/domain/nedador.py`: `TestCss` sense `piscina` ni `acceptat`; `Nedador.test_css` guarda un test o `None` per piscina (data-model §1).
- [ ] T010 [P] [domain] `src/blondswim/domain/derivats.py`: `test_vigent(nedador, piscina)` = `nedador.test_css[piscina]`.
- [ ] T011 [domain] `src/blondswim/domain/valors.py` i el mòdul de validació de `domain/`: `Alias` amb el format de RN-003; elimina `Alias.genera` i `coincideix_amb` i la validació del sufix contra l'id a `valida_nedador`; afegeix la funció de l'alias amb el primer sufix lliure; `valida_aptitud` mira si hi ha algun test (RN-020 sense acceptació). Depèn de T009.
- [ ] T012 [application] `src/blondswim/application/gestio.py`: `substitueix_test` (elimina `afegeix_test` i `accepta_test`); `prepara_alta` (genera l'id, resol l'alias, valida, no desa) separada de `desar`; `alta()` combina totes dues; elimina el reintent d'id (R6, R8). Depèn de T011.
- [ ] T013 [infrastructure] `src/blondswim/infrastructure/dto.py` i `mappers.py`: clau JSON `test_css` en lloc de `tests_css`; regenera les fixtures de test. Depèn de T009.
- [ ] T014 [P] [project] Actualitza `specs/001-*/data-model.md` i `specs/001-*/contracts/fitxers-json.md`: `test_css` per piscina i exemple d'alias segons RN-003.
- [ ] T015 [project] **Checkpoint fase 0.** Demana a l'usuari: `bash scripts/verify.sh` en verd abans de continuar.

### Fase 1 del pla — fonaments

**Tests primer** (depenen de T015; entre ells paral·lels)

- [ ] T016 [P] [domain] Tests a `tests/unit/domain/test_slug.py`: `slug_competicio("Campionat d'Hivern  (25 m)")` = `campionat-d-hivern-25-m` (CA-002-51); lletres amb accent i `ß`/`ł` conservades (R2).
- [ ] T017 [P] [application] Tests a `tests/unit/importacio/test_conversio.py`: data `31/12/2026` → `FORMAT-dia`/`FORMAT-dates` amb fila, columna i valor (CA-002-05); `"` o `;` extra en un valor → `FORMAT-<camp>` (CA-002-60); diversos errors en files diferents, tots llistats i ordenats per fila (CA-002-06).
- [ ] T018 [P] [application] Tests a `tests/unit/importacio/test_flux.py` amb un cas d'ús fals que genera un avís i/o un error i un `RegistreAvisos` i `Rellotge` falsos: avís sense `--confirma` → no desa, `pendent_confirmacio`, registre intacte (CA-002-08); amb `--confirma` → desa i una línia per avís amb `decisio: confirmat`, `rn`, `fitxer`, `camp`, `valor`, `data_hora` del rellotge injectat (CA-002-09); error + avís amb `--confirma` → no desa ni registra (CA-002-10).
- [ ] T019 [P] [application] Tests a `tests/unit/importacio/test_serveis.py` amb `LectorCsv` fals que llança `ErrorLectura`: capçalera diferent (CA-002-02), no UTF-8 (CA-002-03), fitxer sense files de dades (CA-002-59), separador `,` en taula i fila no `clau;valor` en fitxa (CA-002-52): incidència d'origen `fitxer`, res desat; temporada que no segueix RN-031 → incidència `FORMAT-temporada` i no es llegeix res.
- [ ] T020 [P] [infrastructure] Tests a `tests/integration/test_lector_csv.py` amb `tmp_path` i el lector real: capçalera incorrecta (CA-002-02), Latin-1 (CA-002-03), files en blanc intercalades amb numeració de fila del fitxer (CA-002-04), separador `,` (CA-002-52), buit o només capçalera (CA-002-59), BOM ignorat a taula i a parells (CA-002-62).
- [ ] T021 [P] [project] Tests a `tests/architecture/test_capes_vistes.py` (CA-002-49): `lint-imports` passa; `interfaces` no importa `domain` ni `infrastructure`; `infrastructure.csv` no importa `domain` (R9).

**Implementació**

- [ ] T022 [P] [domain] `src/blondswim/domain/definicions.py`: `slug_competicio(nom) -> str` (NFKD, treure `Mn`, `casefold`, no alfanumèrics → `-`, treure `-` dels extrems; RN-008 citada). Fa passar T016.
- [ ] T023 [P] [application] `src/blondswim/application/importacio/entrada.py`: `FilaText`, `ContingutTaula`, `ParellText`, `ContingutParells`, `PeticioCalendari`, `PeticioInscripcions`, `PeticioFitxa`, `ErrorLectura(missatge, esperat)` (data-model §2); i el port `LectorCsv` a `application/ports.py` (`taula`, `parells`); docstring de `RegistreAvisos.afegeix`: `decisio` = `confirmat | None`.
- [ ] T024 [P] [application] `src/blondswim/application/importacio/resultat.py`: `Origen(fila, camp)`, `Incidencia(origen, codi, nivell, valor, missatge, accio)` (`nivell` `bloquejant`|`avís`), `ResumImportacio`, `ResultatImportacio` amb només tipus primitius; conversió d'`ErrorValidacio` i `Avis` a `Incidencia` (R4).
- [ ] T025 [application] `src/blondswim/application/importacio/conversio.py`: text → valors de domini (dates `AAAA-MM-DD`, temps `m:ss.cc`, enters, llistes `\|`, buit = `null`); rebuig de `"` i `;` (codis del catàleg de la spec: `FORMAT-<camp>`, `FORMAT-FILA` per nombre de camps, `FORMAT-CLAU` per a la fitxa); no s'atura al primer error; construeix la traça `camp de domini → Origen` (R5). Depèn de T023, T024; fa passar T017.
- [ ] T026 [application] `src/blondswim/application/importacio/flux.py`: dues passades, càlcul de `ok/desat/pendent_confirmacio`, registre d'avisos amb `decisio: confirmat` només en desar amb `--confirma`; ordena incidències per fila o clau, les de `fitxer` primer. Depèn de T024; fa passar T018.
- [ ] T027 [infrastructure] `src/blondswim/infrastructure/csv/lector.py` `LectorCsvFitxer`: `csv.reader(delimiter=";", quoting=csv.QUOTE_NONE)`, `encoding="utf-8-sig"`, `newline=""`, `line_num` com a fila, ignora files buides o d'espais, comprova capçalera i que hi hagi files, `parells` exigeix dos camps; llança `ErrorLectura`; no importa `domain`. Fa passar T020.
- [ ] T028 [application] `src/blondswim/application/importacio/serveis.py`: esquelet de `ServeisImportacio` (rep `LectorCsv`, repositoris, rellotge, generador d'id, registre, arrel d'entrada); deriva rutes (`<arrel>/<temporada>/calendari.csv`, `inscripcions_<alias>.csv`), valida la temporada (RN-031) i converteix `ErrorLectura` en incidència `fitxer` (D2). Fa passar T019.
- [ ] T029 [project] `pyproject.toml`: contractes import-linter `forbidden` (a) `blondswim.interfaces` no importa `blondswim.domain` ni `blondswim.infrastructure`, (b) `blondswim.infrastructure.csv` no importa `blondswim.domain`, amb `allow_indirect_imports = true`; el contracte `layers` es manté (R9). Fa passar T021.
- [ ] T030 [project] **Checkpoint fonaments.** Demana a l'usuari: `uv run pytest` en verd per a T016–T021 i `bash scripts/verify.sh`.

---

## Phase 3: US1 — Importar el calendari (P1) 🎯 MVP

**Objectiu**: catàleg comú de competicions des de `calendari.csv`, sense editar JSON.
**Test independent**: importar la fixture de T003 desa `competicions/<AAAA-AA>.json` amb id = slug i es carrega amb la spec 001; reimportar amb canvis respecta RN-010 i RN-038.

- [ ] T031 [P] [US1] [application] Tests a `tests/unit/importacio/test_calendari.py` amb repositoris en memòria: CA-002-01 (calendari sense incidències es desa, codi 0), CA-002-30 (tres competicions, id = slug), CA-002-31 (`Campionat d'Hivern` i `campionat d hivern`: RN-008 amb les dues files), CA-002-32 (`seu` buida: avís RN-009, desa amb `seu: null` només amb `--confirma`), CA-002-33 (data fora de la temporada: RN-043 amb fila, data i temporada), CA-002-63 (`nom` `---`: `FORMAT-nom`).
- [ ] T032 [P] [US1] [application] Tests a `tests/unit/importacio/test_calendari_reimportacio.py`: CA-002-34 (canvi de seu conserva l'id), CA-002-35 (treure una competició amb inscripcions: RN-010 amb competició i alias, catàleg intacte), CA-002-36 (sense inscripcions s'esborra sense error ni avís), CA-002-37 (dia desaparegut amb inscripció: RN-038 amb alias, competició i dia), CA-002-65 (canvi a piscina 50 amb inscripció `100;Ei`: RN-038 amb alias, competició i prova); inscripció il·legible → incidència `fitxer` i catàleg intacte (D6).
- [ ] T033 [P] [US1] [infrastructure] Tests a `tests/integration/test_importar_calendari.py`: lector real, repositoris JSON i fixture de T003 amb `tmp_path`; el JSON resultant es carrega sense error amb la spec 001 (CA-002-30).
- [ ] T034 [US1] [application] Comprova a `application/ports.py` que es poden llegir les inscripcions de la temporada de tots els nedadors, arxivats inclosos (D6). Si falta una operació, afegeix-la al port i a la implementació JSON d'`infrastructure/`, amb test d'integració.
- [ ] T035 [US1] [application] `src/blondswim/application/importacio/calendari.py` `importar_calendari`: conversió amb `conversio.py`; slug amb `slug_competicio` (slug buit = `FORMAT-nom`); RN-008, 009, 010, 038, 043; actualitza/afegeix/esborra al catàleg; sense inscripcions tocades. Fa passar T031 i T032.
- [ ] T036 [US1] [application] `serveis.py`: `ServeisImportacio.calendari(temporada, confirma)`. Fa passar T033.

**Checkpoint US1**: `uv run pytest -m ca` per als CA-002-30 a 37, 63 i 65.

---

## Phase 4: US3 — Importar la fitxa del nedador (P1)

**Objectiu**: alta o actualització atòmica d'un nedador amb test CSS i marques (D4).
**Test independent**: la fixture d'alta crea `nedadors/<uuid>/nedador.json` vàlid; la d'actualització canvia només els camps modificables.

- [ ] T037 [P] [US3] [application] Tests a `tests/unit/importacio/test_fitxa_format.py`: CA-002-07 (clau desconeguda, repetida o absent), CA-002-13 (`Cr|Cr`, `Cr|EP`), CA-002-15 (`whatsapp`), CA-002-19 (min > max: alias, RN i acció), CA-002-25 (dues `test_css` de la mateixa piscina), CA-002-26 (cinquè valor), CA-002-54 (t400 ≤ t200: RN-006), CA-002-56 (piscina ≠ 25/50), CA-002-57 (dues `marca` iguals), CA-002-58 (`Agonzalez`, `a_gonzalez`, `agonzález`, `agonzalez1`: RN-003).
- [ ] T038 [P] [US3] [application] Tests a `tests/unit/importacio/test_fitxa_alta.py`: CA-002-01 (alta sense incidències), CA-002-11 (alta sense avisos es desa a la primera passada), CA-002-12 (alias `agonzalez`, `arxivat: false`, informatius a `null`), CA-002-14 (`canal_preferent` buit: RN-035, codi 2), CA-002-16 (correu d'un arxivat: RN-032), CA-002-17 (alias existent: RN-041 amb proposat i assignat, `--confirma` desa, el nedador existent no canvia), CA-002-18 (cap altre nedador canvia), CA-002-53 (RN-035 amb `--confirma` registra `decisio: confirmat`), CA-002-64 (sufix impossible: RN-003).
- [ ] T039 [P] [US3] [application] Tests a `tests/unit/importacio/test_fitxa_actualitzacio.py`: CA-002-20 (id, alias i `versio_esquema` no canvien), CA-002-21 (alias inexistent: RN-003), CA-002-22 (correu d'un altre: RN-032), CA-002-23 (correu buit allibera l'antic), CA-002-24 (`test_css["25"]` substituït, el de 50 no canvia), CA-002-27 (marca millor i posterior s'afegeix; igual o pitjor no fa res ni avisa; millor amb data no posterior: error), CA-002-28 (prova no oficial: RN-030), CA-002-29 (sense `test_css` ni `marca` no canvien), CA-002-61 (arxivat: RN-042).
- [ ] T040 [P] [US3] [infrastructure] Tests a `tests/integration/test_importar_fitxa.py`: lector real i repositoris JSON; el `nedador.json` d'alta es carrega amb la spec 001 (CA-002-12); `avisos.jsonl` amb la línia RN-035 (CA-002-53).
- [ ] T041 [US3] [application] `gestio.py`: `NouNedador` porta `test_css` i `millors_registres`; actualització construeix el `Nedador` final en memòria (`CanviNedador.aplica`, `substitueix_test`, `afegeix_registre`) i es desa una sola vegada (R6).
- [ ] T042 [US3] [application] `src/blondswim/application/importacio/fitxa.py` `importar_fitxa`: claus segons la spec (obligatòries, repetibles `test_css` i `marca`); alta amb `prepara_alta`; actualització; RN-003, 005, 007, 032, 035, 041, 042; `valida_nedador` i `valida_unicitat` del nedador sencer; error → no desa res. Fa passar T037–T040.
- [ ] T043 [US3] [application] `serveis.py`: `ServeisImportacio.fitxa(cami, alta, confirma)`.

**Checkpoint US3**: `uv run pytest -m ca` per als CA-002-11 a 29, 53, 54, 56 a 58, 61 i 64.

---

## Phase 5: US2 — Importar les inscripcions (P2; depèn d'US1 i US3)

**Objectiu**: `inscripcions.json` d'un nedador i temporada des del CSV, amb totes les incidències d'un cop.
**Test independent**: amb catàleg i nedador existents, la fixture de T003 desa dues participacions i es carrega amb la spec 001.

- [ ] T044 [P] [US2] [application] Tests a `tests/unit/importacio/test_inscripcions.py`: CA-002-01, 38 (dues participacions amb proves agrupades), 39 (RN-011), 40 (RN-036 amb les dues files), 41 (RN-015), 42 (RN-030), 43 (RN-016), 44 (RN-037).
- [ ] T045 [P] [US2] [application] Tests a `tests/unit/importacio/test_inscripcions_reimportacio.py`: CA-002-45 (RN-039 amb la participació que desapareix; desa només amb `--confirma`), CA-002-46 (idèntic: cap avís, codi 0), CA-002-47 (classe A sense `principal`: RN-019), CA-002-55 (fitxer inexistent: incidència `fitxer`, res desat).
- [ ] T046 [P] [US2] [infrastructure] Tests a `tests/integration/test_importar_inscripcions.py`: lector real i repositoris JSON; `inscripcions.json` es carrega amb la spec 001 (CA-002-38) i `--confirma` substitueix el fitxer (CA-002-45).
- [ ] T047 [US2] [application] `src/blondswim/application/importacio/inscripcions.py` `importar_inscripcions`: agrupa files per competició en una participació; RN-011, 015, 016, 019, 030, 036, 037, 039 (resum de diferències); substitueix `inscripcions.json` sencer; RN-040 fora d'abast (R7, CA-002-48 pendent). Fa passar T044–T046.
- [ ] T048 [US2] [application] `serveis.py`: `ServeisImportacio.inscripcions(temporada, alias, confirma)`; l'alias és argument, no es llegeix del CSV.

**Checkpoint US2**: `uv run pytest -m ca` per als CA-002-38 a 47 i 55.

---

## Phase 6: CLI i arrel (transversal a les tres històries)

- [ ] T049 [P] [interfaces] Tests a `tests/unit/interfaces/test_cli.py` amb un `ServeisImportacio` fals: per a cada incidència el text conté origen, codi, nivell, valor i acció; codi de sortida 0/1/2 segons `desat`/`ok`/`pendent_confirmacio` sense cap altra lògica (CA-002-50); format de l'informe segons `contracts/cli.md`.
- [ ] T050 [P] [project] Tests a `tests/integration/test_cli_extrem_a_extrem.py`: `blondswim.arrel.main` amb `tmp_path` i les fixtures: calendari → fitxa `--alta` → inscripcions, i un cas d'error per fitxer d'entrada (R12).
- [ ] T051 [interfaces] `src/blondswim/interfaces/cli.py`: `argparse` amb `importar fitxa|calendari|inscripcions`, `--alta`, `--temporada`, `--alias`, `--confirma`; `executa(args, serveis)` només importa `application`; pinta l'informe i tradueix a codi de sortida. Fa passar T049.
- [ ] T052 [project] `src/blondswim/arrel.py`: crea repositoris, `LectorCsvFitxer`, rellotge i generador d'id; construeix `ServeisImportacio` i crida `interfaces.cli.executa` (D1). Fa passar T050.
- [ ] T053 [project] `pyproject.toml`: `[project.scripts]` `blondswim = "blondswim.arrel:main"`.

---

## Phase 7: Polish

- [ ] T054 [project] Comprova la traçabilitat: tots els CA-002 excepte el 48 (pendent spec 003) tenen un test amb `@pytest.mark.ca`; cap marcador òrfic.
- [ ] T055 [project] Demana a l'usuari que validi `specs/002-importacio/quickstart.md` de punta a punta.
- [ ] T056 [project] **Final.** Demana a l'usuari: `bash scripts/verify.sh` en verd.

---

## Dependències i ordre

- Setup → Foundational (fase 0 → fonaments) → històries → CLI → Polish.
- Fase 0 bloqueja tot (T015). Fonaments (T030) bloqueja les històries.
- US1 i US3 són independents i poden anar en paral·lel; `serveis.py` el toquen totes (T036, T043, T048): edicions seqüencials.
- US2 comença quan acaben US1 i US3 (necessita catàleg i nedador).
- CLI (T049–T053) pot començar els tests amb un servei fals un cop fets els fonaments, però T050 exigeix les tres històries.
- Dins de cada història: tests → ports/gestió → cas d'ús → servei.

## Paral·lelisme

```text
Setup:        T002, T003
Fase 0 tests: T005, T006, T007, T008
Fonaments:    T016, T017, T018, T019, T020, T021 | T022, T023, T024
US1 tests:    T031, T032, T033
US3 tests:    T037, T038, T039, T040
US2 tests:    T044, T045, T046
```

## Estratègia

- **MVP**: Setup + Foundational + US1 (calendari): és el catàleg sobre el qual es basen les inscripcions. US3 (P1) s'afegeix a continuació; US2 al final.
- Lliurament incremental: cada checkpoint de història es verifica amb `uv run pytest -m ca` abans de seguir.
- Una spec, una branca (`002-importacio`); commits petits per tasca o grup lògic.
