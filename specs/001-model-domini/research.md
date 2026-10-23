# Research — Spec 001 Model de domini

Fase 0 de `/speckit-plan`. Cada decisió resol un punt obert del Technical Context.

## R1. Validació i mapatge JSON sense dependències noves
- **Decision:** biblioteca estàndard (`json`, `dataclasses`, `datetime`, `re`, `enum`). El domini té `dataclass(frozen=True, slots=True)` i funcions de validació pures. `infrastructure` converteix JSON ↔ domini amb mappers explícits.
- **Rationale:** el principi I prohibeix dependències externes a `domain`. Amb mappers propis, els errors identifiquen el fitxer, el camp i el valor en català (CA-001-03, 39 a 44), i `null` i «camp absent» es distingeixen (principi V).
- **Alternatives considered:** Pydantic a `infrastructure`. Descartat per ara: duplica el model, té missatges en anglès i converteix valors implícitament (`"25"` → `25`), que és una correcció silenciosa (principi IV). Es pot reconsiderar per a la spec 002 (importació).

## R2. Paràmetres de les regles (RN-030, RN-031)
- **Decision:** `config/parametres.json`, versionat, amb un bloc per RN (`"RN-030": {...}`, `"RN-031": {...}`). `infrastructure` el llegeix i l'injecta al domini com a objecte `Parametres`. El domini no té cap constant de negoci.
- **Rationale:** el principi V exigeix que els paràmetres no siguin constants al codi. `docs/regles.md` continua sent el text normatiu (principi III). Un test de coherència comprova que les claus del fitxer són RN existents i no retirades.
- **Alternatives considered:**
  - Constants al domini: viola el principi V.
  - Llegir `docs/regles.md`: és fràgil, perquè és text per a persones.
  - Desar-los a `data/`: `data/` no es versiona i els paràmetres són comuns a tots els nedadors.

## R3. Escriptura estable (CA-001-36)
- **Decision:** UTF-8, `indent=2`, `ensure_ascii=False`, salt de línia final. Ordre de claus fix, el de `data-model.md` (no alfabètic). Els `null` s'escriuen explícitament.
- **Rationale:** amb un ordre determinista, desar dues vegades dona el mateix fitxer byte a byte. L'ordre del model fa els fitxers llegibles per al coach.
- **Alternatives considered:** `sort_keys=True` dona un ordre poc natural (`acceptat` abans de `data`).

## R4. Temps `m:ss.cc`
- **Decision:** objecte de valor `Temps` amb centèsimes enteres. Parseja `^\d+:[0-5]\d\.\d{2}$` i formata sempre amb dues xifres de centèsimes.
- **Rationale:** compara sense errors de coma flotant (RN-006: t400 > t200) i rebutja `1:05.3` (CA-001-07).

## R5. Errors i avisos
- **Decision:** la validació retorna `Resultat(errors: tuple[ErrorValidacio, ...], avisos: tuple[Avis, ...])`. Cada element té `rn`, `fitxer`, `camp`, `valor` i `missatge`. La càrrega acumula tots els errors abans de fallar, en comptes d'aturar-se al primer.
- **Rationale:** el principi IV demana dir per què es bloqueja. Acumular estalvia al coach cicles de corregir i tornar a carregar.
- **Persistència dels avisos:** el principi IV exigeix registrar-los, però deixa el format a «la spec que correspongui», i la 001 no el defineix. La 001 retorna els avisos; registrar-los és d'una spec posterior. Queda justificat a Complexity Tracking.

## R6. Operacions de gestió
- **Decision:** casos d'ús a `application`: crear nedador (RN-002), esborrar nedador (sempre error, RN-004), arxivar, canviar correu, registrar test, acceptar test (CA-001-30), esborrar competició (RN-010).
- **Rationale:** els CA de gestió (21, 24, 25, 30, 37, 45) necessiten operacions, no només càrrega.
- **Fora d'abast:** la CLI (`interfaces`). Els casos d'ús es proven directament.

## R7. Temporada i setmana derivades
- **Decision:**
  - `Temporada.de_codi("AAAA-AA", parametres)` valida el nom (RN-031) i calcula `inici` i `fi`.
  - `setmana_iso(data)` fa servir `date.isocalendar()`.
  - Res d'això es desa.
- **Rationale:** són valors derivats (principi V) i el rellotge no hi intervé.

## R8. Proves de la traçabilitat
- **Decision:**
  - Un test o més per CA, amb `@pytest.mark.ca("CA-001-nn")`.
  - Els tests de domini van a `tests/unit/` i els de lectura i escriptura de fitxers, a `tests/integration/` amb `tmp_path`.
  - CA-001-33, 34 i 38 queden exclosos fins que les specs 004 i 002 estiguin aprovades.
- **Rationale:** principi VII. La traçabilitat passa de «avis» a «bloquejant» en el primer commit d'implementació (AGENTS.md).
