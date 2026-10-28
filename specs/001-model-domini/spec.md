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
- `correu`: obligatori i únic entre tots els nedadors (RN-032). És una dada personal.
- `mobil`: obligatori, en format E.164 (RN-033). Pot ser compartit entre nedadors, amb avís (RN-034). És una dada personal.
- `canal_preferent`: `correu` o `mobil`; qualsevol altre valor és un error de format. Absent o `null`: RN-035.
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
- `millors_registres`: llista de `{estil, distancia, piscina, temps, data, competicio}`.
  - `competicio` és un text lliure, perquè pot ser d'una temporada anterior.
  - Només s'afegeixen registres; pot haver-hi diversos de la mateixa prova i piscina. El millor registre per prova i piscina és un valor derivat (vegeu «Valors derivats»).
  - La prova (`estil`, `distancia`) és oficial per a la `piscina` (RN-030).

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

**Valors derivats (no es desen mai)**
- **Setmana:** setmana ISO 8601 (de dilluns a diumenge), identificada per l'any ISO i el número de setmana.
- CSS i zones.
- Millor registre per prova i piscina: el millor temps de la llista de `millors_registres`.
- Dates d'inici i fi de la temporada (RN-031).
- Proves objectiu.
- Classe de cada prova (s'agafa de la participació).

## Validació: nivells
- **ERROR:** s'incompleix un invariant de format d'aquesta spec o una regla bloquejant.
  - Regles del nedador (aquell nedador queda exclòs): RN-001, RN-003, RN-005, RN-006, RN-011 a RN-016, RN-030 (inscripcions i millors registres), RN-031 (carpeta de temporada), RN-032 i RN-033, i els invariants de format dels fitxers del nedador.
  - Regles del catàleg (falla TOTA la càrrega): RN-008, RN-031 (nom del fitxer) i els invariants de format del catàleg.
- **AVÍS:** RN-009, RN-034 i RN-035. No bloqueja. RN-019 i RN-020 són avisos de planificació.
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
- La unicitat (correu, RN-032; alias, RN-003) i RN-034 es comproven sobre tots els fitxers que es poden llegir, siguin vàlids o no. Una col·lisió identifica tots els nedadors implicats; un ERROR en un altre camp no n'exclou cap de la comprovació. També val per a l'alta.
- Un fitxer que no es pot llegir és un ERROR propi i no participa a la unicitat.

## Modificació del nedador

**Immutables:** `id`, `alias` i `versio_esquema` (aquest només canvia amb una migració). La modificació no els rep com a dada.

**Modificables:** `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament` i `volum_setmanal`.
- Una modificació torna a validar el nedador sencer, unicitat inclosa. Si hi ha un ERROR, no es desa res.
- Canviar `dies_entrenament` o `volum_setmanal` a mitja temporada: la 001 ho permet. La nova planificació és de la spec 005 (CA-001-84).

**Amb operació pròpia:**
- Arxivar i desarxivar: es permeten totes dues (RN-017).
- `tests_css`: només s'hi afegeixen tests. Un test desat no s'edita; el coach l'accepta o no (`acceptat`).
- `millors_registres`: només s'hi afegeixen registres. Un registre desat no s'edita. El millor per prova i piscina és un valor derivat i no es desa.

## Format JSON
- Cada fitxer porta `versio_esquema`.
- Dates en format `AAAA-MM-DD`.
- Temps de registre en format `m:ss.cc` (spec 000).
- Hi ha tres tipus de camp:
  - **Obligatori:** ha de ser-hi amb un valor vàlid. Si falta o és `null`, és error.
  - **Informatiu** (`notes`, `detall_400`, `detall_200` i els seus camps): no intervé en cap regla de planificació. Pot faltar o ser `null`; tots dos casos volen dir «sense valor» i no generen avís.
  - **Opcional amb avís** (`seu`, `canal_preferent`): com un informatiu, però sense valor genera l'avís que indica la spec (RN-009, RN-035).
- En desar, el sistema escriu tots els camps; un camp sense valor s'escriu `null`. No hi ha cap valor per defecte.

## Registre d'avisos
- Tot avís (RN-009, RN-019, RN-020, RN-034, RN-035 i els que defineixin altres specs) s'afegeix a `data/avisos.jsonl`, una línia JSON per avís, amb `data_hora`, `rn`, `fitxer`, `camp`, `valor`, `missatge`, `id_nedador` (o `null`) i `decisio`.
- `decisio` és `confirmat` o `rebutjat` per als avisos d'entrada (la línia s'escriu quan el coach decideix) i `null` per als de càrrega i de planificació.
- RN-034 afegeix una línia per cada nedador afectat, amb el mòbil a `valor`; el `missatge` identifica els altres nedadors que el comparteixen.
- El registre només creix: no s'hi esborra ni s'hi modifica cap línia.
- La data i hora la dona el rellotge del sistema en el moment de registrar l'avís.

## Assumptions
- Un sol coach gestiona totes les dades.
- Els fitxers de `data/` són locals i no es versionen.
- Els fitxers s'editen a mà o els genera la importació (spec 002).
- Spec de model: no té històries d'usuari ni checklist; els criteris d'acceptació són el contracte.
- Fora d'abast d'aquesta versió: la validació del format del correu i la seva verificació.
- El correu i el mòbil són dades personals. Quines dades poden arribar a un LLM ho fixarà l'ADR pendent de l'auditoria G0.
- `data/avisos.jsonl` conté el mòbil (RN-034) i només creix. Com es compleix el dret de supressió (RGPD, art. 17) ho fixa el pendent «ADR de dades personals: supressió» (`docs/estat.md`).

## Clarifications

### Sessions 2026-10-20 a 2026-10-22 (fora de `/speckit-clarify`; detall a l'historial git de la spec)

- P: Què identifica un nedador? → Un id opac, que és el nom de la carpeta (RN-001, RN-002). El correu és una dada de `nedador.json` i és únic (RN-032); l'alias és obligatori (RN-003).
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
- P: Com es defineix la temporada? → De l'1/10 al 30/09 de l'any següent; es deriva del nom de la carpeta (RN-031).
- P: Com s'identifica la persona? → Pel correu, obligatori i únic; no es desen nom ni cognoms (RN-032).
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
- P: Un nedador exclòs per un error compta per a la unicitat? → Sí: continua comptant per a la unicitat de correu i alias (RN-032, RN-003), per a RN-034 i per a l'alta (CA-001-69, 70). Matisada per 2026-10-28 (només compten els fitxers que es poden llegir).
- P: Quin contacte i quin canal preferent? → ADR-0016 substitueix l'ADR-0015. RN-035 és només un avís (`canal_preferent` absent o `null`); un valor no admès és un error de format (CA-001-57 a 59).
- P: Què es pot provar a la 001 de l'alta amb un ERROR? → Que no es desa (CA-001-62). El flux d'importació és el CA-001-72, `[PENDENT spec 002]`.
- P: On es decideix la supressió de dades personals? → Al pendent «ADR de dades personals: supressió» (`docs/estat.md`), quan un nedador ho demani.

### Sessió 2026-10-28 (G1 r2: filtre de validació i modificació)

- N1 — P: Hi ha un validador per a cada moment? → No: un sol validador amb les mateixes regles a l'entrada, a la càrrega i al filtre.
- N1 — P: El filtre s'atura al primer error? → No: passa per tots els nedadors i per tots els camps. Un nedador amb un ERROR no es planifica fins que es corregeix.
- N1 — P: Què dona el resultat? → Per nedador i per camp: alias (o l'UUID de la carpeta si el fitxer no es pot llegir), camp, valor, RN (o «format») i acció.
- N1 — P: Quins fitxers compten per a la unicitat? → Tots els que es poden llegir, vàlids o no (RN-032, RN-003, RN-034). Una col·lisió identifica tots els implicats. Un fitxer il·legible és un ERROR propi i no hi participa.
- N3 — P: Quines dades no canvien mai? → `id`, `alias` i `versio_esquema` (només amb una migració). La modificació no els rep com a dada.
- N3 — P: Què es pot modificar? → `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament` i `volum_setmanal`. La modificació torna a validar el nedador sencer, unicitat inclosa; amb un ERROR no es desa res.
- N3 — P: Quines dades tenen operació pròpia? → Arxivar i desarxivar; `tests_css` (només s'afegeixen; el coach accepta o no); `millors_registres` (només s'afegeixen; el millor per prova i piscina és derivat). Un test o un registre desat no s'edita.
- N3 — P: Es pot canviar `dies_entrenament` o `volum_setmanal` a mitja temporada? → Sí. Replanificar és de la spec 005 (CA-001-84, `[PENDENT spec 005]`).
- N3 — P: Els millors registres s'actualitzen? → No: només s'afegeixen. El millor per prova i piscina és un valor derivat (el millor temps de la llista) i no es desa. RN-007 (unicitat) queda retirada.
- Decisió a — P: Es pot desarxivar? → Sí: un nedador pot tornar una temporada posterior (RN-017).
- Decisió b — P: Es poden canviar `dies_entrenament` i `volum_setmanal` a mitja temporada? → Sí; es torna a planificar amb la configuració nova i la planificació passada es conserva com a registre (CA-001-84, spec 005).
- Decisió c — P: S'editen els tests CSS i els millors registres desats? → No.

## Criteris d'acceptació
- **CA-001-01** — **Donat** un `nedador.json` vàlid, **quan** es carrega i es torna a desar, **aleshores** el contingut desat és equivalent a l'original (mateixos valors; un camp informatiu absent equival a `null`).
- **CA-001-02** — **Donat** un catàleg de competicions i un `inscripcions.json` vàlids, **quan** es carreguen i es tornen a desar, **aleshores** el contingut desat és equivalent a l'original.
- **CA-001-03** — **Donat** un nedador sense estils preferents, sense dies d'entrenament o amb `volum_setmanal.min > max`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp.
- **CA-001-04** — **Donat** un test CSS amb t400 ≤ t200, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error.
- **CA-001-05** — **Donats** dos tests CSS acceptats de la mateixa piscina i un de més recent no acceptat, **quan** es demana el vigent per a aquella piscina, **aleshores** s'obté l'acceptat de data més recent.
- **CA-001-06** — **Donats** dos millors registres amb el mateix estil, distància i piscina, **quan** es carrega, **aleshores** es carrega sense error i el millor registre d'aquella prova i piscina és el de temps menor.
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
- **CA-001-21** — **Donada** una competició del catàleg amb participacions, **quan** s'intenta esborrar, **aleshores** dona un error.
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
- **CA-001-44** — **Donat** un nedador sense `correu`, amb `correu: null`, buit o amb espais, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp (RN-032).
- **CA-001-45** — **Donats** dos nedadors existents, un d'ells arxivat, **quan** es crea un nedador nou, **aleshores** rep un id UUID v4 diferent dels dos (RN-002).
- **CA-001-46** — **Donat** un nedador amb un `alias` que no compleix RN-003 (p. ex. `""`, `marc` sense sufix, `Marc_3f2a9c1` o `marc_cognom_3f2a9c1`), **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp.
- **CA-001-47** — **Donada** una competició amb `seu: null`, **quan** es carrega, **aleshores** `data/avisos.jsonl` té una línia nova amb `rn: "RN-009"`, el fitxer, el camp `seu`, la data i hora i `decisio: null`.
- **CA-001-48** — **Donat** un registre d'avisos amb línies, **quan** es registra un avís nou, **aleshores** les línies anteriors es conserven sense canvis.
- **CA-001-49** — **Donat** un nedador amb un test sense `notes` ni `detall_400`, **quan** es carrega i es torna a desar, **aleshores** es carrega sense error ni avís i el fitxer desat té aquests camps a `null`.
- **CA-001-50** — **Donat** un `nedador.json` sense `alias` o amb `alias: null`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp (RN-003).
- **CA-001-51** — **Donat** un nedador amb un `alias` el sufix del qual no coincideix amb el seu id (p. ex. `marc_0000000` en un nedador amb id `3f2a9c1e-…`), **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp (RN-003).
- **CA-001-52** — **Donat** un nedador nou amb la part d'alias `marc` i un id que comença per `3f2a9c1`, **quan** s'executa l'operació d'alta, **aleshores** l'alias generat és `marc_3f2a9c1` (RN-003).
- **CA-001-53** — **Donat** un nedador existent, **quan** es modifica, **aleshores** l'id i l'alias no canvien.
- **CA-001-54** — **Donat** un nedador sense `mobil` o amb `mobil: null`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp (RN-033).
- **CA-001-55** — **Donat** un nedador amb `mobil` `600000000`, `+34 600 000 000` o `+3460`, **quan** es carrega, **aleshores** aquell nedador no es carrega i dona un error que identifica el camp i el valor (RN-033).
- **CA-001-56** — **Donats** dos nedadors amb el mateix `mobil`, un d'ells arxivat, **quan** es carrega, **aleshores** es carrega sense error i `data/avisos.jsonl` té una línia nova amb `rn: "RN-034"` per a cada nedador, amb el mòbil a `valor` i un `missatge` que identifica els altres nedadors que el comparteixen.
- **CA-001-57** — **Donat** un nedador amb `canal_preferent: null` o sense el camp, **quan** es carrega, **aleshores** es carrega, genera un avís `RN-035` que identifica l'alias i el camp, es registra a `data/avisos.jsonl` amb `decisio: null` i no demana confirmació.
- **CA-001-58** [PENDENT spec 002] — **Donat** un nedador nou amb `canal_preferent: "whatsapp"` en una importació, **quan** s'importa, **aleshores** dona un error de format que indica l'alias, el camp, el valor i les opcions admeses (`correu`, `mobil`), i el nedador no es desa.
- **CA-001-59** — **Donat** un nedador amb `canal_preferent: "whatsapp"` en un JSON, **quan** es carrega, **aleshores** aquell nedador no es carrega i l'error de format indica l'alias, el camp, el valor i les opcions admeses (`correu`, `mobil`).
- **CA-001-60** — **Donats** dos nedadors, un amb `canal_preferent: "whatsapp"` i l'altre vàlid, **quan** es carreguen tots dos, **aleshores** el nedador vàlid es carrega i l'altre no.
- **CA-001-61** — **Donat** un nedador nou l'alias generat del qual ja existeix, **quan** s'executa l'operació d'alta, **aleshores** el sistema genera un id nou i un alias nou (RN-003).
- **CA-001-62** — **Donat** un nedador nou amb un ERROR (p. ex. `mobil: "600000000"`), **quan** s'executa l'operació d'alta, **aleshores** el nedador no es desa i el missatge indica l'alias, la RN i l'acció que cal fer.
- **CA-001-63** [PENDENT spec 002] — **Donat** un nedador nou amb un AVÍS (p. ex. un mòbil compartit amb un altre nedador), **quan** el coach el confirma explícitament, **aleshores** el nedador es desa i el registre d'avisos té una línia amb `decisio: "confirmat"`.
- **CA-001-64** [PENDENT spec 002] — **Donat** un nedador nou amb un AVÍS, **quan** el coach el rebutja, **aleshores** el nedador no es desa, el registre d'avisos té una línia amb `decisio: "rebutjat"`.
- **CA-001-65** — **Donats** dos nedadors, un d'ells amb un `nedador.json` editat a mà que ja no és vàlid (p. ex. `mobil` sense `+`), **quan** es carreguen, **aleshores** aquell nedador no es carrega i l'altre sí.
- **CA-001-66** — **Donats** dos nedadors amb el mateix correu (o el mateix alias) al JSON, **quan** es carreguen, **aleshores** no es carrega cap dels dos i la resta de nedadors sí.
- **CA-001-67** — **Donats** diversos nedadors amb errors i avisos, **quan** es validen, **aleshores** el resultat dona, per a cada nedador, els errors (nivell ERROR) i els avisos (nivell AVÍS) per separat, cadascun amb alias, camp, valor, RN (o «format») i acció.
- **CA-001-68** [PENDENT spec 002] — **Donat** un nedador nou amb l'alias definitiu generat (`marc_3f2a9c1`), **quan** s'importa, **aleshores** el nedador no es desa fins que el coach confirma l'alias (RN-003).
- **CA-001-69** — **Donats** un nedador amb un ERROR en un altre camp (p. ex. `mobil` sense `+`) i un altre nedador amb el mateix correu, tots dos amb el fitxer llegible, **quan** es carreguen, **aleshores** hi ha col·lisió, no es carrega cap dels dos i l'error de col·lisió identifica tots dos (RN-032).
- **CA-001-70** — **Donat** un nedador amb un ERROR en un altre camp i el fitxer llegible, **quan** s'executa l'operació d'alta d'un nedador nou amb el seu correu, **aleshores** dona un ERROR i el nedador nou no es desa (RN-032).
- **CA-001-71** — **Donat** un fitxer de catàleg amb un nom que no segueix RN-031 (p. ex. `2026-28.json`), **quan** es carrega, **aleshores** falla TOTA la càrrega i dona un error que identifica el fitxer.
- **CA-001-72** [PENDENT spec 002] — **Donada** una importació amb un nedador amb un ERROR, **quan** s'importa, **aleshores** aquell nedador no es desa i el flux d'importació en presenta l'error segons la spec 002.
- **CA-001-73** — **Donat** un nedador amb diversos errors (p. ex. `mobil` sense `+` i `estils_preferents` buit), **quan** es valida, **aleshores** el resultat els llista tots, cadascun amb alias, camp, valor, RN (o «format») i acció.
- **CA-001-74** — **Donats** diversos nedadors, un d'ells amb un ERROR, **quan** s'executa el filtre, **aleshores** passa per tots, no s'atura al primer error i el nedador amb l'ERROR no es planifica fins que es corregeix.
- **CA-001-75** — **Donat** un fitxer de nedador que no es pot llegir (p. ex. JSON trencat), **quan** s'executa el filtre, **aleshores** dona un ERROR propi que l'identifica per l'UUID de la carpeta, i el fitxer no participa a la unicitat.
- **CA-001-76** — **Donats** dos nedadors amb el mateix alias, un d'ells amb un ERROR en un altre camp, **quan** es valida, **aleshores** hi ha col·lisió i l'error identifica tots dos (RN-003).
- **CA-001-77** — **Donats** dos nedadors amb el mateix `mobil`, un d'ells amb un ERROR en un altre camp, **quan** es valida, **aleshores** genera l'avís RN-034 per a cada nedador amb el fitxer llegible, amb un `missatge` que identifica els altres (RN-034).
- **CA-001-78** — **Donat** un mateix nedador amb un ERROR, **quan** s'entra, es carrega i passa pel filtre, **aleshores** els tres moments en donen el mateix resultat.
- **CA-001-79** — **Donat** un nedador existent, **quan** es modifica `correu` amb el d'un altre nedador, **aleshores** es torna a validar el nedador sencer, unicitat inclosa, i dona un ERROR (RN-032).
- **CA-001-80** — **Donat** un nedador existent, **quan** es modifica amb un valor que dona un ERROR (p. ex. `volum_setmanal.min > max`), **aleshores** no es desa res i el nedador no canvia.
- **CA-001-81** — **Donat** un nedador arxivat, **quan** es desarxiva, **aleshores** `arxivat` val `false` i la resta del nedador no canvia (RN-017). **Quan** s'arxiva un nedador no arxivat, **aleshores** `arxivat` val `true`.
- **CA-001-82** — **Donat** un test CSS desat, **quan** s'intenta editar, **aleshores** no es permet i el test no canvia; només es pot afegir un test nou o acceptar-lo.
- **CA-001-83** — **Donat** un millor registre desat, **quan** s'afegeix un registre d'una prova que ja en té, **aleshores** el desat es conserva i el nou s'afegeix a la llista; **quan** s'intenta editar un registre desat, **aleshores** no es permet.
- **CA-001-84** [PENDENT spec 005] — **Donat** un nedador al qual es canvia `dies_entrenament` o `volum_setmanal` a mitja temporada, **quan** es planifica, **aleshores** es torna a planificar amb la configuració nova i la planificació passada es conserva com a registre (des de quina setmana: ho decideix la spec 005).