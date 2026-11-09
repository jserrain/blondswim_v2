---

description: "Llista de tasques de la spec 001 — Model de domini"
---

# Tasks: Model de domini

**Input**: Design documents from `/specs/001-model-domini/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/fitxers-json.md

**Tests**: obligatoris. Cada CA no pendent té almenys una tasca de test amb `@pytest.mark.ca("CA-001-nn")`. CA-001-33, 34, 38, 58, 63, 64, 68, 72 i 84 són `[PENDENT]` i no tenen tasca. CA-001-55, 56, 77, 85, 86, 87, 88, 94, 95, 98, 99, 100 i 103 estan retirats. En total, 90 CA amb test (99 actius; taula CA → tasca al final). A més, T050 cobreix el CA-000-10 de la spec 000 (els altres 23 CA de la 000 són `[PENDENT]`).

**Ordre dels IDs**: els IDs no segueixen l'ordre d'execució. L'ordre és el de les fases: T002 va al final (Polish); T035–T050 (US1b) s'executen abans de T017; T051–T052 amb US3 (després de T024) i T053–T054 amb US4 (després de T027).

**Organization**: la spec 001 no té històries d'usuari (§ Assumptions). Les fases s'organitzen per **blocs funcionals** independents, amb les etiquetes US1–US6:

| Etiqueta | Bloc | CA |
|---|---|---|
| US1 | Nedador: càrrega, validació i desament (implementat amb la spec anterior; vegeu US1b) | 49, 01, 03, 04, 06, 07, 17, 24, 26, 27, 31, 32, 35, 36, 39, 40, 41 (test, millor registre), 42 (millor registre), 44, 46 |
| US1b | UUID, alias, contacte, marca de competició i validació (validador únic, filtre, alta, modificació) | 06, 24, 26, 27, 44, 46, 25, 45, 50, 51, 52, 53, 54, 57, 59, 60, 61, 62, 65, 66, 67, 69, 70, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 89, 90, 91, 92, 93, 96, 97, 101, 102, 104, 105, 106, 107, 108, 109, 110, 111, 112 |
| US2 | Catàleg de competicions | 11, 12, 17 (catàleg), 36 (catàleg), 41 (competició), 71 |
| US3 | Inscripcions de temporada i càrrega del catàleg | 02, 08, 09, 10, 17 (inscripcions), 19, 20, 22, 23, 29, 36 (inscripcions), 42 (inscripció), 43 |
| US4 | Derivats i aptitud per planificar | 05, 13, 14, 15, 16, 18, 28 |
| US5 | Operacions de gestió (competició i test) | 21, 30, 37 |
| US6 | Registre d'avisos | 47, 48 i 57 (línia al registre) |

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

**Nota (esmena de la spec 001, 99 CA actius):** el codi i els tests de T003–T010 es van escriure amb la versió anterior de la spec (p. ex. `IdNedador` `n` + 4 dígits, sense `Canal`, `Resultat` sense acció, `Correu` obligatori i sense el format de RN-032). El codi s'adapta a US1b (T040, T042, T043); els tests es reescriuen a T048 i T049. Aquí no es canvia res.

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

**Goal**: adaptar el nedador a ADR-0014 i ADR-0020 (id UUID v4, alias, correu opcional, desat tal com s'entra, amb format mínim i únic, mòbil, `canal_preferent`, millors registres com a llista de millores successives per prova i piscina, sense dependre del catàleg) i construir el validador únic, la càrrega per nedador, el filtre i les operacions sobre el nedador (alta, modificació, arxivar i desarxivar, afegir tests i registres).

**Depends on**: US1 (T011–T016) i Foundational.

**Independent Test**: els CA del bloc passen sense catàleg ni inscripcions. Els avisos es comproven al `Resultat`; la línia al registre és de US6. Tota la funcionalitat de la marca (afegir, ordre, marca vigent) és d'aquest bloc: `competicio` és un nom i no es comprova contra el catàleg.

**Nota:** el codi fet (p. ex. `valors.py` amb `_RE_ID = n[0-9]{4}`) segueix la spec antiga; US1b el modifica. Decisions D1 i D2: `plan.md`, § Decisions de disseny confirmades.

### Tests (s'escriuen primer i han de fallar)

- [x] T048 [US1b] [domain] Reescriure els tests fets de T003 i T011 (`tests/unit/test_valors.py`, `tests/unit/test_nedador.py`) contra la spec nova, abans de T040: fixtures amb UUID v4, `alias`, `correu`, `mobil` i `canal_preferent`; `IdNedador` UUID en lloc de `n` + 4 dígits (CA-001-27); `Correu` opcional segons RN-032 (CA-001-44); CA-001-06 segons el text vigent de la spec (dos registres consecutius amb el mateix temps → error, RN-007); CA-001-96 (llista no ordenada → error); CA-001-97 (`marca_vigent`); CA-001-90 (`competicio` obligatori, text no buit). Els marcadors `@pytest.mark.ca` només canvien on el CA ha canviat. T035, T036 i T038 depenen d'aquesta tasca (mateixos fitxers)
- [x] T049 [US1b] [infrastructure] Reescriure els tests fets de T007 i T012 (`tests/integration/test_dto.py`, `tests/integration/test_nedador_json.py`) contra la spec nova, abans de T040: fixtures amb UUID v4, `alias`, `correu`, `mobil` i `canal_preferent`; `competicio` (nom) als millors registres; `correu` opcional (absent ≡ `null`). Mateixos CA que T012; el CA-001-01 compara el contingut amb el correu idèntic, sense normalitzar
- [x] T050 [P] [US1b] [infrastructure] Test del CA-000-10 de la spec 000 a `tests/integration/test_millor_registre_json.py`, amb `@pytest.mark.ca("CA-000-10")`, abans de T044: un millor registre sense `piscina` (absent o `null`) al JSON és un error del DTO que identifica el camp. Al domini `piscina` ja és un tipus obligatori: no cal test a `domain`. Els altres 23 CA de la spec 000 no tenen tasca (vegeu «CA de la spec 000»)
- [x] T035 [P] [US1b] [domain] Tests de valors i alias a `tests/unit/test_valors.py` (ampliar després de T048) i `tests/unit/test_alias.py`: `IdNedador` rebutja `n0001`, majúscules i UUID v1 (CA-001-27); `Correu` accepta el format bàsic i el conserva idèntic (un exemple per cas de CA-001-104: `a@b.c`, `  Pere@Exemple.cat `, un tabulador al principi, un salt de línia al final i `a@b@example.com`), rebutja un exemple per cas de CA-001-105 (RN-032), accepta `usari@gmial.com` tal qual (CA-001-106) i es compara en minúscules i sense espais en blanc (espais, tabuladors i salts de línia) als extrems; `Canal` només `correu` o `mobil` (CA-001-59); `Alias` `<part>_<sufix>` rebutja `""`, `marc`, `Marc_3f2a9c1` i `marc_cognom_3f2a9c1` (CA-001-46) i un sufix que no coincideix amb l'id (CA-001-51)
- [x] T036 [P] [US1b] [domain] Tests del validador únic a `tests/unit/test_validador.py`: CA-001-24, 26, 44, 50, 54, 57 (avís RN-035 al `Resultat`), 67, 69, 73, 76, 91 (`competicio` que no és al catàleg: cap error ni avís), 93 (`mobil` buit o només amb espais), 105 (correu amb format no vàlid: ERROR), 107 (sense correu: vàlid), 108 (col·lisió `A@b.com` i ` a@b.com `), 110 (`canal_preferent` = `correu` sense correu: avís RN-035), 111 (`mobil` amb només un tabulador o un salt de línia), 96 (llista de marques no ordenada: ERROR que identifica la prova i la piscina), 101 (`mobil` compartit o sense format E.164: cap error ni avís), 102 (en carregar, una marca amb data igual o anterior a la de l'anterior de la mateixa prova i piscina: ERROR)
- [x] T037 [P] [US1b] [application] Tests de càrrega i filtre a `tests/unit/test_carrega_filtre.py`, amb repositoris en memòria: CA-001-60, 65, 66, 74, 78. El CA-001-78 (entrada, càrrega i filtre) fa servir l'alta: depèn de T047 i el seu test no passa fins que T047 és feta
- [x] T038 [P] [US1b] [infrastructure] Tests de fitxer a `tests/integration/test_nedador_json.py` (ampliar després de T049), abans de T044: CA-001-27 (carpeta que no és UUID v4), 57 (`canal_preferent` absent ≡ `null`), 59 (`"whatsapp"`: error de format amb alias, camp, valor i opcions), 75 (JSON trencat: ERROR propi amb l'UUID de la carpeta, fora de la unicitat), 104 (el fitxer desat porta el correu idèntic), 107 (correu absent ≡ `null`), 92 i la regla de D1 (un camp d'identitat que falta o no és text no participa a la unicitat d'aquell camp, però sí a la de l'altre)
- [x] T039 [P] [US1b] [application] Tests de les operacions a `tests/unit/test_gestio_nedador.py`, amb repositoris en memòria i `GeneradorId` fix: CA-001-25, 45, 52, 53, 61, 62, 70, 79, 80, 81, 82, 83 (afegir una marca millor; les piscines no es comparen), 89 (un temps igual o pitjor no fa res), 90 (afegir un registre sense `competicio`), 97 (`marca_vigent`: l'última de la llista de la prova i piscina, després d'afegir marques), 102 (afegir una marca millor amb data igual o anterior a la vigent: ERROR i la llista no canvia), 108 (alta o modificació amb un correu en col·lisió: ERROR i no es desa res), 109 (modificar el correu: es desa tal qual, l'id no canvia i l'antic queda lliure), 112 (modificar amb `correu: null`: el nedador es desa sense correu, l'id no canvia i el correu antic queda lliure per a un altre nedador)

### Implementació

- [x] T040 [US1b] [domain] Adaptar `src/blondswim/domain/valors.py` (T004): `IdNedador` (RN-001); `Correu` opcional, que conserva el valor tal com s'ha entrat, amb el format de RN-032 comprovat només per caràcters (sense expressió regular estricta ni xarxa; els espais en blanc dels extrems —espais, tabuladors i salts de línia— no compten) i amb una clau de comparació per a la unicitat en minúscules i sense espais en blanc (espais, tabuladors i salts de línia) als extrems; `Temporada.de_codi` a `definicions.py` (T006; RN-031), l'únic lloc; `Canal` `correu` \| `mobil`; `Alias` i generació de l'alias (RN-003). Elimina la regla antiga `n` + 4 dígits
- [x] T041 [US1b] [domain] Adaptar `Nedador` a `src/blondswim/domain/nedador.py` (T013): `correu` opcional (sense correu = `None`), `mobil` obligatori, `canal_preferent` opcional amb avís, `alias`, `arxivat`, `MillorRegistre` amb `competicio` (nom, text no buit; sense catàleg); afegir `CanviNedador` amb només `correu` (un valor o `None` per treure'l; cal distingir «no canvia» de «treu el correu»; CA-001-112), `mobil` (text no buit després de treure'n els espais en blanc als extrems; CA-001-111), `canal_preferent`, `estils_preferents`, `dies_entrenament` i `volum_setmanal` (no pot portar `id`, `alias` ni `versio_esquema`; CA-001-53) i una funció pura d'afegir un millor registre: s'afegeix si el temps és menor que la marca vigent de la mateixa prova i piscina (o si no n'hi ha cap); si és igual o pitjor, torna la llista sense canvis; si el temps és menor però la data no és posterior a la de la vigent, error; les piscines no es comparen (RN-007; CA-001-83, 89, 102). Consulta pura `marca_vigent(nedador, prova, piscina)`: l'última de la llista (CA-001-97). Sense cap mètode que editi un test o un registre desat (CA-001-82, 83). Revisa la docstring que cita RN-007: ha de descriure la RN-007 vigent
- [x] T042 [US1b] [domain] Validador únic a `src/blondswim/domain/validacio.py` (adapta T005 i T014): `ErrorValidacio` i `Avis` amb `accio`; un nedador acumula tots els errors (RN-001, 003, 005, 006, 007, 030, 032 i format, inclòs `mobil` buit després de treure'n els espais en blanc (espais, tabuladors i salts de línia): un mòbil amb només un tabulador o un salt de línia és ERROR; CA-001-93, 111) i els avisos (RN-035, també `canal_preferent` = `correu` sense correu; CA-001-110); validació entre nedadors: col·lisió de correu (comparat en minúscules i sense espais en blanc —espais, tabuladors i salts de línia— als extrems; un nedador sense correu no hi participa) o alias (ERROR que identifica tots els implicats; CA-001-24, 26, 69, 76, 108). RN-007: una marca no millor que l'anterior de la mateixa prova i piscina (igual o pitjor) és ERROR, i també una data igual o anterior a la de l'anterior (CA-001-06, 96, 102); `competicio` absent, `null` o buit és ERROR (CA-001-90); no es comprova contra el catàleg (CA-001-91). Resultat per nedador i per camp: alias (o UUID), camp, valor, RN o «format», acció
- [x] T043 [US1b] [application] Ampliar `src/blondswim/application/ports.py` (T010): `RepositoriNedadors` (llegir nedadors, llegir identitats dels fitxers llegibles, desar) i `GeneradorId` (`nou() -> IdNedador`)
- [x] T044 [US1b] [infrastructure] Adaptar `dto.py`, `mappers.py` i `repositoris.py` (T015, T016): camps `correu` (opcional; absent ≡ `null`), `mobil`, `canal_preferent` (absent ≡ `null`; valor fora de `correu`/`mobil` → error de format amb alias, camp, valor i opcions), `alias`, `arxivat`, `competicio` (nom) als millors registres; nom de carpeta (RN-001); fitxer il·legible (JSON trencat o que no és un objecte) → ERROR propi amb l'UUID; DTO mínim d'identitat (D1): `correu` i `alias` com a text cru; el correu comparat en minúscules i sense espais en blanc (espais, tabuladors i salts de línia) als extrems (el valor no canvia) i l'alias tal com és, `extra="ignore"`; si un camp falta o no és text (un correu absent és vàlid, però no participa a la unicitat), el nedador no participa a la unicitat d'aquell camp, però sí a la de l'altre (CA-001-92; tests a T038); `generador_id.py` amb `uuid4()`
- [x] T045 [US1b] [application] Càrrega per nedador a `src/blondswim/application/carrega.py`: un ERROR exclou només aquell nedador; una col·lisió d'unicitat n'exclou tots els implicats; la resta es carrega; el registre d'avisos s'afegeix a T032 (CA-001-60, 65, 66)
- [x] T046 [US1b] [application] Filtre de validació a `src/blondswim/application/filtre.py`: passa per tots els nedadors, no s'atura al primer error, llista tots els errors i avisos per nedador i camp; fitxer il·legible com a ERROR propi; el nedador amb un ERROR no es planifica; entrada, càrrega i filtre donen el mateix resultat (CA-001-67, 73, 74, 75, 78)
- [x] T047 [US1b] [application] Operacions a `src/blondswim/application/gestio.py`: alta (genera id i alias; si l'alias existeix, id nou; un ERROR no es desa; la unicitat compta els fitxers llegibles; el correu es desa tal com s'ha entrat; CA-001-45, 52, 61, 62, 70, 108), modificar amb `CanviNedador` (valida el nedador sencer, unicitat inclosa; amb un ERROR no es desa res; l'id i l'alias no canvien; el correu nou es desa tal qual i l'antic queda lliure; `correu: null` treu el correu i el deixa lliure; CA-001-25, 53, 79, 80, 108, 109, 112), arxivar i desarxivar (CA-001-81), afegir test amb `acceptat: false` i afegir millor registre amb la regla de T041 (CA-001-83, 89, 90, 102), sense cap operació d'edició (CA-001-82, 83)

**Checkpoint**: US1b verda

---

## Phase 4: US2 — Catàleg (P2)

**Goal**: carregar i validar `competicions/<AAAA-AA>.json`.

- [x] T017 [P] [US2] [domain] Tests a `tests/unit/test_cataleg.py`: CA-001-11, 12, 17 (`versio_esquema` desconegut del catàleg: falla TOTA la càrrega), 36 (el fitxer del catàleg desat és idèntic byte a byte), 41 (competició), 71 (nom de fitxer que no segueix RN-031: falla TOTA la càrrega)
- [x] T018 [US2] [domain] `Competicio` i `Cataleg` a `src/blondswim/domain/cataleg.py`. `dates`: «≥ 1»; `seu`: «text \| null» amb avís RN-009; `id` únic (RN-008)
- [x] T019 [US2] [infrastructure] DTO, mapper i `RepositoriCataleg` a `src/blondswim/infrastructure/mappers.py` i `repositoris.py`. El nom del fitxer segueix RN-031; si no, falla TOTA la càrrega (CA-001-71)

---

## Phase 5: US3 — Inscripcions (P3)

**Goal**: carregar i validar `inscripcions.json` contra el catàleg i la temporada.

**Depends on**: US2 (catàleg)

- [x] T020 [P] [US3] [domain] Tests a `tests/unit/test_inscripcions.py`: CA-001-08, 09, 10, 19, 20, 22, 23, 29, 42 (inscripció)
- [x] T021 [P] [US3] [infrastructure] Tests a `tests/integration/test_inscripcions_json.py`: CA-001-02, 17 (`versio_esquema` desconegut d'`inscripcions.json`: aquell nedador no es carrega), 36 (`inscripcions.json` desat idèntic byte a byte), 43
- [x] T022 [US3] [domain] `Participacio` i `Inscripcio` a `src/blondswim/domain/inscripcions.py`. `proves`: «≥ 1» (RN-014); una participació per competició (RN-012); una inscripció per prova (RN-016)
- [x] T023 [US3] [domain] Validació creuada amb el catàleg (RN-011, RN-013, RN-015, RN-030 segons la piscina de la competició, només per a les inscripcions) a `src/blondswim/domain/validacio.py`
- [x] T024 [US3] [infrastructure] DTO, mapper i lectura de `temporades/<AAAA-AA>/inscripcions.json` a `src/blondswim/infrastructure/mappers.py` i `repositoris.py`; una carpeta que no segueix RN-031 → error
- [x] T051 [P] [US3] [application] Tests de càrrega del catàleg i de les inscripcions a `tests/unit/test_carrega_cataleg.py`, amb repositoris en memòria: CA-001-11, 17, 41 i 71 (un ERROR del catàleg falla TOTA la càrrega) i CA-001-19 (un ERROR d'inscripcions exclou només aquell nedador; la resta es carrega)
- [x] T052 [US3] [application] Càrrega del catàleg i de les inscripcions a `src/blondswim/application/carrega.py` i `filtre.py`: un ERROR del catàleg (RN-008, RN-031, format) falla TOTA la càrrega; un ERROR d'inscripcions (RN-011 a RN-016, RN-030 d'inscripcions) exclou només aquell nedador; el filtre ho llista per nedador i camp com a US1b (CA-001-11, 17, 19, 41, 71). Només es demana el catàleg d'una temporada si hi ha inscripcions d'aquella temporada: sense inscripcions, l'absència de catàleg no impedeix carregar nedadors

---

## Phase 6: US4 — Derivats i aptitud (P4)

**Depends on**: US1, US1b i US3. T054 també depèn de T031 (US6).

- [x] T025 [P] [US4] [domain] Tests a `tests/unit/test_derivats.py`: CA-001-05, 13, 14, 15, 16, 18, 28
- [x] T026 [US4] [domain] Consultes `setmana_iso`, `test_vigent` i `proves_objectiu` a `src/blondswim/domain/derivats.py`. Cap d'aquests valors es desa. La temporada és una definició (`Temporada.de_codi`, `definicions.py`, T040; RN-031) i la `marca_vigent` és a T041
- [x] T027 [US4] [domain] Aptitud per planificar a `src/blondswim/domain/validacio.py`: bloquegen RN-017 i RN-018; avisos RN-019 i RN-020 al `Resultat`
- [ ] T053 [P] [US4] [application] Tests del cas d'ús d'aptitud a `tests/unit/test_aptitud.py`, amb registre d'avisos en memòria i rellotge fix: CA-001-13 i 14 (l'avís es registra amb `decisio: null`), 15, 28
- [ ] T054 [US4] [application] Cas d'ús d'aptitud per planificar a `src/blondswim/application/aptitud.py`: aplica T027 i registra els avisos RN-019 i RN-020 al registre d'avisos (T031) amb `decisio: null`, sense confirmació. Depèn de T027 i T031

---

## Phase 7: US5 — Gestió (P5)

**Depends on**: US1b i US3. L'alta, la modificació, arxivar i desarxivar i afegir tests i registres són a T047.

- [x] T028 [P] [US5] [application] Tests a `tests/unit/test_gestio.py`, amb repositoris en memòria: CA-001-21, 30, 37
- [x] T029 [US5] [application] Casos d'ús a `src/blondswim/application/gestio.py`: esborrar nedador (sempre error, el nedador no canvia; RN-004), acceptar test (el test nou passa a ser el vigent; CA-001-30), esborrar competició (error si té participacions, RN-010)

---

## Phase 8: US6 — Registre d'avisos (P6)

**Depends on**: US1b i US2 (avisos RN-009 i RN-035)

- [ ] T030 [P] [US6] [infrastructure] Tests a `tests/integration/test_registre_avisos.py`, amb `tmp_path` i rellotge fix: CA-001-47 (`decisio: null`), 48, 57 (RN-035 amb `decisio: null`, sense demanar confirmació), 110 (RN-035 per `canal_preferent` = `correu` sense correu, identificant `canal_preferent`, amb `decisio: null`)
- [ ] T031 [US6] [infrastructure] `data/avisos.jsonl` en mode afegir a `src/blondswim/infrastructure/registre_avisos.py` (camps `data_hora`, `rn`, `fitxer`, `camp`, `valor`, `missatge`, `id_nedador` i `decisio`: `confirmat` \| `rebutjat` \| `null`) i rellotge del sistema a `src/blondswim/infrastructure/rellotge.py`. Les línies anteriors no es toquen (CA-001-48)
- [ ] T032 [US6] [application] Afegir el registre d'avisos a la càrrega (T045 i T052) a `src/blondswim/application/carrega.py` (RN-009 i RN-035, també `canal_preferent` = `correu` sense correu; CA-001-110): `decisio: null`, sense confirmació. La decisió `confirmat`/`rebutjat` de l'entrada és de la spec 002. Els avisos d'aptitud (RN-019, RN-020) es registren a T054

---

## Phase 9: Polish

- [ ] T002 [project] Canviar `tracabilitat = "avis"` per `"bloquejant"` a `pyproject.toml` (`[tool.blondswim]`) quan tots els CA no pendents de la 001 tinguin test, després de T032 i T054 (AGENTS.md).
- [ ] T033 [project] Executar quickstart.md: `bash scripts/verify.sh` ha d'acabar «LLEST PER SEGUIR», amb la traçabilitat bloquejant
- [ ] T034 [project] Actualitzar `docs/mapa_specs.md`: la spec 001 és implementada

---

## Dependencies & Execution Order

- Setup → Foundational → US1 → US1b → US2 → US3 i US6 → US4 i US5 en paral·lel → Polish.
- US4 depèn de US1b (i T054, de T031, a US6).
- Dins de cada bloc: tests (vermell) → domini → infraestructura o aplicació.
- A US1b, T048 i T049 van abans de T035, T038 i T040 (mateixos fitxers de test i de codi).
- CA-001-78 (T037) depèn de T047: el test es completa després de l'alta.
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

Els CA pendents no tenen tasca: 33, 34 (spec 004), 38, 58, 63, 64, 68, 72 (spec 002), 84 (spec 005). Els CA 55, 56, 77, 85, 86, 87, 88, 94, 95, 98, 99, 100 i 103 estan retirats.

| CA | Tasques de test | CA | Tasques de test |
|---|---|---|---|
| 01 | T012 | 49 | T012 |
| 02 | T021 | 50 | T036 |
| 03 | T011 | 51 | T035 |
| 04 | T011 | 52 | T039 |
| 05 | T025 | 53 | T039 |
| 06 | T011, T048 | 54 | T036 |
| 07 | T012 | 57 | T036, T038, T030 |
| 08 | T020 | 59 | T035, T038 |
| 09 | T020 | 60 | T037 |
| 10 | T020 | 61 | T039 |
| 11 | T017, T051 | 62 | T039 |
| 12 | T017 | 65 | T037 |
| 13 | T025, T053 | 66 | T037 |
| 14 | T025, T053 | 67 | T036 |
| 15 | T025, T053 | 69 | T036 |
| 16 | T025 | 70 | T039 |
| 17 | T012, T017, T021, T051 | 71 | T017, T051 |
| 18 | T025 | 73 | T036 |
| 19 | T020, T051 | 74 | T037 |
| 20 | T020 | 75 | T038 |
| 21 | T028 | 76 | T036 |
| 22 | T020 | 78 | T037 |
| 23 | T020 | 79 | T039 |
| 24 | T011, T036 | 80 | T039 |
| 25 | T039 | 81 | T039 |
| 26 | T011, T036 | 82 | T039 |
| 27 | T012, T035, T038 | 83 | T039 |
| 28 | T025, T053 | 89 | T039 |
| 29 | T020 | 90 | T048, T039 |
| 30 | T028 | 91 | T036 |
| 31 | T012 | 92 | T038 |
| 32 | T011 | 93 | T036 |
| 35 | T011 | 96 | T036, T048 |
| 36 | T012, T017, T021 | 97 | T039, T048 |
| 37 | T028 | 101 | T036 |
| 39 | T011 | 102 | T036, T039 |
| 40 | T011 | 104 | T035, T038 |
| 41 | T011, T017, T051 | 105 | T035, T036 |
| 42 | T011, T020 | 106 | T035 |
| 43 | T021 | 107 | T036, T038 |
| 44 | T011, T036, T048 | 108 | T036, T039 |
| 45 | T039 | 109 | T039 |
| 46 | T011, T035 | 110 | T036, T030 |
| 47 | T030 | 111 | T036 |
| 48 | T030 | 112 | T039 |

Total: 90 CA amb tasca; 0 CA no pendents sense tasca. CA-000-10 (spec 000): T050.

## CA de la spec 000

Inventari del 2026-10-29: dels 24 CA de la spec 000, només el CA-000-10 (millor registre sense piscina) fa servir el domini de la 001 → T050. Els altres 23 són `[PENDENT]` a la spec 000: CA-000-01 (spec 004) i CA-000-02 a 09 i 11 a 24 (spec 006).
