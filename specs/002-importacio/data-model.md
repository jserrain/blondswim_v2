# Data Model: Importació estricta

**Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Els formats dels tres CSV són a la spec (§ Fitxers d'entrada) i no es repeteixen aquí. Aquest document defineix els tipus nous i els canvis al model de la spec 001. Cap camp derivat es desa (principi V).

## 1. Canvis al domini (fase 0 i fonaments)

### TestCss (spec 001, ADR-0022)
| Camp | Tipus | Obligatori | Nota |
|---|---|---|---|
| `data` | data | sí | RN-028 i RN-029 la fan servir |
| `t400`, `t200` | temps `m:ss.cc` | sí | RN-006: t400 > t200 |
| `detall_400`, `detall_200` | `DetallProva` o `null` | no | informatius; la fitxa els deixa `null` |
| `notes` | text o `null` | no | informatiu; la fitxa el deixa `null` |

Desapareixen `piscina` (és la clau) i `acceptat`.

### Nedador.test_css
Un test o `null` per a cada piscina (`25` i `50`). Substitueix `tests_css` (llista). `test_vigent(nedador, piscina)` és la consulta `test_css[piscina]` (no es desa).

### Funcions i valors nous
| Element | Capa | Font |
|---|---|---|
| `slug_competicio(nom) -> str` | domain, `definicions.py` | RN-008, CA-002-51 |
| `Alias` amb el format `^[a-z0-9]{2,9}(\d{2})?$` (fase 0) | domain, `valors.py` | RN-003, ADR-0023 |
| Alias amb el primer sufix `01`…`99` lliure, o error si no n'hi ha o no compleix el format (fase 0) | domain, `valors.py` | RN-003, RN-041 |

## 2. Entrada dels casos d'ús (`application/importacio`)

Tot són valors de text cru, sense tipar (constitució IX).

| Tipus | Camps | Nota |
|---|---|---|
| `FilaText` | `fila: int`, `valors: tuple[str, ...]` | `fila` és el número de línia del fitxer (CA-002-04) |
| `ContingutTaula` | `ruta: str`, `files: tuple[FilaText, ...]` | calendari i inscripcions; la capçalera ja s'ha comprovat |
| `ContingutParells` | `ruta: str`, `parells: tuple[ParellText, ...]` | fitxa; `ParellText(fila, clau, valor)` |
| `PeticioCalendari` | `contingut`, `temporada: str`, `confirma: bool` | temporada segons RN-031 |
| `PeticioInscripcions` | `contingut`, `temporada: str`, `alias: str`, `confirma: bool` | l'alias no surt del CSV |
| `PeticioFitxa` | `contingut`, `alta: bool`, `confirma: bool` | l'alias és la fila `alias`; `alta` ve de `--alta` (ADR-0023) |

`ErrorLectura(missatge, esperat: str | None)` és l'excepció del port `LectorCsv` (no UTF-8, fitxer buit o sense dades, capçalera diferent, fitxer inexistent, fila que no és `clau;valor`). `ServeisImportacio` la converteix en una incidència d'origen `fitxer`.

## 3. Sortida

### ResultatImportacio
| Camp | Tipus | Nota |
|---|---|---|
| `ok` | bool | cap incidència de nivell `bloquejant` |
| `desat` | bool | s'ha escrit el JSON |
| `pendent_confirmacio` | bool | cap error i algun avís que requereix confirmació sense `--confirma`. |
| `incidencies` | llista d'`Incidencia` | ordenades per fila (o per clau) |
| `resum` | `ResumImportacio(ruta, files_llegides, bloquejants, avisos)` | comptadors per nivell |

Estat de l'informe i codi de sortida (R4): `desat` → 0; `pendent_confirmacio` → 2; qualsevol incidència bloquejant → 1. Mai `desat` i `pendent_confirmacio` alhora.

### Incidencia
| Camp | Tipus | Nota |
|---|---|---|
| `origen` | `Origen(fila: int \| None, camp: str \| None)` | `fila` i `camp` buits = fitxer sencer; en una fitxa, `camp` és la clau |
| `codi` | text | RN (`RN-036`) o `FORMAT-<camp>`, `FORMAT-FILA`, `FORMAT-CLAU`, `FORMAT-CAPCALERA`, `FORMAT-FITXER` (spec § Catàleg de codis) |
| `nivell` | `bloquejant` o `avís` | ERROR i AVÍS de la spec, 1:1 |
| `valor` | text | el valor del CSV que provoca la incidència |
| `missatge` | text | en català |
| `accio` | text | què ha de fer el coach |

## 4. Traça d'origen
Mapa intern `camp de domini → Origen` que construeix cada cas d'ús en convertir files a valors. Serveix per traduir els errors del validador (camps del JSON) a fila i columna (R5). No es desa ni surt de `application`.

## 5. Registre d'avisos
Cada avís es desa a `data/avisos.jsonl` només si hi ha desat amb `--confirma`, amb `decisio: confirmat`. Els camps són els de la spec 001 (§ Registre d'avisos): `data_hora` (del rellotge injectat), `rn`, `fitxer` (ruta del CSV), `camp` (columna o clau), `valor`, `missatge`, `id_nedador`, `decisio`.

## 6. Cobertura de la spec

| Element de la spec | On és |
|---|---|
| Format comú i capçalera | `LectorCsvFitxer`; `ErrorLectura` |
| `nom` → `id` | `slug_competicio`, `calendari.py` |
| Participació amb proves | `inscripcions.py`, `Participacio` i `Inscripcio` de la 001 |
| Claus de la fitxa | `fitxa.py`, `conversio.py` |
| Nedador, competició, inscripcions | model de la spec 001 (sense canvis, llevat de `test_css`) |
