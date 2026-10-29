# Regles de negoci

Font única de les regles de negoci (constitució, principi III). Les specs, els plans i el codi s'hi refereixen per ID i no en repeteixen el contingut.

- **Frontera:** si el coach podria voler canviar-ho, és una regla (RN); si és estructura de dades, és model i va a la spec.
- **Identificadors:** `RN-NNN`. No es reutilitzen; una regla que deixa de valer es marca «Retirada».
- **Tipus:** bloquejant · avís · judici LLM. Una regla bloquejant dona el nivell ERROR i una d'avís, el nivell AVÍS (spec 001, § Validació).
- **Moment:** càrrega · gestió (crear, modificar, arxivar) · importació · planificació · composició · render.
- **Coherència:** abans d'acceptar una regla, es comprova contra les existents (duplicats, contradiccions, solapaments) i el resultat s'escriu a la regla.
- Tota regla de tipus judici LLM indica, a més, **Entrades**, **Sortida esperada** i **Comprovació determinista** (principi IV).

## Índex

| ID | Regla | Tipus | Moment | Font |
|---|---|---|---|---|
| RN-001 | Format de l'id del nedador | bloquejant | càrrega | spec 001 |
| RN-002 | Assignació i immutabilitat de l'id | bloquejant | gestió | spec 001 |
| RN-003 | Alias del nedador | bloquejant | càrrega, gestió, importació | spec 001 |
| RN-004 | Els nedadors no s'esborren | bloquejant | gestió | spec 001 |
| RN-005 | Rang de volum setmanal | bloquejant | càrrega | spec 001 |
| RN-006 | Coherència del test CSS | bloquejant | càrrega | spec 001 |
| RN-007 | Un millor registre per prova i piscina | bloquejant | càrrega, gestió | spec 001 |
| RN-008 | Unicitat de l'id de competició | bloquejant | càrrega | spec 001, ADR-0006 |
| RN-009 | Seu desconeguda | avís | càrrega | spec 001 |
| RN-010 | Competició amb participacions | bloquejant | gestió | ADR-0006 |
| RN-011 | Participació d'una competició del catàleg | bloquejant | càrrega | spec 001, ADR-0006 |
| RN-012 | Una participació per competició | bloquejant | càrrega | spec 001 |
| RN-013 | Competició dins de la temporada | bloquejant | càrrega | spec 001 |
| RN-014 | Inscripcions d'una participació | bloquejant | càrrega | spec 001 |
| RN-015 | Dia de la inscripció | bloquejant | càrrega | spec 001 |
| RN-016 | Una inscripció per prova i competició | bloquejant | càrrega | spec 001 |
| RN-017 | Nedador arxivat | bloquejant | planificació | spec 001 |
| RN-018 | Competició A obligatòria | bloquejant | planificació | spec 001 |
| RN-019 | Participació A sense prova principal | avís | planificació | spec 001 |
| RN-020 | Sense ritmes | avís | planificació | spec 001 |
| RN-021 | Cobertura de la biblioteca de tècnica | bloquejant | planificació | ADR-0005 |
| RN-022 | La importació no modifica plans | avís | importació | ADR-0013 |
| RN-023 | Sèrie per zona i descans | bloquejant | composició | ADR-0008, spec 000 |
| RN-024 | Ràtio treball:descans | bloquejant | composició | ADR-0008, spec 000 |
| RN-025 | Ordre de les parts de la sessió | bloquejant | composició | ADR-0004, ADR-0011 |
| RN-026 | Una sola part de tècnica | bloquejant | composició | ADR-0005, ADR-0011 |
| RN-027 | Ús de «Màx» | bloquejant | càrrega, composició | spec 000 |
| RN-028 | Test caducat | avís | planificació | spec 004 |
| RN-029 | Canvi de període de piscina sense test | avís | planificació | spec 004 |
| RN-030 | Prova oficial segons la piscina | bloquejant | càrrega | spec 001 |
| RN-031 | Temporada de natació | bloquejant | càrrega | spec 001 |
| RN-032 | Correu del nedador | bloquejant | càrrega, gestió | spec 001, ADR-0017 |
| RN-033 | Mòbil del nedador (Retirada) | — | — | ADR-0017 |
| RN-034 | Mòbil compartit (Retirada) | — | — | ADR-0017 |
| RN-035 | Canal preferent absent | avís | càrrega, importació | spec 001, ADR-0017 |

## Nedador

### RN-001 — Format de l'id del nedador
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** el nom de la carpeta del nedador és el seu id i és un UUID v4 en forma canònica en minúscules.
- **Missatge:** identifica la carpeta.
- **Font:** spec 001, ADR-0014.
- **Coherència:** revisada contra RN-002 i RN-003; sense conflicte.

### RN-002 — Assignació i immutabilitat de l'id
- **Tipus:** bloquejant · **Moment:** gestió
- **Regla:** l'id el genera el sistema en crear el nedador: un UUID v4 aleatori, diferent de tots els existents (arxivats inclosos). Un id no canvia mai (tampoc quan canvia el correu) i no es reutilitza.
- **Font:** spec 001, ADR-0014.
- **Coherència:** revisada contra RN-001 i RN-004. Com que no s'esborra cap nedador (RN-004), la comprovació contra els existents garanteix que no es reutilitza.

### RN-003 — Alias del nedador
- **Tipus:** bloquejant · **Moment:** càrrega, gestió, importació
- **Regla:** l'alias és obligatori, únic entre tots els nedadors (arxivats inclosos) i immutable. Té la forma `<part>_<sufix>`: `<part>` l'escull el coach i és `[a-z0-9-]` de 2 a 12 caràcters; `<sufix>` són els 7 primers caràcters de l'id del nedador i l'afegeix sempre el sistema. Longitud màxima: 20 caràcters. En crear el nedador, el sistema genera l'id i l'alias definitiu; si l'alias ja existeix, genera un id nou i un altre alias. Cap operació permet canviar l'alias; la càrrega només comprova que el sufix coincideix amb l'id. Confirmació del coach (moment: importació, spec 002): el nedador no es desa fins que el coach confirma l'alias definitiu. Només es fa servir perquè el coach identifiqui el nedador: no apareix en rutes, noms de fitxer, sortides ni prompts de l'LLM.
- **Missatge:** identifica l'alias i, si està repetit, els nedadors que el tenen.
- **Font:** spec 001, ADR-0014.
- **Coherència:** revisada contra RN-001, RN-002 i RN-004. Un alias (màxim 20 caràcters) no pot tenir la forma d'un id (36 caràcters). El sufix deriva de l'id, que és immutable (RN-002), i com que els nedadors no s'esborren (RN-004) l'alias no es reutilitza. El sufix es desa dins de l'alias tot i derivar-se de l'id (principi V): és una definició derivada de l'id, que no canvia mai, i no un paràmetre ajustable; la càrrega en comprova la coherència. Sense conflicte.

### RN-004 — Els nedadors no s'esborren
- **Tipus:** bloquejant · **Moment:** gestió
- **Regla:** un nedador no es pot esborrar; s'arxiva.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-002 i RN-017; sense conflicte.

### RN-005 — Rang de volum setmanal
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** el volum setmanal compleix 0 < min ≤ max.
- **Missatge:** identifica el camp.
- **Font:** spec 001.
- **Coherència:** sense regles relacionades.

### RN-006 — Coherència del test CSS
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** a cada test CSS, t400 > t200.
- **Missatge:** identifica el test.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-020; un test incoherent no compta com a test. Sense conflicte.

### RN-007 — Un millor registre per prova i piscina
- **Tipus:** bloquejant · **Moment:** càrrega, gestió
- **Regla:** `millors_registres` té com a màxim un registre per prova (`{estil, distancia}`) i piscina, i és sempre de competició: `competicio` és obligatori i és l'id d'una competició del catàleg (qualsevol temporada), amb la mateixa piscina que el registre (si no, ERROR). En afegir-ne un d'una prova i piscina que ja en té, si el temps és menor que el desat, el substitueix; si és igual o pitjor, no es fa res (ni error ni avís). Dos registres de la mateixa prova i piscina en un fitxer són un ERROR. Els tests CSS no segueixen aquesta regla: es desen tots, per estudiar-ne l'evolució.
- **Missatge:** identifica la prova i la piscina (o el camp `competicio` i el valor).
- **Font:** spec 001.
- **Coherència:** revisada contra RN-006 (els tests CSS no es substitueixen) i RN-030 (la prova ha de ser oficial). Estat: reinstaurada el 2026-10-29 amb el contingut esmenat; havia estat retirada el 2026-10-28 (G1 r2) quan el millor registre era derivat. Sense conflicte.

### RN-032 — Correu del nedador
- **Tipus:** bloquejant · **Moment:** càrrega, gestió
- **Regla:** tot nedador té un `correu` obligatori, únic entre tots els nedadors (arxivats inclosos) i intransferible. Es normalitza (sense espais als extrems, en minúscules) abans de validar-lo i de desar-lo. Format (ERROR): exactament una «@», part local no buida, domini amb almenys un punt i un TLD de 2 lletres o més, sense espais, 254 caràcters com a màxim. És una regla simple al domini, sense llibreries externes. Es pot modificar (l'id no canvia, RN-002): el correu nou passa format i unicitat, i l'antic queda lliure.
- **Missatge:** identifica el camp i el valor, o els ids dels nedadors que comparteixen correu.
- **Font:** spec 001, ADR-0017.
- **Coherència:** revisada contra RN-002 (l'id no depèn del correu i no canvia quan el correu canvia), RN-003 (l'alias és un identificador a part) i RN-004 (els arxivats compten). La unicitat només s'aplica a correu i alias. Sense conflicte.

### RN-033 — Mòbil del nedador (Retirada)
- **Estat:** Retirada (ADR-0017, 2026-10-29). El `mobil` no té format, unicitat ni avís. No es reutilitza l'ID.

### RN-034 — Mòbil compartit (Retirada)
- **Estat:** Retirada (ADR-0017, 2026-10-29). Compartir el `mobil` entre nedadors no genera cap avís. No es reutilitza l'ID.

### RN-035 — Canal preferent absent
- **Tipus:** avís · **Moment:** càrrega, importació
- **Regla:** un `canal_preferent` absent o `null` genera un avís. No bloqueja. Un valor fora de `correu` i `mobil` no és d'aquesta regla: és un error de format del camp (spec 001, § Entitats).
- **Missatge:** identifica l'alias i el camp.
- **Font:** spec 001, ADR-0017.
- **Coherència:** revisada contra RN-032: `correu` i `mobil` són obligatoris, de manera que tots dos canals existeixen sempre i qualsevol valor admès és utilitzable. No hi ha cap valor per defecte (principi V). Sense conflicte.

## Catàleg de competicions

### RN-008 — Unicitat de l'id de competició
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** l'id de cada competició és únic dins del catàleg de la temporada.
- **Missatge:** identifica l'id repetit.
- **Font:** spec 001, ADR-0006.
- **Coherència:** revisada contra RN-011; sense conflicte.

### RN-009 — Seu desconeguda
- **Tipus:** avís · **Moment:** càrrega
- **Regla:** una competició amb la seu desconeguda es carrega amb `seu: null` i genera un avís.
- **Missatge:** identifica la competició.
- **Font:** spec 001.
- **Coherència:** aplica el principi V de la constitució; sense conflicte.

### RN-010 — Competició amb participacions
- **Tipus:** bloquejant · **Moment:** gestió
- **Regla:** no es pot esborrar una competició del catàleg que tingui participacions (inscripcions) ni que sigui referenciada per un millor registre d'algun nedador.
- **Missatge:** identifica els nedadors afectats.
- **Font:** ADR-0006, spec 001 (esmena 2026-10-29).
- **Coherència:** revisada contra RN-011 i RN-007; garanteix que cap participació ni cap millor registre no queda òrfena. Sense conflicte.

## Inscripcions

### RN-011 — Participació d'una competició del catàleg
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** cada participació apunta a una competició que existeix al catàleg de la mateixa temporada.
- **Missatge:** identifica l'`id_competicio`.
- **Font:** spec 001, ADR-0006.
- **Coherència:** revisada contra RN-008 i RN-010; sense conflicte.

### RN-012 — Una participació per competició
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** un nedador té com a màxim una participació a cada competició.
- **Missatge:** identifica la competició.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-016; RN-012 actua sobre participacions i RN-016 sobre inscripcions dins d'una participació. Sense solapament.

### RN-013 — Competició dins de la temporada
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** totes les dates de la competició d'una participació cauen dins de la temporada del nedador.
- **Missatge:** identifica la competició i la data fora de la temporada.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-015; sense conflicte.

### RN-014 — Inscripcions d'una participació
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** una participació té una o més inscripcions. El sistema no controla el nombre màxim d'inscripcions: el límit és per competició i el controla la federació en el moment de la inscripció.
- **Missatge:** identifica la participació.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-016 i RN-019. RN-014 exigeix alguna inscripció i no en limita el nombre; RN-016 n'impedeix la repetició; RN-019 avisa si cap no és principal. Sense solapament.

### RN-015 — Dia de la inscripció
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** el dia de cada inscripció és una de les dates de la competició.
- **Missatge:** identifica la inscripció i el dia.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-013; sense conflicte.

### RN-016 — Una inscripció per prova i competició
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** un nedador no es pot inscriure dues vegades a la mateixa prova (`{distancia, estil}`) d'una competició, sigui el mateix dia o un altre.
- **Missatge:** identifica la prova i els dies de les inscripcions repetides.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-012 i RN-014. Com que RN-012 admet una sola participació per competició, n'hi ha prou de comprovar-la dins de cada participació. Sense conflicte.

### RN-030 — Prova oficial segons la piscina
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** la prova d'una inscripció o d'un millor registre és una prova individual oficial per a la piscina:
  - Cr: 50, 100, 200, 400, 800 i 1500, a 25 m i a 50 m. La prova d'estil lliure s'identifica amb `Cr`.
  - Esq, Br i Pap: 50, 100 i 200, a 25 m i a 50 m.
  - Ei: 100 només a 25 m; 200 i 400 a 25 m i a 50 m.
- **Missatge:** identifica la prova i la piscina.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-014, RN-015 i RN-016. Els relleus no es modelen (spec 000). Sense conflicte.

### RN-031 — Temporada de natació
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** la temporada `AAAA-AA` va de l'1 d'octubre d'`AAAA` al 30 de setembre de l'any següent; `AA` són els dos últims dígits de l'any següent. La carpeta de temporada del nedador i el catàleg de competicions segueixen aquest nom.
- **Missatge:** identifica la carpeta o el fitxer.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-013, que calcula la temporada del nedador amb aquesta regla. Sense conflicte.

## Aptitud per planificar

### RN-017 — Nedador arxivat
- **Tipus:** bloquejant · **Moment:** planificació
- **Regla:** un nedador arxivat no és apte per planificar.
- **Missatge:** «arxivat».
- **Font:** spec 001.
- **Coherència:** revisada contra RN-004 i RN-018; sense conflicte.

### RN-018 — Competició A obligatòria
- **Tipus:** bloquejant · **Moment:** planificació
- **Regla:** per ser apte per planificar, el nedador té com a mínim una participació de classe A.
- **Missatge:** «falta competició A».
- **Font:** spec 001.
- **Coherència:** revisada contra RN-017, RN-019, RN-020 i RN-021. És l'única condició de contingut per ser apte; RN-019 i RN-020 no bloquegen. Sense conflicte.

### RN-019 — Participació A sense prova principal
- **Tipus:** avís · **Moment:** planificació
- **Regla:** una participació de classe A sense cap inscripció principal genera un avís i no bloqueja la planificació.
- **Missatge:** identifica la participació.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-014 i RN-018; sense conflicte.

### RN-020 — Sense ritmes
- **Tipus:** avís · **Moment:** planificació
- **Regla:** un nedador sense cap test CSS acceptat i sense ritmes introduïts pel coach és apte per planificar i genera un avís. El format dels ritmes introduïts pel coach és de la spec 004.
- **Missatge:** «sense ritmes».
- **Font:** spec 001.
- **Coherència:** revisada contra RN-006, RN-018, RN-023 i RN-029. RN-023 fa que la planificació no depengui dels ritmes. Si el nedador té ritmes d'una altra piscina, RN-020 no salta i RN-029 sí: és el comportament volgut. Sense conflicte.

### RN-021 — Cobertura de la biblioteca de tècnica
- **Tipus:** bloquejant · **Moment:** planificació
- **Regla:** abans de planificar un nedador, la biblioteca de tècnica té exercicis per a cada estil de les seves proves objectiu (derivades de les participacions de classe A). L'estil preferent no hi intervé.
- **Missatge:** identifica els estils sense exercicis.
- **Font:** ADR-0005.
- **Coherència:** revisada contra RN-018; sense proves objectiu no s'arriba a aplicar. Sense conflicte.

## Importació

### RN-022 — La importació no modifica plans
- **Tipus:** avís · **Moment:** importació
- **Regla:** la importació no modifica mai un pla. Si un canvi importat afecta un pla existent, el sistema avisa.
- **Missatge:** identifica el pla afectat i el canvi.
- **Font:** ADR-0013.
- **Coherència:** aplica el principi VI de la constitució; sense conflicte.

## Composició de sessions

### RN-023 — Sèrie per zona i descans
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** tota sèrie que genera el sistema porta una zona de l'escala, o trams, i un descans de tipus `d/`. No porta mai AeM, `c/`, ritme ni temps. L'única excepció són els principals de la sessió de test CSS (RN-027).
- **Font:** ADR-0008, spec 000.
- **Coherència:** revisada contra RN-024 i RN-027; `d/×N` és una forma de `d/` (spec 000, §3), i AeM i `c/` només poden venir de dades importades. Sense conflicte.

### RN-024 — Ràtio treball:descans
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** el descans `d/×N` només s'admet a TOLA, MPLA i Vel. En una sèrie amb trams, s'admet si algun tram és a TOLA, MPLA o Vel; si no, el descans és `d/m:ss`.
- **Font:** ADR-0008, spec 000.
- **Coherència:** revisada contra RN-023; sense conflicte.

### RN-025 — Ordre de les parts de la sessió
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** la sessió segueix l'ordre de parts de l'ADR-0004. El principal II és opcional. La sessió de test CSS no té tècnica (ADR-0011).
- **Font:** ADR-0004, ADR-0011.
- **Coherència:** revisada contra RN-026; sense conflicte.

### RN-026 — Una sola part de tècnica
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** a les sessions d'entrenament, la tècnica és una sola part i no es desdobla. Els exercicis els defineix el coach. La sessió de test CSS no té tècnica.
- **Font:** ADR-0005, ADR-0011.
- **Coherència:** revisada contra RN-025; sense conflicte.

### RN-027 — Ús de «Màx»
- **Tipus:** bloquejant · **Moment:** càrrega, composició
- **Regla:** «Màx» només és vàlid dins d'una seqüència AeM (dades importades) i als principals de la sessió de test CSS. Fora d'aquests casos, la sèrie és invàlida.
- **Missatge:** identifica la sèrie.
- **Font:** spec 000.
- **Coherència:** revisada contra RN-023 i RN-025; sense conflicte.

## Test CSS

### RN-028 — Test caducat
- **Tipus:** avís · **Moment:** planificació
- **Regla:** han passat 8 setmanes des de l'últim test acceptat d'una piscina i no hi ha cap test planificat d'aquella piscina.
- **Missatge:** identifica la piscina i la data de l'últim test acceptat.
- **Font:** spec 004 (pendent).
- **Coherència:** revisada contra RN-020 i RN-029. Sense cap test acceptat, salta RN-020 i RN-028 no s'aplica. Sense solapament.

### RN-029 — Canvi de període de piscina sense test
- **Tipus:** avís · **Moment:** planificació
- **Regla:** un període de piscina (25 m o 50 m) comença i el nedador no té cap test acceptat ni planificat d'aquella piscina.
- **Missatge:** identifica el període i la piscina.
- **Font:** spec 004 (pendent). La definició de període de piscina està pendent (mapa, pregunta 9).
- **Coherència:** revisada contra RN-020 i RN-028. RN-029 mira l'inici del període i RN-028, el temps des de l'últim test. Poden saltar juntes sense contradir-se.
