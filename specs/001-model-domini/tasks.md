---

description: "Llista de tasques de la spec 001 — Model de domini"
---

# Tasks: Model de domini

**Input**: Design documents from `/specs/001-model-domini/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/fitxers-json.md

**Tests**: obligatoris. Cada CA no pendent té almenys una tasca de test amb `@pytest.mark.ca("CA-001-nn")`. CA-001-33, 34, 38, 58, 63, 64, 68, 72 i 84 són `[PENDENT]` i no tenen tasca. En total, 75 CA amb test (taula CA → tasca al final).

**Organization**: la spec 001 no té històries d'usuari (§ Assumptions). Les fases s'organitzen per **blocs funcionals** independents, amb les etiquetes US1–US6:

| Etiqueta | Bloc | CA |
|---|---|---|
| US1 | Nedador: càrrega, validació i desament (implementat amb la spec anterior; vegeu US1b) | 49, 01, 03, 04, 06, 07, 17, 24, 26, 27, 31, 32, 35, 36, 39, 40, 41 (test, millor registre), 42 (millor registre), 44, 46 |
| US1b | UUID, alias, contacte i validació (validador únic, filtre, alta, modificació) | 24, 26, 27, 44, 46, 25, 45, 50, 51, 52, 53, 54, 55, 56, 57, 59, 60, 61, 62, 65, 66, 67, 69, 70, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83 |
| US2 | Catàleg de competicions | 11, 12, 41 (competició), 71 |
| US3 | Inscripcions de temporada | 02, 08, 09, 10, 19, 20, 22, 23, 29, 42 (inscripció), 43 |
| US4 | Derivats i aptitud per planificar | 05, 13, 14, 15, 16, 18, 28 |
| US5 | Operacions de gestió (competició i test) | 21, 30, 37 |
| US6 | Registre d'avisos | 47, 48, 56 i 57 (línia al registre) |

## Format: `[ID] [P?] [Story] [Layer] Description`

- **[P]**: es pot fer en paral·lel (fitxers diferents, sense dependències).
- **[Layer]**: domain | application | infrastructure | interfaces | project.
- Una tasca que afecta diverses capes es divideix en una tasca per capa.

---

## Phase 1: Setup

**Purpose**: dependència

- [x] T001 [project] Afegir Pydantic v2: `uv add pydantic` (research R1)

---

## Phase 2: Foundational

**Purpose**: objectes de valor, definicions, resultat de validació, lectura estricta i escriptura estable, que fan servir tots els blocs

**⚠️ CRITICAL**: cap bloc no comença fins que aquesta fase és completa

- [x] T003 [P] [domain] Tests unitaris dels objectes de valor a `tests/unit/test_valors.py`. `Temps` rebutja `1:05.3` (`^\d+:[0-5]\d\.\d{2}$`, CA-001-07); `Piscina` només 25 i 50 (CA-001-41); `Estil` d'estil preferent només `Cr`, `Esq`, `Br`, `Pap` i `Ei` (CA-001-39); `IdNedador` `n` + 4 dígits (CA-001-27); `Correu` no buit i sense espais (CA-001-44)
- [x] T004 [domain] Objectes de valor a `src/blondswim/domain/valors.py`: `IdNedador`, `Correu` (igualtat sense distingir majúscules), `Alias`, `Estil`, `Dia`, `Piscina`, `Temps` (centèsimes enteres), `Prova`, `Classe`, `Prioritat`, `CodiTemporada`
- [x] T005 [P] [domain] `Resultat(errors, avisos)`, `ErrorValidacio` i `Avis` (camps `rn`, `fitxer`, `camp`, `valor`, `missatge`) a `src/blondswim/domain/validacio.py` (research R5)
- [x] T006 [P] [domain] Definicions a `src/blondswim/domain/definicions.py`, citant l'ID: proves oficials per piscina i estil (RN-030) i inici de temporada 1/10 (RN-031). Únic lloc del codi amb aquests valors (principi V, 1.3.0)
- [x] T007 [P] [infrastructure] Test a `tests/integration/test_dto.py`: `"piscina": "25"`, `"acceptat": "yes"` i un camp desconegut són error amb missatge en català i ruta del camp (research R1)
- [x] T008 [infrastructure] Base dels DTO a `src/blondswim/infrastructure/dto.py` (`strict=True`, `extra="forbid"`, `frozen=True`) i catàleg de missatges en català per `type` d'error
- [x] T009 [P] [infrastructure] Escriptura estable a `src/blondswim/infrastructure/json_io.py`: UTF-8, `indent=2`, `ensure_ascii=False`, salt de línia final, ordre de claus del data model, `null` explícits (research R3)
- [x] T010 [P] [application] Ports a `src/blondswim/application/ports.py`: `RepositoriNedadors`, `RepositoriCataleg`, `RegistreAvisos`, `Rellotge` (Protocols)

**Nota (esmena de la spec 001, 84 CA):** el codi de T003–T010 es va escriure amb la versió anterior de la spec (p. ex. `IdNedador` `n` + 4 dígits, sense `Mobil` ni `Canal`, `Resultat` sense acció). L'adaptació és a US1b (T040, T042, T043); aquí no es canvia res.

**Checkpoint**: base llesta

---

## Phase 3: US1 — Nedador (P1) 🎯 MVP

**Goal**: carregar, validar i desar `nedador.json`.

**Independent Test**: els CA del bloc US1 passen sense catàleg ni inscripcions.

### Tests (s'escriuen primer i han de fallar)

- [x] T011 [P] [US1] [domain] Tests de validació del nedador a `tests/unit/test_nedador.py`: CA-001-03, 04, 06, 24, 26, 32, 35, 39, 40, 41 (test i millor registre), 42 (millor registre), 44, 46
- [x] T012 [P] [US1] [infrastructure] Tests de fitxer a `tests/integration/test_nedador_json.py`: CA-001-01, 07, 17, 27, 31, 36, 49

### Implementació

- [x] T013 [US1] [domain] `Nedador`, `TestCss`, `DetallProva` i `MillorRegistre` a `src/blondswim/domain/nedador.py`. `estils_preferents` i `dies_entrenament`: «≥ 1, sense repetir»; `volum_setmanal`: RN-005; `t400 > t200`: RN-006; `rpe` «enter 0–10 \| null»; `parcials` «4 al 400 i 2 al 200 \| null»
- [x] T014 [US1] [domain] Validació del nedador i entre nedadors (RN-003, RN-007, RN-030, RN-032) a `src/blondswim/domain/validacio.py`
- [x] T015 [US1] [infrastructure] DTO de `nedador.json` a `dto.py` i mapper DTO ↔ `Nedador` a `src/blondswim/infrastructure/mappers.py`: camp obligatori absent o `null` → error; camp informatiu absent ≡ `null` sense avís (CA-001-49); `versio_esquema` ≠ 1 → error (CA-001-17); errors amb fitxer, camp i valor
- [x] T016 [US1] [infrastructure] `RepositoriNedadors` sobre `data/nedadors/<id>/` a `src/blondswim/infrastructure/repositoris.py`. L'id és el nom de la carpeta (RN-001)

**Checkpoint**: US1 verda (contra la spec anterior; l'adaptació és a US1b)

---

## Phase 3b: US1b — UUID, alias, contacte i validació

**Goal**: adaptar el nedador a ADR-0014 i ADR-0016 (id UUID v4, alias, correu i mòbil, `canal_preferent`) i construir el validador únic, la càrrega per nedador, el filtre i les operacions sobre el nedador (alta, modificació, arxivar i desarxivar, afegir tests i registres).

**Depends on**: US1 (T011–T016) i Foundational.

**Independent Test**: els CA del bloc passen sense catàleg ni inscripcions. Els avisos es comproven al `Resultat`; la línia al registre és de US6.

**Nota:** el codi fet (p. ex. `valors.py` amb `_RE_ID = n[0-9]{4}`) segueix la spec antiga; US1b el modifica. Decisions D1 i D2: `plan.md`, § Decisions de disseny confirmades.

### Tests (s'escriuen primer i han de fallar)

- [ ] T035 [P] [US1b] [domain] Tests de valors i alias a `tests/unit/test_valors.py` (ampliar) i `tests/unit/test_alias.py`: `IdNedador` rebutja `n0001`, majúscules i UUID v1 (CA-001-27); `Mobil` rebutja `600000000`, `+34 600 000 000` i `+3460` (CA-001-55); `Canal` només `correu` o `mobil` (CA-001-59); `Alias` `<part>_<sufix>` rebutja `""`, `marc`, `Marc_3f2a9c1` i `marc_cognom_3f2a9c1` (CA-001-46) i un sufix que no coincideix amb l'id (CA-001-51)
- [ ] T036 [P] [US1b] [domain] Tests del validador únic a `tests/unit/test_validador.py`: CA-001-24, 26, 44, 50, 54, 56 (avís RN-034 al `Resultat`), 57 (avís RN-035 al `Resultat`), 67, 69, 73, 76, 77
- [ ] T037 [P] [US1b] [application] Tests de càrrega i filtre a `tests/unit/test_carrega_filtre.py`, amb repositoris en memòria: CA-001-60, 65, 66, 74, 78
- [ ] T038 [P] [US1b] [infrastructure] Tests de fitxer a `tests/integration/test_nedador_json.py` (ampliar): CA-001-27 (carpeta que no és UUID v4), 57 (`canal_preferent` absent ≡ `null`), 59 (`"whatsapp"`: error de format amb alias, camp, valor i opcions), 75 (JSON trencat: ERROR propi amb l'UUID de la carpeta, fora de la unicitat)
- [ ] T039 [P] [US1b] [application] Tests de les operacions a `tests/unit/test_gestio_nedador.py`, amb repositoris en memòria i `GeneradorId` fix: CA-001-25, 45, 52, 53, 61, 62, 70, 79, 80, 81, 82, 83

### Implementació

- [ ] T040 [US1b] [domain] Adaptar `src/blondswim/domain/valors.py` (T004): `IdNedador` UUID v4 canònic en minúscules (RN-001); `Mobil` E.164 «`+` i de 8 a 15 dígits» (RN-033); `Canal` `correu` \| `mobil`; `Alias` `<part>_<sufix>` amb el sufix = 7 primers caràcters de l'id i generació de l'alias (RN-003). Elimina la regla antiga `n` + 4 dígits
- [ ] T041 [US1b] [domain] Adaptar `Nedador` a `src/blondswim/domain/nedador.py` (T013): `mobil` obligatori, `canal_preferent` opcional amb avís, `alias`, `arxivat`; afegir `CanviNedador` amb només `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament` i `volum_setmanal` (no pot portar `id`, `alias` ni `versio_esquema`; CA-001-53). Sense cap mètode que editi un test o un registre desat (CA-001-82, 83)
- [ ] T042 [US1b] [domain] Validador únic a `src/blondswim/domain/validacio.py` (adapta T005 i T014): `ErrorValidacio` i `Avis` amb `accio`; un nedador acumula tots els errors (RN-001, 003, 005, 006, 030, 032, 033 i format) i els avisos (RN-034, RN-035); validació entre nedadors: col·lisió de correu o alias (ERROR que identifica tots els implicats; CA-001-24, 26, 69, 76) i RN-034 (un avís per nedador amb fitxer llegible; CA-001-56, 77). Treu RN-007 (retirada). Resultat per nedador i per camp: alias (o UUID), camp, valor, RN o «format», acció
- [ ] T043 [US1b] [application] Ampliar `src/blondswim/application/ports.py` (T010): `RepositoriNedadors` (llegir nedadors, llegir identitats dels fitxers llegibles, desar) i `GeneradorId` (`nou() -> IdNedador`)
- [ ] T044 [US1b] [infrastructure] Adaptar `dto.py`, `mappers.py` i `repositoris.py` (T015, T016): camps `mobil`, `canal_preferent` (absent ≡ `null`; valor fora de `correu`/`mobil` → error de format amb alias, camp, valor i opcions), `alias`, `arxivat`; nom de carpeta UUID v4 (RN-001); fitxer il·legible (JSON trencat o que no és un objecte) → ERROR propi amb l'UUID; DTO mínim d'identitat (D1): `correu`, `alias` i `mobil` com a text cru, normalitzats com la validació, `extra="ignore"`; si un camp falta o no és text, el nedador no participa a la unicitat d'aquell camp, però sí a la dels altres; `generador_id.py` amb `uuid4()`
- [ ] T045 [US1b] [application] Càrrega per nedador a `src/blondswim/application/carrega.py`: un ERROR exclou només aquell nedador; una col·lisió d'unicitat n'exclou tots els implicats; la resta es carrega; el registre d'avisos s'afegeix a T032 (CA-001-60, 65, 66)
- [ ] T046 [US1b] [application] Filtre de validació a `src/blondswim/application/filtre.py`: passa per tots els nedadors, no s'atura al primer error, llista tots els errors i avisos per nedador i camp; fitxer il·legible com a ERROR propi; el nedador amb un ERROR no es planifica; entrada, càrrega i filtre donen el mateix resultat (CA-001-67, 73, 74, 75, 78)
- [ ] T047 [US1b] [application] Operacions a `src/blondswim/application/gestio.py`: alta (genera id i alias; si l'alias existeix, id nou; un ERROR no es desa; la unicitat compta els fitxers llegibles; CA-001-45, 52, 61, 62, 70), modificar amb `CanviNedador` (valida el nedador sencer, unicitat inclosa; amb un ERROR no es desa res; l'id i l'alias no canvien; CA-001-25, 53, 79, 80), arxivar i desarxivar (CA-001-81), afegir test amb `acceptat: false` i afegir millor registre, sense cap operació d'edició (CA-001-82, 83)

**Checkpoint**: US1b verda

---

## Phase 4: US2 — Catàleg (P2)

**Goal**: carregar i validar `competicions/<AAAA-AA>.json`.

- [ ] T017 [P] [US2] [domain] Tests a `tests/unit/test_cataleg.py`: CA-001-11, 12, 41 (competició), 71 (nom de fitxer que no segueix RN-031: falla TOTA la càrrega)
- [ ] T018 [US2] [domain] `Competicio` i `Cataleg` a `src/blondswim/domain/cataleg.py`. `dates`: «≥ 1»; `seu`: «text \| null» amb avís RN-009; `id` únic (RN-008)
- [ ] T019 [US2] [infrastructure] DTO, mapper i `RepositoriCataleg` a `src/blondswim/infrastructure/mappers.py` i `repositoris.py`. El nom del fitxer segueix RN-031; si no, falla TOTA la càrrega (CA-001-71)

---

## Phase 5: US3 — Inscripcions (P3)

**Goal**: carregar i validar `inscripcions.json` contra el catàleg i la temporada.

**Depends on**: US2 (catàleg)

- [ ] T020 [P] [US3] [domain] Tests a `tests/unit/test_inscripcions.py`: CA-001-08, 09, 10, 19, 20, 22, 23, 29, 42 (inscripció)
- [ ] T021 [P] [US3] [infrastructure] Tests a `tests/integration/test_inscripcions_json.py`: CA-001-02, 43
- [ ] T022 [US3] [domain] `Participacio` i `Inscripcio` a `src/blondswim/domain/inscripcions.py`. `proves`: «≥ 1» (RN-014); una participació per competició (RN-012); una inscripció per prova (RN-016)
- [ ] T023 [US3] [domain] Validació creuada amb el catàleg (RN-011, RN-013, RN-015, RN-030 segons la piscina de la competició) a `src/blondswim/domain/validacio.py`
- [ ] T024 [US3] [infrastructure] DTO, mapper i lectura de `temporades/<AAAA-AA>/inscripcions.json` a `src/blondswim/infrastructure/mappers.py` i `repositoris.py`; una carpeta que no segueix RN-031 → error

---

## Phase 6: US4 — Derivats i aptitud (P4)

**Depends on**: US1 i US3

- [ ] T025 [P] [US4] [domain] Tests a `tests/unit/test_derivats.py`: CA-001-05, 13, 14, 15, 16, 18, 28
- [ ] T026 [US4] [domain] `temporada`, `setmana_iso`, `test_vigent` i `proves_objectiu` a `src/blondswim/domain/derivats.py`. Cap d'aquests valors es desa
- [ ] T027 [US4] [domain] Aptitud per planificar a `src/blondswim/domain/validacio.py`: bloquegen RN-017 i RN-018; avisos RN-019 i RN-020

---

## Phase 7: US5 — Gestió (P5)

**Depends on**: US1b i US3. L'alta, la modificació, arxivar i desarxivar i afegir tests i registres són a T047.

- [ ] T028 [P] [US5] [application] Tests a `tests/unit/test_gestio.py`, amb repositoris en memòria: CA-001-21, 30, 37
- [ ] T029 [US5] [application] Casos d'ús a `src/blondswim/application/gestio.py`: esborrar nedador (sempre error, el nedador no canvia; RN-004), acceptar test (el test nou passa a ser el vigent; CA-001-30), esborrar competició (error si té participacions, RN-010)

---

## Phase 8: US6 — Registre d'avisos (P6)

**Depends on**: US1b i US2 (avisos RN-009, RN-034, RN-035)

- [ ] T030 [P] [US6] [infrastructure] Tests a `tests/integration/test_registre_avisos.py`, amb `tmp_path` i rellotge fix: CA-001-47 (`decisio: null`), 48, 56 (una línia RN-034 per nedador, amb el mòbil a `valor`), 57 (RN-035 amb `decisio: null`, sense demanar confirmació)
- [ ] T031 [US6] [infrastructure] `data/avisos.jsonl` en mode afegir a `src/blondswim/infrastructure/registre_avisos.py` (camps `data_hora`, `rn`, `fitxer`, `camp`, `valor`, `missatge`, `id_nedador` i `decisio`: `confirmat` \| `rebutjat` \| `null`) i rellotge del sistema a `src/blondswim/infrastructure/rellotge.py`. Les línies anteriors no es toquen (CA-001-48)
- [ ] T032 [US6] [application] Afegir el registre d'avisos a la càrrega (T045) i als casos d'ús d'aptitud per planificar a `src/blondswim/application/carrega.py` (RN-009, RN-019, RN-020, RN-034, RN-035): `decisio: null`, sense confirmació. La decisió `confirmat`/`rebutjat` de l'entrada és de la spec 002

---

## Phase 9: Polish

- [ ] T002 [project] Canviar `tracabilitat = "avis"` per `"bloquejant"` a `pyproject.toml` (`[tool.blondswim]`) quan tots els CA no pendents de la 001 tinguin test, després de T032 (AGENTS.md)
- [ ] T033 [project] Executar quickstart.md: `bash scripts/verify.sh` ha d'acabar «LLEST PER SEGUIR», amb la traçabilitat bloquejant
- [ ] T034 [project] Actualitzar `docs/mapa_specs.md`: la spec 001 és implementada

---

## Dependencies & Execution Order

- Setup → Foundational → US1 → US1b → US2 → US3 i US6 → US4 i US5 en paral·lel → Polish.
- Dins de cada bloc: tests (vermell) → domini → infraestructura o aplicació.
- T002 s'executa al final (Polish): amb mode bloquejant, `verify.sh` fallaria mentre quedin CA sense test.

## Parallel Example: US1

```bash
Task: "T011 Tests de validació del nedador a tests/unit/test_nedador.py"
Task: "T012 Tests de fitxer a tests/integration/test_nedador_json.py"
```

## Implementation Strategy

1. Setup i Foundational.
2. **MVP:** US1 (nedador) i US1b (UUID, alias, contacte i validació). Validar i aturar-se.
3. US2 → US3 i US6 → US4 i US5.
4. Polish. Cada tasca s'acaba amb `bash scripts/verify.sh` en verd (principi VII).

## Taula CA → tasca

Els CA pendents no tenen tasca: 33, 34 (spec 004), 38, 58, 63, 64, 68, 72 (spec 002), 84 (spec 005).

| CA | Tasques de test | CA | Tasques de test |
|---|---|---|---|
| 01 | T012 | 43 | T021 |
| 02 | T021 | 44 | T011, T036 |
| 03 | T011 | 45 | T039 |
| 04 | T011 | 46 | T011, T035 |
| 05 | T025 | 47 | T030 |
| 06 | T011 | 48 | T030 |
| 07 | T012 | 49 | T012 |
| 08 | T020 | 50 | T036 |
| 09 | T020 | 51 | T035 |
| 10 | T020 | 52 | T039 |
| 11 | T017 | 53 | T039 |
| 12 | T017 | 54 | T036 |
| 13 | T025 | 55 | T035 |
| 14 | T025 | 56 | T036, T030 |
| 15 | T025 | 57 | T036, T038, T030 |
| 16 | T025 | 59 | T035, T038 |
| 17 | T012 | 60 | T037 |
| 18 | T025 | 61 | T039 |
| 19 | T020 | 62 | T039 |
| 20 | T020 | 65 | T037 |
| 21 | T028 | 66 | T037 |
| 22 | T020 | 67 | T036 |
| 23 | T020 | 69 | T036 |
| 24 | T011, T036 | 70 | T039 |
| 25 | T039 | 71 | T017 |
| 26 | T011, T036 | 73 | T036 |
| 27 | T012, T035, T038 | 74 | T037 |
| 28 | T025 | 75 | T038 |
| 29 | T020 | 76 | T036 |
| 30 | T028 | 77 | T036 |
| 31 | T012 | 78 | T037 |
| 32 | T011 | 79 | T039 |
| 35 | T011 | 80 | T039 |
| 36 | T012 | 81 | T039 |
| 37 | T028 | 82 | T039 |
| 39 | T011 | 83 | T039 |
| 40 | T011 | | |
| 41 | T011, T017 | | |
| 42 | T011, T020 | | |

Total: 75 CA amb tasca; 0 CA no pendents sense tasca.
