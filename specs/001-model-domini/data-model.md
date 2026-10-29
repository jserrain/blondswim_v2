# Data model — Spec 001

Model del domini (`src/blondswim/domain/`). L'ordre dels camps és el de l'escriptura JSON (research R3). Les regles es citen per ID; el text normatiu és a `docs/regles.md`.

## Objectes de valor

| Objecte | Representació | Validació |
|---|---|---|
| `IdNedador` | text, UUID v4 canònic en minúscules | RN-001, ADR-0014 |
| `Correu` | text normalitzat | RN-032 |
| `Canal` | `correu` \| `mobil` | un altre valor és un error de format; absent o `null`: RN-035 |
| `Alias` | text | RN-003 |
| `Estil` | enum `Cr`, `Esq`, `Br`, `Pap`, `Ei` | spec 000 §4; als estils preferents només aquests cinc (CA-001-39) |
| `Dia` | enum `dl`…`dg` | CA-001-40 |
| `Piscina` | enum 25, 50 | CA-001-41 |
| `Temps` | centèsimes (int) ↔ `m:ss.cc` | research R4; CA-001-07 |
| `Prova` | `{distancia: int, estil: Estil}` | oficial per a la piscina: RN-030 |
| `Classe` | enum A, B, C | |
| `Prioritat` | enum `principal`, `secundària` | spec 000 §7 |
| `CodiTemporada` | text `AAAA-AA` | RN-031; deriva `inici` i `fi` |
| Definicions | proves oficials (RN-030), inici de temporada (RN-031) | constants a `domain/definicions.py` (research R2) |

## Entitats

Tipus de camp (spec, § Format JSON): **obligatori** (ha de ser-hi amb valor), **informatiu** (pot faltar o ser `null`, sense avís) i **opcional amb avís**. En desar s'escriuen tots els camps.

### Nedador (`nedadors/<id>/nedador.json`)
| Camp | Tipus | Obligatori | Regla / CA |
|---|---|---|---|
| `versio_esquema` | int | sí | CA-001-17 |
| `correu` | `Correu` | sí | RN-032; CA-001-24, 44, 85 a 88 |
| `mobil` | text no buit (sense espais als extrems) | sí | ADR-0017; CA-001-54, 93 |
| `canal_preferent` | `Canal` \| null | opcional amb avís | RN-035; CA-001-57 a 60 |
| `alias` | `Alias` | sí | RN-003; CA-001-26, 46, 50 a 53, 61 |
| `arxivat` | bool | sí | RN-017; `false` en crear-lo |
| `estils_preferents` | llista d'`Estil`, ≥ 1, sense repetir | sí | CA-001-03, 39 |
| `dies_entrenament` | llista de `Dia`, ≥ 1, sense repetir | sí | CA-001-03, 40 |
| `volum_setmanal` | `{min, max}` en metres | sí | RN-005 |
| `tests_css` | llista de `TestCss` | sí (pot ser buida) | RN-006 |
| `millors_registres` | llista de `MillorRegistre` | sí (pot ser buida) | RN-007, RN-030 |

L'id no és al fitxer: és el nom de la carpeta.

### TestCss
| Camp | Tipus | Obligatori |
|---|---|---|
| `data` | data | sí |
| `piscina` | `Piscina` | sí |
| `t400`, `t200` | `Temps` | sí; t400 > t200 (RN-006) |
| `acceptat` | bool | sí (CA-001-35); `false` en registrar-lo |
| `detall_400`, `detall_200` | `DetallProva` \| null | informatiu |
| `notes` | text \| null | informatiu |

**DetallProva:** `parcials` (llista de `Temps`: 4 al 400 i 2 al 200 \| null), `bracades_per_llarg` (> 0 \| null), `sr` (> 0 \| null), `rpe` (enter 0–10 \| null). Un `null` no genera cap avís (CA-001-32).

### MillorRegistre
| Camp | Tipus | Obligatori |
|---|---|---|
| `estil`, `distancia` | `Prova` (oficial per a la piscina: RN-030) | sí |
| `piscina` | `Piscina` | sí |
| `temps` | `Temps` (centèsimes) | sí |
| `data` | data | sí |
| `competicio` | id de competició del catàleg, amb la mateixa piscina | sí (CA-001-90, 91, 94) |

Un sol registre per prova i piscina, només de competició (RN-007). En afegir-ne un: si el temps és menor que el desat, el substitueix (CA-001-83); si és igual o pitjor, no es fa res (CA-001-89). Dos registres de la mateixa prova i piscina en un fitxer: ERROR (CA-001-06). Els tests CSS es desen tots.

### Competició (`competicions/<AAAA-AA>.json`, catàleg)
Fitxer: `{versio_esquema, competicions: [...]}`.
| Camp | Tipus | Regla |
|---|---|---|
| `id` | text estable | RN-008 |
| `nom` | text | |
| `dates` | llista de dates, ≥ 1 | |
| `piscina` | `Piscina` | |
| `seu` | text \| null | opcional amb avís (RN-009) |

### Inscripcions de temporada (`nedadors/<id>/temporades/<AAAA-AA>/inscripcions.json`)
Fitxer: `{versio_esquema, participacions: [...]}`.

**Participació:** `id_competicio` (RN-011), `classe`, `proves` (≥ 1 inscripció, RN-014). Una per competició (RN-012). Totes les dates de la competició són dins de la temporada (RN-013, RN-031).

**Inscripció:** `prova` (RN-030, segons la piscina de la competició), `dia` (RN-015), `prioritat`. Una per prova i competició (RN-016).

## Consultes (no es desen)
- `proves_objectiu(nedador)`: inscripcions de les participacions A (CA-001-16).
- `test_vigent(nedador, piscina)`: l'últim test acceptat de la piscina (CA-001-05, 30).
- `setmana_iso(data)` (CA-001-18).
- CSS i zones: spec 004.

**Definició (no és una consulta):** inici i fi de temporada (RN-031), a `domain/definicions.py`.

## Validació (nivells)
1. **ERROR / AVÍS per nedador** (entrada, càrrega i filtre, amb un sol validador; spec, § Validació). Inclou les regles que creuen fitxers: RN-003 i RN-032 entre nedadors, RN-011 i RN-007 (competició del millor registre) amb el catàleg. Un ERROR en un fitxer del nedador deixa fora aquell nedador (a la càrrega, tots els implicats en una col·lisió). La unicitat (només correu i alias) es comprova sobre tots els fitxers que es poden llegir, vàlids o no; una col·lisió identifica tots els implicats. Un fitxer que no es pot llegir és un ERROR propi i no hi participa. Un ERROR en un fitxer del catàleg (RN-008) fa fallar TOTA la càrrega. Un AVÍS no exclou ningú.
2. **Filtre:** passa per tots els nedadors i no s'atura al primer error; un nedador amb un ERROR no es planifica fins que es corregeix.
3. **Aptitud per planificar:** RN-017 i RN-018 són motius de bloqueig; RN-019 i RN-020 són avisos.

Resultat: `Resultat(errors, avisos)` per nedador (research R5). Cada element: identificador (alias, o l'UUID de la carpeta si el fitxer no es pot llegir), camp, valor, RN (o «format») i acció.

## Registre d'avisos (`data/avisos.jsonl`)
Una línia JSON per avís: `data_hora` (ISO 8601), `rn`, `fitxer`, `camp`, `valor`, `missatge`, `id_nedador` (o `null`), `decisio` (`confirmat`, `rebutjat` o `null`). `null` per als avisos de càrrega i de planificació. Només s'hi afegeix (CA-001-47, 48, 57, 63, 64).

## Dades immutables i modificables (nedador)
| Tipus | Camps | Regla |
|---|---|---|
| Immutables | `id`, `alias`, `versio_esquema` | `versio_esquema` només canvia amb una migració; la modificació no els rep com a dada (CA-001-53) |
| Modificables | `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament`, `volum_setmanal` | torna a validar el nedador sencer, unicitat inclosa; amb un ERROR no es desa res (CA-001-79, 80); el correu antic queda lliure (CA-001-88) |
| Operació pròpia | `arxivat` | arxivar i desarxivar (RN-017; CA-001-81) |
| Operació pròpia | `tests_css` | només s'afegeixen; un test desat no s'edita; el coach l'accepta (CA-001-30, 82) |
| Operació pròpia | `millors_registres` | s'afegeixen; un temps menor substitueix el desat i un d'igual o pitjor no fa res (RN-007; CA-001-83, 89); un registre desat no s'edita |

Canvi de `dies_entrenament` o `volum_setmanal` a mitja temporada: la 001 el permet; la replanificació és de la spec 005 (CA-001-84).

## Transicions d'estat
| Entitat | Transició | Regla |
|---|---|---|
| Nedador | creat → arxivat | RN-004, RN-017; CA-001-81 |
| Nedador | arxivat → desarxivat | RN-017; CA-001-81 |
| Nedador | esborrar | sempre error (RN-004, CA-001-37) |
| TestCss | registrat (`acceptat: false`) → acceptat | CA-001-30; canvia el test vigent. Un test desat no s'edita (CA-001-82) |
| Competició | esborrar | error si té participacions o és referenciada per un millor registre (RN-010; CA-001-21, 95) |
