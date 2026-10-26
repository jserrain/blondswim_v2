# Data model — Spec 001

Model del domini (`src/blondswim/domain/`). L'ordre dels camps és el de l'escriptura JSON (research R3). Les regles es citen per ID; el text normatiu és a `docs/regles.md`.

## Objectes de valor

| Objecte | Representació | Validació |
|---|---|---|
| `IdNedador` | text, UUID v4 canònic en minúscules | RN-001, ADR-0014 |
| `Correu` | text | RN-032 (no buit, sense espais); igualtat sense distingir majúscules |
| `Mobil` | text E.164 (`+` i de 8 a 15 dígits) | RN-033 |
| `Canal` | `correu` \| `mobil` | RN-035 |
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
| `correu` | `Correu` | sí | RN-032; CA-001-24, 44 |
| `mobil` | `Mobil` | sí | RN-033, RN-034; CA-001-54 a 56 |
| `canal_preferent` | `Canal` \| null | informatiu | RN-035; CA-001-57 a 60 |
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
`estil`, `distancia`, `piscina`, `temps`, `data` i `competicio` (text lliure). Únic per (estil, distància, piscina) (RN-007). La prova és oficial (RN-030).

### Competició (`competicions/<AAAA-AA>.json`, catàleg)
Fitxer: `{versio_esquema, competicions: [...]}`.
| Camp | Tipus | Regla |
|---|---|---|
| `id` | text estable | RN-008 |
| `nom` | text no buit | |
| `dates` | llista de dates, ≥ 1 | |
| `piscina` | `Piscina` | |
| `seu` | text \| null | opcional amb avís (RN-009) |

### Inscripcions de temporada (`nedadors/<id>/temporades/<AAAA-AA>/inscripcions.json`)
Fitxer: `{versio_esquema, participacions: [...]}`.

**Participació:** `id_competicio` (RN-011), `classe`, `proves` (≥ 1 inscripció, RN-014). Una per competició (RN-012). Totes les dates de la competició són dins de la temporada (RN-013, RN-031).

**Inscripció:** `prova` (RN-030, segons la piscina de la competició), `dia` (RN-015), `prioritat`. Una per prova i competició (RN-016).

## Valors derivats (no es desen)
- `Temporada.inici` i `Temporada.fi` (RN-031).
- `setmana_iso(data)` (CA-001-18).
- `proves_objectiu(nedador)`: inscripcions de les participacions A (CA-001-16).
- `test_vigent(nedador, piscina)`: l'últim test acceptat de la piscina (CA-001-05, 30).
- CSS i zones: spec 004.

## Validació (dos nivells)
1. **Model vàlid** (càrrega). Inclou les regles que creuen fitxers: RN-003, RN-032 i RN-034 entre nedadors, RN-011 amb el catàleg.
2. **Aptitud per planificar:** RN-017 i RN-018 són motius de bloqueig; RN-019 i RN-020 són avisos.

Resultat: `Resultat(errors, avisos)` (research R5).

## Registre d'avisos (`data/avisos.jsonl`)
Una línia JSON per avís: `data_hora` (ISO 8601), `rn`, `fitxer`, `camp`, `valor`, `missatge`, `id_nedador` (o `null`). Només s'hi afegeix (CA-001-47, 48).

## Transicions d'estat
| Entitat | Transició | Regla |
|---|---|---|
| Nedador | creat → arxivat | RN-004, RN-017; no hi ha transició inversa en aquesta spec |
| Nedador | esborrar | sempre error (RN-004, CA-001-37) |
| TestCss | registrat (`acceptat: false`) → acceptat | CA-001-30; canvia el test vigent |
| Competició | esborrar | error si té participacions (RN-010) |
