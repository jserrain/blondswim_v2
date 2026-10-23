# Research — Spec 001 Model de domini

Fase 0 de `/speckit-plan`. Cada decisió resol un punt obert del Technical Context.

## R1. Lectura JSON amb Pydantic estricte
- **Decision:** Pydantic v2 només a `infrastructure`, amb models de lectura (DTO) en mode estricte: `ConfigDict(strict=True, extra="forbid", frozen=True)` i `model_validate_json`. Cada DTO es converteix a les dataclasses del domini, que continua sense dependències (principi I).
- **Rationale (verificat amb Pydantic 2.14):** en mode estricte, `"25"` o `25.0` a `piscina`, `"yes"` o `1` a `acceptat` i camps desconeguts són error. Les dates ISO s'accepten perquè en JSON una data és text. Camps obligatoris sense valor per defecte (absent o `null` → error); camps informatius i opcionals amb avís com a `X | None = None` (absent ≡ `null`), que és la semàntica de la spec (§ Format JSON). En desar s'escriuen tots els camps (`exclude_none=False`). Les rutes d'error (`tests_css.0.t400`) identifiquen el camp. `model_dump_json` respecta l'ordre dels camps (R3).
- **Missatges:** catàleg en català per `type` d'error (`missing`, `int_type`, `bool_type`, `enum`, `extra_forbidden`…).
- **Alternatives considered:**
  - Mappers manuals: més codi per obtenir el mateix.
  - Pydantic en mode per defecte (lax): converteix `"25"` → `25` i `"yes"` → `True` sense avisar, cosa que contradiu el principi IV.

## R2. Definicions de RN-030 i RN-031
- **Decision:** constants del domini a `src/blondswim/domain/definicions.py`: proves oficials per piscina (RN-030) i inici de temporada (RN-031), amb l'ID de la RN citat. Cap fitxer de configuració.
- **Rationale:** el principi V (1.3.0) admet constants del domini per a les definicions fixades al glossari o a una RN. La font continua sent `docs/regles.md`; el codi la implementa i CA-001-42 i 43 ho comproven.
- **Alternatives considered:** `config/parametres.json`. Descartat: afegeix lectura, injecció i una font de valors més, sense facilitar cap canvi real. `config/` queda per als paràmetres ajustables (el primer serà RN-028, spec 004).

## R3. Escriptura estable (CA-001-36)
- **Decision:** UTF-8, `indent=2`, `ensure_ascii=False`, salt de línia final. Ordre de claus fix, el de `data-model.md` (no alfabètic). Els `null` s'escriuen explícitament.
- **Rationale:** amb un ordre determinista, desar dues vegades dona el mateix fitxer byte a byte. L'ordre del model fa els fitxers llegibles per al coach.
- **Alternatives considered:** `sort_keys=True` dona un ordre poc natural (`acceptat` abans de `data`).

## R4. Temps `m:ss.cc`
- **Decision:** objecte de valor `Temps` amb centèsimes enteres. Parseja `^\d+:[0-5]\d\.\d{2}$` i formata sempre amb dues xifres de centèsimes.
- **Rationale:** compara sense errors de coma flotant (RN-006: t400 > t200) i rebutja `1:05.3` (CA-001-07).

## R5. Errors, avisos i registre
- **Decision:**
  - La validació retorna `Resultat(errors, avisos)`. Cada element té `rn`, `fitxer`, `camp`, `valor` i `missatge`. La càrrega acumula tots els errors abans de fallar.
  - `application` registra els avisos a través del port `RegistreAvisos`, amb la data i hora del port `Rellotge`.
  - `infrastructure` implementa el registre com a `data/avisos.jsonl` en mode afegir (spec 001, § Registre d'avisos).
- **Rationale:** el principi IV demana avisos persistents i consultables; el domini continua sense I/O ni rellotge (principi I).
- **Alternatives considered:** un registre per nedador. Descartat: els avisos del catàleg no són de cap nedador, i un sol fitxer es consulta millor.

## R6. Operacions de gestió
- **Decision:** casos d'ús a `application`: crear nedador (RN-002), esborrar nedador (sempre error, RN-004), arxivar, canviar correu, registrar test, acceptar test (CA-001-30), esborrar competició (RN-010).
- **Rationale:** els CA de gestió (21, 24, 25, 30, 37, 45) necessiten operacions, no només càrrega.
- **Fora d'abast:** la CLI (`interfaces`). Els casos d'ús es proven directament.

## R7. Temporada i setmana derivades
- **Decision:**
  - `Temporada.de_codi("AAAA-AA")` valida el nom (RN-031) i calcula `inici` i `fi`.
  - `setmana_iso(data)` fa servir `date.isocalendar()`.
  - Res d'això es desa.
- **Rationale:** són valors derivats (principi V) i el rellotge no hi intervé.

## R8. Proves de la traçabilitat
- **Decision:**
  - Un test o més per CA, amb `@pytest.mark.ca("CA-001-nn")`.
  - Els tests de domini van a `tests/unit/` i els de lectura i escriptura de fitxers, a `tests/integration/` amb `tmp_path`.
  - CA-001-33, 34 i 38 queden exclosos fins que les specs 004 i 002 estiguin aprovades.
- **Rationale:** principi VII. La traçabilitat passa de «avis» a «bloquejant» en el primer commit d'implementació (AGENTS.md).
