# Implementation Plan: Model de domini

**Branch**: `001-model-domini` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-model-domini/spec.md`

## Summary

Implementar les entitats, els invariants i el format JSON de la spec 001: nedador (identificat per correu), tests CSS, millors registres, catàleg de competicions i inscripcions per temporada. També les operacions de gestió que els CA exigeixen i les dues validacions: model vàlid i aptitud per planificar.

Enfocament:
- Domini pur amb objectes de valor immutables.
- Mappers JSON explícits a `infrastructure`, amb biblioteca estàndard.
- Paràmetres de les regles (RN-030, RN-031) a `config/parametres.json`, injectats.
- Escriptura determinista.

Sense LLM i sense rellotge.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: cap de nova. Biblioteca estàndard (research R1)

**Storage**: fitxers JSON a `data/` (no versionat) i `config/parametres.json` (versionat)

**Testing**: pytest amb `@pytest.mark.ca`, mypy estricte, import-linter, ruff (`verify.sh`)

**Target Platform**: macOS local (Mac del coach)

**Project Type**: biblioteca amb casos d'ús. La CLI queda fora d'abast

**Performance Goals**: N/A. Escala petita

**Constraints**: domini sense I/O, LLM, rellotge ni dependències externes; escriptura estable byte a byte (CA-001-36); errors en català amb fitxer, camp i valor

**Scale/Scope**: desenes de nedadors i de competicions per temporada; 46 CA, 3 dels quals pendents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Arquitectura per capes:** objectes de valor, entitats i validació a `domain`; casos d'ús i ports a `application`; JSON i paràmetres a `infrastructure`. Sense imports cap amunt. El domini no té cap dependència externa.
- [x] **II. Primer la spec:** totes les regles surten de la spec 001 i de `docs/regles.md`. No queda cap `NEEDS CLARIFICATION`.
- [x] **III. Regles de negoci identificades i amb una sola font:** el codi cita les RN per ID. Els valors de RN-030 i RN-031 són a `config/parametres.json`, amb la clau de cada RN, i un test comprova que les claus són RN vigents (research R2).
- [~] **IV. El sistema avisa; el coach decideix:** errors i avisos acumulats amb motiu (research R5). La persistència dels avisos és d'una spec posterior (Complexity Tracking).
- [x] **V. Dades honestes:** temporada, setmana, test vigent i proves objectiu es deriven. No hi ha valors per defecte en carregar. Els paràmetres no són constants al codi.
- [x] **VI. El pla es persisteix i es versiona:** no aplica. La 001 no genera plans.
- [x] **VII. Traçabilitat de la spec al test:** cada tasca porta capa; cada CA no pendent té test amb `@pytest.mark.ca`. La traçabilitat passa a «bloquejant» al primer commit d'implementació.
- [x] **VIII. Documents genèrics i sense història:** els exemples de contracte fan servir valors fictius.

**Re-check post-disseny:** igual. Només IV queda justificat.

## Project Structure

### Documentation (this feature)

```text
specs/001-model-domini/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── fitxers-json.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
config/
└── parametres.json            # RN-030, RN-031 (versionat)

src/blondswim/
├── domain/
│   ├── valors.py              # IdNedador, Correu, Alias, Estil, Dia, Piscina, Temps, Prova, Classe, Prioritat, CodiTemporada
│   ├── parametres.py          # Parametres (dades injectades)
│   ├── nedador.py             # Nedador, TestCss, DetallProva, MillorRegistre
│   ├── cataleg.py             # Competicio, Cataleg
│   ├── inscripcions.py        # Participacio, Inscripcio
│   ├── derivats.py            # temporada, setmana ISO, test vigent, proves objectiu
│   └── validacio.py           # Resultat, ErrorValidacio, Avis; model vàlid i aptitud
├── application/
│   ├── ports.py               # RepositoriNedadors, RepositoriCataleg, FontParametres (Protocols)
│   └── gestio.py              # crear, arxivar, esborrar, canviar correu, registrar/acceptar test, esborrar competició
└── infrastructure/
    ├── json_io.py             # lectura/escriptura estable (R3)
    ├── mappers.py             # JSON ↔ domini, errors amb fitxer/camp/valor
    ├── repositoris.py         # implementació dels ports sobre data/
    └── parametres.py          # lectura de config/parametres.json

tests/
├── unit/                      # domini i casos d'ús amb repositoris en memòria
└── integration/               # fitxers reals amb tmp_path
```

**Structure Decision**: estructura existent de quatre capes (principi I). `interfaces` no es toca en aquesta spec. `config/` és nova i és el lloc dels paràmetres de regles versionats.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| IV: els avisos no es persisteixen en aquesta spec | El principi IV deixa el format «a la spec que correspongui», i la 001 no el defineix | Inventar-ne el format seria una regla nova sense spec (principi II). Els avisos es retornen i es podran registrar quan existeixi aquesta spec |
| `config/parametres.json` repeteix valors de RN-030 i RN-031 | El principi V prohibeix constants al codi | Llegir `docs/regles.md` és fràgil; desar-los a `data/` els deixaria sense versionar. Mitigació: un test lliga cada clau a una RN vigent |
