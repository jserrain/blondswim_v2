Implementa T048–T050 i T035–T047 de specs/001-model-domini/tasks.md (Phase 3b, US1b: UUID, alias, contacte, validació i millor marca).

Llegeix només: specs/001-model-domini/spec.md (els CA citats a les tasques de la fase), tasks.md (Phase 3b i la taula CA → tasca), plan.md (§ Decisions de disseny confirmades: D1 i D2), data-model.md, research.md (R5, R6), contracts/fitxers-json.md (nedador i millors registres); docs/decisions/0014 i 0020; docs/regles.md només per a les RN que citen les tasques; specs/000-glossari.md només per a CA-000-10.
Del codi, el que hi ha a src/blondswim/ i tests/: adapta'l, no el reescriguis de zero.
No llegeixis altres specs, docs/auditoria/ ni la v1.

Ordre (no te'l saltis):
1. Tests: T048 i T049 (reescriure els tests fets contra la spec nova), després T050 i T035–T039. Han de fallar abans d'implementar.
2. Domini: T040, T041, T042.
3. Ports i infraestructura: T043, T044.
4. Aplicació: T045, T046, T047.
Atura't i informa'm al final de cada pas (1 a 4) amb el diff del pas i l'ordre que he d'executar per comprovar-lo. No passis al pas següent fins que t'ho digui.

Regles:
- Cada test porta `@pytest.mark.ca("CA-001-nn")` (o `CA-000-10`); els números poden tenir tres xifres.
- Correu (ADR-0020): opcional; es desa EXACTAMENT tal com s'ha entrat; només la comprovació de format mínim de RN-032 i la unicitat comparant en minúscules i sense espais en blanc als extrems. Cap normalització del valor desat, cap regex estricta, cap xarxa.
- Mòbil: obligatori (no buit després de treure espais en blanc als extrems), no únic, sense format.
- Millor marca: llista de millores successives per prova i piscina; s'afegeix només si és millor i de data posterior a la vigent; igual o pitjor no fa res; `competicio` és un nom, sense catàleg.
- `GeneradorId` (D2) s'injecta a l'alta; als tests, un generador fix.
- Pydantic només a infrastructure. Domini sense I/O ni dependències externes.
- No toquis catàleg, inscripcions, consultes, aptitud ni registre d'avisos (US2–US6), ni la CLI.
- No facis T002: va al final (Polish).
- No executis cap ordre ni facis commit. Respon només amb el diff i les ordres de consola que he d'executar.
