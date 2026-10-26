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
- `nedador.json` té un `alias` obligatori i immutable per a ús del coach a la CLI (RN-003).
- La immutabilitat de l'alias és una regla de gestió: la CLI no ofereix cap manera de canviar-lo. La càrrega no la pot comprovar, perquè el fitxer es pot editar a mà; només comprova que el sufix coincideix amb l'id.

## Entitats

**Nedador** (`nedador.json`)
- `correu`: obligatori i únic entre tots els nedadors (RN-032). És una dada personal.
- `mobil`: obligatori, en format E.164 (RN-033). Pot ser compartit entre nedadors, amb avís (RN-034). És una dada personal.
- `canal_preferent`: `correu`, `mobil` o `null`; informatiu (RN-035).
- `alias`: obligatori, `<part>_<sufix>` (RN-003).
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
  - Unicitat: RN-007.
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
- Dates d'inici i fi de la temporada (RN-031).
- Proves objectiu.
- Classe de cada prova (s'agafa de la participació).

## Validació: dues categories
- **Model vàlid:** compleix els invariants de format d'aquesta spec i les regles de càrrega RN-001, RN-003, RN-005 a RN-008, RN-011 a RN-016 i RN-030 a RN-033. Si no els compleix, error de càrrega.
- **Incidència resoluble:** RN-035. El nedador afectat no avança fins que el coach la resol (§ Incidències resolubles).
- **Apte per planificar:** a més del model vàlid, compleix RN-017 i RN-018. Si no ho és, la planificació queda bloquejada i el missatge indica què falta.
- **Avisos (no bloquegen):** RN-009, RN-019, RN-020, RN-034.

## Format JSON
- Cada fitxer porta `versio_esquema`.
- Dates en format `AAAA-MM-DD`.
- Temps de registre en format `m:ss.cc` (spec 000).
- Hi ha tres tipus de camp:
  - **Obligatori:** ha de ser-hi amb un valor vàlid. Si falta o és `null`, és error.
  - **Informatiu** (`canal_preferent`, `notes`, `detall_400`, `detall_200` i els seus camps): no intervé en cap regla de planificació. Pot faltar o ser `null`; tots dos casos volen dir «sense valor» i no generen avís.
  - **Opcional amb avís** (`seu`): com un informatiu, però sense valor genera l'avís que indica la spec (RN-009).
- En desar, el sistema escriu tots els camps; un camp sense valor s'escriu `null`. No hi ha cap altre valor per defecte.

## Incidències resolubles
- Una incidència resoluble és un valor no vàlid que el coach pot corregir sense editar el fitxer. Aplica a RN-035.
- El domini no corregeix res ni hi posa cap valor per defecte: retorna el fitxer, el camp, el valor i les opcions admeses.
- En mode interactiu, la CLI mostra les opcions al coach: triar un valor admès, deixar el camp sense valor (només si és informatiu) o cancel·lar. El fitxer només s'escriu després que el coach triï i confirmi.
- En mode no interactiu (importació per lots, scripts), la incidència és un error que indica el camp, el valor i les opcions, i el fitxer no es modifica.
- En una operació amb diversos nedadors, la incidència d'un nedador no atura els altres.

## Registre d'avisos
- Tot avís (RN-009, RN-019, RN-020, RN-034 i els que defineixin altres specs) s'afegeix a `data/avisos.jsonl`, una línia JSON per avís, amb `data_hora`, `rn`, `fitxer`, `camp`, `valor`, `missatge` i `id_nedador` (o `null`).
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
- `data/avisos.jsonl` conté el mòbil (RN-034) i només creix. Com es compleix el dret de supressió (RGPD, art. 17) ho fixarà el mateix ADR pendent.

## Clarifications

### Sessions 2026-10-20 a 2026-10-22 (fora de `/speckit-clarify`; detall a l'historial git de la spec)

- P: Què identifica un nedador? → Un id opac, que és el nom de la carpeta (RN-001, RN-002). El correu és una dada de `nedador.json` i és únic (RN-032); l'alias és obligatori (RN-003).
- P: Es pot esborrar un nedador? → No: s'arxiva (RN-004, RN-017).
- P: Es pot planificar un nedador sense test CSS? → Sí: és apte i es genera l'avís «sense ritmes» (CA-001-14).
- P: Quin test CSS s'aplica? → El test vigent: l'últim acceptat de la piscina del període. Registrar-ne un no canvia els ritmes fins que el coach l'accepta.
- P: Qui col·loca la sessió de test CSS al pla? → El coach, a mà; el sistema no ho fa mai (ADR-0011).
- P: Quins camps poden faltar? → Només els informatius (`canal_preferent`, `notes`, `detall_400`, `detall_200` i els seus camps) i `seu`; en desar s'escriuen com a `null` (§ Format JSON).
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

### Sessió 2026-10-25 (esmena: id i alias)

- P: Quin format té l'id del nedador? → UUID v4 en minúscules, generat pel sistema; no es pot endevinar (ADR-0014, RN-001, RN-002).
- P: L'alias és opcional? → No: és obligatori, únic i immutable, amb la forma `<part>_<sufix>`; el sufix són els 7 primers caràcters de l'id i l'afegeix sempre el sistema (RN-003).
- P: Es pot corregir un alias mal escrit? → No: en crear el nedador es mostra l'alias definitiu i es demana confirmació (RN-003).
- P: I si l'alias nou coincideix amb un d'existent? → El sistema genera un id nou i torna a proposar l'alias (RN-003).
- P: Quines dades de contacte té el nedador? → Correu i mòbil, tots dos obligatoris; el correu és únic i el mòbil pot ser compartit, amb avís (ADR-0015, RN-032 a RN-034).
- P: Com s'escriu el mòbil? → En E.164 (`+34…`). Afegir `+34` a un número sense prefix és feina de l'entrada de dades, no de la càrrega (ADR-0015).
- P: Què és `canal_preferent`? → `correu` o `mobil`; informatiu, sense avís si falta. Un valor no admès és una incidència resoluble (RN-035).

## Criteris d'acceptació
- **CA-001-01** — **Donat** un `nedador.json` vàlid, **quan** es carrega i es torna a desar, **aleshores** el contingut desat és equivalent a l'original (mateixos valors; un camp informatiu absent equival a `null`).
- **CA-001-02** — **Donat** un catàleg de competicions i un `inscripcions.json` vàlids, **quan** es carreguen i es tornen a desar, **aleshores** el contingut desat és equivalent a l'original.
- **CA-001-03** — **Donat** un nedador sense estils preferents, sense dies d'entrenament o amb `volum_setmanal.min > max`, **quan** es carrega, **aleshores** dona un error que identifica el camp.
- **CA-001-04** — **Donat** un test CSS amb t400 ≤ t200, **quan** es carrega, **aleshores** dona un error.
- **CA-001-05** — **Donats** dos tests CSS acceptats de la mateixa piscina i un de més recent no acceptat, **quan** es demana el vigent per a aquella piscina, **aleshores** s'obté l'acceptat de data més recent.
- **CA-001-06** — **Donats** dos millors registres amb el mateix estil, distància i piscina, **quan** es carrega, **aleshores** dona un error.
- **CA-001-07** — **Donat** un millor registre amb temps `1:05.3`, **quan** es carrega, **aleshores** dona un error de format.
- **CA-001-08** — **Donada** una participació sense inscripcions, **quan** es carrega, **aleshores** dona un error.
- **CA-001-09** — **Donada** una inscripció amb un dia que no és de la competició, **quan** es carrega, **aleshores** dona un error.
- **CA-001-10** — **Donada** una participació a una competició amb alguna data fora de la temporada del nedador, **quan** es carrega, **aleshores** dona un error.
- **CA-001-11** — **Donats** dos ids de competició repetits al catàleg, **quan** es carrega, **aleshores** dona un error.
- **CA-001-12** — **Donada** una competició amb `seu: null` o sense el camp `seu`, **quan** es carrega, **aleshores** es carrega correctament i genera un avís.
- **CA-001-13** — **Donada** una participació de classe A sense cap inscripció principal, **quan** es valida, **aleshores** genera un avís i no bloqueja la planificació.
- **CA-001-14** — **Donat** un nedador vàlid, no arxivat, sense cap test CSS acceptat i sense ritmes, amb una participació de classe A, **quan** es demana si és apte per planificar, **aleshores** la resposta és «sí» i genera l'avís «sense ritmes».
- **CA-001-15** — **Donat** un nedador sense cap participació de classe A, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «falta competició A».
- **CA-001-16** — **Donat** un nedador amb participacions A, B i C, **quan** es demanen les proves objectiu, **aleshores** s'obtenen només les inscripcions de les participacions A.
- **CA-001-17** — **Donat** un fitxer amb un `versio_esquema` desconegut, **quan** es carrega, **aleshores** dona un error.
- **CA-001-18** — **Donada** una competició en una data qualsevol, **quan** es demana la setmana, **aleshores** es calcula a partir de la data (any ISO + setmana) i no es llegeix del fitxer.
- **CA-001-19** — **Donada** una participació amb un `id_competicio` que no és al catàleg, **quan** es carrega, **aleshores** dona un error.
- **CA-001-20** — **Donats** dos nedadors que participen a la mateixa competició amb classes diferents (A i C), **quan** es carreguen, **aleshores** tots dos són vàlids i cadascun conserva la seva classe.
- **CA-001-21** — **Donada** una competició del catàleg amb participacions, **quan** s'intenta esborrar, **aleshores** dona un error.
- **CA-001-22** — **Donat** un canvi de data d'una competició al catàleg, **quan** es consulten les participacions dels nedadors, **aleshores** totes veuen la data nova.
- **CA-001-23** — **Donat** un nedador amb dues participacions a la mateixa competició, **quan** es carrega, **aleshores** dona un error.
- **CA-001-24** — **Donats** dos nedadors amb el mateix correu, escrit amb majúscules diferents i un d'ells arxivat, **quan** es valida el model, **aleshores** dona un error que identifica els dos ids (RN-032).
- **CA-001-25** — **Donat** un nedador existent, **quan** se'n canvia el correu, **aleshores** l'id no canvia.
- **CA-001-26** — **Donats** dos nedadors amb el mateix `alias`, un d'ells arxivat, **quan** es carrega, **aleshores** dona un error que identifica els dos ids (RN-003).
- **CA-001-27** — **Donada** una carpeta de nedador amb un nom que no compleix RN-001 (p. ex. `n0001`, `3F2A9C1E-7B4D-4E8A-9C2F-1D6B5E0A8F47` o un UUID v1), **quan** es carrega, **aleshores** dona un error.
- **CA-001-28** — **Donat** un nedador arxivat, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «arxivat».
- **CA-001-29** — **Donada** una participació amb la mateixa prova inscrita en dos dies diferents de la competició, **quan** es carrega, **aleshores** dona un error (RN-016).
- **CA-001-30** — **Donat** un nedador amb un test acceptat vigent, **quan** es registra un test nou de la mateixa piscina, **aleshores** el test nou té `acceptat: false` i el vigent no canvia; **quan** el coach l'accepta, **aleshores** el test nou passa a ser el vigent.
- **CA-001-31** — **Donat** un test amb `detall_400` i `detall_200` amb tots els camps a `null`, **quan** es carrega i es torna a desar, **aleshores** el contingut desat és equivalent a l'original i els `null` es conserven.
- **CA-001-32** — **Donat** un test amb `notes` i tots els camps de detall a `null`, **quan** es carrega, **aleshores** no genera cap avís (principi V).
- **CA-001-33** [PENDENT spec 004] — **Donat** un nedador amb l'últim test acceptat d'una piscina més antic que el termini de RN-028 i cap test planificat d'aquella piscina, **quan** es planifica, **aleshores** genera l'avís de test caducat (RN-028).
- **CA-001-34** [PENDENT spec 004] — **Donat** un període de piscina que comença sense cap test acceptat ni planificat d'aquella piscina, **quan** es planifica, **aleshores** genera l'avís de canvi de període sense test (RN-029).
- **CA-001-35** — **Donat** un test sense el camp `acceptat`, **quan** es carrega, **aleshores** dona un error de càrrega.
- **CA-001-36** — **Donat** un fitxer desat pel sistema, **quan** es carrega i es torna a desar, **aleshores** el fitxer resultant és idèntic byte a byte.
- **CA-001-37** — **Donat** un nedador, **quan** es demana esborrar-lo, **aleshores** dona un error que indica que s'ha d'arxivar, i el nedador no canvia (RN-004).
- **CA-001-38** [PENDENT spec 002] — **Donada** una importació que no inclou un nedador existent, **quan** s'importa, **aleshores** el nedador no s'esborra ni s'arxiva (RN-004).
- **CA-001-39** — **Donat** un nedador amb un estil preferent fora de Cr, Esq, Br, Pap i Ei (p. ex. `EP`) o amb un estil repetit, **quan** es carrega, **aleshores** dona un error que identifica el camp i el valor.
- **CA-001-40** — **Donat** un nedador amb un dia d'entrenament no vàlid o repetit, **quan** es carrega, **aleshores** dona un error que identifica el camp i el valor.
- **CA-001-41** — **Donada** una `piscina` diferent de 25 o 50 en una competició, un test o un millor registre, **quan** es carrega, **aleshores** dona un error que identifica el fitxer, el camp i el valor.
- **CA-001-42** — **Donada** una inscripció o un millor registre amb una prova que no és oficial per a la seva piscina (p. ex. `100 Ei` en piscina de 50 m), **quan** es carrega, **aleshores** dona un error que identifica la prova i la piscina (RN-030).
- **CA-001-43** — **Donada** una carpeta de temporada amb un nom que no segueix RN-031 (p. ex. `2026-28`), **quan** es carrega, **aleshores** dona un error que identifica la carpeta.
- **CA-001-44** — **Donat** un nedador sense `correu`, amb `correu: null`, buit o amb espais, **quan** es carrega, **aleshores** dona un error que identifica el camp (RN-032).
- **CA-001-45** — **Donats** dos nedadors existents, un d'ells arxivat, **quan** es crea un nedador nou, **aleshores** rep un id UUID v4 diferent dels dos (RN-002).
- **CA-001-46** — **Donat** un nedador amb un `alias` que no compleix RN-003 (p. ex. `""`, `marc` sense sufix, `Marc_3f2a9c1` o `marc_cognom_3f2a9c1`), **quan** es carrega, **aleshores** dona un error que identifica el camp.
- **CA-001-47** — **Donada** una competició amb `seu: null`, **quan** es carrega, **aleshores** `data/avisos.jsonl` té una línia nova amb `rn: "RN-009"`, el fitxer, el camp `seu` i la data i hora.
- **CA-001-48** — **Donat** un registre d'avisos amb línies, **quan** es registra un avís nou, **aleshores** les línies anteriors es conserven sense canvis.
- **CA-001-49** — **Donat** un nedador amb un test sense `notes` ni `detall_400`, **quan** es carrega i es torna a desar, **aleshores** es carrega sense error ni avís i el fitxer desat té aquests camps a `null`.
- **CA-001-50** — **Donat** un `nedador.json` sense `alias` o amb `alias: null`, **quan** es carrega, **aleshores** dona un error que identifica el camp (RN-003).
- **CA-001-51** — **Donat** un nedador amb un `alias` el sufix del qual no coincideix amb el seu id (p. ex. `marc_0000000` en un nedador amb id `3f2a9c1e-…`), **quan** es carrega, **aleshores** dona un error que identifica el camp (RN-003).
- **CA-001-52** — **Donat** un nedador nou amb la part d'alias `marc` i un id que comença per `3f2a9c1`, **quan** es crea, **aleshores** l'alias proposat és `marc_3f2a9c1` i el nedador no es desa fins que el coach el confirma (RN-003).
- **CA-001-53** — **Donat** un nedador existent, **quan** se'n vol canviar l'`alias` des de la CLI, **aleshores** dona un error (RN-003).
- **CA-001-54** — **Donat** un nedador sense `mobil` o amb `mobil: null`, **quan** es carrega, **aleshores** dona un error que identifica el camp (RN-033).
- **CA-001-55** — **Donat** un nedador amb `mobil` `600000000`, `+34 600 000 000` o `+3460`, **quan** es carrega, **aleshores** dona un error que identifica el camp i el valor (RN-033).
- **CA-001-56** — **Donats** dos nedadors amb el mateix `mobil`, un d'ells arxivat, **quan** es carrega, **aleshores** es carrega sense error i `data/avisos.jsonl` té una línia nova amb `rn: "RN-034"` per a cada nedador, amb el mòbil a `valor`.
- **CA-001-57** — **Donat** un nedador amb `canal_preferent: null` o sense el camp, **quan** es carrega, **aleshores** es carrega sense error i sense cap avís.
- **CA-001-58** — **Donat** un nedador amb `canal_preferent: "whatsapp"`, **quan** es carrega en mode interactiu, **aleshores** la CLI ofereix triar `correu` o `mobil`, deixar-lo sense valor o cancel·lar, i el fitxer no canvia fins que el coach confirma (RN-035).
- **CA-001-59** — **Donat** un nedador amb `canal_preferent: "whatsapp"`, **quan** es carrega en mode no interactiu, **aleshores** dona un error que indica el camp, el valor i les opcions, i el fitxer no canvia (RN-035).
- **CA-001-60** — **Donats** dos nedadors, un amb `canal_preferent: "whatsapp"` i l'altre vàlid, **quan** es carreguen tots dos, **aleshores** el nedador vàlid es carrega i només l'altre queda pendent (RN-035).
- **CA-001-61** — **Donat** un nedador nou l'alias proposat del qual ja existeix, **quan** es crea, **aleshores** el sistema genera un id nou i proposa un alias nou abans de demanar confirmació (RN-003).
