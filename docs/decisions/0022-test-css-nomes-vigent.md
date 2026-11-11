# ADR-0022 — Test CSS: només el vigent per piscina

**Estat:** Acceptat (2026-11-11). Esmena la spec 001 (§ `tests_css`).

## Context
La spec 001 desa tots els tests CSS del nedador en una llista, amb un camp `acceptat`, per estudiar-ne l'evolució (decisió del 2026-10-28/29). La planificació només fa servir el test vigent de cada piscina, i l'evolució del nedador es pot seguir pel registre d'entrenaments i per les competicions B/C. Amb la fitxa com a canal d'entrada (ADR-0021), entrar un test ja és la decisió del coach d'aplicar-lo.

## Decisió
- El nedador té com a màxim **un test CSS per piscina** (25 m i 50 m): `test_css` amb una entrada per piscina, o cap.
- Un test nou de la mateixa piscina **substitueix** l'anterior. No es conserva cap històric.
- Entrar el test és acceptar-lo: els ritmes derivats s'apliquen a la següent planificació. El camp `acceptat` es retira.
- Es conserva la `data` del test: RN-028 (test caducat a 8 setmanes) i RN-029 (període sense test) segueixen igual.
- Les validacions del test (ràtio T400/T200, 200 no màxim, regularitat) continuen sent avisos (spec 004). Confirmar l'avís substitueix igualment l'anterior.
- Els camps informatius del test (`detall_400`, `detall_200` i els seus subcamps, `notes`) es mantenen a la spec 001 i poden ser `null`. La fitxa (ADR-0021) només porta `piscina|data|t400|t200`; els camps informatius queden `null`. No s'hi afegeix res més si augmenta la complexitat del lector.

## Alternatives
- **Llista de tests per estudiar l'evolució (spec 001 fins avui):** descartat; cap regla de planificació la fa servir i la fitxa l'hauria de portar.
- **Mantenir `acceptat` com a pas separat:** descartat; amb la fitxa, el coach ja decideix en escriure el test.
- **Retirar també els camps informatius:** descartat; costen zero a `null` i poden servir més endavant.
- **Un `rpe` únic a la fitxa:** descartat; la spec 001 té un `rpe` per detall (400 i 200) i copiar-ne un als dos inventa una dada.

## Conseqüències (spec 001)
- `tests_css` (llista) → `test_css`: objecte amb claus `25` i `50`, cada una un test o `null`. Camps del test: `data`, `t400`, `t200` (obligatoris); `detall_400`, `detall_200`, `notes` (informatius).
- Consulta `test_vigent(piscina)` = `test_css[piscina]`.
- CA retirats: CA-001-05 (vigent entre diversos acceptats), CA-001-30 (test nou no acceptat), CA-001-35 (falta `acceptat`), CA-001-82 (test desat no s'edita). CA-001-04, 31, 32 i 49 es reescriuen sobre `test_css[piscina]`.
- Nova operació: «substituir test de la piscina P» (via fitxa, spec 002).
- § Clarifications: anotar que la decisió del 2026-10-28/29 sobre l'històric de tests queda substituïda per aquest ADR.
- Mapa de specs, pregunta 8c: sense canvis (les zones surten del test de la piscina del període).
