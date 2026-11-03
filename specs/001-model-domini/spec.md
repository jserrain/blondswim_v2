# Spec 001 — Model de domini

**Estat:** Aprovada

## Objectiu
Definir les entitats, els invariants i el format JSON del catàleg de competicions i de l'espai de cada nedador (ADR-0006).

Fora d'abast:
- Pla i registre (specs 003–008).
- Zones derivades del CSS (spec 004).
- Períodes no disponibles i canvis de disponibilitat (spec 003).
- Importació des del CSV (spec 002, ADR-0013).
- Aigües obertes (AAOO).
- Relleus: no es modelen (spec 000).
- Programa de proves de la competició: no es desa al catàleg.

## Organització

```
data/
  competicions/<AAAA-AA>.json        # catàleg comú de la temporada
  nedadors/<id>/
    nedador.json
    temporades/<AAAA-AA>/
      inscripcions.json
```

- L'id del nedador és el nom de la carpeta i no es repeteix dins del fitxer.
- Les proves objectiu no es desen enlloc: es deriven de les participacions de classe A.

## Identificador del nedador
- L'id del nedador és el nom de la carpeta (`nedadors/<id>/`); per exemple, `3f2a9c1e-7b4d-4e8a-9c2f-1d6b5e0a8f47`. Format: RN-001 (ADR-0014).
- Assignació i immutabilitat: RN-002. Els nedadors no s'esborren, s'arxiven: RN-004.
- El correu és una dada de `nedador.json` (RN-032), no forma part de l'id.
- L'alias del nedador és una dada de `nedador.json`: RN-003.

## Entitats

**Nedador** (`nedador.json`)
- `correu`: opcional (absent o `null` = sense correu). Format i unicitat: RN-032 (ADR-0020). Es desa tal com s'ha entrat. És una dada personal.

  > **El correu electrònic és un camp de contacte opcional. El sistema no corregeix, normalitza ni verifica que el correu sigui rebible. Si s'introdueix un correu incorrecte, les notificacions no es podran lliurar; la responsabilitat és de qui l'ha introduït, que l'haurà de modificar. El sistema només comprova que el correu contingui el símbol @ i que el domini tingui un punt.**

- `mobil`: obligatori; text no buit després de treure'n els espais en blanc als extrems (espais, tabuladors i salts de línia; buit: ERROR). Cap altra validació: sense format, unicitat ni avís (ADR-0020). No intervé en cap regla de planificació. És una dada personal.
- `canal_preferent`: `correu` o `mobil`; qualsevol altre valor és un error de format. Absent o `null`: RN-035. `correu` en un nedador sense correu: RN-035 (avís).
- `alias`: RN-003.
- `arxivat`: booleà. En crear el nedador val `false` (RN-017).
- `estils_preferents`: un o més codis, sense repetir. Admesos: Cr, Esq, Br, Pap, Ei (spec 000, §4). `Ei` indica un especialista en estils.
- `dies_entrenament`: un o més dies de la setmana (dl, dt, dc, dj, dv, ds, dg), sense repetir. Les competicions no hi compten.
- `volum_setmanal`: `{min, max}` en metres (RN-005).
- `tests_css`: llista de tests (RN-006). Cada test té:
  - `data`, `piscina` (25 o 50), `t400` i `t200` (`m:ss.cc`): obligatoris.
  - `acceptat`: booleà, obligatori. En registrar el test val `false`.
  - `detall_400` i `detall_200`: informatius. Cada un és un objecte amb aquests camps, tots informatius:
    - `parcials`: temps `m:ss.cc` de cada 100 m (4 al 400, 2 al 200);
    - `bracades_per_llarg`: cicles per llarg, mitjana de la prova (nombre positiu);
    - `sr`: cicles per minut, mitjana de la prova (nombre positiu);
    - `rpe`: enter de 0 a 10 (escala CR-10 modificada de Foster).
  - `notes`: text o `null` (informatiu).
  - Sempre en crol. Protocol: spec 000 (§9) i ADR-0011.
  - El coach col·loca la sessió de test a mà al pla del nedador i en registra el resultat a mà. El sistema no col·loca mai el test. Afegir-la al pla genera una versió nova del pla (principi VI); la mecànica la decideix la spec del pla.
  - **Test vigent:** l'últim test acceptat de la piscina del període. Registrar un test no canvia els ritmes fins que el coach l'accepta.
  - Les validacions del test (ràtio T400/T200, 200 no màxim, regularitat del 400) són de la spec 004. Avisos del test: RN-028 i RN-029.
  - El CSS i les zones es calculen a partir del test vigent (spec 004); no es desen. SWOLF i longitud de braçada són derivats: no es desen.
- `millors_registres`: llista de millores successives de la marca de competició per prova i piscina (RN-007). Cada registre és `{estil, distancia, piscina, temps, data, competicio}`, tots obligatoris.
  - `competicio`: el nom de la competició (text no buit). És informatiu: no es comprova contra el catàleg.
  - La prova (`estil`, `distancia`) és oficial per a la `piscina` (RN-030).
  - Els tests CSS no funcionen així: es desen tots, per estudiar-ne l'evolució.

**Temporada** (carpeta `temporades/<AAAA-AA>/`)
- No té fitxer propi. El nom de la carpeta i les dates d'inici i fi segueixen RN-031.

**Competició** (catàleg `competicions/<AAAA-AA>.json`)
- `id`: estable (RN-008).
- `nom`, `dates` (un o més dies), `piscina` (25 o 50).
- `seu`: un text, o `null` si no es coneix (RN-009).
- Esborrat: RN-010.

**Participació** (dins de `inscripcions.json` del nedador)
- `id_competicio` (RN-011).
- `classe`: A, B o C.
- `proves`: llista d'inscripcions (RN-014). Sense límit màxim al sistema.
- Regles: RN-012, RN-013.

**Inscripció**
- `prova`: `{distancia, estil}`, una prova individual del programa de la competició, oficial per a la piscina de la competició (RN-030).
- `dia`: una data (RN-015).
- `prioritat`: principal o secundària.
- Una sola inscripció per prova i competició: RN-016.

**Consultes (no es desen mai)**
- `setmana_iso`: setmana ISO 8601 (de dilluns a diumenge), identificada per l'any ISO i el número de setmana.
- `test_vigent`: vegeu `tests_css`.
- `marca_vigent(nedador, prova, piscina)`: l'última marca de la llista `millors_registres` d'aquella prova i piscina (RN-007).
- `proves_objectiu`: les inscripcions de les participacions de classe A.
- CSS i zones: spec 004.
- Classe de cada prova (s'agafa de la participació).

**Definició** (no és una consulta): la temporada, amb les dates d'inici i fi, és una definició del domini (RN-031).

## Validació: nivells
- **ERROR:** s'incompleix un invariant de format d'aquesta spec o una regla bloquejant.
  - Regles del nedador (aquell nedador queda exclòs): RN-001, RN-003, RN-005 a RN-007, RN-011 a RN-016, RN-030 (inscripcions i millors registres), RN-031 (carpeta de temporada), RN-032, i els invariants de format dels fitxers del nedador.
  - Regles del catàleg (falla TOTA la càrrega): RN-008, RN-031 (nom del fitxer) i els invariants de format del catàleg.
- **AVÍS:** RN-009 i RN-035. No bloqueja. RN-019 i RN-020 són avisos de planificació.
- **Apte per planificar:** continua regit per RN-017 i RN-018. Si no ho és, la planificació queda bloquejada i el missatge indica què falta.
- Cap nedador queda en un estat intermedi per culpa de les dades: o es desa o es carrega complet, o no.
- La 001 només dona el resultat de la validació per nedador i per nivell.

### Un sol validador
- L'entrada, la càrrega i el filtre apliquen el mateix validador, amb les mateixes regles.

### A l'entrada
- ERROR: el nedador no es desa. El missatge indica l'alias, la RN (si n'hi ha) i l'acció que cal fer; un error de format indica el camp.
- AVÍS: el nedador només es desa si el coach ho confirma explícitament (flux d'importació: spec 002).

### A la càrrega
- Es tornen a aplicar les mateixes regles (el JSON es pot haver editat a mà).
- ERROR en un fitxer del nedador: aquell nedador no es carrega; la resta de nedadors sí.
- ERROR en un fitxer del catàleg: falla TOTA la càrrega. Una inscripció que apunta a una competició inexistent (RN-011) és un ERROR només d'aquell nedador.
- Col·lisió d'unicitat (correu o alias): no es carrega cap dels nedadors implicats.
- AVÍS: es retorna al resultat i es desa al registre d'avisos, sense demanar confirmació.

### Filtre de validació
- El filtre passa per tots els nedadors i no s'atura al primer error. Un nedador amb un ERROR no es planifica fins que es corregeix.
- El resultat és per nedador i per camp: alias (o l'UUID de la carpeta si el fitxer no es pot llegir), camp, valor, RN (o «format» si no n'hi ha) i acció.
- Un nedador pot tenir diversos errors: els llista tots.
- La unicitat (correu, RN-032; alias, RN-003) es comprova sobre tots els fitxers que es poden llegir, siguin vàlids o no. El correu es compara en minúscules i sense espais als extrems; un nedador sense correu no hi participa. La unicitat només s'aplica a correu i alias. Una col·lisió identifica tots els nedadors implicats; un ERROR en un altre camp no n'exclou cap de la comprovació. També val per a l'alta.
- Un fitxer que no es pot llegir és un ERROR propi i no participa a la unicitat.

## Modificació del nedador

**Immutables:** `id`, `alias` i `versio_esquema` (aquest només canvia amb una migració). La modificació no els rep com a dada.

**Modificables:** `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament` i `volum_setmanal`.
- Una modificació torna a validar el nedador sencer, unicitat inclosa. Si hi ha un ERROR, no es desa res.
- Un `correu` nou passa RN-032 i es desa tal com s'ha entrat. L'id no canvia (RN-002).
- Canviar `dies_entrenament` o `volum_setmanal` a mitja temporada: la 001 ho permet. La nova planificació és de la spec 005 (CA-001-84).

**Amb operació pròpia:**
- Arxivar i desarxivar: es permeten totes dues (RN-017).
- `tests_css`: només s'hi afegeixen tests. Un test desat no s'edita; el coach l'accepta o no (`acceptat`).
- `millors_registres`: només s'hi afegeixen marques, segons RN-007. Un registre desat no s'edita.

## Format JSON
- Cada fitxer porta `versio_esquema`.
- Dates en format `AAAA-MM-DD`.
- Temps de registre en format `m:ss.cc` (spec 000).
- Hi ha tres tipus de camp:
  - **Obligatori:** ha de ser-hi amb un valor vàlid. Si falta o és `null`, és error.
  - **Informatiu** (`correu`, `notes`, `detall_400`, `detall_200` i els seus camps): no intervé en cap regla de planificació. Pot faltar o ser `null`; tots dos casos volen dir «sense valor» i no generen avís.
  - **Opcional amb avís** (`seu`, `canal_preferent`): com un informatiu, però sense valor genera l'avís que indica la spec (RN-009, RN-035).
- En desar, el sistema escriu tots els camps; un camp sense valor s'escriu `null`. No hi ha cap valor per defecte.

## Registre d'avisos
- Tot avís (RN-009, RN-019, RN-020, RN-035 i els que defineixin altres specs) s'afegeix a `data/avisos.jsonl`, una línia JSON per avís, amb `data_hora`, `rn`, `fitxer`, `camp`, `valor`, `missatge`, `id_nedador` (o `null`) i `decisio`.
- `decisio` és `confirmat` o `rebutjat` per als avisos d'entrada (la línia s'escriu quan el coach decideix) i `null` per als de càrrega i de planificació.
- El registre només creix: no s'hi esborra ni s'hi modifica cap línia.
- La data i hora la dona el rellotge del sistema en el moment de registrar l'avís.

## Assumptions
- Un sol coach gestiona totes les dades.
- Els fitxers de `data/` són locals i no es versionen.
- Els fitxers s'editen a mà o els genera la importació (spec 002).
- Spec de model: no té històries d'usuari ni checklist; els criteris d'acceptació són el contracte.
- El format del correu és a RN-032 (ADR-0020) i es comprova només per caràcters, sense xarxa (menys de 10 ms). El sistema no verifica ni normalitza el correu.
- El correu i el mòbil són dades personals. Quines dades poden arribar a un LLM ho fixarà l'ADR pendent de l'auditoria G0.
- `data/avisos.jsonl` només creix i cap avís vigent no hi porta el correu ni el mòbil. Com es compleix el dret de supressió (RGPD, art. 17) a `nedador.json` i al registre ho fixa el pendent «ADR de dades personals: supressió» (`docs/estat.md`).

## Clarifications

### Sessions 2026-10-20 a 2026-10-22 (fora de `/speckit-clarify`; detall a l'historial git de la spec)

- P: Què identifica un nedador? → Un id opac, que és el nom de la carpeta (RN-001, RN-002). El correu és una dada de `nedador.json` i és únic (RN-032); l'alias és obligatori (RN-003). Matisada per 2026-11-03 (vespre) (el correu és opcional).
- P: Es pot esborrar un nedador? → No: s'arxiva (RN-004, RN-017).
- P: Es pot planificar un nedador sense test CSS? → Sí: és apte i es genera l'avís «sense ritmes» (CA-001-14).
- P: Quin test CSS s'aplica? → El test vigent: l'últim acceptat de la piscina del període. Registrar-ne un no canvia els ritmes fins que el coach l'accepta.
- P: Qui col·loca la sessió de test CSS al pla? → El coach, a mà; el sistema no ho fa mai (ADR-0011).
- P: Quins camps poden faltar? → Només els informatius (`canal_preferent`, `notes`, `detall_400`, `detall_200` i els seus camps) i `seu`; en desar s'escriuen com a `null` (§ Format JSON). Substituïda per 2026-10-27 (`canal_preferent` passa a opcional amb avís).
- P: Com es defineix la setmana? → Setmana ISO 8601; és un valor derivat i no es desa.
- P: A què s'inscriu un nedador? → A proves individuals del programa de la competició, una inscripció per prova (RN-016), sense límit màxim al sistema. Els relleus i el programa de proves no es modelen.
- P: La spec repeteix el text de les regles? → No: s'hi refereix per ID a `docs/regles.md` (principi III).
- P: Què passa amb els criteris que depenen d'una spec futura? → Porten `[PENDENT spec NNN]` i no es comproven fins que aquella spec és Aprovada.

### Sessió 2026-10-23 (auditoria G1)

- P: Què vol dir que un fitxer desat sigui «idèntic»? → Contingut equivalent a l'original (mateixos valors; un camp informatiu absent equival a `null`); desar dues vegades seguides dona fitxers idèntics byte a byte.
- P: Què passa si es demana esborrar un nedador? → Error que indica que s'ha d'arxivar; una importació que no l'inclou no l'esborra ni l'arxiva.
- P: Quins estils preferents s'admeten? → Cr, Esq, Br, Pap i Ei. `EP` i els codis de sèrie (FRIM, PEB, Ei inv) no.
- P: Quines piscines s'admeten? → 25 m i 50 m; no hi ha altres mides oficials.
- P: Quines proves s'admeten? → Només les proves individuals oficials per a la piscina (RN-030).
- P: Com es defineix la temporada? → De l'1/10 al 30/09 de l'any següent; el nom de la carpeta en dona la definició (RN-031).
- P: Com s'identifica la persona? → Pel correu, obligatori i únic; no es desen nom ni cognoms (RN-032). Substituïda per 2026-10-25 (l'id és un UUID) i matisada per 2026-11-03 (vespre) (el correu és opcional i no identifica).
- P: On es registren els avisos? → A `data/avisos.jsonl`, que només creix (§ Registre d'avisos).

### Sessió 2026-10-25 (esmena: id, alias i contacte)

- P: Quin format té l'id del nedador? → UUID v4 en minúscules, generat pel sistema; no es pot endevinar (ADR-0014, RN-001, RN-002).
- P: L'alias és opcional? → No: és obligatori, únic i immutable, amb la forma `<part>_<sufix>`; el sufix són els 7 primers caràcters de l'id i l'afegeix sempre el sistema (RN-003).
- P: Es pot corregir un alias mal escrit? → No: en crear el nedador es mostra l'alias definitiu i es demana confirmació (RN-003). Substituïda per 2026-10-27 (la confirmació del coach és de la spec 002).
- P: I si l'alias nou coincideix amb un d'existent? → El sistema genera un id nou i torna a proposar l'alias (RN-003). Substituïda per 2026-10-27 (l'alta genera l'alias, sense proposar-lo).
- P: Quines dades de contacte té el nedador? → Correu i mòbil, tots dos obligatoris; el correu és únic i el mòbil pot ser compartit, amb avís (ADR-0015, RN-032 a RN-034). Substituïda per 2026-10-27 (ADR-0016 substitueix l'ADR-0015).
- P: Com s'escriu el mòbil? → En E.164 (`+34…`). Afegir `+34` a un número sense prefix és feina de l'entrada de dades, no de la càrrega (ADR-0015). Substituïda per 2026-10-27 (ADR-0016 substitueix l'ADR-0015).
- P: Què és `canal_preferent`? → `correu` o `mobil`; informatiu, sense avís si falta. Un valor no admès és una incidència resoluble (RN-035). Substituïda per 2026-10-27 (sense valor, avís; valor no admès, error de format).

### Sessió 2026-10-27 (re-auditoria G1: validació per nivells)

- P: Què passa amb un nedador que té un error a l'entrada? → No es desa; el missatge indica l'alias, la RN i l'acció que cal fer.
- P: I amb un avís a l'entrada? → Es mostra al coach i el nedador només es desa si el coach ho confirma explícitament. Rebutjar-lo no és un error.
- P: Pot un nedador quedar en un estat intermedi per les dades? → No. L'aptitud per planificar continua regida per RN-017 i RN-018.
- P: Com acaba cada ordre i on són el resum i el codi de sortida? → Són de la spec 002. La 001 només dona el resultat de la validació per nedador i per nivell (CA-001-67).
- P: Un error d'un nedador fa fallar tota la càrrega? → No: aquell nedador no es carrega i la resta sí. Amb una col·lisió de correu o d'alias no es carrega cap dels implicats. Els avisos de càrrega es desen al registre, sense confirmació.
- P: Què registra el registre d'avisos sobre la decisió del coach? → El camp `decisio`: `confirmat`, `rebutjat` o `null` (avisos de càrrega i de planificació).
- P: Falta `canal_preferent`? → Avís (a la càrrega o a la importació; RN-035). Un valor fora de `correu` i `mobil` és un error de format del camp, no de RN-035. Ja no hi ha incidències resolubles ni valor per defecte.
- P: Què vol dir `[PENDENT spec 002]` a la 001? → Que el criteri depèn del flux d'importació. Les operacions de domini no parlen de CLI: l'alta genera l'id i l'alias i rebutja un ERROR (CA-001-52, 61, 62); la confirmació de l'alias és el CA-001-68; `canal_preferent` no admès en una importació és el CA-001-58. Cap operació permet canviar l'alias (CA-001-53).
- P: Com s'entren els nedadors i quina n'és la font? → A la 001 no hi ha entrada per CLI: el format d'entrada de nedadors el defineix la spec 002 i no es justifica amb cap ADR. Els criteris que en depenen (CA-001-58, 63, 64, 68 i 72) són `[PENDENT spec 002]`, que també ha de definir com es confirmen els avisos en una importació massiva.
- P: Un error del catàleg fa fallar un sol nedador? → No: fa fallar TOTA la càrrega. El criteri per nedador només s'aplica als fitxers del nedador. Una inscripció que apunta a una competició inexistent és un ERROR només d'aquell nedador (RN-011).
- P: Un nedador exclòs per un error compta per a la unicitat? → Sí: continua comptant per a la unicitat de correu i alias (RN-032, RN-003), per a RN-034 i per a l'alta (CA-001-69, 70). Matisada per 2026-10-28 (només compten els fitxers que es poden llegir). Substituïda per 2026-10-29 quant a RN-034 (retirada).
- P: Quin contacte i quin canal preferent? → ADR-0016 substitueix l'ADR-0015. RN-035 és només un avís (`canal_preferent` absent o `null`); un valor no admès és un error de format (CA-001-57 a 59). Substituïda per 2026-10-29 (ADR-0017 substitueix l'ADR-0016).
- P: Què es pot provar a la 001 de l'alta amb un ERROR? → Que no es desa (CA-001-62). El flux d'importació és el CA-001-72, `[PENDENT spec 002]`.
- P: On es decideix la supressió de dades personals? → Al pendent «ADR de dades personals: supressió» (`docs/estat.md`), quan un nedador ho demani.

### Sessió 2026-10-28 (G1 r2: filtre de validació i modificació)

- N1 — P: Hi ha un validador per a cada moment? → No: un sol validador amb les mateixes regles a l'entrada, a la càrrega i al filtre.
- N1 — P: El filtre s'atura al primer error? → No: passa per tots els nedadors i per tots els camps. Un nedador amb un ERROR no es planifica fins que es corregeix.
- N1 — P: Què dona el resultat? → Per nedador i per camp: alias (o l'UUID de la carpeta si el fitxer no es pot llegir), camp, valor, RN (o «format») i acció.
- N1 — P: Quins fitxers compten per a la unicitat? → Tots els que es poden llegir, vàlids o no (RN-032, RN-003, RN-034). Una col·lisió identifica tots els implicats. Un fitxer il·legible és un ERROR propi i no hi participa. Substituïda per 2026-10-29 quant a RN-034 (retirada).
- N3 — P: Quines dades no canvien mai? → `id`, `alias` i `versio_esquema` (només amb una migració). La modificació no els rep com a dada.
- N3 — P: Què es pot modificar? → `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament` i `volum_setmanal`. La modificació torna a validar el nedador sencer, unicitat inclosa; amb un ERROR no es desa res.
- N3 — P: Quines dades tenen operació pròpia? → Arxivar i desarxivar; `tests_css` (només s'afegeixen; el coach accepta o no); `millors_registres` (només s'afegeixen; el millor per prova i piscina és derivat). Un test o un registre desat no s'edita. Substituïda per 2026-10-29 (decisió B) quant a `millors_registres`.
- N3 — P: Es pot canviar `dies_entrenament` o `volum_setmanal` a mitja temporada? → Sí. Replanificar és de la spec 005 (CA-001-84, `[PENDENT spec 005]`).
- N3 — P: Els millors registres s'actualitzen? → No: només s'afegeixen. El millor per prova i piscina és un valor derivat (el millor temps de la llista) i no es desa. RN-007 (unicitat) queda retirada. Substituïda per 2026-10-29 (decisió B).
- Decisió a — P: Es pot desarxivar? → Sí: un nedador pot tornar una temporada posterior (RN-017).
- Decisió b — P: Es poden canviar `dies_entrenament` i `volum_setmanal` a mitja temporada? → Sí; es torna a planificar amb la configuració nova i la planificació passada es conserva com a registre (CA-001-84, spec 005).
- Decisió c — P: S'editen els tests CSS i els millors registres desats? → No.

### Sessió 2026-10-29 (decisions A, B i C; correccions del G2)

- Decisió A — P: Quin contacte té el nedador? → ADR-0017 substitueix l'ADR-0016. El correu és obligatori, únic entre tots els nedadors (arxivats inclosos) i intransferible; es normalitza (sense espais als extrems, en minúscules) abans de validar-lo i desar-lo, i té un format simple (RN-032). RN-033 i RN-034 queden retirades: el mòbil és obligatori, sense format, sense unicitat i sense avís. Substituïda per 2026-11-03 (ADR-0019 substitueix l'ADR-0017; el format és l'expressió regular de RN-032) i per 2026-11-03 (vespre) (ADR-0020).
- Decisió A — P: Es pot modificar el correu? → Sí: l'id no canvia (RN-002); el correu nou passa format i unicitat, i l'antic queda lliure (CA-001-79, 88). Matisada per 2026-11-03 (vespre) (el correu es desa tal qual; CA-001-88 retirat, ara CA-001-109).
- Decisió A — P: A què s'aplica la unicitat? → Només a correu i alias (RN-003, RN-032).
- Decisió A — P: Un nedador amb un camp d'identitat il·legible (que falta o no és text) participa a la unicitat? → A la dels altres camps sí; a la d'aquell camp no. L'error del camp el dona el validador (CA-001-92).
- Decisió B — P: Què és un millor registre? → El de competició, un sol per prova i piscina, amb `temps`, `data` i `competicio` (id del catàleg, obligatori). Un temps menor substitueix el desat; igual o pitjor, no es fa res, ni error ni avís (RN-007, CA-001-83, 89 a 91). Desfà la decisió del 2026-10-28 (millor registre derivat i només-afegir). Substituïda per 2026-11-03 (decisió 1).
- Decisió B — P: I els tests CSS? → Es desen tots, per estudiar l'evolució; sense canvis.
- Decisió B — P: Què és una consulta i què una definició? → Consultes (no es desen): `proves_objectiu`, `test_vigent`, `marca_vigent`, `setmana_iso`. L'inici i el fi de temporada són una definició del domini (RN-031).
- Decisió C — P: Els CA de la spec 000 sense test? → Només el CA-000-10 (millor registre sense piscina) fa servir el domini de la 001: té tasca a la US1b. El CA-000-01 és `[PENDENT spec 004]` i els CA-000-02 a 09 i 11 a 24, `[PENDENT spec 006]`. La part d'estils de CA-000-02 i 03 ja la cobreix CA-001-39.
- Decisió 2 (2026-10-29) — P: Quan és vàlid el `mobil`? → Si no és buit després de treure'n els espais als extrems; buit és un ERROR. Cap altra validació (CA-001-54, 93).
- Decisió 3 (2026-10-29) — P: Què s'exigeix a `millors_registres.competicio`? → Que la piscina del registre coincideixi amb la de la competició; si no, ERROR (CA-001-94). RN-010 s'amplia: no es pot esborrar una competició referenciada per inscripcions ni per millors registres (CA-001-21, 95). Substituïda per 2026-11-03 (decisió 1).

### Sessió 2026-11-03 (decisions 1 i 3; correccions de les auditories G1 i G2 del 29/10)

- Decisió 1 — P: Què és un millor registre? → Una llista de millores successives per prova i piscina, només de competició. Camps, tots obligatoris: prova (`estil` i `distancia`), `piscina`, `temps`, `data` i `competicio` (el nom, text no buit). La competició és informativa: no es comprova contra el catàleg (RN-007, CA-001-91).
- Decisió 1 — P: Quan s'afegeix una marca? → Només si és millor que la marca vigent de la mateixa prova i piscina; si és igual o pitjor, no es fa res (ni error ni avís). Les marques de 25 m i de 50 m no es comparen mai (CA-001-83, 89).
- Decisió 1 — P: I una llista que no és ordenada al fitxer? → ERROR: dins de cada prova i piscina, cada marca ha de ser millor que l'anterior (RN-007, CA-001-06, 96).
- Decisió 1 — P: Quina és la marca vigent? → L'última de la llista de la prova i piscina; és una consulta i no es desa (CA-001-97).
- Decisió 1 — P: RN-010 i la competició d'un millor registre? → RN-010 torna a cobrir només les inscripcions. CA-001-94 i 95 retirats.
- Decisió 3 — P: Quin format té el correu? → El de RN-032, que és una expressió regular completa aplicada després de normalitzar-lo (CA-001-87). Substituïda per 2026-11-03 (vespre) (format mínim, sense normalitzar; ADR-0020).
- Decisió 3 — P: Es verifica que el correu existeix? → No a la 001: és una spec pròpia futura (ADR-0018). El nedador té `correu_verificat`, obligatori, `false` en crear-lo i en modificar-ne el correu; cap operació de la 001 el posa a `true` (CA-001-98 a 100). Substituïda per 2026-11-03 (vespre) (no es verifica; `correu_verificat` desapareix).
- N-1 — P: Quin és l'ADR vigent del contacte? → L'ADR-0019 substitueix sencer l'ADR-0017: correu obligatori, únic, normalitzat i amb l'expressió regular de RN-032; mòbil obligatori (no buit), sense format ni unicitat; `canal_preferent` sense canvis; la verificació és de l'ADR-0018. Substituïda per 2026-11-03 (vespre) (ADR-0020 substitueix l'ADR-0019 i l'ADR-0018).
- N-3 — P: Quina data ha de tenir una marca nova? → Posterior a la de la marca vigent de la mateixa prova i piscina; si no ho és, ERROR (RN-007, CA-001-102). Un temps igual o pitjor continua sense fer res.
- N-4 — P: Quan torna `correu_verificat` a `false`? → Només si el correu normalitzat canvia; un canvi de majúscules o d'espais el conserva (ADR-0018, CA-001-99, 103). Substituïda per 2026-11-03 (vespre) (`correu_verificat` desapareix; CA-001-99 i 103 retirats).
- Correcció — P: Un mòbil compartit o sense format E.164 dona error o avís? → No: s'accepta sense error ni avís (CA-001-101).

### Sessió 2026-11-03 (vespre) (esmena del correu: ADR-0020)

- A — P: Quin és el contacte del nedador? → ADR-0020 substitueix l'ADR-0019 i l'ADR-0018. El correu és un camp de contacte opcional (absent o `null` = sense correu); el sistema no el corregeix, normalitza ni verifica. Si és incorrecte, les notificacions no es podran lliurar i la responsabilitat és de qui l'ha introduït. Es desa exactament tal com s'ha entrat.
- A — P: Quin format té el correu? → Només es comprova per caràcters, sense xarxa: una `@`, part local no buida, domini no buit amb un punt i cap espai en blanc al mig; els espais dels extrems no compten (RN-032). L'expressió regular estricta i la normalització desapareixen (CA-001-85 a 87 retirats).
- A — P: Com és la unicitat? → Si hi ha correu, és únic entre tots els nedadors (arxivats inclosos), comparat en minúscules i sense espais als extrems; el valor desat no canvia. Un nedador sense correu no hi participa.
- B — P: Es verifica el correu? → No: ni correu de confirmació, ni MX, ni SMTP. `correu_verificat` desapareix de la documentació; CA-001-98 a 100 i 103 retirats. La spec 009 del mapa i les entrades del `BACKLOG.md` sobre verificació i variants de Gmail queden retirades.
- C — P: Què passa amb `canal_preferent: correu` si no hi ha correu? → Avís (RN-035, CA-001-110). Absent o `null` continua sent avís; un valor fora de `correu` i `mobil`, error de format.
- D — P: Quan és buit el `mobil`? → Si és buit després de treure'n els espais en blanc als extrems (espais, tabuladors i salts de línia); un mòbil amb només un tabulador o un salt de línia és un ERROR (CA-001-111).
- E — P: I els CA que normalitzaven el correu o en miraven la verificació? → Retirats: CA-001-85, 86, 87, 88, 98, 99, 100 i 103. CA-001-01 i 44 es revisen; CA-001-101 (mòbil) continua vigent. CA nous: CA-001-104 a 111.
- F — P: Quins canvis té el pla? → `tasks.md` (T035, T036, T038 a T042, T044, T047 i la taula CA → tasca), `plan.md` (D1: el correu es compara en minúscules i sense espais, el valor no canvia), `research.md`, `data-model.md`, contracte i quickstart. Recomptes: 98 CA actius (89 amb test, 9 pendents) i 13 retirats.

## CA retirats

Els números no es reutilitzen.

| CA | Motiu |
|---|---|
| CA-001-55 | Format de mòbil: RN-033 retirada (ADR-0020) |
| CA-001-56 | Mòbil compartit: RN-034 retirada (ADR-0020) |
| CA-001-77 | Avís de mòbil compartit amb un ERROR en un altre camp: RN-034 retirada (ADR-0020) |
| CA-001-85 | Normalització del correu (minúscules, espais): el correu es desa tal com s'entra (ADR-0020) |
| CA-001-86 | Correu de format vàlid segons l'expressió regular: substituïda pel format mínim (CA-001-104, ADR-0020) |
| CA-001-87 | Correus no vàlids segons l'expressió regular: substituïda pel format mínim (CA-001-105, ADR-0020) |
| CA-001-88 | Modificar el correu (normalitzat; l'antic queda lliure): substituït pel CA-001-109 (ADR-0020) |
| CA-001-94 | Piscina del registre igual a la de la competició: la competició és un nom informatiu (decisió 1, 2026-11-03) |
| CA-001-95 | Esborrar una competició referenciada per un millor registre: RN-010 només cobreix les inscripcions (decisió 1, 2026-11-03) |
| CA-001-98 | `correu_verificat` a `false` en l'alta: el camp desapareix (ADR-0020) |
| CA-001-99 | `correu_verificat` en canviar el correu: el camp desapareix (ADR-0020) |
| CA-001-100 | `correu_verificat` en canviar un altre camp: el camp desapareix (ADR-0020) |
| CA-001-103 | `correu_verificat` en canviar només majúscules o espais: el camp desapareix (ADR-0020) |

## Criteris d'acceptació
- **CA-001-01** — **Donat** un `nedador.json` vàlid, **quan** es carrega i es torna a desar, **aleshores** el contingut desat és equivalent a l'original (mateixos valors; el correu es desa i es torna a llegir idèntic, sense normalitzar; un camp informatiu absent equival a `null`).
- **CA-001-02** — **Donat** un catàleg de competicions i un `inscripcions.json` vàlids, **quan** es carreguen i es tornen a desar, **aleshores** el contingut desat és equivalent a l'original.
- **CA-001-03** — **Donat** un nedador sense estils preferents, sense dies d'entrenament o amb `volum_setmanal.min > max`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp.
- **CA-001-04** — **Donat** un test CSS amb t400 ≤ t200, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-05** — **Donats** dos tests CSS acceptats de la mateixa piscina i un de més recent no acceptat, **quan** es demana el vigent per a aquella piscina, **aleshores** s'obté l'acceptat de data més recent.
- **CA-001-06** — **Donats** dos millors registres consecutius amb el mateix estil, distància i piscina i el mateix temps, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica la prova i la piscina (RN-007).
- **CA-001-07** — **Donat** un millor registre amb temps `1:05.3`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error de format.
- **CA-001-08** — **Donada** una participació sense inscripcions, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-09** — **Donada** una inscripció amb un dia que no és de la competició, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-10** — **Donada** una participació a una competició amb alguna data fora de la temporada del nedador, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-11** — **Donats** dos ids de competició repetits al catàleg, **quan** es carrega, **aleshores** falla TOTA la càrrega i dona un error.
- **CA-001-12** — **Donada** una competició amb `seu: null` o sense el camp `seu`, **quan** es carrega, **aleshores** es carrega correctament i genera un avís.
- **CA-001-13** — **Donada** una participació de classe A sense cap inscripció principal, **quan** es valida, **aleshores** genera un avís i no bloqueja la planificació.
- **CA-001-14** — **Donat** un nedador vàlid, no arxivat, sense cap test CSS acceptat i sense ritmes, amb una participació de classe A, **quan** es demana si és apte per planificar, **aleshores** la resposta és «sí» i genera l'avís «sense ritmes».
- **CA-001-15** — **Donat** un nedador sense cap participació de classe A, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «falta competició A».
- **CA-001-16** — **Donat** un nedador amb participacions A, B i C, **quan** es demanen les proves objectiu, **aleshores** s'obtenen només les inscripcions de les participacions A.
- **CA-001-17** — **Donat** un fitxer amb un `versio_esquema` desconegut, **quan** es carrega, **aleshores** si és el d'un fitxer del catàleg, falla TOTA la càrrega i dona un error; si és el d'un fitxer del nedador, aquell nedador no es carrega i dona un error.
- **CA-001-18** — **Donada** una competició en una data qualsevol, **quan** es demana la setmana, **aleshores** es calcula a partir de la data (any ISO + setmana) i no es llegeix del fitxer.
- **CA-001-19** — **Donada** una participació amb un `id_competicio` que no és al catàleg, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-20** — **Donats** dos nedadors que participen a la mateixa competició amb classes diferents (A i C), **quan** es carreguen, **aleshores** tots dos són vàlids i cadascun conserva la seva classe.
- **CA-001-21** — **Donada** una competició del catàleg amb inscripcions, **quan** s'intenta esborrar, **aleshores** dona un error.
- **CA-001-22** — **Donat** un canvi de data d'una competició al catàleg, **quan** es consulten les participacions dels nedadors, **aleshores** totes veuen la data nova.
- **CA-001-23** — **Donat** un nedador amb dues participacions a la mateixa competició, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-24** — **Donats** dos nedadors amb el mateix correu, escrit amb majúscules diferents i un d'ells arxivat, **quan** es carreguen, **aleshores** no es carrega cap dels dos i es dona un error que identifica els dos ids (RN-032).
- **CA-001-25** — **Donat** un nedador existent, **quan** se'n canvia el correu, **aleshores** l'id no canvia.
- **CA-001-26** — **Donats** dos nedadors amb el mateix `alias`, un d'ells arxivat, **quan** es carreguen, **aleshores** no es carrega cap dels dos i es dona un error que identifica els dos ids (RN-003).
- **CA-001-27** — **Donada** una carpeta de nedador amb un nom que no compleix RN-001 (p. ex. `n0001`, `3F2A9C1E-7B4D-4E8A-9C2F-1D6B5E0A8F47` o un UUID v1), **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-28** — **Donat** un nedador arxivat, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «arxivat».
- **CA-001-29** — **Donada** una participació amb la mateixa prova inscrita en dos dies diferents de la competició, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error (RN-016).
- **CA-001-30** — **Donat** un nedador amb un test acceptat vigent, **quan** es registra un test nou de la mateixa piscina, **aleshores** el test nou té `acceptat: false` i el vigent no canvia; **quan** el coach l'accepta, **aleshores** el test nou passa a ser el vigent.
- **CA-001-31** — **Donat** un test amb `detall_400` i `detall_200` amb tots els camps a `null`, **quan** es carrega i es torna a desar, **aleshores** el contingut desat és equivalent a l'original i els `null` es conserven.
- **CA-001-32** — **Donat** un test amb `notes` i tots els camps de detall a `null`, **quan** es carrega, **aleshores** no genera cap avís (principi V).
- **CA-001-33** [PENDENT spec 004] — **Donat** un nedador amb l'últim test acceptat d'una piscina més antic que el termini de RN-028 i cap test planificat d'aquella piscina, **quan** es planifica, **aleshores** genera l'avís de test caducat (RN-028).
- **CA-001-34** [PENDENT spec 004] — **Donat** un període de piscina que comença sense cap test acceptat ni planificat d'aquella piscina, **quan** es planifica, **aleshores** genera l'avís de canvi de període sense test (RN-029).
- **CA-001-35** — **Donat** un test sense el camp `acceptat`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-36** — **Donat** un fitxer desat pel sistema, **quan** es carrega i es torna a desar, **aleshores** el fitxer resultant és idèntic byte a byte.
- **CA-001-37** — **Donat** un nedador, **quan** es demana esborrar-lo, **aleshores** dona un error que indica que s'ha d'arxivar, i el nedador no canvia (RN-004).
- **CA-001-38** [PENDENT spec 002] — **Donada** una importació que no inclou un nedador existent, **quan** s'importa, **aleshores** el nedador no s'esborra ni s'arxiva (RN-004).
- **CA-001-39** — **Donat** un nedador amb un estil preferent fora de Cr, Esq, Br, Pap i Ei (p. ex. `EP`) o amb un estil repetit, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp i el valor.
- **CA-001-40** — **Donat** un nedador amb un dia d'entrenament no vàlid o repetit, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp i el valor.
- **CA-001-41** — **Donada** una `piscina` diferent de 25 o 50 en una competició, un test o un millor registre, **quan** es carrega, **aleshores** si és en una competició del catàleg, falla TOTA la càrrega; si és en un test o un millor registre, aquell nedador no es carrega; en tots dos casos dona un error que identifica el fitxer, el camp i el valor.
- **CA-001-42** — **Donada** una inscripció o un millor registre amb una prova que no és oficial per a la seva piscina (p. ex. `100 Ei` en piscina de 50 m), **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica la prova i la piscina (RN-030).
- **CA-001-43** — **Donada** una carpeta de temporada amb un nom que no segueix RN-031 (p. ex. `2026-28`), **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica la carpeta.
- **CA-001-44** — **Donat** un nedador amb `correu` buit o només amb espais en blanc, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp (RN-032). Un correu absent o `null` és vàlid (CA-001-107).
- **CA-001-45** — **Donats** dos nedadors existents, un d'ells arxivat, **quan** es crea un nedador nou, **aleshores** rep un id UUID v4 diferent dels dos (RN-002).
- **CA-001-46** — **Donat** un nedador amb un `alias` que no compleix RN-003 (p. ex. `""`, `marc` sense sufix, `Marc_3f2a9c1` o `marc_cognom_3f2a9c1`), **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp.
- **CA-001-47** — **Donada** una competició amb `seu: null`, **quan** es carrega, **aleshores** `data/avisos.jsonl` té una línia nova amb `rn: "RN-009"`, el fitxer, el camp `seu`, la data i hora i `decisio: null`.
- **CA-001-48** — **Donat** un registre d'avisos amb línies, **quan** es registra un avís nou, **aleshores** les línies anteriors es conserven sense canvis.
- **CA-001-49** — **Donat** un nedador amb un test sense `notes` ni `detall_400`, **quan** es carrega i es torna a desar, **aleshores** es carrega sense error ni avís i el fitxer desat té aquests camps a `null`.
- **CA-001-50** — **Donat** un `nedador.json` sense `alias` o amb `alias: null`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp (RN-003).
- **CA-001-51** — **Donat** un nedador amb un `alias` el sufix del qual no coincideix amb el seu id (p. ex. `marc_0000000` en un nedador amb id `3f2a9c1e-…`), **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp (RN-003).
- **CA-001-52** — **Donat** un nedador nou amb la part d'alias `marc` i un id que comença per `3f2a9c1`, **quan** s'executa l'operació d'alta, **aleshores** l'alias generat és `marc_3f2a9c1` (RN-003).
- **CA-001-53** — **Donat** un nedador existent, **quan** es modifica, **aleshores** l'id i l'alias no canvien.
- **CA-001-54** — **Donat** un nedador sense `mobil` o amb `mobil: null`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error de format que identifica el camp.
- **CA-001-57** — **Donat** un nedador amb `canal_preferent: null` o sense el camp, **quan** es carrega, **aleshores** es carrega, genera un avís `RN-035` que identifica l'alias i el camp, es registra a `data/avisos.jsonl` amb `decisio: null` i no demana confirmació.
- **CA-001-58** [PENDENT spec 002] — **Donat** un nedador nou amb `canal_preferent: "whatsapp"` en una importació, **quan** s'importa, **aleshores** dona un error de format que indica l'alias, el camp, el valor i les opcions admeses (`correu`, `mobil`), i el nedador no es desa.
- **CA-001-59** — **Donat** un nedador amb `canal_preferent: "whatsapp"` en un JSON, **quan** es carrega, **aleshores** aquell nedador no es carrega i l'error de format indica l'alias, el camp, el valor i les opcions admeses (`correu`, `mobil`).
- **CA-001-60** — **Donats** dos nedadors, un amb `canal_preferent: "whatsapp"` i l'altre vàlid, **quan** es carreguen tots dos, **aleshores** el nedador vàlid es carrega i l'altre no.
- **CA-001-61** — **Donat** un nedador nou l'alias generat del qual ja existeix, **quan** s'executa l'operació d'alta, **aleshores** el sistema genera un id nou i un alias nou (RN-003).
- **CA-001-62** — **Donat** un nedador nou amb un ERROR (p. ex. `correu: "nedador.example.com"`), **quan** s'executa l'operació d'alta, **aleshores** el nedador no es desa i el missatge indica l'alias, la RN i l'acció que cal fer.
- **CA-001-63** [PENDENT spec 002] — **Donat** un nedador nou amb un AVÍS (p. ex. sense `canal_preferent`), **quan** el coach el confirma explícitament, **aleshores** el nedador es desa i el registre d'avisos té una línia amb `decisio: "confirmat"`.
- **CA-001-64** [PENDENT spec 002] — **Donat** un nedador nou amb un AVÍS, **quan** el coach el rebutja, **aleshores** el nedador no es desa, el registre d'avisos té una línia amb `decisio: "rebutjat"`.
- **CA-001-65** — **Donats** dos nedadors, un d'ells amb un `nedador.json` editat a mà que ja no és vàlid (p. ex. `correu` sense `@`), **quan** es carreguen, **aleshores** aquell nedador no es carrega i l'altre sí.
- **CA-001-66** — **Donats** dos nedadors amb el mateix correu (o el mateix alias) al JSON, **quan** es carreguen, **aleshores** no es carrega cap dels dos i la resta de nedadors sí.
- **CA-001-67** — **Donats** diversos nedadors amb errors i avisos, **quan** es validen, **aleshores** el resultat dona, per a cada nedador, els errors (nivell ERROR) i els avisos (nivell AVÍS) per separat, cadascun amb alias, camp, valor, RN (o «format») i acció.
- **CA-001-68** [PENDENT spec 002] — **Donat** un nedador nou amb l'alias definitiu generat (`marc_3f2a9c1`), **quan** s'importa, **aleshores** el nedador no es desa fins que el coach confirma l'alias (RN-003).
- **CA-001-69** — **Donats** un nedador amb un ERROR en un altre camp (p. ex. `estils_preferents` buit) i un altre nedador amb el mateix correu, tots dos amb el fitxer llegible, **quan** es carreguen, **aleshores** hi ha col·lisió, no es carrega cap dels dos i l'error de col·lisió identifica tots dos (RN-032).
- **CA-001-70** — **Donat** un nedador amb un ERROR en un altre camp i el fitxer llegible, **quan** s'executa l'operació d'alta d'un nedador nou amb el seu correu, **aleshores** dona un ERROR i el nedador nou no es desa (RN-032).
- **CA-001-71** — **Donat** un fitxer de catàleg amb un nom que no segueix RN-031 (p. ex. `2026-28.json`), **quan** es carrega, **aleshores** falla TOTA la càrrega i dona un error que identifica el fitxer.
- **CA-001-72** [PENDENT spec 002] — **Donada** una importació amb un nedador amb un ERROR, **quan** s'importa, **aleshores** aquell nedador no es desa i el flux d'importació en presenta l'error segons la spec 002.
- **CA-001-73** — **Donat** un nedador amb diversos errors (p. ex. `correu` sense `@` i `estils_preferents` buit), **quan** es valida, **aleshores** el resultat els llista tots, cadascun amb alias, camp, valor, RN (o «format») i acció.
- **CA-001-74** — **Donats** diversos nedadors, un d'ells amb un ERROR, **quan** s'executa el filtre, **aleshores** passa per tots, no s'atura al primer error i el nedador amb l'ERROR no es planifica fins que es corregeix.
- **CA-001-75** — **Donat** un fitxer de nedador que no es pot llegir (p. ex. JSON trencat), **quan** s'executa el filtre, **aleshores** dona un ERROR propi que l'identifica per l'UUID de la carpeta, i el fitxer no participa a la unicitat.
- **CA-001-76** — **Donats** dos nedadors amb el mateix alias, un d'ells amb un ERROR en un altre camp, **quan** es valida, **aleshores** hi ha col·lisió i l'error identifica tots dos (RN-003).
- **CA-001-78** — **Donat** un mateix nedador amb un ERROR, **quan** s'entra, es carrega i passa pel filtre, **aleshores** els tres moments en donen el mateix resultat.
- **CA-001-79** — **Donat** un nedador existent, **quan** es modifica `correu` amb el d'un altre nedador, arxivat o no, **aleshores** es torna a validar el nedador sencer, unicitat inclosa, i dona un ERROR (RN-032).
- **CA-001-80** — **Donat** un nedador existent, **quan** es modifica amb un valor que dona un ERROR (p. ex. `volum_setmanal.min > max`), **aleshores** no es desa res i el nedador no canvia.
- **CA-001-81** — **Donat** un nedador arxivat, **quan** es desarxiva, **aleshores** `arxivat` val `false` i la resta del nedador no canvia (RN-017). **Quan** s'arxiva un nedador no arxivat, **aleshores** `arxivat` val `true`.
- **CA-001-82** — **Donat** un test CSS desat, **quan** s'intenta editar, **aleshores** no es permet i el test no canvia; només es pot afegir un test nou o acceptar-lo.
- **CA-001-83** — **Donat** un millor registre desat, **quan** s'afegeix un registre de la mateixa prova i piscina amb un temps menor, **aleshores** s'afegeix a la llista i el desat es conserva (RN-007); **quan** s'afegeix un registre de la mateixa prova a l'altra piscina, **aleshores** s'afegeix sense comparar-lo amb el de la primera, tingui el temps que tingui; **quan** s'intenta editar un registre desat, **aleshores** no es permet.
- **CA-001-84** [PENDENT spec 005] — **Donat** un nedador al qual es canvia `dies_entrenament` o `volum_setmanal` a mitja temporada, **quan** es planifica, **aleshores** es torna a planificar amb la configuració nova i la planificació passada es conserva com a registre (des de quina setmana: ho decideix la spec 005).
- **CA-001-89** — **Donat** un millor registre desat, **quan** s'afegeix un registre de la mateixa prova i piscina amb un temps igual o pitjor, **aleshores** no es fa res: el desat no canvia i no hi ha ni ERROR ni AVÍS (RN-007).
- **CA-001-90** — **Donat** un millor registre sense `competicio`, amb `competicio: null` o amb `competicio: ""`, **quan** es carrega o s'afegeix, **aleshores** aquell nedador no es carrega (o el registre no s'afegeix) i dona un error que identifica el camp (RN-007).
- **CA-001-91** — **Donat** un millor registre amb una `competicio` que no és al catàleg (o amb el catàleg buit), **quan** es carrega, **aleshores** el nedador es carrega, sense error ni avís: la competició és informativa (RN-007).
- **CA-001-92** — **Donats** un nedador amb un `correu` que no és text (p. ex. un número) i un altre nedador amb el mateix alias, **quan** es carreguen, **aleshores** el primer no participa a la unicitat del correu però sí a la de l'alias: no es carrega cap dels dos, l'error d'alias identifica tots dos i el primer té a més un error de format al correu (RN-003, RN-032).
- **CA-001-93** — **Donat** un nedador amb `mobil: ""` o només amb espais, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error de format que identifica el camp.
- **CA-001-96** — **Donats** tres millors registres de la mateixa prova i piscina amb els temps `1:10.00`, `1:08.00` i `1:09.00` en aquest ordre al fitxer, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica la prova i la piscina (RN-007).
- **CA-001-97** — **Donat** un nedador amb tres marques d'una prova i piscina i una altra marca de la mateixa prova a l'altra piscina, **quan** es demana la `marca_vigent` d'aquella prova i piscina, **aleshores** s'obté l'última de la llista d'aquella piscina i la consulta no desa res.
- **CA-001-101** — **Donats** dos nedadors amb el mateix `mobil`, i un altre amb un `mobil` que no té format E.164 (p. ex. `600 00 00 00`), **quan** es carreguen, **aleshores** es carreguen tots, sense error ni avís (ADR-0020).
- **CA-001-102** — **Donat** un millor registre desat amb data D, **quan** s'afegeix un registre de la mateixa prova i piscina amb un temps menor i una data igual o anterior a D, **aleshores** dona un error que identifica la prova i la piscina i la llista no canvia; **quan** es carrega un fitxer amb dues marques de la mateixa prova i piscina on la segona té una data igual o anterior a la de la primera, **aleshores** aquell nedador no es carrega i dona el mateix error (RN-007).
- **CA-001-104** — **Donat** un nedador amb un correu de format bàsic (p. ex. `a@b.c` o `  Pere@Exemple.cat `), **quan** el coach l'entra (alta), el modifica o es carrega, **aleshores** s'accepta i es desa idèntic, amb les majúscules i els espais dels extrems inclosos (RN-032).
- **CA-001-105** — **Donat** un nedador amb un correu sense `@` (`nedador.example.com`), amb `@` sense part local (`@example.com`), amb `@` sense domini (`nedador@`), amb un domini sense punt (`nedador@example`) o amb un espai al mig (`a b@example.com`), **quan** el coach l'entra (alta), el modifica o es carrega, **aleshores** dona un ERROR que identifica el camp i el valor: a l'alta i a la modificació no es desa, a la càrrega aquell nedador no es carrega (RN-032). Un exemple per cas.
- **CA-001-106** — **Donat** un nedador amb un correu amb un error tipogràfic (p. ex. `usari@gmial.com`), **quan** el coach l'entra (alta), el modifica o es carrega, **aleshores** s'accepta i es desa tal qual, sense error ni avís (RN-032).
- **CA-001-107** — **Donat** un nedador sense `correu` (absent o `null`) i amb `canal_preferent: mobil`, **quan** el coach l'entra (alta), el modifica o es carrega, **aleshores** és vàlid, es desa amb `correu: null` i no dona cap error ni avís (RN-032).
- **CA-001-108** — **Donats** dos nedadors amb els correus `A@b.com` i ` a@b.com `, un d'ells arxivat, **quan** es carreguen, o quan el coach dona d'alta o modifica un nedador amb un d'aquests correus mentre l'altre existeix, **aleshores** hi ha col·lisió: a la càrrega no es carrega cap dels dos i l'error identifica tots dos; a l'alta i a la modificació dona un ERROR i no es desa res. El valor desat de cada nedador no canvia (RN-032).
- **CA-001-109** — **Donat** un nedador existent, **quan** el coach en modifica el correu per un valor nou vàlid que no té cap altre nedador (p. ex. `  Nou@Exemple.cat `), **aleshores** es desa tal qual, l'id no canvia i el correu antic queda lliure: un nedador nou el pot fer servir (RN-032, RN-002).
- **CA-001-110** — **Donat** un nedador amb `canal_preferent: correu` i sense `correu`, **quan** el coach l'entra (alta), el modifica o es carrega, **aleshores** genera un AVÍS RN-035 que identifica l'alias i el camp, no bloqueja i, a la càrrega, es registra a `data/avisos.jsonl` amb `decisio: null` (RN-035).
- **CA-001-111** — **Donat** un nedador amb `mobil` que només té un tabulador o un salt de línia, **quan** el coach l'entra (alta), el modifica o es carrega, **aleshores** dona un error de format que identifica el camp: a l'alta i a la modificació no es desa, a la càrrega aquell nedador no es carrega (ADR-0020).