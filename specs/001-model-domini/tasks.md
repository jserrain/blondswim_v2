---

description: "Llista de tasques de la spec 001 — Model de domini"
---

# Tasks: Model de domini

**Input**: Design documents from `/specs/001-model-domini/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/fitxers-json.md

**Tests**: obligatoris. Cada CA no pendent té almenys una tasca de test amb `@pytest.mark.ca("CA-001-nn")`. CA-001-33, 34 i 38 són `[PENDENT]` i no tenen tasca. En total, 46 CA amb test.

**Organization**: la spec 001 no té històries d'usuari (§ Assumptions). Les fases s'organitzen per **blocs funcionals** independents, amb les etiquetes US1–US5:

| Etiqueta | Bloc | CA |
|---|---|---|
| US1 | Nedador: càrrega, validació i desament | 49, 01, 03, 04, 06, 07, 17, 24, 26, 27, 31, 32, 35, 36, 39, 40, 41 (test, millor registre), 42 (millor registre), 44, 46 |
| US2 | Catàleg de competicions | 11, 12, 41 (competició) |
| US3 | Inscripcions de temporada | 02, 08, 09, 10, 19, 20, 22, 23, 29, 42 (inscripció), 43 |
| US4 | Derivats i aptitud per planificar | 05, 13, 14, 15, 16, 18, 28 |
| US5 | Operacions de gestió | 21, 25, 30, 37, 45 |
| US6 | Registre d'avisos | 47, 48 |

## Format: `[ID] [P?] [Story] [Layer] Description`

- **[P]**: es pot fer en paral·lel (fitxers diferents, sense dependències).
- **[Layer]**: domain | application | infrastructure | interfaces | project.
- Una tasca que afecta diverses capes es divideix en una tasca per capa.

---

## Phase 1: Setup

**Purpose**: dependència i traçabilitat activa

- [ ] T001 [project] Afegir Pydantic v2: `uv add pydantic` (research R1)
- [ ] T002 [project] Canviar `tracabilitat = "avis"` per `"bloquejant"` a `pyproject.toml` (`[tool.blondswim]`), en el mateix commit que la primera tasca de codi (AGENTS.md)

---

## Phase 2: Foundational

**Purpose**: objectes de valor, definicions, resultat de validació, lectura estricta i escriptura estable, que fan servir tots els blocs

**⚠️ CRITICAL**: cap bloc no comença fins que aquesta fase és completa

- [ ] T003 [P] [domain] Tests unitaris dels objectes de valor a `tests/unit/test_valors.py`. `Temps` rebutja `1:05.3` (`^\d+:[0-5]\d\.\d{2}$`, CA-001-07); `Piscina` només 25 i 50 (CA-001-41); `Estil` d'estil preferent només `Cr`, `Esq`, `Br`, `Pap` i `Ei` (CA-001-39); `IdNedador` `n` + 4 dígits (CA-001-27); `Correu` no buit i sense espais (CA-001-44)
- [ ] T004 [domain] Objectes de valor a `src/blondswim/domain/valors.py`: `IdNedador`, `Correu` (igualtat sense distingir majúscules), `Alias`, `Estil`, `Dia`, `Piscina`, `Temps` (centèsimes enteres), `Prova`, `Classe`, `Prioritat`, `CodiTemporada`
- [ ] T005 [P] [domain] `Resultat(errors, avisos)`, `ErrorValidacio` i `Avis` (camps `rn`, `fitxer`, `camp`, `valor`, `missatge`) a `src/blondswim/domain/validacio.py` (research R5)
- [ ] T006 [P] [domain] Definicions a `src/blondswim/domain/definicions.py`, citant l'ID: proves oficials per piscina i estil (RN-030) i inici de temporada 1/10 (RN-031). Únic lloc del codi amb aquests valors (principi V, 1.3.0)
- [ ] T007 [P] [infrastructure] Test a `tests/integration/test_dto.py`: `"piscina": "25"`, `"acceptat": "yes"` i un camp desconegut són error amb missatge en català i ruta del camp (research R1)
- [ ] T008 [infrastructure] Base dels DTO a `src/blondswim/infrastructure/dto.py` (`strict=True`, `extra="forbid"`, `frozen=True`) i catàleg de missatges en català per `type` d'error
- [ ] T009 [P] [infrastructure] Escriptura estable a `src/blondswim/infrastructure/json_io.py`: UTF-8, `indent=2`, `ensure_ascii=False`, salt de línia final, ordre de claus del data model, `null` explícits (research R3)
- [ ] T010 [P] [application] Ports a `src/blondswim/application/ports.py`: `RepositoriNedadors`, `RepositoriCataleg`, `RegistreAvisos`, `Rellotge` (Protocols)

**Checkpoint**: base llesta

---

## Phase 3: US1 — Nedador (P1) 🎯 MVP

**Goal**: carregar, validar i desar `nedador.json`.

**Independent Test**: els CA del bloc US1 passen sense catàleg ni inscripcions.

### Tests (s'escriuen primer i han de fallar)

- [ ] T011 [P] [US1] [domain] Tests de validació del nedador a `tests/unit/test_nedador.py`: CA-001-03, 04, 06, 24, 26, 32, 35, 39, 40, 41 (test i millor registre), 42 (millor registre), 44, 46
- [ ] T012 [P] [US1] [infrastructure] Tests de fitxer a `tests/integration/test_nedador_json.py`: CA-001-01, 07, 17, 27, 31, 36, 49

### Implementació

- [ ] T013 [US1] [domain] `Nedador`, `TestCss`, `DetallProva` i `MillorRegistre` a `src/blondswim/domain/nedador.py`. `estils_preferents` i `dies_entrenament`: «≥ 1, sense repetir»; `volum_setmanal`: RN-005; `t400 > t200`: RN-006; `rpe` «enter 0–10 \| null»; `parcials` «4 al 400 i 2 al 200 \| null»
- [ ] T014 [US1] [domain] Validació del nedador i entre nedadors (RN-003, RN-007, RN-030, RN-032) a `src/blondswim/domain/validacio.py`
- [ ] T015 [US1] [infrastructure] DTO de `nedador.json` a `dto.py` i mapper DTO ↔ `Nedador` a `src/blondswim/infrastructure/mappers.py`: camp obligatori absent o `null` → error; camp informatiu absent ≡ `null` sense avís (CA-001-49); `versio_esquema` ≠ 1 → error (CA-001-17); errors amb fitxer, camp i valor
- [ ] T016 [US1] [infrastructure] `RepositoriNedadors` sobre `data/nedadors/<id>/` a `src/blondswim/infrastructure/repositoris.py`. L'id és el nom de la carpeta (RN-001)

**Checkpoint**: US1 verda

---

## Phase 4: US2 — Catàleg (P2)

**Goal**: carregar i validar `competicions/<AAAA-AA>.json`.

- [ ] T017 [P] [US2] [domain] Tests a `tests/unit/test_cataleg.py`: CA-001-11, 12, 41 (competició)
- [ ] T018 [US2] [domain] `Competicio` i `Cataleg` a `src/blondswim/domain/cataleg.py`. `dates`: «≥ 1»; `seu`: «text \| null» amb avís RN-009; `id` únic (RN-008)
- [ ] T019 [US2] [infrastructure] DTO, mapper i `RepositoriCataleg` a `src/blondswim/infrastructure/mappers.py` i `repositoris.py`. El nom del fitxer segueix RN-031

---

## Phase 5: US3 — Inscripcions (P3)

**Goal**: carregar i validar `inscripcions.json` contra el catàleg i la temporada.

**Depends on**: US2 (catàleg)

- [ ] T020 [P] [US3] [domain] Tests a `tests/unit/test_inscripcions.py`: CA-001-08, 09, 10, 19, 20, 22, 23, 29, 42 (inscripció)
- [ ] T021 [P] [US3] [infrastructure] Tests a `tests/integration/test_inscripcions_json.py`: CA-001-02, 43
- [ ] T022 [US3] [domain] `Participacio` i `Inscripcio` a `src/blondswim/domain/inscripcions.py`. `proves`: «≥ 1» (RN-014); una participació per competició (RN-012); una inscripció per prova (RN-016)
- [ ] T023 [US3] [domain] Validació creuada amb el catàleg (RN-011, RN-013, RN-015, RN-030 segons la piscina de la competició) a `src/blondswim/domain/validacio.py`
- [ ] T024 [US3] [infrastructure] DTO, mapper i lectura de `temporades/<AAAA-AA>/inscripcions.json`; una carpeta que no segueix RN-031 → error

---

## Phase 6: US4 — Derivats i aptitud (P4)

**Depends on**: US1 i US3

- [ ] T025 [P] [US4] [domain] Tests a `tests/unit/test_derivats.py`: CA-001-05, 13, 14, 15, 16, 18, 28
- [ ] T026 [US4] [domain] `temporada`, `setmana_iso`, `test_vigent` i `proves_objectiu` a `src/blondswim/domain/derivats.py`. Cap d'aquests valors es desa
- [ ] T027 [US4] [domain] Aptitud per planificar a `src/blondswim/domain/validacio.py`: bloquegen RN-017 i RN-018; avisos RN-019 i RN-020

---

## Phase 7: US5 — Gestió (P5)

**Depends on**: US1 i US3

- [ ] T028 [P] [US5] [application] Tests a `tests/unit/test_gestio.py`, amb repositoris en memòria: CA-001-21, 25, 30, 37, 45
- [ ] T029 [US5] [application] Casos d'ús a `src/blondswim/application/gestio.py`: crear nedador (id = més alt existent, arxivats inclosos, + 1; RN-002), arxivar, esborrar nedador (sempre error, RN-004), canviar correu, registrar test (`acceptat: false`), acceptar test, esborrar competició (error si té participacions, RN-010)

---

## Phase 8: US6 — Registre d'avisos (P6)

**Depends on**: US2 (avís RN-009)

- [ ] T030 [P] [US6] [infrastructure] Tests a `tests/integration/test_registre_avisos.py`, amb `tmp_path` i rellotge fix: CA-001-47, 48
- [ ] T031 [US6] [infrastructure] `data/avisos.jsonl` en mode afegir a `src/blondswim/infrastructure/registre_avisos.py` (camps `data_hora`, `rn`, `fitxer`, `camp`, `valor`, `missatge`, `id_nedador`) i rellotge del sistema a `src/blondswim/infrastructure/rellotge.py`
- [ ] T032 [US6] [application] Cas d'ús de càrrega que registra els avisos a `src/blondswim/application/carrega.py`

---

## Phase 9: Polish

- [ ] T033 [project] Executar quickstart.md: `bash scripts/verify.sh` ha d'acabar «LLEST PER SEGUIR», amb la traçabilitat bloquejant
- [ ] T034 [project] Actualitzar `docs/mapa_specs.md`: la spec 001 és implementada

---

## Dependencies & Execution Order

- Setup → Foundational → US1 i US2 en paral·lel → US3 i US6 → US4 i US5 en paral·lel → Polish.
- Dins de cada bloc: tests (vermell) → domini → infraestructura o aplicació.
- T002 va en el mateix commit que la primera tasca de codi (T004).

## Parallel Example: US1

```bash
Task: "T011 Tests de validació del nedador a tests/unit/test_nedador.py"
Task: "T012 Tests de fitxer a tests/integration/test_nedador_json.py"
```

## Implementation Strategy

1. Setup i Foundational.
2. **MVP:** US1 (nedador). Validar i aturar-se.
3. US2 → US3 i US6 → US4 i US5.
4. Polish. Cada tasca s'acaba amb `bash scripts/verify.sh` en verd (principi VII).
