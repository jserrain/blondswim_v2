# Research: Importació estricta

**Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Cada decisió porta raó i alternatives. Les decisions de disseny D1, D4, D5 i D6 estan confirmades pel coach (2026-11-11).

## R1 — Lectura del CSV
- **Decisió:** `csv.reader(delimiter=";", quoting=csv.QUOTE_NONE)` sobre un fitxer obert amb `encoding="utf-8-sig"` i `newline=""`. El número de fila és `reader.line_num`. Les files buides o només amb espais s'ignoren sense canviar la numeració.
- **Raó:** `utf-8-sig` accepta i ignora el BOM i falla amb `UnicodeDecodeError` si no és UTF-8 (CA-002-03, 62). `QUOTE_NONE` implementa «no hi ha escapament»: les cometes queden com a caràcter i la capa d'aplicació les detecta (CA-002-60). `line_num` dona els números de fila del fitxer (CA-002-04).
- **Files amb més o menys camps que la capçalera:** el lector les retorna tal com són; el cas d'ús genera `FORMAT-fila` (un `;` addicional és un valor que en conté un, CA-002-60). La fitxa exigeix exactament dos camps per fila.
- **Alternatives:** `csv` amb cometes (contradiu la decisió de no escapar); llegir amb `str.split(";")` (perd la comprovació de l'estàndard i no gestiona `line_num`); pandas (dependència nova, prohibida).

## R2 — Slug de l'id de competició (RN-008)
- **Decisió:** `unicodedata.normalize("NFKD", nom)`, treure els caràcters de categoria `Mn`, `casefold()`, substituir cada seqüència de caràcters que no compleixin `str.isalnum()` per un sol `-` i treure els `-` dels extrems. Funció pura a `domain/definicions.py` (únic lloc de les definicions, principi V), amb l'ID de la font i CA-002-51.
- **Raó:** és la lectura literal de RN-008 («lletres o xifres»): una lletra no ASCII sense descomposició (`ß`, `ł`) es conserva. CA-002-31 i 51 queden coberts.
- **Alternatives:** només `[a-z0-9]` (descarta lletres vàlides i contradiu la lletra de la regla); transliteració externa (`unidecode`, dependència nova).
- **Slug buit (resolt):** un `nom` sense cap lletra ni xifra dona un slug buit i és ERROR de format del camp `nom` (spec 002, CA-002-63). El cas d'ús ho comprova abans de construir la competició.

## R3 — Cablatge i regla de capa (X)
- **Decisió:** `blondswim/arrel.py` (fora de les quatre capes) construeix `ServeisImportacio` amb les implementacions d'`infrastructure` i el passa a `interfaces.cli.executa(args, serveis)`. *Confirmada* (D1).
- **Raó:** la CLI necessita repositoris, lector, rellotge i generador d'id, però X no li permet importar `infrastructure`. El punt d'entrada de `pyproject` actual (`blondswim:main`) no serveix: importar `blondswim` carregaria `infrastructure` en qualsevol test de domini.
- **Alternatives:** cablar dins `interfaces` (viola X); un contenidor d'injecció a `application` (importaria `infrastructure`); service locator global (estat ocult).

## R4 — Resultat d'importació (IX)
- **Decisió:** `ResultatImportacio` amb `ok`, `desat`, `pendent_confirmacio`, `incidencies[]`, `resum`. `Incidencia(origen, codi, nivell, valor, missatge, accio)` amb `nivell` `bloquejant` o `avís`. Només tipus primitius (`str`, `int`, `bool`) perquè cap tipus de domini arribi a la vista.
- **Raó:** constitució IX i decisió del 2026-11-11 (una sola llista). El `codi` és la RN o `FORMAT-<camp>` (o `FORMAT-fila`, `FORMAT-fitxer`).
- **Conversió:** `ErrorValidacio` i `Avis` del domini porten `rn`, `fitxer`, `camp`, `valor`, `missatge` i `accio`; la conversió els copia i hi afegeix l'origen (R5). El `valor` es converteix a text.
- **Alternatives:** dues llistes (contradiu IX); excepcions per als errors (perd el resum).

## R5 — Origen fila/columna dels errors del domini
- **Decisió:** en convertir les files a objectes de domini, els casos d'ús guarden una traça `camp de domini → (fila, columna)` (p. ex. `participacions.0.proves.1.dia` → fila 7, columna `dia`). Un error del validador amb un camp present a la traça rep l'origen; si no, rep l'origen `fitxer`.
- **Raó:** el validador de la 001 informa de camps del model JSON, no del CSV. Cal traduir-los sense posar regles a la vista (IX).
- **Risc:** és la peça més delicada; les RN que afecten diverses files (RN-016, RN-036, RN-008) s'han d'informar amb totes les files implicades i es detecten al cas d'ús abans de construir el domini.
- **Alternatives:** validar fila per fila sense el validador (duplicaria regles, contradiu «un sol validador»).

## R6 — Fitxa: alta i actualització atòmiques
- **Decisió:** `importar_fitxa` converteix les claus; amb `--alta` és una alta (si l'alias ja existeix, hi afegeix el primer sufix `01`…`99` lliure i emet RN-041, que deixa l'alta pendent de confirmar; si no es pot, ERROR RN-003, CA-002-64); sense `--alta` l'alias ha de correspondre a un nedador existent (RN-042 si és arxivat; si no existeix, ERROR RN-003, CA-002-21). Construeix el `Nedador` final en memòria (`CanviNedador.aplica`, `substitueix_test`, `afegeix_registre`), el valida (`valida_nedador` i `valida_unicitat`) i desa una vegada. *Confirmada* (D4).
- **Canvis a `gestio.py`:** `prepara_alta` (genera l'id, resol l'alias, valida, no desa) separada de `desar`; `NouNedador` amb l'alias proposat (en lloc de la part), `test_css` i `millors_registres`. `alta()` existent es manté com a combinació d'ambdues. El reintent d'id per col·lisió d'alias desapareix (l'id és independent de l'alias).
- **Raó:** una alta amb un avís que requereix confirmació (p. ex. RN-035) no pot desar res a la primera passada, i una fitxa amb test i marques s'ha de validar com un tot (CA-002-19). Cridar `modifica`, `afegeix_test` i `afegeix_millor_registre` de manera successiva desaria parcialment.
- **Alternatives:** cridar les operacions existents una a una (no atòmic); duplicar la validació a la importació.

## R7 — RN-040 (pla possiblement desfasat)
- **Decisió:** no s'implementa en aquesta spec. No hi ha plans (spec 003) i el CA-002-48 és `[PENDENT spec 003]`.
- **Raó:** sense entitat de pla, la condició «si hi ha pla a la temporada» mai no es compleix. Crear un port buit seria inventar una interfície.
- **Alternatives:** port `ConsultaPlans` amb una implementació buida (disseny sense spec).

## R8 — Migració de la fase 0
- **Decisió:** `TestCss` perd `piscina` i `acceptat`; `Nedador.test_css` guarda un test o `None` per piscina; `test_vigent(nedador, piscina)` és la consulta directa (CA-001-04, 14). `gestio.afegeix_test` passa a `substitueix_test`; s'elimina `accepta_test`. El JSON passa de `tests_css` (llista) a `test_css` amb claus `"25"` i `"50"`. `versio_esquema` es manté a 1 (*confirmada*, D5: cap nedador real desat encara, ADR-0023).
- **Raó:** ADR-0022, spec 001 (§ Entitats, § Consultes, § Modificació) i els CA reescrits. `RN-020` deixa de parlar d'acceptació; `valida_aptitud` mira si hi ha algun test.
- **Alias (ADR-0023):** `Alias` valida `^[a-z0-9]{2,9}(\d{2})?$` (RN-003); desapareixen `Alias.genera` (sufix de l'id) i `coincideix_amb`, i la validació del sufix contra l'id (`valida_nedador`); apareix una funció de domini que, donat l'alias proposat i els existents, retorna l'alias amb el primer sufix lliure o un error. L'alias deixa de dependre de l'id. `contracts/fitxers-json.md` i `data-model.md` de la 001 canvien l'exemple d'alias.
- **Tests:** es retiren els de CA-001-05, 30, 35, 68 i 82; es reescriuen els de CA-001-04, 14, 31, 32, 46, 49, 51, 52 i 61; es revisen CA-001-33 i 34 (pendents de la spec 004). La traçabilitat no els exigeix perquè són a «CA retirats».
- **Contracte i dades:** `contracts/fitxers-json.md` i `data-model.md` de la 001 s'actualitzen a la fase 0.
- **Alternatives:** mantenir la llista i filtrar l'últim (contradiu ADR-0022); pujar `versio_esquema` (només si hi ha dades desades).

## R9 — Import-linter
- **Decisió:** afegir contractes `forbidden` a `pyproject.toml`: (a) `blondswim.interfaces` no importa `blondswim.domain` ni `blondswim.infrastructure` (X); (b) `blondswim.infrastructure.csv` no importa `blondswim.domain`. Amb `allow_indirect_imports = true` perquè `interfaces` arribi a `domain` a través d'`application`. El contracte `layers` existent es manté.
- **Raó:** CA-002-49 exigeix que l'incompliment falli a `verify.sh`.
- **Alternatives:** només `layers` (permet `interfaces` → `infrastructure`).

## R10 — Calendari: lectura de les inscripcions de tots els nedadors
- **Decisió:** per a RN-010 i RN-038 es llegeixen, per a tots els nedadors (arxivats inclosos) amb la temporada, les participacions i els dies. Si un fitxer no es pot llegir, hi ha una incidència bloquejant d'origen `fitxer` amb el nedador, i el catàleg no canvia. *Confirmada* (D6).
- **Raó:** no es pot garantir que cap participació quedi òrfena (RN-010) sense llegir-les (principi IV: res es descarta sense avisar).
- **Alternatives:** ignorar els il·legibles (podria esborrar una competició amb inscripcions).

## R11 — Alias de l'alta entre les dues passades (resolt, ADR-0023)
- **Decisió:** l'alias l'escriu el coach i és determinista; no hi ha alias definitiu a confirmar (CA-001-68 retirat). Una alta sense avisos que requereixin confirmació es desa a la primera passada. RN-041 (alias existent amb `--alta`) requereix confirmació: l'alta queda pendent fins a `--confirma`.
- **Raó:** l'alias d'abans incloïa el sufix de l'UUID aleatori; dues passades donaven alias diferents. Ara el sufix numèric depèn només dels alias existents, que no canvien entre passades.
- **Risc mitigat:** tornar a executar `--alta` amb la mateixa fitxa un cop desada activa RN-041; com que requereix confirmació, l'alta queda pendent (codi 2) i no es crea cap duplicat sense `--confirma`.
- **Alternatives:** conservar l'id entre passades amb un estat pendent (descartat a l'ADR-0023); confirmar només la part (descartat).

## R12 — Fixtures com a plantilla
- **Decisió:** `tests/fixtures/entrada/` té una fitxa d'alta, una d'actualització, un calendari i unes inscripcions d'exemple, amb noms fictius, i un cas d'error per fitxer d'entrada. Són la plantilla que el coach copia.
- **Raó:** `## Assumptions` de la spec; els exemples poden tenir noms concrets (principi VIII).
- **Alternatives:** plantilles a `docs/` (sense test que les validi).

## R13 — Dependències
- **Decisió:** cap. `csv`, `unicodedata`, `argparse`, `uuid` (ja usada pel generador d'id) i `datetime` són de la biblioteca estàndard.
- **Alternatives:** Click o Typer per a la CLI (dependència nova, prohibida).
