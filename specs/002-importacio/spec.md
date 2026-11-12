# Spec 002 — Importació estricta

**Estat:** Esborrany

## Objectiu
Entrar les dades del nedador (fitxa), el catàleg de competicions (calendari) i les inscripcions de cada nedador a partir de tres CSV de format estricte (ADR-0013, ADR-0021), convertint-los a JSON segons la spec 001. Cap normalització de dades heretades: el que no s'ajusta al format és un error.

Fora d'abast:
- Arxivar i desarxivar nedadors (operació pròpia de la spec 001, sense canal d'entrada en aquesta spec).
- Interfície web (spec 009).
- Qualsevol lectura dels Excels de la v1 (`claude/fonts_dades.md` és referència històrica).
- Migració del model de la spec 001 a `test_css` (ADR-0022) i retirada dels tests dels CA retirats: prerequisit de codi, no regla d'aquesta spec.

## Històries d'usuari
- **US1 (P1, independent)** — Com a coach, importo el calendari de la temporada des d'un CSV per tenir el catàleg comú sense editar JSON.
- **US2 (P2, depèn de US1 i US3)** — Com a coach, importo les inscripcions d'un nedador des del seu CSV i veig totes les incidències d'un cop, amb fila i columna. Necessita el catàleg (US1) i el nedador (US3).
- **US3 (P1, independent)** — Com a coach, mantinc la fitxa de cada nedador en un full de càlcul i la importo per donar-lo d'alta o actualitzar-lo, test CSS i millors marques incloses.

## Fitxers d'entrada

```
data/entrada/nedadors/<nom lliure>.csv            # fitxa, una per nedador
data/entrada/<AAAA-AA>/calendari.csv
data/entrada/<AAAA-AA>/inscripcions_<alias>.csv
```

Format comú (ADR-0013): UTF-8 (un BOM inicial s'accepta i s'ignora), separador `;`, valors compostos o llistes dins d'un camp separats per `|`, camp buit = `null`. Les files en blanc s'ignoren. Un fitxer sense cap fila de dades (buit o només capçalera) és ERROR de format `fitxer`. No hi ha escapament: un valor que conté `"` o `;` és ERROR de format del camp. Al calendari i a les inscripcions la primera fila és la capçalera amb els noms exactes de columna; qualsevol columna de més, de menys o en un altre ordre és error de format del fitxer.

### Fitxa del nedador (`clau;valor`)
Sense capçalera. Cada fila és `clau;valor`. L'ordre de les files és lliure. Una clau desconeguda, o repetida quan no és repetible, és error. Una clau obligatòria absent és error.

| Clau | Valor | Regla |
|---|---|---|
| `alias` | text | obligatòria; alias segons RN-003. Amb `--alta` és una proposta (si ja existeix, RN-041); sense `--alta` ha de correspondre a un nedador existent |
| `correu` | text o buit | obligatòria; valor buit admès; RN-032; es desa tal qual |
| `mobil` | text no buit | obligatòria (spec 001) |
| `canal_preferent` | `correu`, `mobil` o buit | obligatòria; valor buit admès; buit = avís RN-035; altre valor = error |
| `estils_preferents` | llista de Cr, Esq, Br, Pap, Ei | obligatòria; un o més, sense repetir |
| `dies_entrenament` | llista de dl, dt, dc, dj, dv, ds, dg | obligatòria; un o més, sense repetir |
| `volum_setmanal` | `min\|max` en metres | obligatòria (RN-005) |
| `test_css` | `piscina\|data\|t400\|t200` | repetible, màxim una per piscina (25, 50). Substitueix el test de la piscina (ADR-0022) |
| `marca` | `estil\|distancia\|piscina\|temps\|data\|competicio` | repetible, màxim una per estil+distància+piscina. S'afegeix només si millora la vigent (RN-007); si no, no es fa res |

- Totes les claus excepte `test_css` i `marca` són obligatòries; així una actualització mai no perd un valor per omissió.
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

L'`id` de la competició el genera el sistema a partir del nom i és estable entre reimportacions (RN-008).

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
blondswim importar fitxa <camí> [--alta] [--confirma]
blondswim importar calendari --temporada <AAAA-AA> [--confirma]
blondswim importar inscripcions --temporada <AAAA-AA> --alias <alias> [--confirma]
```

- Fitxa: la identitat és la fila `alias` del fitxer (ADR-0021); `--alta` indica que és una alta (ADR-0023).
- Inscripcions: l'alias és un argument; el nom del fitxer se'n deriva; no es llegeix del CSV (ADR-0013). Un alias que no correspon a cap nedador no arxivat és error (RN-037).
- La temporada és un argument; la carpeta se'n deriva. Un nom que no segueix RN-031 és error.

## Flux en dues passades (sense diàleg interactiu)
1. Sense `--confirma`: valida i mostra l'informe. Desa només si no hi ha cap error ni cap avís que requereixi confirmació.
2. Amb `--confirma`: valida, desa si no hi ha errors i registra cada avís que requereix confirmació a `data/avisos.jsonl` amb `decisio: confirmat`.
- Rebutjar = no tornar a executar amb `--confirma`. No s'escriu cap línia al registre (CA-001-64 retirat).
- Qualsevol error bloquejant → no es desa res del fitxer, ni amb `--confirma`.
- Codi de sortida: `0` desat; `1` errors; `2` pendent de confirmar.

## Efecte sobre les dades
- **Fitxa, alta (`--alta`):** id UUID v4 generat (RN-002), `arxivat: false`; l'alias és el de la fitxa (RN-003) i, si ja existeix, el sistema hi afegeix el primer sufix numèric lliure (RN-041: l'alta queda pendent de confirmar). Una alta sense avisos que requereixin confirmació es desa a la primera passada. Unicitat de correu i alias contra tots els nedadors, arxivats inclosos.
- **Fitxa, actualització (sense `--alta`):** l'alias ha de correspondre a un nedador existent; si no, ERROR RN-003. Es torna a validar el nedador sencer, unicitat inclosa; se substitueixen els camps modificables; id, alias i `versio_esquema` no canvien (CA-001-53). `test_css` substitueix el test de la piscina indicada. `marca` s'afegeix si millora (RN-007) i amb data posterior a la vigent (CA-001-102); si no millora, no es fa res ni s'avisa. Una fitxa d'un nedador arxivat és ERROR (RN-042): cal desarxivar-lo abans (operació de la spec 001).
- **Calendari:** el CSV és la font. Competició existent amb el mateix slug → s'actualitzen nom, dates, piscina i seu, mateix id; slug nou → competició nova; competició del catàleg sense fila al CSV → s'esborra si no té inscripcions, i si en té és error (RN-010). Dues files amb el mateix slug → error (RN-008). Si un canvi de dates o de piscina deixa invàlida una inscripció existent (dia inexistent o prova no oficial) → error (RN-038). Totes les dates han de ser dins la temporada (RN-043); la importació del calendari no toca les inscripcions.
- **Inscripcions:** el CSV és la font: `inscripcions.json` del nedador i temporada se substitueix sencer. Quan ja existeix un `inscripcions.json` i el resultat en difereix (participacions o proves que desapareixen o canvien), es genera l'avís RN-039 amb el resum de les diferències; es desa només amb `--confirma`. Les files s'agrupen per competició en una participació (classe) amb les seves proves.
- **Plans:** la importació no modifica mai cap pla. Si el nedador té un pla a la temporada i canvia una participació de classe A o la data d'una competició amb participació → avís RN-040 «el pla pot quedar desfasat».

## Validació
Un sol validador (spec 001): la importació aplica les mateixes regles que la càrrega. Aquesta spec només afegeix els errors de format del CSV i les RN-036 a RN-042.

- **ERROR** (bloquejant): format del fitxer (codificació, capçalera, columnes; claus de la fitxa), format d'un camp o valor, qualsevol RN de nivell ERROR de la spec 001, RN-036, RN-037, RN-038, RN-042, RN-043, RN-008, RN-010, RN-011.
- **AVÍS**: RN-009, RN-019, RN-035, RN-039, RN-040, RN-041.

## Contracte del cas d'ús (constitució IX)
Un cas d'ús per fitxer (`importar_fitxa`, `importar_calendari`, `importar_inscripcions`) a `application/`:
- Entrada: DTO amb el contingut del fitxer com a text cru (sense tipar) i els arguments (`temporada`, `alias`, `alta`, `confirma`).
- Sortida: `ResultatImportacio` amb `ok`, `desat`, `pendent_confirmacio` (bool), `incidencies[]`, `resum`. Cada incidència: `origen` (fila i columna o clau, o `fitxer`), `codi` (vegeu § Catàleg de codis), `nivell` (`bloquejant` o `avís`; l'ERROR i l'AVÍS d'aquesta spec hi mapegen 1:1, constitució IX), `valor`, `missatge`, `accio`.
- El lector CSV (`infrastructure/`) només obre el fitxer, comprova codificació i capçalera (o parells clau;valor), i retorna text. La CLI (`interfaces/`) només pinta el resultat i tradueix `ok/desat/pendent_confirmacio` a codi de sortida (0/1/2). Cap dels dos conté regles.
- El rellotge s'injecta (línies del registre d'avisos).

## Catàleg de codis
| Codi | Nivell | Quan |
|---|---|---|
| `RN-NNN` | el de la regla a `docs/regles.md` | s'incompleix una regla de negoci |
| `FORMAT-FITXER` | bloquejant | fitxer inexistent, codificació no UTF-8, fitxer sense files de dades |
| `FORMAT-CAPCALERA` | bloquejant | capçalera del calendari o de les inscripcions diferent de l'esperada |
| `FORMAT-CLAU` | bloquejant | fitxa amb una clau desconeguda, repetida (no repetible) o obligatòria absent |
| `FORMAT-<camp>` | bloquejant | valor amb format no vàlid, amb `"` o `;`, o fora dels admesos. `<camp>`: `nom`, `dates`, `piscina`, `seu`, `competicio`, `classe`, `dia`, `distancia`, `estil`, `prioritat`, `alias`, `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament`, `volum_setmanal`, `test_css`, `marca`, `temporada` |

## Informe (CLI)
Per fitxer: ruta, files llegides; errors i avisos ordenats per fila (o per clau), cada un amb origen, codi, valor i acció; línia final amb el resum i l'estat (`desat`, `pendent de confirmar`, `no desat`).

## Assumptions
- Un sol coach; execució local.
- El coach escriu els CSV amb una fulla de càlcul exportant amb `;` i UTF-8; no es dona suport a cap altra configuració.
- Els CSV es conserven a `data/entrada/` com a font; el sistema no els modifica ni els esborra.
- Els exemples de CSV viuen a `tests/fixtures/entrada/` i fan de plantilla per al coach.

## Dades i accions sensibles
- La fitxa conté correu i mòbil (dades personals, spec 001) i un alias que pot contenir un cognom (ADR-0023): dades personals que viuen a `data/`, no versionat, i no arriben a cap LLM. La fitxa viu a `data/entrada/`. L'informe de la CLI mostra el valor només a la incidència que l'afecta.
- Cap dada del CSV arriba a un LLM: aquesta spec no té punts de judici LLM.
- Accions destructives i la seva protecció: substituir `inscripcions.json` (RN-039, confirmació); esborrar una competició sense inscripcions del catàleg (RN-010 per a les que en tenen; les altres s'esborren sense avís perquè el CSV és la font); substituir el test CSS d'una piscina (ADR-0022, és la intenció del coach); substituir els camps modificables del nedador (spec 001 § Modificació).

## Clarifications

### Sessió 2026-11-10 (decisions preses al xat abans de `/speckit-specify`)
- P: Interfície web per a l'entrada de dades? → Diferida a la spec 009. L'entrada actual és CSV estricte (ADR-0013 revisat); el contracte de cas d'ús (constitució IX) permet afegir la web com a vista sense refer res.
- P: On es desen els CSV? → `data/entrada/`; calendari i inscripcions per temporada, fitxes a `nedadors/`.
- P: Com s'identifica el nedador en importar inscripcions? → L'alias és argument de l'ordre; el nom del fitxer se'n deriva; no es llegeix del CSV.
- P: Com s'entren els nedadors? → Tercer CSV només d'altes (`nedadors.csv`). Substituïda per 2026-11-11 (fitxa per nedador, ADR-0021 revisat).
- P: Qui posa l'id de la competició? → El sistema, com a slug del nom; les inscripcions referencien el nom.
- P: Com es confirmen avisos i alias? → Dues passades amb `--confirma`, sense diàleg. Rebutjar = no confirmar; CA-001-64 retirat. Matisada per 2026-11-11 (pla): l'alias ja no es confirma (ADR-0023).
- P: Canvi de dates que deixa una inscripció sense dia? → Error en importar el calendari (RN-038); el catàleg no canvia.

### Sessió 2026-11-11 (auditoria G1 r1, ADR-0021 revisat, ADR-0022)
- P: L'ADR-0021 (fitxa per nedador) contradiu la spec? → Sí; es manté l'ADR-0021 revisat: una fitxa `clau;valor` per nedador, alta o actualització, amb test CSS i marques com a estat actual. `nedadors.csv` desapareix.
- P: Històric de tests CSS? → No: un test per piscina, el nou substitueix l'anterior; entrar-lo és acceptar-lo (ADR-0022).
- P: Regles sense RN? → RN-036 a RN-041 definides aquí i a `docs/regles.md`.
- P: CA-002-01 vs CA-002-10? → Una alta sempre queda pendent (alias a confirmar); CA-002-01 s'aplica a calendari, inscripcions i actualitzacions de fitxa. Substituïda per 2026-11-11 (pla): l'alta sense avisos que requereixin confirmació es desa a la primera passada.
- P: Substituir `inscripcions.json` sense avís? → Avís RN-039 amb resum de diferències; es desa amb `--confirma`.
- P: Alias sense sufix que coincideix amb la part d'un nedador existent? → Alta nova amb avís RN-041 (abans: fila ignorada). Substituïda per 2026-11-11 (pla): RN-041 proposa un sufix numèric i l'alta queda pendent de confirmar (ADR-0023).
- Revisió 2 de la spec: fitxa del nedador segons ADR-0021 revisat i ADR-0022; correccions de l'auditoria G1 r1.

### Sessió 2026-11-11 (auditoria G1 r2)
- P: Què fa una clau opcional absent en una actualització? → No n'hi ha: totes les claus excepte `test_css` i `marca` són obligatòries; `correu` i `canal_preferent` admeten el valor buit. Una actualització mai no perd un valor per omissió.
- P: La fitxa porta `rpe` del test CSS? → No: `test_css` és `piscina|data|t400|t200`; un cinquè valor és error de format i `detall_400`, `detall_200` i `notes` queden `null` (ADR-0022).
- P: On és la derivació de l'id de competició? → A RN-008 (slug del nom).
- P: BOM? → El BOM UTF-8 inicial s'accepta i s'ignora; només la codificació no UTF-8 és error de format del fitxer (CA-002-03, 62).
- P: Fitxer buit o només capçalera? → ERROR de format `fitxer`: no es desa res (CA-002-59).
- P: Cometes i `;` dins d'un valor? → No hi ha escapament: un valor que conté `"` o `;` és ERROR de format del camp (CA-002-60).
- P: Estructura del resultat? → `incidencies[]` única, amb `nivell: bloquejant | avís` (constitució IX); ERROR i AVÍS de la spec hi mapegen 1:1; `errors[]` i `avisos[]` desapareixen (CA-002-50).
- P: Fitxa d'un nedador arxivat? → ERROR RN-042: cal desarxivar-lo abans (operació de la spec 001), com per a les inscripcions (RN-037) (CA-002-61).
- P: `rpe` únic a la fitxa? → Descartat (ADR-0022, Alternatives): la fitxa no el porta.

### Sessió 2026-11-11 (pla)
- P: Com s'escriu l'alias? → El coach l'escriu a la fila `alias`, amb el format de RN-003 (`^[a-z0-9]{2,9}(\d{2})?$`); el sistema no rep ni desa nom ni cognoms (ADR-0023).
- P: Com es distingeix una alta d'una actualització? → Per l'indicador `--alta` de l'ordre: amb `--alta` és una alta; sense, l'alias ha d'existir (si no, ERROR RN-003) (CA-002-20, 21).
- P: Alias existent en una alta? → El sistema hi afegeix el primer sufix numèric lliure (`01`…`99`) i ho indica amb l'avís RN-041, que requereix `--confirma` (evita duplicar un nedador en repetir una alta); si no es pot afegir cap sufix vàlid, ERROR RN-003 (CA-002-17, 64).
- P: Es confirma l'alias? → No: és determinista; CA-001-68 retirat. Una alta sense avisos que requereixin confirmació es desa a la primera passada (CA-002-11). RN-041 requereix confirmació i es registra amb `decisio: confirmat`.
- P: Nom de competició amb slug buit (cap lletra ni xifra)? → ERROR de format del camp `nom` (CA-002-63).
- P: Pla d'implementació? → Cablatge fora de les capes (`arrel.py`), fitxa atòmica, `versio_esquema` sense canvi i lectura de les inscripcions de tots els nedadors al calendari: decisions confirmades (D1, D4, D5, D6 de `plan.md`).
- P: Moment de les RN aplicades en importar? → RN-008, RN-010 i RN-019 inclouen el moment `importació`.

### Sessió 2026-11-12 (auditoria G1 r3)
- P: Canvi de piscina d'una competició amb inscripcions? → RN-038 ampliada: la reimportació no pot deixar cap inscripció invàlida (dia o prova no oficial); ERROR (CA-002-65).
- P: Quina regla exigeix dates dins la temporada? → RN-043, bloquejant a la càrrega i a la importació (CA-002-33).
- P: `incidencies[]` o `errors[]`? → `incidencies[]` amb `nivell`; la constitució IX (1.4.1) i l'ADR-0013 s'hi alineen.
- P: Catàleg de codis? → § Catàleg de codis.
- P: Independència de les històries? → US1 i US3 independents (P1); US2 depèn de totes dues (P2).

## Criteris d'acceptació

Format i lectura
- **CA-002-01** — Donat un CSV de calendari, d'inscripcions o una fitxa (alta o actualització) amb cap incidència, quan s'importa sense `--confirma`, aleshores es desa, el codi de sortida és 0 i l'informe diu `desat`.
- **CA-002-02** — Donat un CSV de calendari o d'inscripcions amb una columna de menys, de més o en un altre ordre, quan s'importa, aleshores no es desa res, hi ha un ERROR d'origen `fitxer` que identifica la capçalera esperada, i el codi és 1.
- **CA-002-03** — Donat un CSV amb codificació no UTF-8, quan s'importa, aleshores no es desa res i hi ha un ERROR d'origen `fitxer`.
- **CA-002-04** — Donat un CSV amb files en blanc (buides o només amb espais) intercalades, quan s'importa, aleshores s'ignoren sense error ni avís i els números de fila de l'informe són els del fitxer.
- **CA-002-05** — Donat un CSV amb una data `31/12/2026`, quan s'importa, aleshores hi ha un ERROR `FORMAT-<camp>` que indica fila, columna i valor, i no es desa res.
- **CA-002-06** — Donat un CSV amb diversos errors en files diferents, quan s'importa, aleshores l'informe els llista tots, ordenats per fila, i no s'atura al primer.
- **CA-002-07** — Donada una fitxa amb una clau desconeguda, una clau no repetible repetida o una clau obligatòria absent, quan s'importa, aleshores ERROR d'origen la clau (o `fitxer` si és absent) i no es desa res.

Confirmació
- **CA-002-08** — Donat un fitxer amb un avís i cap error, quan s'importa sense `--confirma`, aleshores no es desa res, el codi és 2, l'informe diu `pendent de confirmar` i `avisos.jsonl` no canvia.
- **CA-002-09** — Donat un fitxer amb un avís i cap error, quan s'importa amb `--confirma`, aleshores es desa, el codi és 0 i `avisos.jsonl` té una línia per avís amb `decisio: confirmat`, `rn`, `fitxer` (la ruta), `camp` (la columna o la clau), `valor` i `data_hora` del rellotge injectat.
- **CA-002-10** — Donat un fitxer amb un error i un avís, quan s'importa amb `--confirma`, aleshores no es desa res, el codi és 1 i `avisos.jsonl` no canvia.
- **CA-002-11** — Donada una fitxa d'alta (`--alta`) sense cap avís, quan s'importa sense `--confirma`, aleshores es desa a la primera passada, el codi és 0 i l'informe diu `desat`.

Fitxa: alta
- **CA-002-12** — Donada una fitxa d'alta vàlida (`--alta`) amb l'alias `agonzalez` que no existeix, quan s'importa, aleshores es crea `nedadors/<uuid>/nedador.json` vàlid segons la spec 001, amb l'alias `agonzalez` (CA-001-52), `arxivat: false`, i els camps informatius no presents a la fitxa a `null`.
- **CA-002-13** — Donada una fitxa amb `estils_preferents` `Cr|Cr` o `Cr|EP`, quan s'importa, aleshores ERROR que identifica clau i valor (CA-001-39).
- **CA-002-14** — Donada una fitxa amb `canal_preferent` buit, quan s'importa, aleshores AVÍS RN-035, no es desa res i el codi és 2 (CA-001-57).
- **CA-002-15** — Donada una fitxa amb `canal_preferent` `whatsapp`, quan s'importa, aleshores ERROR de format que indica les opcions admeses (CA-001-58).
- **CA-002-16** — Donada una fitxa d'alta amb un correu ja existent en un nedador arxivat (comparat en minúscules i sense espais als extrems), quan s'importa, aleshores ERROR RN-032 i no es desa res.
- **CA-002-17** — Donada una fitxa d'alta (`--alta`) amb un `alias` que ja existeix, quan s'importa, aleshores AVÍS RN-041 que indica l'alias proposat i l'assignat (el primer sufix `01`…`99` lliure), no es desa sense `--confirma` (codi 2), amb `--confirma` es desa amb l'alias assignat, i el nedador existent no canvia (CA-001-61).
- **CA-002-18** — Donat un nedador existent sense fitxa importada, quan s'importa la fitxa d'un altre nedador, aleshores el primer no s'esborra, no s'arxiva ni canvia (CA-001-38).
- **CA-002-19** — Donada una fitxa amb un ERROR (p. ex. `volum_setmanal` amb min > max), quan s'importa, aleshores no es desa res i el missatge indica l'alias, la RN i l'acció (CA-001-62, 72).

Fitxa: actualització, test i marques
- **CA-002-20** — Donada una fitxa, sense `--alta`, amb l'`alias` d'un nedador existent i `mobil` i `dies_entrenament` diferents dels desats, quan s'importa, aleshores es desen els valors nous, id, alias i `versio_esquema` no canvien (CA-001-53) i la resta de camps queden com a la fitxa.
- **CA-002-21** — Donada una fitxa, sense `--alta`, amb un `alias` que no correspon a cap nedador, quan s'importa, aleshores ERROR RN-003 i no es desa res.
- **CA-002-22** — Donada una fitxa d'actualització amb el `correu` d'un altre nedador, quan s'importa, aleshores ERROR RN-032 i no es desa res (CA-001-79).
- **CA-002-23** — Donada una fitxa d'actualització amb `correu` buit en un nedador que en tenia, quan s'importa, aleshores el nedador queda sense correu i l'antic queda lliure (CA-001-112).
- **CA-002-24** — Donada una fitxa amb `test_css;25|<data>|<t400>|<t200>` en un nedador amb test de 25 m, quan s'importa, aleshores `test_css["25"]` és el nou, el de 50 m no canvia i els camps informatius no presents queden `null` (ADR-0022).
- **CA-002-25** — Donada una fitxa amb dues files `test_css` de la mateixa piscina, quan s'importa, aleshores ERROR que identifica la clau i les dues files.
- **CA-002-26** — Donada una fitxa amb `test_css` amb un cinquè valor, quan s'importa, aleshores ERROR de format que identifica la clau; els camps `detall_400`, `detall_200` i `notes` del test desat són `null`.
- **CA-002-27** — Donada una fitxa amb una `marca` millor que la vigent de la mateixa prova i piscina i data posterior, quan s'importa, aleshores s'afegeix a `millors_registres` (RN-007); amb temps igual o pitjor, no es fa res ni s'avisa (CA-001-89); amb temps millor i data no posterior, ERROR (CA-001-102).
- **CA-002-28** — Donada una fitxa amb una `marca` d'una prova no oficial per a la piscina, quan s'importa, aleshores ERROR RN-030 (CA-001-42).
- **CA-002-29** — Donada una fitxa sense cap fila `test_css` ni `marca` en un nedador que en té, quan s'importa, aleshores tests i marques no canvien.

Calendari
- **CA-002-30** — Donat `calendari.csv` amb tres competicions, quan s'importa, aleshores `competicions/<AAAA-AA>.json` té tres competicions amb id = slug del nom, i es carrega sense error amb la spec 001.
- **CA-002-31** — Donats els noms `Campionat d'Hivern` i `campionat d hivern`, quan s'importa, aleshores ERROR RN-008 (slug duplicat) que identifica les dues files.
- **CA-002-32** — Donada una fila amb `seu` buida, quan s'importa, aleshores AVÍS RN-009 i es desa amb `seu: null` només amb `--confirma`.
- **CA-002-33** — Donada una fila amb una data fora de la temporada de l'argument, quan s'importa, aleshores ERROR RN-043 que identifica la fila, la data i la temporada.
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
- **CA-002-44** — Donat un `--alias` que no correspon a cap nedador no arxivat, quan s'importa, aleshores ERROR RN-037 i no es desa res.
- **CA-002-45** — Donat un `inscripcions.json` existent, quan es reimporta un CSV amb una participació menys, aleshores AVÍS RN-039 amb la participació que desapareix, no es desa sense `--confirma`, i amb `--confirma` el fitxer només té les participacions del CSV.
- **CA-002-46** — Donat un `inscripcions.json` existent, quan es reimporta un CSV idèntic en contingut, aleshores no hi ha avís RN-039 i es desa amb codi 0.
- **CA-002-47** — Donada una participació de classe A sense cap prova `principal`, quan s'importa, aleshores AVÍS RN-019 (CA-001-13) i es desa només amb `--confirma`.
- **CA-002-48** [PENDENT spec 003] — Donat un nedador amb pla a la temporada, quan es reimporten inscripcions que canvien una participació A, aleshores AVÍS RN-040 i el pla no canvia.

Arquitectura
- **CA-002-49** — Donat el codi d'`interfaces/` i d'`infrastructure/csv`, quan passa import-linter, aleshores no importen `domain/` ni llegeixen fitxers JSON (constitució X).
- **CA-002-50** — Donat un `ResultatImportacio` amb incidències de nivell `bloquejant` i `avís`, quan la CLI el pinta, aleshores el text conté per a cada incidència origen, codi, nivell, valor i acció, i el codi de sortida segueix `ok/desat/pendent_confirmacio` (0, 1, 2) sense cap lògica addicional.
- **CA-002-51** — Donada la funció de slug, quan rep `Campionat d'Hivern  (25 m)`, aleshores retorna `campionat-d-hivern-25-m` (RN-008).

Casos límit i parts de CA separades (els números no es reutilitzen)
- **CA-002-52** — Donat un calendari o unes inscripcions amb separador `,`, quan s'importa, aleshores no es desa res i hi ha un ERROR d'origen `fitxer` que identifica la capçalera esperada; en una fitxa, ERROR (fila que no és `clau;valor`) i no es desa res.
- **CA-002-53** — Donada una fitxa amb `canal_preferent` buit, quan s'importa amb `--confirma`, aleshores es desa i `avisos.jsonl` té una línia RN-035 amb `decisio: confirmat` (CA-001-63).
- **CA-002-54** — Donada una fitxa amb `test_css` amb t400 ≤ t200, quan s'importa, aleshores ERROR RN-006 que identifica la clau (CA-001-04).
- **CA-002-55** — Donat un `inscripcions_<alias>.csv` inexistent, quan s'importa, aleshores ERROR d'origen `fitxer` i no es desa res.
- **CA-002-56** — Donada una fitxa amb `test_css` amb una piscina diferent de 25 o 50, quan s'importa, aleshores ERROR de format que identifica la clau i el valor (CA-001-41).
- **CA-002-57** — Donada una fitxa amb dues files `marca` de la mateixa prova i piscina, quan s'importa, aleshores ERROR que identifica la clau i les dues files.
- **CA-002-58** — Donada una fitxa amb un `alias` que no compleix el format de RN-003 (p. ex. `Agonzalez`, `a_gonzalez`, `agonzález` o `agonzalez1`), quan s'importa, aleshores ERROR RN-003 que identifica la clau i el valor i no es desa res.
- **CA-002-59** — Donat un calendari, unes inscripcions o una fitxa sense cap fila de dades (buit o només capçalera), quan s'importa, aleshores ERROR de format d'origen `fitxer` i no es desa res.
- **CA-002-60** — Donat un CSV amb un valor que conté `"` o un `;` addicional, quan s'importa, aleshores ERROR de format del camp que indica fila, columna (o clau) i valor, i no es desa res.
- **CA-002-61** — Donada una fitxa d'un nedador arxivat, quan s'importa, aleshores ERROR RN-042 que identifica l'alias i l'acció (desarxivar-lo abans) i no es desa res.
- **CA-002-62** — Donat un CSV amb un BOM UTF-8 inicial, quan s'importa, aleshores el BOM s'ignora i el fitxer es llegeix com si no en tingués (la primera capçalera o clau no el conté).
- **CA-002-63** — Donat un calendari amb un `nom` sense cap lletra ni xifra (p. ex. `---`), quan s'importa, aleshores ERROR de format del camp `nom` que indica fila, columna i valor, i no es desa res.
- **CA-002-64** — Donada una fitxa d'alta (`--alta`) amb un `alias` que ja existeix i al qual no es pot afegir cap sufix vàlid (ja en té un de dos dígits, o els sufixos `01`…`99` estan ocupats), quan s'importa, aleshores ERROR RN-003 que identifica la clau i el valor i no es desa res.
- **CA-002-65** — Donat un catàleg amb una competició de piscina 25 i una inscripció d'un nedador a `100;Ei`, quan es reimporta un calendari que la canvia a piscina 50, aleshores ERROR RN-038 que identifica l'alias, la competició i la prova, i el catàleg no canvia.
