# Implementation Plan: Model de domini

**Branch**: `001-model-domini` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-model-domini/spec.md`

## Summary

Implementar les entitats, els invariants i el format JSON de la spec 001: nedador (id UUID v4 i alias immutables, contacte: correu i mòbil; ADR-0014 i ADR-0016), tests CSS, millors registres, catàleg de competicions i inscripcions per temporada. També les operacions de gestió que els CA exigeixen (alta, modificació, arxivar i desarxivar, afegir tests i registres), un sol validador amb nivells ERROR i AVÍS per nedador, el filtre de validació i l'aptitud per planificar.

Enfocament:
- Domini pur amb objectes de valor immutables.
- Un sol validador: entrada, càrrega i filtre apliquen les mateixes regles.
- Mappers JSON explícits a `infrastructure`, amb biblioteca estàndard.
- Definicions de RN-030 i RN-031 com a constants del domini (principi V, 1.3.0).
- Lectura JSON amb Pydantic estricte a `infrastructure`.
- Registre d'avisos a `data/avisos.jsonl`, amb el camp `decisio`.
- Escriptura determinista.
- Nedadors immutables (`id`, `alias`, `versio_esquema`) i modificables (§ Modificació del nedador): la modificació rep un `CanviNedador` que no pot portar els immutables.

Sense LLM. El rellotge només s'injecta per registrar avisos.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Pydantic v2, només a `infrastructure` i en mode estricte (research R1)

**Storage**: fitxers JSON a `data/` i registre `data/avisos.jsonl` (no versionats)

**Testing**: pytest amb `@pytest.mark.ca`, mypy estricte, import-linter, ruff (`verify.sh`)

**Target Platform**: macOS local (Mac del coach)

**Project Type**: biblioteca amb casos d'ús. La CLI queda fora d'abast

**Performance Goals**: N/A. Escala petita

**Constraints**: domini sense I/O, LLM, rellotge ni dependències externes; escriptura estable byte a byte (CA-001-36); errors en català amb fitxer, camp i valor

**Scale/Scope**: desenes de nedadors i de competicions per temporada; 84 CA, 9 dels quals pendents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Arquitectura per capes:** objectes de valor, entitats i validació a `domain`; casos d'ús i ports a `application`; JSON i paràmetres a `infrastructure`. Sense imports cap amunt. El domini no té cap dependència externa.
- [x] **II. Primer la spec:** totes les regles surten de la spec 001 i de `docs/regles.md`. No queda cap `NEEDS CLARIFICATION`.
- [x] **III. Regles de negoci identificades i amb una sola font:** el codi cita les RN per ID. RN-030 i RN-031 s'implementen a `domain/definicions.py`; la font és `docs/regles.md` (research R2). RN-007 està retirada: el codi no la cita.
- [x] **IV. El sistema avisa; el coach decideix:** errors i avisos acumulats per nedador i per camp, amb motiu i acció; un sol validador; avisos registrats a `data/avisos.jsonl` amb `decisio` (research R5; CA-001-47, 48, 56, 57, 67, 73). Un avís mai no bloqueja; un ERROR no es desa ni es carrega.
- [x] **V. Dades honestes:** temporada, setmana, test vigent i proves objectiu es deriven. No hi ha valors per defecte en carregar. Només hi ha constants per a definicions (RN-030, RN-031), com permet la versió 1.3.0.
- [x] **VI. El pla es persisteix i es versiona:** no aplica. La 001 no genera plans.
- [x] **VII. Traçabilitat de la spec al test:** cada tasca porta capa; cada un dels 75 CA no pendents té test amb `@pytest.mark.ca` (taula CA → tasca a `tasks.md`). La traçabilitat passa a «bloquejant» amb T002, quan tots tenen test (AGENTS.md).
- [x] **VIII. Documents genèrics i sense història:** els exemples de contracte fan servir valors fictius.

**Re-check post-disseny:** compleix tots els principis, amb l'esmena de la spec 001 (84 CA). Les decisions D1 i D2 (§ Decisions de disseny confirmades) no canvien cap principi.

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
src/blondswim/
├── domain/
│   ├── valors.py              # IdNedador (UUID v4), Correu, Mobil, Canal, Alias, Estil, Dia, Piscina, Temps, Prova, Classe, Prioritat, CodiTemporada
│   ├── definicions.py         # RN-030 proves oficials, RN-031 inici de temporada
│   ├── nedador.py             # Nedador, CanviNedador, TestCss, DetallProva, MillorRegistre
│   ├── cataleg.py             # Competicio, Cataleg
│   ├── inscripcions.py        # Participacio, Inscripcio
│   ├── derivats.py            # temporada, setmana ISO, test vigent, proves objectiu
│   └── validacio.py           # Resultat, ErrorValidacio, Avis (alias o UUID, camp, valor, RN o «format», acció); validador únic per nedador i entre nedadors (unicitat, RN-034); aptitud
├── application/
│   ├── ports.py               # RepositoriNedadors, RepositoriCataleg, RegistreAvisos, Rellotge, GeneradorId (Protocols)
│   ├── carrega.py             # carregar per nedador (error → exclou aquell nedador; col·lisió → exclou els implicats) i registrar els avisos
│   ├── filtre.py              # filtre de validació: tots els nedadors, tots els camps, fitxer il·legible com a ERROR propi
│   └── gestio.py              # alta (id i alias), modificar, arxivar/desarxivar, esborrar (error), afegir test, acceptar test, afegir millor registre, esborrar competició
└── infrastructure/
    ├── json_io.py             # escriptura estable (R3)
    ├── dto.py                 # models Pydantic estrictes (R1); DTO mínim d'identitat per a la unicitat (D1)
    ├── mappers.py             # DTO ↔ domini; errors en català amb fitxer/camp/valor
    ├── repositoris.py         # implementació dels ports sobre data/
    ├── registre_avisos.py     # data/avisos.jsonl, només afegir, amb `decisio`
    ├── generador_id.py        # GeneradorId amb uuid4
    └── rellotge.py            # Rellotge del sistema

tests/
├── unit/                      # domini i casos d'ús amb repositoris en memòria
└── integration/               # fitxers reals amb tmp_path
```

**Structure Decision**: estructura existent de quatre capes (principi I). `interfaces` no es toca en aquesta spec.

## Decisions de disseny confirmades

- **D1 — Lectura d'identitat per a la unicitat (confirmada).** La unicitat (correu, alias) i RN-034 compten tots els fitxers llegibles, encara que tinguin un ERROR en un altre camp (CA-001-69, 70, 76, 77). El DTO estricte complet falla sencer i no serveix. Decisió: un DTO mínim d'identitat (`correu`, `alias`, `mobil`) a `dto.py`, amb `extra="ignore"`. «Llegible» = JSON ben format que és un objecte. Els tres camps es llegeixen com a text cru i es normalitzen com a la validació (el correu sense distingir majúscules; RN-032, RN-003, RN-034). Si un camp falta o no és text, aquell nedador no participa a la unicitat d'aquell camp, però sí a la dels altres. L'error del camp ja el dona el validador. *Alternativa descartada:* DTO complet que acumuli errors i conservi valors parcials (més complex).
- **D2 — Generació de l'id (confirmada).** L'alta genera un UUID v4 (RN-002) i reintenta si l'alias col·lisiona (CA-001-61). Decisió: port `GeneradorId` (Protocol, `nou() -> IdNedador`) a `application/ports.py`, implementat amb `uuid4()` a `infrastructure/generador_id.py` i injectat, com el `Rellotge`. Els tests el substitueixen per una seqüència fixa (CA-001-45, 52, 61). *Alternativa descartada:* `uuid4()` directe a `application`: CA-001-61 no es pot provar de manera determinista.

## Complexity Tracking

Cap violació per justificar.
