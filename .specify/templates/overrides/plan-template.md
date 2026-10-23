# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] **I. Arquitectura per capes:** cada component té capa; cap import cap amunt (import-linter); `domain` és pur.
- [ ] **II. Primer la spec:** cap regla de negoci fora de la spec; els punts oberts, marcats [NEEDS CLARIFICATION].
- [ ] **III. Regles de negoci identificades i amb una sola font:** cada regla té RN-NNN a `docs/regles.md`; les regles noves, comprovades contra les existents.
- [ ] **IV. El sistema avisa; el coach decideix:** cap guarda silenciosa; avisos persistents; l'LLM només en regles de judici, amb entrades, sortida i comprovació.
- [ ] **V. Dades honestes:** cap valor derivat desat; cap valor per defecte; paràmetres ajustables a dades o configuració; definicions com a constants del domini en un sol lloc, amb l'ID de la font i un CA.
- [ ] **VI. El pla es persisteix i es versiona.**
- [ ] **VII. Traçabilitat de la spec al test:** cada tasca té capa; cada CA-ID no pendent té test amb `@pytest.mark.ca`.
- [ ] **VIII. Documents genèrics i sense història:** cap nedador, competició ni data fora dels tests i dels exemples.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/blondswim/
├── domain/
├── application/
├── infrastructure/
└── interfaces/

tests/
├── unit/
└── integration/
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
