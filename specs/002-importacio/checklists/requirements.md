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
- [x] Requisits comprovables i sense ambigüitat (CA-002-01 a 65)
- [x] Criteris mesurables (codis de sortida 0/1/2, estat de l'informe)
- [x] Criteris sense tecnologia concreta (excepte format i ordres fixats per ADR)
- [x] Escenaris d'acceptació definits
- [x] Casos límit identificats (reimportació, RN-010, RN-038 dates i piscina, RN-043, slugs duplicats, fitxer buit, BOM, alias existent)
- [x] Abast delimitat (fora d'abast explícit)
- [x] Dependències i supòsits identificats (secció Assumptions; CA-002-48 `[PENDENT spec 003]`; US2 depèn de US1 i US3)

## Feature Readiness

- [x] Tots els requisits tenen criteri d'acceptació
- [x] Els escenaris cobreixen els fluxos principals (fitxa alta/actualització, calendari, inscripcions, confirmació)
- [x] Compleix la constitució IX (contracte) i X (regla de capa)
- [x] Sense fuites d'implementació més enllà dels contractes normatius

## Notes

- Revisada després de l'auditoria G1 r3 (2026-11-12).
