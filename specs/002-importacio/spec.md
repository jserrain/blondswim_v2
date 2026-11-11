# Spec 002 — Importació estricta

**Estat:** Esborrany

## Objectiu
Donar d'alta nedadors i carregar el catàleg de competicions i les inscripcions de cada nedador a partir de tres CSV de format estricte (ADR-0013), convertint-los a JSON segons la spec 001. Cap normalització de dades heretades: el que no s'ajusta al format és un error.

Fora d'abast:
- Modificar, arxivar o desarxivar nedadors; tests CSS; millors registres (ordres de CLI pròpies, fora d'aquesta spec).
- Interfície web (spec 009).
- Qualsevol lectura dels Excels de la v1 (`claude/fonts_dades.md` és referència històrica).

## Històries d'usuari
- **US1 (P1)** — Com a coach, importo el calendari de la temporada des d'un CSV per tenir el catàleg comú sense editar JSON.
- **US2 (P1)** — Com a coach, importo les inscripcions d'un nedador des del seu CSV i veig totes les incidències d'un cop, amb fila i columna.
- **US3 (P2)** — Com a coach, dono d'alta els nedadors des d'un CSV i confirmo els alias generats abans que es desin.

## Fitxers d'entrada

```
data/entrada/nedadors.csv
data/entrada/<AAAA-AA>/calendari.csv
data/entrada/<AAAA-AA>/inscripcions_<alias>.csv
```

Format comú: UTF-8 (sense BOM), separador `;`, primera fila = capçalera amb els noms exactes de columna, llistes dins d'un camp separades per `|`, camp buit = `null`. Les files en blanc s'ignoren. Qualsevol columna de més o de menys, o en un altre ordre, és error de format del fitxer.

### nedadors.csv
`alias_part;correu;mobil;canal_preferent;estils_preferents;dies_entrenament;volum_min;volum_max`

| Camp | Tipus | Regla |
|---|---|---|
| alias_part | text | part de l'alias (RN-003); el sufix l'afegeix el sistema |
| correu | text o buit | RN-032; es desa tal qual |
| mobil | text no buit | spec 001 |
| canal_preferent | `correu`, `mobil` o buit | buit = avís RN-035; altre valor = error |
| estils_preferents | llista de Cr, Esq, Br, Pap, Ei | un o més, sense repetir |
| dies_entrenament | llista de dl, dt, dc, dj, dv, ds, dg | un o més, sense repetir |
| volum_min, volum_max | enters en metres | RN-005 |

### calendari.csv
`nom;dates;piscina;seu`

| Camp | Tipus | Regla |
|---|---|---|
| nom | text no buit | genera l'id |
| dates | llista d'`AAAA-MM-DD` | una o més, dins la temporada de la carpeta (RN-031) |
| piscina | `25` o `50` | |
| seu | text o buit | buit = avís RN-009 |

L'`id` de la competició el genera el sistema a partir del nom (slug: minúscules, sense accents ni diacrítics, qualsevol seqüència de caràcters que no siguin lletres o xifres → un sol `-`, sense `-` als extrems). És estable entre reimportacions (RN-008).

### inscripcions_<alias>.csv
`competicio;classe;dia;distancia;estil;prioritat`

Una fila per prova inscrita.

| Camp | Tipus | Regla |
|---|---|---|
| competicio | text | nom exacte d'una competició del catàleg de la temporada |
| classe | A, B o C | igual a totes les files de la mateixa competició |
| dia | `AAAA-MM-DD` | una de les dates de la competició (RN-015) |
| distancia | enter en metres | |
| estil | Cr, Esq, Br, Pap, Ei | prova oficial per a la piscina de la competició (RN-030) |
| prioritat | `principal` o `secundaria` | |

## Ordres

```
blondswim importar nedadors [--confirma]
blondswim importar calendari --temporada <AAAA-AA> [--confirma]
blondswim importar inscripcions --temporada <AAAA-AA> --alias <alias> [--confirma]
```

- L'alias és un argument; el nom del fitxer se'n deriva. No es llegeix mai de dins del CSV.
- La temporada és un argument; la carpeta se'n deriva. Un nom de temporada que no segueix RN-031 és error.

## Flux en dues passades (sense diàleg interactiu)
1. Sense `--confirma`: valida i mostra l'informe. Desa només si no hi ha cap error, cap avís ni cap alias pendent de confirmar.
2. Amb `--confirma`: valida, desa si no hi ha errors i registra cada avís a `data/avisos.jsonl` amb `decisio: confirmat`. Per a nedadors, `--confirma` també confirma els alias generats (CA-001-68).
- Rebutjar = no tornar a executar amb `--confirma`. No s'escriu cap línia al registre. (CA-001-64 queda retirat; `decisio` només val `confirmat` o `null`.)
- Qualsevol error bloquejant → no es desa res del fitxer, ni amb `--confirma`.
- Codi de sortida: `0` desat; `1` errors; `2` avisos o alias pendents de confirmar.

## Efecte sobre les dades
- **Nedadors:** cada fila vàlida és una alta (id UUID v4 i alias generats, RN-002, RN-003; `arxivat: false`). Una fila amb un `alias_part` que ja correspon a un nedador existent (comparant la part sense sufix) s'ignora amb avís. Una importació no modifica, arxiva ni esborra cap nedador (CA-001-38). La unicitat de correu i alias es comprova contra tots els nedadors existents, arxivats inclosos, i entre les files del mateix CSV.
- **Calendari:** el CSV és la font. El catàleg `competicions/<AAAA-AA>.json` resulta d'aquestes regles: competició existent amb el mateix slug → s'actualitzen nom, dates, piscina i seu, mateix id; slug nou → competició nova; competició del catàleg sense fila al CSV → s'esborra si no té inscripcions, i si en té és error (RN-010) que identifica la competició i els alias afectats. Dues files amb el mateix slug → error (RN-008). Si un canvi de dates afecta una inscripció existent (dia que deixa d'existir) → error que identifica l'alias i la inscripció; la importació del calendari no toca les inscripcions.
- **Inscripcions:** el CSV és la font: `inscripcions.json` del nedador i temporada se substitueix sencer. Les files s'agrupen per competició en una participació (classe) amb les seves proves. Participació sense files no existeix per definició (CA-001-08 no es pot donar).
- **Plans:** la importació no modifica mai cap pla. Si el nedador té un pla a la temporada i canvia alguna participació de classe A o alguna data de competició amb participació → avís «el pla pot quedar desfasat» (la replanificació és d'altres specs).

## Validació
Un sol validador (spec 001): la importació aplica les mateixes regles que la càrrega. Aquesta spec només afegeix els errors de format del CSV i els d'efecte sobre les dades.

Nivells:
- **ERROR** (bloquejant): format del fitxer (codificació, capçalera, nombre de columnes), format d'un camp (tipus, valor fora dels admesos, data, llista buida o repetida), qualsevol RN de nivell ERROR de la spec 001, competició no trobada, classe inconsistent, slug duplicat, RN-010.
- **AVÍS**: RN-009, RN-035, `alias_part` existent (fila ignorada), pla possiblement desfasat, i els avisos de planificació de la 001 no s'avaluen aquí.

## Contracte del cas d'ús (constitució IX)
Un cas d'ús per fitxer (`importar_nedadors`, `importar_calendari`, `importar_inscripcions`) a `application/`:
- Entrada: DTO amb les files ja tipades com a text (una llista de diccionaris columna → valor cru) i els arguments (`temporada`, `alias`, `confirma`).
- Sortida: `ResultatImportacio` amb `ok` (bool), `desat` (bool), `errors[]`, `avisos[]`, `alias_generats[]` (només nedadors), `resum` (comptadors per nivell). Cada incidència: `origen` (fila i columna, o `fitxer`), `codi` (RN o `FORMAT-<camp>`), `nivell`, `valor`, `missatge`, `accio`.
- El lector CSV (`infrastructure/`) només obre el fitxer, comprova codificació i capçalera, i retorna files de text. La CLI (`interfaces/`) només pinta el resultat i tradueix `ok/desat` a codi de sortida. Cap dels dos conté regles.
- El rellotge s'injecta (línies del registre d'avisos).

## Informe (CLI)
Per fitxer: ruta, nombre de files llegides; llista d'errors i avisos ordenats per fila, cada un amb `fila:columna`, codi, valor i acció; alias generats (`alias_part → alias`); línia final amb el resum i l'estat (`desat`, `pendent de confirmar`, `no desat`).

## Assumptions
- Un sol coach; execució local.
- El coach escriu els CSV amb una fulla de càlcul exportant a CSV amb `;` i UTF-8; no es dona suport a cap altra configuració.
- Els CSV es conserven a `data/entrada/` com a font; el sistema no els modifica ni els esborra.

## Dades i accions sensibles
- `nedadors.csv` conté correu i mòbil (dades personals, spec 001). El fitxer viu a `data/entrada/`, no versionat. L'informe de la CLI mostra el valor només a la incidència que l'afecta.
- Cap dada del CSV arriba a un LLM: aquesta spec no té punts de judici LLM.
- Acció destructiva: la reimportació substitueix `inscripcions.json` sencer i pot esborrar competicions sense inscripcions del catàleg. Totes dues queden protegides pel flux de dues passades i per RN-010.

## Clarifications

### Sessió 2026-11-10 (decisions preses al xat abans de `/speckit-specify`)
- P: Interfície web per a l'entrada de dades? → Diferida a la spec 009. L'entrada actual és CSV estricte (ADR-0013 revisat); el contracte de cas d'ús (constitució IX) permet afegir la web com a vista sense refer res.
- P: On es desen els CSV? → `data/entrada/nedadors.csv`, `data/entrada/<AAAA-AA>/calendari.csv`, `data/entrada/<AAAA-AA>/inscripcions_<alias>.csv`.
- P: Com s'identifica el nedador en importar inscripcions? → L'alias és argument de l'ordre; el nom del fitxer se'n deriva; no es llegeix del CSV.
- P: Com s'entren els nedadors? → Tercer CSV, només altes; modificar, arxivar, tests i marques van per ordres de CLI pròpies.
- P: Qui posa l'id de la competició? → El sistema, com a slug del nom; les inscripcions referencien el nom.
- P: Com es confirmen avisos i alias? → Dues passades amb `--confirma`, sense diàleg. Rebutjar = no confirmar; CA-001-64 retirat.
- P: Canvi de dates que deixa una inscripció sense dia? → Error en importar el calendari; el catàleg no canvia.

## Criteris d'acceptació

Format i lectura
- **CA-002-01** — Donat un CSV amb la capçalera correcta i cap incidència, quan s'importa sense `--confirma`, aleshores es desa, el codi de sortida és 0 i l'informe diu `desat`.
- **CA-002-02** — Donat un CSV amb una columna de menys, de més o en un altre ordre, quan s'importa, aleshores no es desa res, hi ha un ERROR d'origen `fitxer` que identifica la capçalera esperada, i el codi és 1.
- **CA-002-03** — Donat un CSV amb separador `,` o codificació no UTF-8, quan s'importa, aleshores no es desa res i hi ha un ERROR d'origen `fitxer`.
- **CA-002-04** — Donat un CSV amb files en blanc intercalades, quan s'importa, aleshores les files en blanc s'ignoren sense error ni avís i els números de fila de l'informe són els del fitxer.
- **CA-002-05** — Donat un CSV amb una data `10/11/2026`, quan s'importa, aleshores hi ha un ERROR `FORMAT-dates` (o `FORMAT-dia`) que indica fila, columna i valor, i no es desa res.
- **CA-002-06** — Donat un CSV amb diversos errors en files diferents, quan s'importa, aleshores l'informe els llista tots, ordenats per fila, i no s'atura al primer.

Confirmació
- **CA-002-07** — Donat un CSV amb un avís i cap error, quan s'importa sense `--confirma`, aleshores no es desa res, el codi és 2, l'informe diu `pendent de confirmar` i `avisos.jsonl` no canvia.
- **CA-002-08** — Donat el mateix CSV, quan s'importa amb `--confirma`, aleshores es desa, el codi és 0 i `avisos.jsonl` té una línia per avís amb `decisio: confirmat`, `rn`, `fitxer`, `camp`, `valor` i `data_hora` del rellotge injectat.
- **CA-002-09** — Donat un CSV amb un error i un avís, quan s'importa amb `--confirma`, aleshores no es desa res, el codi és 1 i `avisos.jsonl` no canvia.
- **CA-002-10** — Donada una importació de nedadors amb un alias pendent i cap avís, quan s'importa sense `--confirma`, aleshores no es desa res, el codi és 2 i l'informe mostra `alias_part → alias` (CA-001-68).

Nedadors
- **CA-002-11** — Donat `nedadors.csv` amb dues files vàlides, quan s'importa amb `--confirma`, aleshores es creen dues carpetes `nedadors/<uuid>/` amb `nedador.json` vàlid segons la spec 001, alias amb el sufix de l'id (CA-001-52) i `arxivat: false`.
- **CA-002-12** — Donada una fila amb `estils_preferents` `Cr|Cr` o `Cr|EP`, quan s'importa, aleshores ERROR que identifica fila, columna i valor (CA-001-39).
- **CA-002-13** — Donada una fila amb `canal_preferent` buit, quan s'importa, aleshores AVÍS RN-035 i la fila es desa només amb `--confirma` (CA-001-57, 63).
- **CA-002-14** — Donada una fila amb `canal_preferent` `whatsapp`, quan s'importa, aleshores ERROR de format que indica les opcions admeses (CA-001-58).
- **CA-002-15** — Donada una fila amb un correu ja existent en un nedador arxivat (comparat en minúscules i sense espais als extrems), quan s'importa, aleshores ERROR RN-032 i cap fila del fitxer no es desa.
- **CA-002-16** — Donades dues files del mateix CSV amb el mateix correu, quan s'importa, aleshores ERROR RN-032 que identifica les dues files.
- **CA-002-17** — Donada una fila amb un `alias_part` que ja correspon a un nedador existent, quan s'importa, aleshores la fila s'ignora amb AVÍS, el nedador existent no canvia i la resta de files es processen (CA-001-38).
- **CA-002-18** — Donat un nedador existent que no és al CSV, quan s'importa, aleshores no s'esborra ni s'arxiva (CA-001-38).
- **CA-002-19** — Donada una fila amb un ERROR (p. ex. `volum_min > volum_max`), quan s'importa, aleshores cap fila del fitxer no es desa i el missatge indica `alias_part`, la RN i l'acció (CA-001-62, 72).

Calendari
- **CA-002-20** — Donat `calendari.csv` amb tres competicions, quan s'importa, aleshores `competicions/<AAAA-AA>.json` té tres competicions amb id = slug del nom, i es carrega sense error amb la spec 001.
- **CA-002-21** — Donats els noms `Campionat d'Hivern` i `campionat d hivern`, quan s'importa, aleshores ERROR RN-008 (slug duplicat) que identifica les dues files.
- **CA-002-22** — Donada una fila amb `seu` buida, quan s'importa, aleshores AVÍS RN-009 i es desa amb `seu: null` només amb `--confirma`.
- **CA-002-23** — Donada una fila amb una data fora de la temporada de l'argument, quan s'importa, aleshores ERROR que identifica la fila i la temporada.
- **CA-002-24** — Donat un catàleg existent, quan es reimporta un CSV on una competició ha canviat de seu, aleshores conserva l'id, actualitza la seu, i les inscripcions que hi apunten continuen vàlides (CA-001-22).
- **CA-002-25** — Donat un catàleg amb una competició amb inscripcions d'un nedador, quan es reimporta un CSV sense aquella competició, aleshores ERROR RN-010 que identifica la competició i l'alias, i el catàleg no canvia.
- **CA-002-26** — Donat un catàleg amb una competició sense inscripcions, quan es reimporta un CSV sense aquella competició, aleshores la competició desapareix del catàleg sense error ni avís.
- **CA-002-27** — Donat un catàleg i una inscripció d'un nedador en el dia D d'una competició, quan es reimporta un calendari on aquella competició ja no inclou D, aleshores ERROR que identifica l'alias, la competició i el dia, i el catàleg no canvia.

Inscripcions
- **CA-002-28** — Donat `inscripcions_<alias>.csv` amb tres files de dues competicions, quan s'importa, aleshores `inscripcions.json` té dues participacions amb la seva classe i les proves agrupades, i es carrega sense error amb la spec 001.
- **CA-002-29** — Donada una fila amb un nom de competició que no és al catàleg, quan s'importa, aleshores ERROR RN-011 que identifica fila i valor.
- **CA-002-30** — Donades dues files de la mateixa competició amb classes A i B, quan s'importa, aleshores ERROR que identifica les dues files.
- **CA-002-31** — Donada una fila amb un `dia` que no és cap data de la competició, quan s'importa, aleshores ERROR RN-015 (CA-001-09).
- **CA-002-32** — Donada una fila `100;Ei` en una competició de piscina 50, quan s'importa, aleshores ERROR RN-030 (CA-001-42).
- **CA-002-33** — Donades dues files amb la mateixa competició, distància i estil, quan s'importa, aleshores ERROR RN-016 (CA-001-29).
- **CA-002-34** — Donat un `--alias` que no correspon a cap nedador no arxivat, o un fitxer `inscripcions_<alias>.csv` inexistent, quan s'importa, aleshores ERROR d'origen `fitxer` i no es desa res.
- **CA-002-35** — Donat un `inscripcions.json` existent, quan es reimporta un CSV amb una participació menys, aleshores el fitxer resultant només té les participacions del CSV.
- **CA-002-36** — Donada una participació de classe A sense cap prova `principal`, quan s'importa, aleshores AVÍS (CA-001-13) i es desa només amb `--confirma`.
- **CA-002-37** [PENDENT spec 003] — Donat un nedador amb pla a la temporada, quan es reimporten inscripcions que canvien una participació A, aleshores AVÍS «pla possiblement desfasat» i el pla no canvia.

Arquitectura
- **CA-002-38** — Donat el codi d'`interfaces/` i d'`infrastructure/csv`, quan passa import-linter, aleshores no importen `domain/` ni es llegeixen fitxers JSON des de cap vista (constitució X).
- **CA-002-39** — Donat un `ResultatImportacio` amb errors i avisos, quan la CLI el pinta, aleshores el text conté per a cada incidència `fila:columna`, codi, valor i acció, i el codi de sortida segueix `ok/desat` (0, 1, 2) sense cap lògica addicional.

## Canvis en altres documents
- Spec 001: CA-001-64 a «CA retirats» (motiu: rebutjar = no confirmar, spec 002); § Registre d'avisos: `decisio` val `confirmat` o `null`. Els CA `[PENDENT spec 002]` (38, 58, 63, 68, 72) passen a tenir test via els CA-002 indicats.
- ADR-0013: ja revisat (tres CSV, ubicació, alias com a argument).
- `AGENTS.md`: afegir la regla de capa i les ordres `importar`.
