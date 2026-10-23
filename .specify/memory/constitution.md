# BlondSwim v2 Constitution

## Core Principles

### I. Arquitectura per capes (NON-NEGOTIABLE)
- El codi s'organitza en quatre capes: `domain`, `application`, `infrastructure` i
  `interfaces`.
- Una capa només importa capes inferiors. import-linter ho verifica i una violació bloqueja.
- `domain` és pur: no fa I/O, no crida cap LLM, no llegeix el rellotge ni secrets i no té
  dependències externes.
- El rellotge, l'LLM i l'accés a dades arriben a `application` a través de ports
  (Protocols), injectats des de les capes exteriors.

Raó: a la v1, funcions que semblaven pures llegien la data o carregaven secrets.

### II. Primer la spec
- Tota feina parteix d'una spec de `specs/`. Si no n'hi ha, la feina s'atura i es demana.
- No s'inventen regles de negoci. Tot el que la spec no diu es marca [NEEDS CLARIFICATION]
  i es pregunta.
- Cada branca porta una sola spec, amb canvis petits.

### III. Regles de negoci identificades i amb una sola font
- Tota regla de negoci té un identificador `RN-NNN` i un tipus: bloquejant, avís o judici
  LLM.
- Les regles viuen a `docs/regles.md`, que n'és l'única font. Les specs, els plans i el
  codi s'hi refereixen per ID i no en repeteixen el contingut.
- Abans d'acceptar una regla nova, cal comprovar-la contra les existents: duplicats,
  contradiccions i solapaments. El resultat d'aquesta comprovació queda escrit.

Raó: a la v1 hi havia regles duplicades amb valors diferents i regles que es bloquejaven
entre elles.

### IV. El sistema avisa; el coach decideix
- Cap guarda retalla, corregeix o descarta una dada o un pla sense avisar-ne.
- Una regla bloquejant atura el procés i diu per què. Una regla d'avís deixa continuar i
  ho comunica.
- Els avisos es registren de manera persistent i consultable. El format el decideix la spec
  que correspongui.
- L'LLM només actua en els punts de judici, i cadascun és una regla de tipus judici LLM a
  `docs/regles.md`. Tota la resta és determinista.
- Tota regla de tipus judici LLM indica les seves entrades, la sortida esperada i la
  comprovació determinista que valida la sortida abans d'acceptar-la. Una sortida que no
  passa la comprovació no s'accepta.

### V. Dades honestes
- Un valor derivat no es desa mai: es calcula quan cal.
- Una dada obligatòria que falta és un error. Una dada opcional desconeguda es desa com a
  `null`; genera avís només si la spec ho indica.
- Els paràmetres vénen de les dades o de la spec, mai de constants al codi.

### VI. El pla es persisteix i es versiona
- Un pla generat es desa i se'n guarden les versions. No es regenera ni se sobreescriu
  sense que quedi constància.
- Els identificadors persistits són estables entre execucions.

### VII. Traçabilitat de la spec al test
- Tota tasca indica a quina capa pertany: `domain`, `application`, `infrastructure`,
  `interfaces` o `project`. `project` és per a la configuració, les eines i la documentació;
  no és una capa de codi i no forma part de l'arquitectura del principi I.
- Cada criteri d'acceptació té un ID amb el format `CA-<spec>-<nn>`, on `<spec>` és el
  número de la spec i admet un sufix de lletra (per exemple, `CA-002b-01`).
- Un test es lliga a un criteri amb el marcador pytest `@pytest.mark.ca("<ID>")`. Un test
  pot portar diversos marcadors i un criteri pot tenir diversos tests.
- Tot criteri d'una spec aprovada té almenys un test amb el seu marcador, i
  `scripts/verify.sh` ho comprova. Mentre no hi ha implementació, la comprovació només
  avisa (AGENTS.md). Se n'exclouen els criteris marcats `[PENDENT spec NNN]`, que depenen
  d'una spec que encara no existeix.
- Una tasca no s'acaba fins que `bash scripts/verify.sh` passa en verd.

### VIII. Documents genèrics i sense història
- Les specs, els ADR, les regles i el codi no anomenen mai cap nedador, competició ni data
  concreta. Això només és permès als tests i als exemples.
- A cada document normatiu hi ha només l'estat actual. El perquè va a l'ADR i la
  història, a git.

## Fonts normatives

Són normatives, per aquest ordre de precedència:
1. Aquesta constitució.
2. Els ADR acceptats de `docs/decisions/`.
3. `specs/000-glossari.md`.
4. `docs/regles.md`.
5. Les specs aprovades de `specs/`.

Una spec és aprovada quan la capçalera diu `**Estat:** Aprovada`. Mentre és un esborrany,
diu `**Estat:** Esborrany`.

Si dues fonts entren en conflicte, la feina s'atura i el conflicte es resol amb una esmena
explícita de la font de rang inferior (o un ADR nou). Mentrestant, preval la de rang
superior.

Les decisions fixades són als ADR. La constitució no en reprodueix el contingut, i
canviar-ne una requereix un ADR nou que la substitueixi.

No són normatius: `docs/mapa_specs.md`, les guies, els inventaris, el codi i els documents
de la v1. Una regla de la v1 només és vàlida quan queda recollida en un ADR, en una spec o
a `docs/regles.md`.

## Flux de treball i portes de qualitat

- Tot s'executa amb `uv run`, i les dependències només s'afegeixen amb `uv add`.
- `bash scripts/verify.sh` és la porta única: lint, format, mypy estricte, import-linter,
  tests, traçabilitat dels criteris d'acceptació i comprovacions de seguretat.
- Els secrets només els llegeix `infrastructure`, i no es versionen mai.
- La v1 només es pot llegir.

## Governance

- La constitució té precedència sobre qualsevol altra pràctica o document. `AGENTS.md` és
  la guia operativa i ha de ser coherent amb la constitució.
- Una esmena es fa amb un canvi explícit en aquest fitxer, amb l'increment de versió
  corresponent:
  - MAJOR: es treu o es redefineix un principi.
  - MINOR: s'afegeix un principi o una secció, o se n'amplia materialment el contingut.
  - PATCH: aclariments i redacció.
- El *Constitution Check* de `/speckit-plan` i `/speckit-analyze` verifica el compliment.
  Una violació s'ha de justificar o corregir abans d'implementar.

**Version**: 1.2.1 | **Ratified**: 2026-10-18 | **Last Amended**: 2026-10-23
