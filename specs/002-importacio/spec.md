# Spec 002 — Importació estricta

**Estat:** Esborrany (revisió 2, 2026-11-11: fitxa del nedador segons ADR-0021 revisat i ADR-0022; correccions de l'auditoria G1 del 2026-11-11)

## Objectiu
Entrar les dades del nedador (fitxa), el catàleg de competicions (calendari) i les inscripcions de cada nedador a partir de tres CSV de format estricte (ADR-0013, ADR-0021), convertint-los a JSON segons la spec 001. Cap normalització de dades heretades: el que no s'ajusta al format és un error.

Fora d'abast:
- Arxivar i desarxivar nedadors (operació pròpia de la spec 001, sense canal d'entrada en aquesta spec).
- Interfície web (spec 009).
- Qualsevol lectura dels Excels de la v1 (`claude/fonts_dades.md` és referència històrica).
- Migració del model de la spec 001 a `test_css` (ADR-0022): prerequisit de codi, no regla d'aquesta spec; el pla la inclou com a fase 0.

## Històries d'usuari
- **US1 (P1)** — Com a coach, importo el calendari de la temporada des d'un CSV per tenir el catàleg comú sense editar JSON.
- **US2 (P1)** — Com a coach, importo les inscripcions d'un nedador des del seu CSV i veig totes les incidències d'un cop, amb fila i columna.
- **US3 (P1)** — Com a coach, mantinc la fitxa de cada nedador en un full de càlcul i la importo per donar-lo d'alta o actualitzar-lo, test CSS i millors marques incloses.

## Fitxers d'entrada

```
data/entrada/nedadors/<nom lliure>.csv            # fitxa, una per nedador
data/entrada/<AAAA-AA>/calendari.csv
data/entrada/<AAAA-AA>/inscripcions_<alias>.csv
```

Format comú (ADR-0013): UTF-8 (sense BOM), separador `;`, valors compostos o llistes dins d'un camp separats per `|`, camp buit = `null`. Les files en blanc s'ignoren. Al calendari i a les inscripcions la primera fila és la capçalera amb els noms exactes de columna; qualsevol columna de més, de menys o en un altre ordre és error de format del fitxer.

### Fitxa del nedador (`clau;valor`)
Sense capçalera. Cada fila és `clau;valor`. L'ordre de les files és lliure. Una clau desconeguda, o repetida quan no és repetible, és error. Una clau obligatòria absent és error.

| Clau | Valor | Regla |
|---|---|---|
| `alias` | text | obligatòria. Sense sufix (`part`) → alta; amb sufix (`part_xxxxxxx`) que coincideix amb un nedador → actualització; amb sufix sense coincidència → error (RN-003) |
| `correu` | text o buit | RN-032; es desa tal qual |
| `mobil` | text no buit | obligatòria (spec 001) |
| `canal_preferent` | `correu`, `mobil` o buit | buit = avís RN-035; altre valor = error |
| `estils_preferents` | llista de Cr, Esq, Br, Pap, Ei | obligatòria; un o més, sense repetir |
| `dies_entrenament` | llista de dl, dt, dc, dj, dv, ds, dg | obligatòria; un o més, sense repetir |
| `volum_setmanal` | `min\|max` en metres | obligatòria (RN-005) |
| `test_css` | `piscina\|data\|t400\|t200[\|rpe]` | repetible, màxim una per piscina (25, 50). `rpe` enter 0-10, opcional. Substitueix el test de la piscina (ADR-0022); rpe es desa a detall_400.rpe i detall_200.rpe |
| `marca` | `estil\|distancia\|piscina\|temps\|data\|competicio` | repetible, màxim una per estil+distància+piscina. S'afegeix només si millora la vigent (RN-007); si no, no es fa res |

- Les claus de contacte, estils, dies i volum descriuen l'**estat complet** del nedador: en una actualització substitueixen el valor desat (spec 001 § Modificació). Un `correu` buit en una actualització deixa el nedador sense correu (CA-001-112).
- `test_css` i `marca` són **incrementals**: una fitxa sense `test_css` no esborra cap test; una fitxa sense `marca` no toca les marques.
- Dates `AAAA-MM-DD`; temps `m:ss.cc` (spec 000).

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
| classe | A, B o C | igual a totes les files de la mateixa competició (RN-036) |
| dia | `AAAA-MM-DD` | una de les dates de la competició (RN-015) |
| distancia | enter en metres | |
| estil | Cr, Esq, Br, Pap, Ei | prova oficial per a la piscina de la competició (RN-030) |
| prioritat | `principal` o `secundaria` | |

## Ordres

```
blondswim importar fitxa <camí> [--confirma]
blondswim importar calendari --temporada <AAAA-AA> [--confirma]
blondswim importar inscripcions --temporada <AAAA-AA> --alias <alias> [--confirma]
```

- Fitxa: la identitat és la fila `alias` del fitxer (ADR-0021).
- Inscripcions: l'alias és un argument; el nom del fitxer se'n deriva; no es llegeix del CSV (ADR-0013). Un alias que no correspon a cap nedador no arxivat és error (RN-037).
- La temporada és un argument; la carpeta se'n deriva. Un nom que no segueix RN-031 és error.

## Flux en dues passades (sense diàleg interactiu)
1. Sense `--confirma`: valida i mostra l'informe. Desa només si no hi ha cap error ni cap element pendent de confirmar (avisos; alias generat en una alta).
2. Amb `--confirma`: valida, desa si no hi ha errors i registra cada avís a `data/avisos.jsonl` amb `decisio: confirmat`. En una alta, `--confirma` confirma també l'alias generat (CA-001-68).
- Rebutjar = no tornar a executar amb `--confirma`. No s'escriu cap línia al registre (CA-001-64 retirat).
- Qualsevol error bloquejant → no es desa res del fitxer, ni amb `--confirma`.
- Codi de sortida: `0` desat; `1` errors; `2` pendent de confirmar.

## Efecte sobre les dades
- **Fitxa, alta:** id UUID v4 i alias generats (RN-002, RN-003), `arxivat: false`. L'alta sempre queda pendent de confirmar a la primera passada (l'alias generat s'ha de confirmar). Unicitat de correu i alias contra tots els nedadors, arxivats inclosos.
- **Fitxa, actualització:** es torna a validar el nedador sencer, unicitat inclosa; se substitueixen els camps modificables; id, alias i `versio_esquema` no canvien (CA-001-53). `test_css` substitueix el test de la piscina indicada. `marca` s'afegeix si millora (RN-007) i amb data posterior a la vigent (CA-001-102); si no millora, no es fa res ni s'avisa. Un nedador arxivat es pot actualitzar; no es desarxiva.
- **Calendari:** el CSV és la font. Competició existent amb el mateix slug → s'actualitzen nom, dates, piscina i seu, mateix id; slug nou → competició nova; competició del catàleg sense fila al CSV → s'esborra si no té inscripcions, i si en té és error (RN-010). Dues files amb el mateix slug → error (RN-008). Si un canvi de dates deixa una inscripció existent sense el seu dia → error (RN-038); la importació del calendari no toca les inscripcions.
- **Inscripcions:** el CSV és la font: `inscripcions.json` del nedador i temporada se substitueix sencer. Quan ja existeix un `inscripcions.json` i el resultat en difereix (participacions o proves que desapareixen o canvien), es genera l'avís RN-039 amb el resum de les diferències; es desa només amb `--confirma`. Les files s'agrupen per competició en una participació (classe) amb les seves proves.
- **Plans:** la importació no modifica mai cap pla. Si el nedador té un pla a la temporada i canvia una participació de classe A o la data d'una competició amb participació → avís RN-040 «el pla pot quedar desfasat».

## Regles de negoci noves (a `docs/regles.md`)
| RN | Nivell | Regla |
|---|---|---|
| RN-036 | ERROR | Totes les files d'una mateixa competició al CSV d'inscripcions tenen la mateixa classe |
| RN-037 | ERROR | L'alias de l'ordre d'importar inscripcions correspon a un nedador existent no arxivat |
| RN-038 | ERROR | Una reimportació del calendari no pot treure una data en què un nedador té una inscripció |
| RN-039 | AVÍS | Reimportar inscripcions sobre un fitxer existent amb diferències requereix confirmació |
| RN-040 | AVÍS | Canvi en una participació A o en la data d'una competició amb participació, amb pla existent: el pla pot quedar desfasat |
| RN-041 | AVÍS | Fitxa amb `alias` sense sufix que coincideix amb la part d'un nedador existent: es tracta com a alta d'un nedador nou (la unicitat d'alias la resol el sufix); l'avís demana confirmar que no és una actualització |

## Validació
Un sol validador (spec 001): la importació aplica les mateixes regles que la càrrega. Aquesta spec només afegeix els errors de format del CSV i les RN-036 a RN-041.

- **ERROR** (bloquejant): format del fitxer (codificació, capçalera, columnes; claus de la fitxa), format d'un camp o valor, qualsevol RN de nivell ERROR de la spec 001, RN-036, RN-037, RN-038, RN-008, RN-010, RN-011.
- **AVÍS**: RN-009, RN-035, RN-039, RN-040, RN-041, CA-001-13 (participació A sense prova principal).

## Contracte del cas d'ús (constitució IX)
Un cas d'ús per fitxer (`importar_fitxa`, `importar_calendari`, `importar_inscripcions`) a `application/`:
- Entrada: DTO amb les files com a text (llista de diccionaris columna → valor cru; per a la fitxa, llista de parells clau → valor) i els arguments (`temporada`, `alias`, `confirma`).
- Sortida: `ResultatImportacio` amb `ok`, `desat`, `pendent_confirmacio` (bool), `errors[]`, `avisos[]`, `alias_generat` (només alta), `resum`. Cada incidència: `origen` (fila i columna o clau, o `fitxer`), `codi` (RN o `FORMAT-<camp>`), `nivell`, `valor`, `missatge`, `accio`.
- El lector CSV (`infrastructure/`) només obre el fitxer, comprova codificació i capçalera (o parells clau;valor), i retorna text. La CLI (`interfaces/`) només pinta el resultat i tradueix `ok/desat/pendent_confirmacio` a codi de sortida (0/1/2). Cap dels dos conté regles.
- La funció de slug és una regla d'id (RN-008) i viu a `domain/`.
- El rellotge s'injecta (línies del registre d'avisos).

## Informe (CLI)
Per fitxer: ruta, files llegides; errors i avisos ordenats per fila (o per clau), cada un amb origen, codi, valor i acció; alias generat (`part → alias`) en una alta; línia final amb el resum i l'estat (`desat`, `pendent de confirmar`, `no desat`).

## Assumptions
- Un sol coach; execució local.
- El coach escriu els CSV amb una fulla de càlcul exportant amb `;` i UTF-8; no es dona suport a cap altra configuració.
- Els CSV es conserven a `data/entrada/` com a font; el sistema no els modifica ni els esborra.
- Els exemples de CSV viuen a `tests/fixtures/entrada/` i fan de plantilla per al coach.

## Dades i accions sensibles
- La fitxa conté correu i mòbil (dades personals, spec 001). Viu a `data/entrada/`, no versionat. L'informe de la CLI mostra el valor només a la incidència que l'afecta.
- Cap dada del CSV arriba a un LLM: aquesta spec no té punts de judici LLM.
- Accions destructives i la seva protecció: substituir `inscripcions.json` (RN-039, confirmació); esborrar una competició sense inscripcions del catàleg (RN-010 per a les que en tenen; les altres s'esborren sense avís perquè el CSV és la font); substituir el test CSS d'una piscina (ADR-0022, és la intenció del coach); substituir els camps modificables del nedador (spec 001 § Modificació).

## Clarifications

### Sessió 2026-11-10 (decisions preses al xat abans de `/speckit-specify`)
- P: Interfície web per a l'entrada de dades? → Diferida a la spec 009. L'entrada actual és CSV estricte (ADR-0013 revisat); el contracte de cas d'ús (constitució IX) permet afegir la web com a vista sense refer res.
- P: On es desen els CSV? → `data/entrada/`; calendari i inscripcions per temporada, fitxes a `nedadors/`.
- P: Com s'identifica el nedador en importar inscripcions? → L'alias és argument de l'ordre; el nom del fitxer se'n deriva; no es llegeix del CSV.
- P: Com s'entren els nedadors? → Tercer CSV només d'altes (`nedadors.csv`). Substituïda per 2026-11-11 (fitxa per nedador, ADR-0021 revisat).
- P: Qui posa l'id de la competició? → El sistema, com a slug del nom; les inscripcions referencien el nom.
- P: Com es confirmen avisos i alias? → Dues passades amb `--confirma`, sense diàleg. Rebutjar = no confirmar; CA-001-64 retirat.
- P: Canvi de dates que deixa una inscripció sense dia? → Error en importar el calendari (RN-038); el catàleg no canvia.

### Sessió 2026-11-11 (auditoria G1 r1, ADR-0021 revisat, ADR-0022)
- P: L'ADR-0021 (fitxa per nedador) contradiu la spec? → Sí; es manté l'ADR-0021 revisat: una fitxa `clau;valor` per nedador, alta o actualització, amb test CSS i marques com a estat actual. `nedadors.csv` desapareix.
- P: Històric de tests CSS? → No: un test per piscina, el nou substitueix l'anterior; entrar-lo és acceptar-lo (ADR-0022).
- P: Regles sense RN? → RN-036 a RN-041 definides aquí i a `docs/regles.md`.
- P: CA-002-01 vs CA-002-10? → Una alta sempre queda pendent (alias a confirmar); CA-002-01 s'aplica a calendari, inscripcions i actualitzacions de fitxa.
- P: Substituir `inscripcions.json` sense avís? → Avís RN-039 amb resum de diferències; es desa amb `--confirma`.
- P: Alias sense sufix que coincideix amb la part d'un nedador existent? → Alta nova amb avís RN-041 (abans: fila ignorada).

## Criteris d'acceptació

Format i lectura
- **CA-002-01** — Donat un CSV de calendari, d'inscripcions o una fitxa d'actualització amb cap incidència, quan s'importa sense `--confirma`, aleshores es desa, el codi de sortida és 0 i l'informe diu `desat`.
- **CA-002-02** — Donat un CSV de calendari o d'inscripcions amb una columna de menys, de més o en un altre ordre, quan s'importa, aleshores no es desa res, hi ha un ERROR d'origen `fitxer` que identifica la capçalera esperada, i el codi és 1.
- **CA-002-03** — Donat un CSV amb separador `,` o codificació no UTF-8, quan s'importa, aleshores no es desa res i hi ha un ERROR d'origen `fitxer`.
- **CA-002-04** — Donat un CSV amb files en blanc intercalades, quan s'importa, aleshores s'ignoren sense error ni avís i els números de fila de l'informe són els del fitxer.
- **CA-002-05** — Donat un CSV amb una data `31/12/2026`, quan s'importa, aleshores hi ha un ERROR `FORMAT-<camp>` que indica fila, columna i valor, i no es desa res.
- **CA-002-06** — Donat un CSV amb diversos errors en files diferents, quan s'importa, aleshores l'informe els llista tots, ordenats per fila, i no s'atura al primer.
- **CA-002-07** — Donada una fitxa amb una clau desconeguda, una clau no repetible repetida o una clau obligatòria absent, quan s'importa, aleshores ERROR d'origen la clau (o `fitxer` si és absent) i no es desa res.

Confirmació
- **CA-002-08** — Donat un fitxer amb un avís i cap error, quan s'importa sense `--confirma`, aleshores no es desa res, el codi és 2, l'informe diu `pendent de confirmar` i `avisos.jsonl` no canvia.
- **CA-002-09** — Donat el mateix fitxer, quan s'importa amb `--confirma`, aleshores es desa, el codi és 0 i `avisos.jsonl` té una línia per avís amb `decisio: confirmat`, `rn`, `fitxer`, `camp`, `valor` i `data_hora` del rellotge injectat.
- **CA-002-10** — Donat un fitxer amb un error i un avís, quan s'importa amb `--confirma`, aleshores no es desa res, el codi és 1 i `avisos.jsonl` no canvia.
- **CA-002-11** — Donada una fitxa d'alta sense cap avís, quan s'importa sense `--confirma`, aleshores no es desa res, el codi és 2 i l'informe mostra `part → alias` (CA-001-68); amb `--confirma`, es desa.

Fitxa: alta
- **CA-002-12** — Donada una fitxa d'alta vàlida, quan s'importa amb `--confirma`, aleshores es crea `nedadors/<uuid>/nedador.json` vàlid segons la spec 001, amb alias amb el sufix de l'id (CA-001-52), `arxivat: false`, i els camps informatius no presents a la fitxa a `null`.
- **CA-002-13** — Donada una fitxa amb `estils_preferents` `Cr|Cr` o `Cr|EP`, quan s'importa, aleshores ERROR que identifica clau i valor (CA-001-39).
- **CA-002-14** — Donada una fitxa amb `canal_preferent` buit, quan s'importa, aleshores AVÍS RN-035 i es desa només amb `--confirma` (CA-001-57, 63).
- **CA-002-15** — Donada una fitxa amb `canal_preferent` `whatsapp`, quan s'importa, aleshores ERROR de format que indica les opcions admeses (CA-001-58).
- **CA-002-16** — Donada una fitxa d'alta amb un correu ja existent en un nedador arxivat (comparat en minúscules i sense espais als extrems), quan s'importa, aleshores ERROR RN-032 i no es desa res.
- **CA-002-17** — Donada una fitxa d'alta amb `alias` igual a la part de l'alias d'un nedador existent, quan s'importa, aleshores AVÍS RN-041, i amb `--confirma` es crea un nedador nou amb sufix diferent; el nedador existent no canvia.
- **CA-002-18** — Donat un nedador existent sense fitxa importada, quan s'importa la fitxa d'un altre nedador, aleshores el primer no s'esborra, no s'arxiva ni canvia (CA-001-38).
- **CA-002-19** — Donada una fitxa amb un ERROR (p. ex. `volum_setmanal` amb min > max), quan s'importa, aleshores no es desa res i el missatge indica l'alias, la RN i l'acció (CA-001-62, 72).

Fitxa: actualització, test i marques
- **CA-002-20** — Donada una fitxa amb `alias` amb sufix d'un nedador existent i `mobil` i `dies_entrenament` diferents dels desats, quan s'importa, aleshores es desen els valors nous, id, alias i `versio_esquema` no canvien (CA-001-53) i la resta de camps queden com a la fitxa.
- **CA-002-21** — Donada una fitxa amb `alias` amb sufix que no correspon a cap nedador, quan s'importa, aleshores ERROR RN-003 i no es desa res.
- **CA-002-22** — Donada una fitxa d'actualització amb el `correu` d'un altre nedador, quan s'importa, aleshores ERROR RN-032 i no es desa res (CA-001-79).
- **CA-002-23** — Donada una fitxa d'actualització amb `correu` buit en un nedador que en tenia, quan s'importa, aleshores el nedador queda sense correu i l'antic queda lliure (CA-001-112).
- **CA-002-24** — Donada una fitxa amb `test_css;25|<data>|<t400>|<t200>` en un nedador amb test de 25 m, quan s'importa, aleshores `test_css["25"]` és el nou, el de 50 m no canvia i els camps informatius no presents queden `null` (ADR-0022).
- **CA-002-25** — Donada una fitxa amb dues files `test_css` de la mateixa piscina, o amb t400 ≤ t200, quan s'importa, aleshores ERROR que identifica la clau (CA-001-04).
- **CA-002-26** — Donada una fitxa amb `test_css` amb `rpe` 11, quan s'importa, aleshores ERROR de format; amb `rpe` 7, es desa a `detall_400.rpe` i `detall_200.rpe` del test (l'rpe únic de la fitxa es desa a tots dos detalls).
- **CA-002-27** — Donada una fitxa amb una `marca` millor que la vigent de la mateixa prova i piscina i data posterior, quan s'importa, aleshores s'afegeix a `millors_registres` (RN-007); amb temps igual o pitjor, no es fa res ni s'avisa (CA-001-89); amb temps millor i data no posterior, ERROR (CA-001-102).
- **CA-002-28** — Donada una fitxa amb una `marca` d'una prova no oficial per a la piscina, quan s'importa, aleshores ERROR RN-030 (CA-001-42).
- **CA-002-29** — Donada una fitxa sense cap fila `test_css` ni `marca` en un nedador que en té, quan s'importa, aleshores tests i marques no canvien.

Calendari
- **CA-002-30** — Donat `calendari.csv` amb tres competicions, quan s'importa, aleshores `competicions/<AAAA-AA>.json` té tres competicions amb id = slug del nom, i es carrega sense error amb la spec 001.
- **CA-002-31** — Donats els noms `Campionat d'Hivern` i `campionat d hivern`, quan s'importa, aleshores ERROR RN-008 (slug duplicat) que identifica les dues files.
- **CA-002-32** — Donada una fila amb `seu` buida, quan s'importa, aleshores AVÍS RN-009 i es desa amb `seu: null` només amb `--confirma`.
- **CA-002-33** — Donada una fila amb una data fora de la temporada de l'argument, quan s'importa, aleshores ERROR que identifica la fila i la temporada.
- **CA-002-34** — Donat un catàleg existent, quan es reimporta un CSV on una competició ha canviat de seu, aleshores conserva l'id, actualitza la seu, i les inscripcions que hi apunten continuen vàlides (CA-001-22).
- **CA-002-35** — Donat un catàleg amb una competició amb inscripcions d'un nedador, quan es reimporta un CSV sense aquella competició, aleshores ERROR RN-010 que identifica la competició i l'alias, i el catàleg no canvia.
- **CA-002-36** — Donat un catàleg amb una competició sense inscripcions, quan es reimporta un CSV sense aquella competició, aleshores la competició desapareix del catàleg sense error ni avís.
- **CA-002-37** — Donat un catàleg i una inscripció d'un nedador en el dia D d'una competició, quan es reimporta un calendari on aquella competició ja no inclou D, aleshores ERROR RN-038 que identifica l'alias, la competició i el dia, i el catàleg no canvia.

Inscripcions
- **CA-002-38** — Donat `inscripcions_<alias>.csv` amb tres files de dues competicions i cap `inscripcions.json` previ, quan s'importa, aleshores `inscripcions.json` té dues participacions amb la seva classe i les proves agrupades, i es carrega sense error amb la spec 001.
- **CA-002-39** — Donada una fila amb un nom de competició que no és al catàleg, quan s'importa, aleshores ERROR RN-011 que identifica fila i valor.
- **CA-002-40** — Donades dues files de la mateixa competició amb classes A i B, quan s'importa, aleshores ERROR RN-036 que identifica les dues files.
- **CA-002-41** — Donada una fila amb un `dia` que no és cap data de la competició, quan s'importa, aleshores ERROR RN-015 (CA-001-09).
- **CA-002-42** — Donada una fila `100;Ei` en una competició de piscina 50, quan s'importa, aleshores ERROR RN-030 (CA-001-42).
- **CA-002-43** — Donades dues files amb la mateixa competició, distància i estil, quan s'importa, aleshores ERROR RN-016 (CA-001-29).
- **CA-002-44** — Donat un `--alias` que no correspon a cap nedador no arxivat, o un fitxer `inscripcions_<alias>.csv` inexistent, quan s'importa, aleshores ERROR RN-037 (o d'origen `fitxer`) i no es desa res.
- **CA-002-45** — Donat un `inscripcions.json` existent, quan es reimporta un CSV amb una participació menys, aleshores AVÍS RN-039 amb la participació que desapareix, no es desa sense `--confirma`, i amb `--confirma` el fitxer només té les participacions del CSV.
- **CA-002-46** — Donat un `inscripcions.json` existent, quan es reimporta un CSV idèntic en contingut, aleshores no hi ha avís RN-039 i es desa amb codi 0.
- **CA-002-47** — Donada una participació de classe A sense cap prova `principal`, quan s'importa, aleshores AVÍS (CA-001-13) i es desa només amb `--confirma`.
- **CA-002-48** [PENDENT spec 003] — Donat un nedador amb pla a la temporada, quan es reimporten inscripcions que canvien una participació A, aleshores AVÍS RN-040 i el pla no canvia.

Arquitectura
- **CA-002-49** — Donat el codi d'`interfaces/` i d'`infrastructure/csv`, quan passa import-linter, aleshores no importen `domain/` ni llegeixen fitxers JSON (constitució X).
- **CA-002-50** — Donat un `ResultatImportacio` amb errors i avisos, quan la CLI el pinta, aleshores el text conté per a cada incidència origen, codi, valor i acció, i el codi de sortida segueix `ok/desat/pendent_confirmacio` (0, 1, 2) sense cap lògica addicional.
- **CA-002-51** — Donada la funció de slug, quan rep `Campionat d'Hivern  (25 m)`, aleshores retorna `campionat-d-hivern-25-m`, i és a `domain/`.

## Canvis en altres documents
- Spec 001: fets (CA-001-64 retirat; ADR-0022 aplicat).
- `docs/regles.md`: afegir RN-036 a RN-041.
- `AGENTS.md`: fet (regla de capa, ordres `importar`, ADR-0021 i 0022).
- Pla (fase 0): migrar el codi de la spec 001 a `test_css` sense `acceptat` i retirar els tests de CA-001-05, 30, 35 i 82.
