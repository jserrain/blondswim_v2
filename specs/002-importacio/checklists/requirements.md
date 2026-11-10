# Specification Quality Checklist: Importació estricta

**Purpose**: Validar la completesa i la qualitat de la spec abans de planificar
**Created**: 2026-11-10
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Sense detalls d'implementació injustificats (els formats CSV, ordres i contracte de capes són requisits de l'ADR-0013 i la constitució IX/X)
- [x] Centrada en el valor per al coach
- [ ] Escrita per a no tècnics (no aplica: la spec és normativa i tècnica per convenció del projecte, com la 001)
- [x] Seccions obligatòries completes (format del projecte «Spec NNN», no la plantilla genèrica)

## Requirement Completeness

- [x] Cap marcador [NEEDS CLARIFICATION]
- [x] Requisits comprovables i sense ambigüitat (CA-002-01 a 39)
- [x] Criteris mesurables (codis de sortida 0/1/2, estat de l'informe)
- [x] Criteris sense tecnologia concreta (excepte format i ordres fixats per ADR)
- [x] Escenaris d'acceptació definits
- [x] Casos límit identificats (reimportació, RN-010, canvi de dates, slugs duplicats)
- [x] Abast delimitat (fora d'abast explícit)
- [x] Dependències i supòsits identificats (secció Assumptions, CA-002-37 `[PENDENT spec 003]`)

## Feature Readiness

- [x] Tots els requisits tenen criteri d'acceptació
- [x] Els escenaris cobreixen els fluxos principals (nedadors, calendari, inscripcions, confirmació)
- [x] Compleix la constitució IX (contracte) i X (regla de capa)
- [x] Sense fuites d'implementació més enllà dels contractes normatius

## Notes

- Document normatiu: conté dates i noms d'exemple als CA (`10/11/2026`, `Campionat d'Hivern`); la constitució VIII només ho permet a tests i exemples. Revisar a `/auditar` (G1).
- Pendent a altres documents (secció «Canvis en altres documents»): spec 001 (CA-001-64, `decisio`), `AGENTS.md` (regla de capa i ordres `importar`).
