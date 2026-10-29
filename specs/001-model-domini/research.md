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
- **Rationale:** compara sense errors de coma flotant (RN-006: t400 > t200; RN-007: un temps menor substitueix el millor registre) i rebutja `1:05.3` (CA-001-07).
- **Alternatives considered:**
  - `float` de segons: descartat; errors de coma flotant en comparar i en tornar a escriure.
  - `datetime.timedelta`: descartat; no imposa el format `m:ss.cc` ni les dues xifres de centèsimes.
  - Comparar el text: descartat; `10:00.00` quedaria abans de `9:59.00`.

## R5. Errors, avisos i registre
- **Decision:**
  - La validació retorna `Resultat(errors, avisos)`. Cada element té `rn` (o «format»), `fitxer`, `camp`, `valor`, `missatge` i acció, i s'identifica per l'alias (o per l'UUID de la carpeta si el fitxer no es pot llegir).
  - Un sol validador, amb les mateixes regles a l'entrada, a la càrrega i al filtre. El filtre passa per tots els nedadors i no s'atura al primer error.
  - La càrrega acumula els errors per nedador i exclou el nedador amb error; un error del catàleg fa fallar tota la càrrega.
  - La unicitat (RN-032, RN-003) i RN-034 es comproven sobre tots els fitxers que es poden llegir, vàlids o no. Una col·lisió identifica tots els implicats. Un fitxer il·legible és un ERROR propi i no hi participa.
  - `application` registra els avisos a través del port `RegistreAvisos`, amb la data i hora del port `Rellotge`.
  - `infrastructure` implementa el registre com a `data/avisos.jsonl` en mode afegir (spec 001, § Registre d'avisos).
- **Rationale:** el principi IV demana avisos persistents i consultables; el domini continua sense I/O ni rellotge (principi I).
- **Alternatives considered:** un registre per nedador. Descartat: els avisos del catàleg no són de cap nedador, i un sol fitxer es consulta millor.

## R6. Operacions de gestió
- **Decision:** casos d'ús a `application`: alta (genera l'id UUID v4 i l'alias `<part>_<sufix>`, reintenta si l'alias col·lisiona, rebutja un ERROR; RN-002, RN-003; CA-001-45, 52, 61, 62, 70), esborrar nedador (sempre error, RN-004), arxivar i desarxivar (RN-017), modificar nedador, afegir test, acceptar test (CA-001-30), afegir un millor registre (substitueix el desat si el temps és menor; si és igual o pitjor, no fa res; RN-007), esborrar competició (RN-010).
  - Immutables: `id`, `alias`, `versio_esquema`. La modificació no els rep com a dada.
  - Modificables: `correu`, `mobil`, `canal_preferent`, `estils_preferents`, `dies_entrenament`, `volum_setmanal`. Una modificació torna a validar el nedador sencer, unicitat inclosa; amb un ERROR no es desa res.
  - Un test o un millor registre desat no s'edita.
- **Rationale:** els CA de gestió (21, 25, 30, 37, 45, 52, 53, 61, 62, 70, 79 a 83, 88, 89) necessiten operacions, no només càrrega.
- **Alternatives considered:**
  - Una operació genèrica de desament que accepti qualsevol canvi: descartada; permetria canviar l'id o l'alias i editar tests i registres desats.
  - Permetre editar tests i registres desats: descartat (decisió c, 2026-10-28).
  - Desar tots els millors registres i derivar el millor: descartat el 2026-10-29 (decisió B); un sol registre de competició per prova i piscina és la dada que el coach consulta.
  - Casos d'ús dins de les entitats del domini: descartat; necessiten repositoris i generador d'id, i el domini no fa I/O.
- **D1 (confirmada) — lectura d'identitat per a la unicitat:** un DTO mínim (`correu`, `alias`, `extra="ignore"`) llegeix els dos camps com a text cru i els normalitza com la validació. Si un camp falta o no és text, aquell nedador no participa a la unicitat d'aquell camp, però sí a la de l'altre. «Llegible» = JSON ben format que és un objecte.
- **D2 (confirmada) — port `GeneradorId`:** `nou() -> IdNedador`, implementat amb `uuid4()` i injectat a l'alta. Detall a `plan.md`, § Decisions de disseny confirmades.
- **Fora d'abast:** la CLI (`interfaces`). Els casos d'ús es proven directament.

## R7. Temporada i setmana derivades
- **Decision:**
  - `Temporada.de_codi("AAAA-AA")` valida el nom (RN-031) i calcula `inici` i `fi`.
  - `setmana_iso(data)` fa servir `date.isocalendar()`.
  - Res d'això es desa. L'inici i el fi de temporada són una definició (RN-031); la setmana és una consulta.
- **Rationale:** són valors derivats o definicions (principi V) i el rellotge no hi intervé.
- **Alternatives considered:**
  - Desar `temporada.json` amb l'inici i el fi: descartat; duplicaria el que ja diu el nom de la carpeta.
  - Calcular la setmana amb una fórmula pròpia: descartat; `isocalendar()` ja implementa ISO 8601 i evita els errors de canvi d'any.
  - Desar la setmana (`AAAA-Www`) al fitxer: descartat; es calcula de la data (CA-001-18).

## R8. Proves de la traçabilitat
- **Decision:**
  - Un test o més per CA, amb `@pytest.mark.ca("CA-001-nn")`.
  - Els tests de domini van a `tests/unit/` i els de lectura i escriptura de fitxers, a `tests/integration/` amb `tmp_path`.
  - CA-001-33, 34, 38, 58, 63, 64, 68, 72 i 84 queden exclosos fins que les specs 004, 002 i 005 estiguin aprovades.
- **Rationale:** principi VII. La traçabilitat és «avis» durant la implementació i passa a «bloquejant» quan tots els criteris de la primera spec implementada tenen test (AGENTS.md); és l'última tasca, T002.
