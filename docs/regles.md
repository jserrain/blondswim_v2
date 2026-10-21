# Regles de negoci

Font única de les regles de negoci (constitució, principi III). Les specs, els plans i el codi s'hi refereixen per ID i no en repeteixen el contingut.

- **Frontera:** si el coach podria voler canviar-ho, és una regla (RN); si és estructura de dades, és model i va a la spec.
- **Identificadors:** `RN-NNN`. No es reutilitzen; una regla que deixa de valer es marca «Retirada».
- **Tipus:** bloquejant · avís · judici LLM.
- **Moment:** càrrega · gestió (crear, modificar, arxivar) · importació · planificació · composició · render.
- **Coherència:** abans d'acceptar una regla, es comprova contra les existents (duplicats, contradiccions, solapaments) i el resultat s'escriu a la regla.
- Tota regla de tipus judici LLM indica, a més, **Entrades**, **Sortida esperada** i **Comprovació determinista** (principi IV).

## Índex

| ID | Regla | Tipus | Moment | Font |
|---|---|---|---|---|
| RN-001 | Format de l'id del nedador | bloquejant | càrrega | spec 001 |
| RN-002 | Assignació i immutabilitat de l'id | bloquejant | gestió | spec 001 |
| RN-003 | Alias del nedador | bloquejant | càrrega | spec 001 |
| RN-004 | Els nedadors no s'esborren | bloquejant | gestió | spec 001 |
| RN-005 | Rang de volum setmanal | bloquejant | càrrega | spec 001 |
| RN-006 | Coherència del test CSS | bloquejant | càrrega | spec 001 |
| RN-007 | Unicitat dels millors registres | bloquejant | càrrega | spec 001 |
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
| RN-022 | La importació no modifica plans | avís | importació | ADR-0007 |
| RN-023 | Sèrie per zona i descans | bloquejant | composició | ADR-0008 |
| RN-024 | Ràtio treball:descans | bloquejant | composició | ADR-0008, spec 000 |
| RN-025 | Ordre de les parts de la sessió | bloquejant | composició | ADR-0004 |
| RN-026 | Una sola part de tècnica | bloquejant | composició | ADR-0005 |

## Nedador

### RN-001 — Format de l'id del nedador
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** el nom de la carpeta del nedador és el seu id i té el format `n` + 4 dígits.
- **Missatge:** identifica la carpeta.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-002 i RN-003; sense conflicte.

### RN-002 — Assignació i immutabilitat de l'id
- **Tipus:** bloquejant · **Moment:** gestió
- **Regla:** l'id l'assigna el sistema en crear el nedador: el més alt existent (arxivats inclosos) + 1. Un id no canvia mai (tampoc quan canvia el nom) i no es reutilitza.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-001 i RN-004. Que no es reutilitzi depèn de RN-004: com que no s'esborra cap nedador, el més alt existent és sempre el més alt assignat.

### RN-003 — Alias del nedador
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** l'alias és opcional. Si hi és, és únic entre tots els nedadors, només conté `[a-z0-9-]`, té de 2 a 20 caràcters i no té la forma d'un id (`n` + 4 dígits).
- **Missatge:** identifica l'alias i, si està repetit, els nedadors que el tenen.
- **Font:** spec 001.
- **Coherència:** revisada contra RN-001; la restricció de forma evita que un alias es confongui amb un id. Sense conflicte.

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
- **Coherència:** revisada contra RN-020; un test incoherent no es carrega i no compta com a test. Sense conflicte.

### RN-007 — Unicitat dels millors registres
- **Tipus:** bloquejant · **Moment:** càrrega
- **Regla:** per a cada combinació d'estil, distància i piscina hi ha com a màxim un millor registre.
- **Missatge:** identifica la combinació repetida.
- **Font:** spec 001.
- **Coherència:** sense regles relacionades.

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
- **Regla:** no es pot esborrar una competició del catàleg que tingui participacions.
- **Missatge:** identifica els nedadors que hi participen.
- **Font:** ADR-0006.
- **Coherència:** revisada contra RN-011; garanteix que cap participació no queda òrfena. Sense conflicte.

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
- **Regla:** un nedador sense cap test CSS i sense ritmes introduïts pel coach és apte per planificar i genera un avís. El format dels ritmes introduïts pel coach és de la spec 004.
- **Missatge:** «sense ritmes».
- **Font:** spec 001.
- **Coherència:** revisada contra RN-006, RN-018 i RN-023; RN-023 fa que la planificació no depengui dels ritmes. Sense conflicte.

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
- **Font:** ADR-0007.
- **Coherència:** aplica el principi VI de la constitució; sense conflicte.

## Composició de sessions

### RN-023 — Sèrie per zona i descans
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** tota sèrie que genera el sistema porta una zona i un descans de tipus `d/`, i no porta cap ritme ni cap temps.
- **Font:** ADR-0008.
- **Coherència:** revisada contra RN-024; `d/×N` és una forma de `d/` (spec 000, §3). Sense conflicte.

### RN-024 — Ràtio treball:descans
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** el descans `d/×N` només s'admet a TOLA, MPLA i Vel.
- **Font:** ADR-0008, spec 000.
- **Coherència:** revisada contra RN-023; sense conflicte.

### RN-025 — Ordre de les parts de la sessió
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** la sessió segueix l'ordre de parts de l'ADR-0004. El principal II és opcional.
- **Font:** ADR-0004.
- **Coherència:** revisada contra RN-026; sense conflicte.

### RN-026 — Una sola part de tècnica
- **Tipus:** bloquejant · **Moment:** composició
- **Regla:** la tècnica és una sola part de la sessió; no es desdobla.
- **Font:** ADR-0005.
- **Coherència:** revisada contra RN-025; sense conflicte.
