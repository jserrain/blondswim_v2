# Auditoria de reutilització — BlondSwim v1 → v2

*2026-10-14 · Font: `../ws_blondswim` (HEAD 565792c, només lectura) · Context: `AGENTS.md`, `docs/guides/…Pla d'acció…`, `docs/inventari/moduls.md`, `docs/inventari/regles.md`. No s'ha modificat cap fitxer ni s'ha llegit cap `.env`.*

**Execució.** Aquest document és el lliurable. Com que la tasca és de només lectura, en aprovar-lo no s'escriu cap fitxer al repositori. Si es vol desar, la proposta és `docs/inventari/auditoria.md`, però només si ho demanes.

**Abast.** El Pla d'acció situa l'auditoria *després* de la constitució i de l'especificació del domini. Encara no hi ha cap spec, per tant aquesta auditoria compara amb l'inventari i amb les decisions fixades a `AGENTS.md`. És provisional i s'ha de revalidar quan existeixi la spec del domini (Q10).

**Convencions.** Les rutes de la v1 són relatives a `src/blondswim/`, com a l'inventari. Les regles noves continuen la numeració (R220…), igual que els conflictes (C33…) i els buits (B29…). G1…G8 són conflictes entre els documents de govern de la v2. D = determinista, J = judici LLM.

---

## 1. Validació i compleció de l'inventari

### 1.1 Comprovacions que es confirmen
- La llista de codi mort de `moduls.md` és correcta: cap d'aquestes funcions es crida des de `src/` ni des de `scripts/`, només des dels tests.
- Els recomptes de tests per fitxer també quadren. Hi ha 527 `def test_` en 37 fitxers, i 676 casos si es compten les parametritzacions. Hi ha 3 fitxers de test buits.
- Els mòduls marcats «Lògica + IO: no» no fan IO, amb una excepció: `periodificacio.avui()`, que ja està anotada.
- S'han comprovat contra el codi unes 45 regles (R035-R051, R079, R084, R098-R123, R156-R161, R165-R202 i R216-R218) i els conflictes C01, C02, C08 i C21. Són correctes, llevat dels matisos de §1.4.

### 1.2 Mòduls, fitxers i dades que l'inventari no cobreix o descriu malament

| Element | Troballa | Impacte a v2 |
|---|---|---|
| `.gitignore` de v1 | Exclou `data/nedadors/`, `data/competicions.json` i `data/processed/`. Les dades que es volen reutilitzar **no són a git**: només existeixen al disc. | Cal copiar-les del directori de treball. A v2, decidir si es versionen (ADR-015). |
| `data/nedadors/` | **Només hi ha el Jep.** Lou, Cris i Pere només surten com a fixtures de test i als docs. Lou té CSS real i la taula de ritmes a `data/raw/Provisional26-27.xlsx`. Cris i Pere van en mode RPE fins al primer test. Cap d'ells té dies ni calendari registrats. | La v2 és per a 4 nedadors i només en té 1 de dades. Bloqueja provar les plantilles de dies variables (B08) i el mode RPE (B03). |
| `jep/resultats_vi.json` | És l'únic resultat del Jep (100 L, 78,4 s, `font: video`), però el codi només llegeix `resultats.json`, que no existeix. `progressio` i l'informe no veuen cap resultat. | Migrar-lo o reanomenar-lo (Q7). |
| `jep/macrocicle_referencia.json` | Macrocicle de referència del coach, extret de l'Excel. Només el llegeix `scripts/prova_generacio_microcicle.py`. | Cas golden de volums i fases. |
| `jep/setmanes/*.xlsx` | Fulls de piscina generats per v1 (W40-W42 i `meso_1`). | Sortida de referència per comparar amb v2. |
| `jep/registres/*.xlsx` | Fulls de registre **buits** (0 files a Sessions i SRSS). | No hi ha dades reals de seguiment. R185-R191 no s'han pogut provar mai amb dades reals. |
| `jep/log_decisions/*` | Logs obsolets (`jep_1..4` numeren la setmana dins el meso) o que només contenen la metodologia. | Descartar. |
| `jep/nedador.json.bak` | Zones d'abans del test CSS del 05/10. És l'única traça de com han canviat les zones. | Arxiu. |
| `data/raw/*.xlsx` (3) | Excel originals del coach. `Provisional26-27.xlsx` conté les dades de Lou i els objectius A de tots els nedadors. | Única font de dades dels altres nedadors (Q5). |
| `data/raw/docs/*.md` (11) | Documentació de disseny de v1. L'inventari la cita però no la llista. | Referència per a la spec. |
| `data/raw/jutge/casos.jsonl` | Només **7** casos. | Joc golden insuficient per mesurar R218 (≥85% d'encert). |
| `data/raw/jutge/referencies.jsonl` | `avaluar_jutge.py:119` el fa servir per defecte, però el fitxer no existeix. | — |
| `data/processed/jutge/*.jsonl` (8) | Execucions d'avaluació del jutge del 06/10. | Només si es manté el jutge (M3). |
| `llm/client.py:15` | `load_dotenv(override=True)` **en importar el mòdul**: qualsevol import carrega `.env` i sobreescriu l'entorn de la shell. | A v2 s'ha d'evitar: secrets només a `infrastructure/secrets.py`. |
| `generar_macrocicle.py:592` | També llegeix el rellotge (`avui()`), no només l'LLM. | El rellotge s'ha d'injectar. |
| `scripts/generar_temporada.py:33` | Importa `anthropic` directament. | — |
| Codi mort no llistat | `models/registre.etiqueta_cr10`; `generar_microcicle._recalcular_taper_i_pics` (mort de manera transitiva); `xlsx_to_json.InconsistentDataWarning` (no es llança mai). | Afegir a la llista. |
| Arrel | `errors*.txt` (bolcats de pytest antics), `egg-info`, `.aider*`, `Makefile` (objectiu `aider` amb `deepseek`), `.env.example` buit, `conftest.py` buit. | Descartar. |

### 1.3 Defectes de flux que l'inventari descriu malament (importants)
- **R033, R043 i R044 no salten mai al flux real** (R250 i R251 són regles noves; vegeu la taula de §1.5). `validar_pla_complet` només rep el mesocicle actual, de ≤4 setmanes i sense `historial_previ` (`validacio.py:176-187, 326-331`; `generar_temporada.py:289-322`). Conseqüències:
  - L'ACWR necessita 4 setmanes prèvies i no les té.
  - L'avís `descarrega_periodica` no pot sortir.
  - Els efectes descrits a C10 i C12 són teòrics.
- **Guard ACWR (R042).** El defecte és real: `micro.setmana` és la setmana ISO de 1 a 53, i `//100` sempre dona 0. Però la descripció cal matisar-la:
  - L'historial només serveix de porta. Si és buit, el guard no actua (`acwr_omet`).
  - Si no és buit, el guard compara amb les setmanes *planificades* del mateix mesocicle, i la primera setmana s'ignora.
  - El canvi d'any assumeix 52 setmanes (el 2026 en té 53).
  - Cap test cobreix `acwr_limitat`.
  - Per tant, l'exemple de C09 (historial de 9.000 m) no pot passar així.
- **Causa comuna (ADR-007).** El model guarda la setmana sense l'any. D'aquí surten els errors del guard, l'ordenació dels microcicles quan es creua el cap d'any (`validacio.py:331`) i la rotació de tècnica.

### 1.4 Regles de `regles.md` mal descrites

| Regla | Correcció |
|---|---|
| R020 | `detectar_retaper` sí que es crida (`taper.py:157`). Marca qualsevol competició de `pics_prioritzats`, no només les B, i el flag no té cap efecte. |
| R032 | El test CSS només és una etiqueta a les notes («Càrrega + Test CSS»). No es programa cap sessió de test. |
| R033 / R043 / R044 | Al flux real són inactives (§1.3). |
| R041 | Només s'aplica a càrrega, qualitat i descàrrega sense B. A més, també pot *baixar* el volum interpolat fins al mínim. |
| R042 | L'efecte real no fa servir mai l'historial (§1.3). |
| R047 | Hi falta el pes del rol «mitjana» = 1,0. |
| R056 | La branca «càrrega + `dies_qualitat`» no s'executa mai: `dies_qualitat` val False a Base. |
| R077 | `sessions_des_de` sempre és el dilluns següent: a la pràctica no filtra res. |
| R094 | El codi accepta noms normalitzats i ignora les parts desconegudes sense comptar-ho com a problema. |
| R100 | L'A3 i el làctic de les parts fixes es resten **només del pressupost d'A3**. El de làctic no baixa. |
| R111 | Només es fan complir els mínims. Els màxims (i el ×2 de velocitat i làctic) no es comproven. |
| R113 | `corregir_cicles` **no** requereix ritme conegut: actua sobre tota sèrie no fixa de ≥2 repeticions (també cames, aletes i biblioteca) i omple els descansos que falten. El ritme conegut només el demana `problemes_cicles` (la validació que reintenta) i l'1:1 de l'A3. |
| R121 | Comprova l'última part no fixa amb exercicis, no la «tornada a la calma» pel nom. Els estils hi queden exempts. |
| R137 | El nivell de la variant depèn del tipus de setmana, no de la fase. Per això les descàrregues de Build reben variants de Base. |
| R143 | No és «25…800» sinó una llista tancada: 25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 600 i 800 (no hi ha 350 ni 700). |
| R174 | Només les **dues primeres** proves P tenen sèrie. Una tercera P es queda sense, i no hi ha cap avís. |
| R177 | L'avís de «sense registre» només surt si hi ha registres anteriors del pic. Després de retrocedir, el comptador es reinicia. |
| R178 | El descans de la descàrrega és 1:00 a Base i 0:45 a la resta. El d/0:45 de Build1 compta la 3a setmana *del bloc*. |
| R199 | La banda comença a la data del primer control, no «ara». |
| C11 | És més ampli: amb un terra de 12.000 i un factor de 0,7, qualsevol càrrega de menys de 17.143 m aixeca la descàrrega. També passa a **Base** (15.000 → 10.500 → 12.000). |
| C12 | El conflicte entre regles existeix, però l'avís no surt mai (§1.3). |

### 1.5 Regles noves (no inventariades)

| id | Regla | Origen | D/J | Relació |
|---|---|---|---|---|
| R220 | El volum setmanal i el del mesocicle s'arrodoneixen a 25 m. Les sessions i les parts, a 100 m. | generar_macrocicle.py:51-53, 674-679 | D | R050 |
| R221 | Una descàrrega sense cap càrrega prèvia al bloc es calcula sobre el mínim de la fase; si n'hi ha, sobre el volum *final* de la càrrega anterior (després del terra i del mínim post-competició). | generar_macrocicle.py:327-329, 453-454 | D | refina R036 |
| R222 | El Peak d'1 setmana d'un doble pic fa servir el factor 0,60. | generar_macrocicle.py:75-78 | D | R037, C15 |
| R223 | Una setmana amb B no té terra ni mínim post-competició, i pot baixar de 12.000 m. | generar_macrocicle.py:430-440 | D | R039, R041 |
| R224 | El ×0,8 de la B s'aplica comenci el dia que comenci la B. L'activació i la setmana post-competició només es fixen en el cap de setmana. | periodificacio.py:286-291 | D | **C34** |
| R225 | Peak, Cursa i Transició formen un sol bloc per tram continu, sense límit de setmanes i sense descàrrega. | periodificacio.py:262-270 | D | R027 |
| R226 | Les setmanes de Build2 entre les dues A d'un doble pic es divideixen en blocs amb descàrrega (amb 2 setmanes surt [C, D] i l'avís `bloc_curt`). | periodificacio.py:197-202 | D | R011, R028 |
| R227 | El Peak és curt si l'A anterior és a ≤28 dies, encara que ja hagi passat. El doble pic es detecta encara que la primera A sigui passada. | periodificacio.py:154-155; Fase3.md:513 | D | R011 |
| R228 | Una data de referència fora de la temporada és un error. «Avui» es calcula en hora d'Europe/Madrid. | generar_macrocicle.py:612-616 | D | — |
| R229 | Separació màxima de 12 setmanes entre A. Existeix com a paràmetre, però no es comprova. | context_competicio.py:44 | D | — |
| R230 | Abast: només les categories absolut i màster (el júnior queda fora). Proves de piscina de 50 a 1.500 m i aigües obertes. | Fase2.md:14 | D | **C35** |
| R231 | A les competicions A, una prova per dia. | Fase3.md:483 | D | R019, B05 |
| R232 | Budapest (aigües obertes + piscina de 50 m) és un sol bloc competitiu amb un únic taper. La piscina del pic és la de la primera competició (`aaoo`), de manera que no es troba cap control per a la prova de piscina. | FulldeRuta_1002.md:130; proves.py:52-54, 157 | D | B06 |
| R233 | Integritat del calendari: competició repetida → error; inscripció fora del catàleg → error (excepte simulacions); una simulació dura 1 dia; piscina ∈ {25m, 50m, aaoo}. | models/calendari.py:27, 74-136 | D | R014, R015 |
| R234 | Una competició del calendari sense proves vol dir «encara no decidit» i s'avisa. El codi només avisa per a les A. | Manual.md:109; proves.py:206-211 | D | R197 |
| R235 | `piscina_m` no està restringida a 25/50: qualsevol altre valor agafa la llista de 25 m. La taula del prompt diu sempre «piscina de 25 m». | generar_microcicle.py:740-742; prompt:121 | D | R143 |
| R236 | Una resposta sense `tool_use` deixa la sessió buida **sense reintent**. | generar_microcicle.py:1621-1627 | D | R157, R158 |
| R237 | Un exercici que pydantic rebutja es descarta només amb un log, i les parts desconegudes s'ignoren. Cap dels dos casos compta com a problema. | generar_microcicle.py:929-1033 | D | R093, R094 |
| R238 | Un exercici de biblioteca afegit pel codi agafa la dosi del `format` (4x25 si no es pot llegir), la distància vàlida següent i A1. | generar_microcicle.py:1275-1283 | D | R139, B26 |
| R239 | Valors per defecte: un rol desconegut agafa el pressupost d'aeròbica; una qualitat de tipus desconegut, el de Base; la papallona, 50 m; el material, el de Base. Un nedador sense proves agafa la metodologia del «200 lliure». | pla_setmanal.py:565-604, 968; generar_microcicle.py:282 | D | — |
| R240 | Factors de temps: esquena 1,10, braça 1,17, papallona 1,05, estils 1,08, cames 1,30, aletes ×0,92. | models/nedador.py:41-76 | D | R117 |
| R241 | Selecció de tècnica: una família que no cobreix cap prova del nedador no es tria mai, encara que sigui prioritària. La biblioteca no té el nivell «Refinament» que diuen els docs. | tecnica.py:61-64; Fase3.md:505 | D | R136 |
| R242 | Descans per a nedadors sense zones: A3 ≥15 s/100 i AeM ≥20 s/100. Es valida, però no es corregeix. | cicles.py:182, 214-220 | D | B03 |
| R243 | Ritme de cursa en 50 m: descans ≥ temps nedat. Avís si un descans és massa llarg per a la zona. Només és al prompt; l'avís no està implementat. | cicles.py:395; FulldeRuta_1002.md:77 | D (avui J) | R111 |
| R244 | Gimnàs i «altres»: `durada_min > 0`, volum 0, sense parts, i poden anar en cap de setmana. | models/franja.py:45-53; esquelet_sessions.py:382-412 | D | R072, R060 |
| R245 | L'avís de gimnàs s'emet només si el gimnàs va *abans* de la tècnica o l'activació del mateix dia. Està pendent. | Fase3.md:455 | D | resol C17 |
| R246 | Separació qualitat-gimnàs: ≥6 h, o ≥3 h si la resistència va primer. Matí + vespre és correcte. | Fase3.md:258, 337 | D | R073 |
| R247 | Material disponible per nedador (Jep: tot). Només és als docs; la fitxa no té aquest camp. | Fase3.md:486 | D | R131-R133 |
| R248 | Rangs del registre: CR-10 enter de 0 a 10; assoliment de 1 a 5; SRSS 4+4 ítems de 0 a 6; temps >0. | models/registre.py; models/historial.py:37-47 | D | R185, R192 |
| R249 | Ingestió del registre: RPE sense minuts → error; SRSS a mitges → error; capçaleres exactes; un «1:40» llegit com a hora → min:seg. **Però** els metres buits passen a 0. | ingestion/registre_setmana.py:87-183 | D | **C38** |
| R250 | Protocol del test CSS (escalfament, 400 i 200 a tota). T400 > T200, o error. Es registra abans de generar la setmana. | Manual.md:287; zones_css.py:82-85 | D | R165, R170 |
| R251 | Sense test CSS: marques provisionals d'entrenament fins al primer test. Els offsets són iguals per a tot l'equip llevat de motiu fisiològic. | metodologia_ritmes.md:63, 66 | D | alternativa a R172 |
| R252 | Resultats: la competició ha de ser al calendari (si no, error); la prova no inscrita només avisa; un resultat per competició i prova (`--substituir`); es fa `.bak`; només resultats reals; si n'hi ha diversos, compta el millor. | scripts/registrar_resultat.py:78-96; progressio.py:200-208 | D | — |
| R253 | Clau canònica de prova (lliure/crol, im/estils). Una prova del pic que no és a la fitxa compta com a S. | utils/proves.py:8-30; proves.py:121-128 | D | R194 |
| R254 | Identificador del nedador: `^[a-z0-9][a-z0-9_-]*$`, igual al nom de la carpeta i al de `nedador.json`. | rutes.py:45-55, 144-157 | D | AGENTS.md |
| R255 | Noms de fitxer: `<tipus>_<id>_<YYYY>-W<ww>.xlsx`. | rutes.py:58-60, 109-116 | D | — |
| R256 | El full de registre que ja existeix no se sobreescriu mai. `macrocicle.json` i el full de la setmana sí que se sobreescriuen, i sense `.bak`. | generar_temporada.py:331-447 | D | **C37** |
| R257 | Si falten el calendari, l'historial, els resultats o el catàleg, es fa servir una llista buida. Si falta `nedador.json`, error. | rutes.py:144-189 | D | — |
| R258 | Si hi ha `setmana_tipus`, sobreescriu `dies_disponibles`. Valors per defecte de la fitxa: dl-dj (activa l'esquelet antic), piscina 25, 105 min, terra 12.000. | models/nedador.py:151-255 | D | B08 |
| R259 | Ajustos del coach: 4 primitives (volum, classe, eliminar competició, log amb motiu de només afegir). El sistema no tria mai el volum reduït. Avui és codi mort. | generar_microcicle.py:49-484; Fase2.md:26-27, 206-283 | D | R002, M5 |
| R260 | Continuïtat (G3): si l'RPE de la setmana anterior va per sobre del pla o hi ha alertes, prioritzar la qualitat d'execució per davant de la densitat. Està pendent. | FulldeRuta_1002.md:111-117 | J | R190, B15 |
| R261 | F3-F6, pendents: base de volum mòbil de 4-6 setmanes reals; taper exponencial (−41-60% sobre el Build2); avís de salt de volum; totals d'intensitat per bloc. | Fase3.md:414-417 | D | **C36** |
| R262 | Accions per zona de resultat: blava → proposar pujar l'objectiu; vermella → revisar l'entrenament si es repeteix i cap fatiga no ho explica. | Disseny_proves_objectius.md:167-170 | D + coach | R203 |
| R263 | Planificador setmanal: s'atura per a l'aprovació del coach (`--aprovar`), desa el pla aprovat a `log_decisions/` i fa 1 reintent si no valida els límits. | Disseny_proves_objectius.md:123-130 | D | R214 |
| R264 | Format del full de piscina: una pestanya per setmana; capçalera de dia + franja + rol; columnes fixes; total; gimnàs en una línia; temps m:ss. | Fase3.md:110-114, 370; Manual.md:147 | D | R064 |
| R265 | Jutge: si un exercici s'assembla a una referència correcta, no es rebutja per terminologia; «sense referències» no és motiu de rebuig; les referències que trenquen normes s'exclouen. | referencies.py:17-19, 243-259; jutge.py:151-159 | J | R216 |
| R266 | Plantilla d'exercici del jutge: sèries × distància, execució i intensitat són obligatòries; l'execució no repeteix la intensitat. | jutge.py:104-109 | D | R142 |

**Buits nous.**
- **B29.** Lesions, malalties, vacances, absències i sessions no fetes: cap regla. Només hi ha les primitives d'ajust (R259), que són codi mort, i l'edició a mà del full.
- **B30.** Es llegeixen tots els `registre_*.xlsx` sense eliminar duplicats.
- **B31.** No hi ha historial de plans generats ni de tests CSS (FulldeRuta_1002.md:53-54). Sense aquest historial, R069 i B16 no són possibles.

---

## 2. Classificació dels mòduls

**Criteri aplicat.** La tasca demana 3 categories, però l'inventari i la guia en fan servir 4. He repartit «adaptar» així:
- **REUTILITZAR**: la lògica sobreviu amb canvis mecànics (separar IO, passar constants a paràmetres de la spec, injectar el rellotge), protegida amb tests de caracterització. No s'importa mai de v1: es copia.
- **REESCRIURE**: la lògica es torna a derivar de la spec. Se'n poden aprofitar funcions concretes, que s'indiquen.

Vegeu Q1.

### Nucli de planificació

| Mòdul | Decisió | Capa | Motiu |
|---|---|---|---|
| `agents/pla_setmanal.py` | REESCRIURE | domain (plantilla, pressupost, papallona) + application (text del prompt) | És la cadena de regles amb conflictes C01-C04 i C24-C27. Aprofitable: `assignar_metres_parts` (residu més gran) i els casos de test del comptador de papallona. |
| `agents/esquelet_sessions.py` | REESCRIURE | domain | Hi conviuen dues lògiques incompatibles (C21); l'esquelet antic se substitueix per una plantilla per nedador (ADR-011). |
| `agents/generar_microcicle.py` | REESCRIURE | application (orquestració) + domain (correccions) + infrastructure (LLM) | Monòlit amb codi mort i defectes silenciosos (R236, R237). Aprofitable: detecció de farciment, normalització de noms de part i `ajustar_volum`. |
| `agents/generar_macrocicle.py` | REESCRIURE | domain (volums) + application | Defecte de l'ACWR, volums en conflicte (C09-C11, C22) i regeneració a cada execució (B17). |
| `agents/periodificacio.py` | REUTILITZAR | domain | És pura i està provada. Cal treure `avui()`, unificar la mesura del doble pic (C13) i caracteritzar R225-R227. |
| `agents/context_competicio.py` | REUTILITZAR (només `validar_espaiat_pics_a`) | domain | La resta és codi mort. Cal alinear-lo amb C13 i comprovar R229. |
| `agents/validacio.py` | REESCRIURE | domain (verificador) | El patró d'avisos purs és bo, però al flux real les validacions no reben dades (§1.3). Cal redissenyar-ne les entrades amb l'historial. |
| `agents/taper.py` | DESCARTAR | — | Els seus dies (14/3/1) no governen res i el flag `retaper` no té efecte (D17, P21). |
| `agents/cicles.py` | REUTILITZAR | domain; la taula per al prompt → application | El parser i el càlcul de temps i descansos estan ben provats. Cal corregir la descripció de R113 a la spec. |
| `agents/ritme_objectiu.py` | REUTILITZAR (progressió i forma) | domain | El càlcul és pur i recent. La inserció a la sessió es reescriu i depèn de P12 i C20. |
| `agents/tecnica.py` | REUTILITZAR | domain (selecció) + infrastructure (càrrega del JSON) | Cal arreglar la rotació un cop el bloc tingui un id estable (B17). |
| `agents/seleccio_model.py` | DESCARTAR | — | La metodologia per distància queda superada per la metodologia per fase o focus (C18, C32). |
| `agents/zones_css.py` | REUTILITZAR | domain | Pur, petit i provat. |
| `agents/carrega.py` | REUTILITZAR | domain | Pur. Cal connectar-hi les exclusions (B16). |
| `agents/recuperacio.py` | REUTILITZAR | domain | Pur; els llindars passen a la spec. |
| `agents/proves.py` | REUTILITZAR | domain | Pur. Cal corregir la piscina del pic en els blocs mixtos (R232). |
| `agents/progressio.py` | REUTILITZAR | domain (càlcul) + interfaces (`format_informe`) | |
| `agents/jutge.py` | REUTILITZAR (condicionat a M3) | application (port i prompt) + infrastructure (HTTP) | L'esquema i el parser són aprofitables. El glossari que rep té el significat d'A2/A3 invertit (C33). |
| `agents/referencies.py` | REUTILITZAR (condicionat a M3) | infrastructure (BM25) + domain (normalització d'abreviatures) | |
| `agents/diccionari.py` | REUTILITZAR | domain (glossari) + infrastructure (lectura) | |

### Infraestructura, models i utilitats

| Mòdul | Decisió | Capa | Motiu |
|---|---|---|---|
| `llm/client.py` | REESCRIURE | infrastructure | Trivial, però fa `load_dotenv(override=True)` en importar-se. A v2 ja hi ha `infrastructure/secrets.py`, que es posa darrere un port `LLMClient`. |
| `config.py` | DESCARTAR | — | Codi mort i duplicat. |
| `rutes.py` | REUTILITZAR | domain (validació de l'id, R254) + infrastructure (rutes i IO) | |
| `models/nedador.py` | REESCRIURE | domain | És l'entitat central del model nou. Té camps obsolets i valors per defecte que porten regles (R258, B08). Serveix de referència de camps. |
| `models/sessio.py` | REESCRIURE | domain | Percentatges redundants; l'estructura canvia (G3). |
| `models/macrocicle.py` | REESCRIURE | domain | La setmana sense any és la causa dels defectes de §1.3. Dates com a text i camps heretats de l'Excel. |
| `models/calendari.py` | REUTILITZAR | domain | Recent i provat (R233). |
| `models/franja.py` | REUTILITZAR | domain | |
| `models/registre.py` | REUTILITZAR | domain | `etiqueta_cr10` és codi mort. |
| `models/historial.py`, `models/resultat.py` | REUTILITZAR | domain | |
| `models/decisio.py` | DESCARTAR | — | Lligat a `seleccio_model`. |
| `utils/dates.py` | REUTILITZAR | domain | Ha de treballar amb una setmana ISO *amb any*. La lectura del rang de dates sobra. |
| `utils/temps.py`, `utils/proves.py` | REUTILITZAR | domain | |

### Ingestió, exportació, prompts i dades

| Element | Decisió | Capa o destí | Motiu |
|---|---|---|---|
| `ingestion/xlsx_to_json.py` | DESCARTAR | — | Migració d'un sol ús. Excepció possible: una importació puntual de Lou, Cris i Pere des de `Provisional26-27.xlsx` (Q5). |
| `ingestion/registre_setmana.py` | REUTILITZAR | infrastructure (Excel) + domain (validació de files) | Depèn de G8 (l'Excel com a entrada). Cal corregir els metres buits → 0 (C38). |
| `ingestion/migracio.py` | DESCARTAR | — | Migració ja feta. |
| `export/mesocicle_excel.py` | REUTILITZAR | infrastructure | La regla de la rutina d'espatlla (R064) va al domini. Format a R264. |
| `export/registre_excel.py` | REUTILITZAR | infrastructure | Depèn de G8. |
| `prompts/generar_microcicle.md` | REESCRIURE | application (plantilla) | Té regles incrustades i contradictòries (C05-C07, C18). |
| `tecnica/biblioteca_tecnica.json` | REUTILITZAR (dades) | `data/` | Abans cal la revisió del coach i resoldre C01, C29 i el nivell inexistent (R241). |
| `tecnica/diccionari.json` | REUTILITZAR (dades) | `data/` | Abans cal corregir A2/A3 (C33) i «Ei» (P03). |
| `data/raw/jutge/casos.jsonl` | REUTILITZAR | `tests/` (golden) | Només 7 casos. |
| `data/competicions.json`, `jep/{nedador,calendari,historial}.json` | REUTILITZAR | `data/` | No són a git: cal copiar-les del disc i validar-les contra el model nou. |
| `jep/resultats_vi.json` | REUTILITZAR | `data/jep/resultats.json` | Q7. |
| `jep/macrocicle_referencia.json`, `jep/setmanes/*.xlsx` | REUTILITZAR | `tests/` (golden i referència) | |
| `jep/registres/*.xlsx`, `log_decisions/*`, `nedador.json.bak`, `data/processed/jutge/*` | DESCARTAR | — | Buits, obsolets o lligats al jutge. |
| `data/raw/*.xlsx`, `data/raw/docs/*` | REUTILITZAR com a font | referència (fora de `src/`) | |

### Scripts, tests i arrel

| Element | Decisió | Capa | Motiu |
|---|---|---|---|
| `scripts/generar_temporada.py` | REESCRIURE | application (cas d'ús) + interfaces (CLI) | Barreja orquestració, regles (R022) i consola. |
| `scripts/registrar_test_css.py`, `registrar_resultat.py` | REESCRIURE | interfaces + application | Han de quedar com a CLI primes. Les regles (R250, R252) van al cas d'ús. |
| `scripts/informe_progressio.py` | REUTILITZAR | interfaces | Ja és una CLI prima. |
| `scripts/avaluar_jutge.py` | REUTILITZAR (condicionat a M3) | interfaces | |
| `scripts/prova_generacio_microcicle.py`, `migrar_a_carpetes.py` | DESCARTAR | — | |
| `tests/` | REUTILITZAR de manera selectiva | `tests/unit` | Només com a caracterització dels mòduls REUTILITZAR, revisats contra la spec. |
| `Makefile`, `errors*.txt`, `egg-info`, `.aider*` | DESCARTAR | — | |

**Resum** (comptant per element de les taules): 36 a REUTILITZAR (5 condicionats a M3 o a G8), 13 a REESCRIURE i 16 a DESCARTAR.

---

## 3. Regles de negoci: determinisme i conflictes

### 3.1 Determinista o judici LLM

**Criteri.** Una regla és D si un programa la pot comprovar o calcular amb les dades estructurades. És J si demana interpretar text o triar entre opcions vàlides. La columna «dura/tova» de `regles.md` és ortogonal a aquesta.

| Secció | D | J (es queden a l'LLM) | Reclassificacions proposades |
|---|---|---|---|
| 1. Principis | R001-R004, R006 | — | **R005 → D**: el codi ja garanteix que l'LLM no toqui els camps deterministes; només el text és LLM. |
| 2-3. Calendari i periodització | R007-R034, R220-R234 | — | — |
| 4-5. Volum i taper | R035-R064, R220-R223 | — | — |
| 6. Organització setmanal | R065-R077, R244-R247 | — | — |
| 7. Estructura de la sessió | R078-R081, R084-R090, R092-R094 | R083 (cada exercici a la part que li correspon), R095 (no repetir), R096 (sessions del dia) | **R082 → D** (les sumes per part es poden calcular). **R091 → D** (Rec/A1 i sense cames: `_RE_CAMES` ja existeix). |
| 8. Pressupost | R097-R107 | R109 (descripció per fase) | **R108 → D parcial** (formes numèriques: 4-6x15-25 d/45"). |
| 9. Descansos | R110-R117, R242 | — | **R243 → D**. **R111 i R113**: actualitzar segons §1.4. |
| 10. Papallona i estils | R118-R128 | R129 (estils segons les proves) | **R130 → D** (suau i curt = intensitat + distància). |
| 11. Material | R134 | — | **R131, R132 i R133 → D**: estil, material i metres ja es detecten a `cicles.py:90-135`. Resol P19. |
| 12. Tècnica | R136-R139, R141 | R135 (premisses tècniques) | **R140**: el transport és D; l'aplicació, J. |
| 13. Format | R142-R145, R147, R148, R150-R152, R154, R155 | R149 (terminologia real) | **R146 → D** (regex; tanca C06). **R153 → D parcial**. |
| 14. Generació | R156-R162, R164 | R163 (seguir el few-shot) | — |
| 15-18. Zones, sèrie objectiu, càrrega, progressió | R165-R209, R248-R253, R262 | — | — |
| 19. Metodologia | R210, R211, R213 | R212 | **R214 → D (límits) + J (tria del focus)**. **R215 → D** (és pas de dades). |
| 20. Jutge | R218, R266 | R216, R217, R219, R265 | — |
| Dades i coach | R254-R259, R261, R263, R264 | R260 | — |

**Resultat:** al voltant de 250 regles D i 14 J. Els punts de judici que realment queden a l'LLM, i que l'ADR-006 hauria de tancar, són quatre:
1. Redactar els exercicis dins d'una estructura i un pressupost ja fixats: R083, R095, R096, R109, R129, R135, R149 i R163.
2. Triar el focus de la sessió, si s'adopta R214.
3. El jutge semàntic, si es manté (R216-R219, R265).
4. Els textos justificatius (R005), que són opcionals.

**Regles «dures» que no es fan complir.**
- R070 (la tècnica no baixa a A1 el dia de tècnica), els màxims de R111 i R147 (estils de 300 i 400 acceptats).
- Totes les que provoquen reintent (R051, R093, R115, R139…): després de 2 reintents la sessió s'exporta igualment (B02).
- La spec ha de distingir entre **bloquejant** (el pla no surt) i **amb reintent i avís**.

### 3.2 Conflictes

**Tipus:**
- **Bloqueig**: dues regles dures que no es poden complir alhora. El sistema entra en bucle de reintents o genera per construcció el que ell mateix rebutja.
- **Definició**: el mateix terme vol dir dues coses.
- **Font**: la documentació i el codi diuen coses diferents (es resol amb P01).
- **Silenciós**: una regla guanya sense cap avís.

| Conflicte | Tipus | Regles | Efecte |
|---|---|---|---|
| **C01** | **Bloqueig** | R070/R099/R107 ↔ R136/R138 | Exercici obligatori de biblioteca a A2 amb pressupost A2 = 0 i sense possibilitat de retall: s'esgoten els reintents. |
| **C02** | **Bloqueig** | R174/R179 ↔ R099/R100 | La sèrie objectiu A3 fixa supera el 5% d'A3 de l'aeròbica: el pressupost queda a 0 i la sessió infringeix el límit per construcció. |
| **C04** | **Bloqueig** | R130 ↔ R118/R122 | Estils «suaus» amb màxim de papallona 0: el retall no pot arribar a 0 i hi ha reintent. |
| **C11** | **Bloqueig** | R036 ↔ R039 | La descàrrega (0,7×) no es compleix mai si la càrrega és <17.143 m (Base i Build). |
| **C12** | **Bloqueig** (latent) | R028 ↔ R033 | La periodització genera 4 setmanes de càrrega seguides, i la validació ho prohibiria si s'executés (§1.3). |
| **C16** | **Bloqueig** | R060 ↔ R059 | Competició en diumenge: activació a l'aigua el dissabte, quan el cap de setmana no es neda. |
| **C21** | **Bloqueig** | R053/R056 ↔ R068 | Esquelet antic en Build: tots els dies són de qualitat, quan n'hi ha d'haver un. |
| **C03** | **Bloqueig** | R088 ↔ R174/R057 | A3 a 2 dies d'una B, quan les cames A3 ho prohibeixen. |
| **C05** | **Bloqueig** (prompt) | R143 ↔ R146 | El prompt alhora demana i prohibeix distàncies dins de l'execució. El codi mateix ho incompleix. |
| **C20** | Definició | R179 ↔ R166/R111 | La sèrie objectiu és A3 i ritme de cursa alhora. |
| **C33** *(nou)* | **Definició, bloqueja el glossari** | diccionari.json:78-80 i jutge.py:77 (A3 = llindar, A2 = aeròbic mitjà) ↔ R166/R111 (A2 = CSS = llindar, A3 = VO2) | El jutge rep el glossari amb les zones invertides. |
| C13 | Definició | R011 ↔ R011 | Dues mesures del doble pic. |
| P23 | Definició | — | «Qualitat» com a tipus de setmana i com a rol. |
| C08, C09, C10, C14, C15, C17, C22, C23 | Silenciós o incoherència | vegeu `regles.md` | C09, C10 i C12 són avui latents (§1.3). |
| C24-C32 | Font | vegeu `regles.md` | Es resolen amb P01 (ADR-001). |
| **C34** *(nou)* | Silenciós | R224 ↔ R017/R059 | Una B en dimecres redueix el volum de la setmana però no té activació ni setmana post-competició. |
| **C35** *(nou)* | Font | R230 (júnior fora d'abast) ↔ R033 | La validació aplica una regla de júnior, però el contingut es genera com a absolut. |
| **C36** *(nou)* | Font | R261 (F4, taper exponencial sobre el Build2) i Fase3.md:48 (−30-40%) ↔ R037 (base fixa de 13.000) | Tres definicions del taper. |
| **C37** *(nou)* | Silenciós | R252 i `registrar_test_css` (fan `.bak`) ↔ R256 | `macrocicle.json` i el full de la setmana se sobreescriuen sense `.bak`. |
| **C38** *(nou)* | Silenciós | registre_setmana.py:7-8 («mai valors per defecte») ↔ R249 | Els metres buits passen a 0. |

**Grups de regles que es bloquegen entre elles.** Si es resol el nus central, cauen la majoria dels conflictes del grup.

1. **Sèrie objectiu**. Nus: P12 (zona pròpia «ritme de cursa» o A3). Conflictes: C02, C03, C19, C20, B13, B22, R174 (tercera P).
2. **Tècnica a Rec/A1 o biblioteca**. Nus: P13. Conflictes: C01, D07, R070, R107.
3. **Taper i recuperació**. Nus: P08 + P21. Conflictes: C10, C14, C15, C22, C23, C36, R057, R222.
4. **Volum, terra i descàrrega**. Nus: P07 + P15. Conflictes: C08, C09, C11, R039, R040, R223.
5. **Papallona i estils**. Nus: P05 + P14. Conflictes: C04, C07, C24, B22.
6. **Glossari de zones i termes**. Nus: C33 + P23 + P03. Bloqueja la spec del domini.
7. **Dies variables**. Nus: P16. Conflictes: C21, B08, R053-R056, R258, i els 3 nedadors sense dades.

---

## 4. Decisions a registrar com a ADR (`docs/decisions/`)

Els valors de negoci (pressupostos, volums, límits de papallona) van a la spec, no a un ADR. A ADR només hi van les decisions estructurals o transversals.

| # | Títol | Frase |
|---|---|---|
| ADR-001 | Font de veritat de les regles heretades | Quan la documentació i el codi de v1 divergeixen (C24-C32), decidir quina mana o que el coach decideix cas per cas (P01). |
| ADR-002 | Capes i ubicació de les specs | Fixar 4 capes amb `interfaces` (com diu AGENTS.md i aplica import-linter) en lloc de les 3 de la guia, i triar `specs/` o `docs/spec/` (G1, G2). |
| ADR-003 | Criteri de reutilització i migració sense importar v1 | Definir 3 categories (o 4, amb «adaptar»), i que el codi de v1 entri només copiat i amb tests de caracterització, mai importat. |
| ADR-004 | Proveïdor LLM i port `LLMClient` | Triar Anthropic al núvol, llama.cpp local o tots dos darrere un sol port. Secrets només via `infrastructure/secrets.py`, mai `load_dotenv` en importar. |
| ADR-005 | El sistema avisa, no modifica | Cap càlcul canvia el pla sense decisió del coach: el guard ACWR passa a avís (C09) i els ajustos són primitives amb log de només afegir (R259, M5). |
| ADR-006 | Punts de judici LLM i fallades | Llista tancada dels punts on intervé l'LLM (§3.1), problemes bloquejants o amb reintent, i què passa si l'LLM falla o no retorna res (R006, R236, B01, B02). |
| ADR-007 | Model temporal | Setmana com a `(any ISO, setmana)` o `YYYY-Www`, dates reals en lloc de text, rellotge injectat i temporada per nedador (§1.3, R022, B28). |
| ADR-008 | Persistència i estabilitat del pla | El macrocicle es persisteix i es versiona en lloc de regenerar-se, amb ids de bloc estables i `.bak` o historial de plans (B17, B31, C37). |
| ADR-009 | Glossari de zones d'intensitat | Significat únic d'A1-A3, AeM, MPLA i TOLA, i si «ritme de cursa» és una zona pròpia (C20, C33, P12). |
| ADR-010 | Nedadors sense zones | Com es prescriu «zona + descans» en mode RPE o amb marques provisionals (B03, R172, R251, G7). |
| ADR-011 | Plantilla setmanal per nedador | Substituir l'esquelet antic per plantilles de 3-6 dies derivades de `setmana_tipus` (B08, C21, P16). |
| ADR-012 | Estructura de la sessió | Com encaixen les parts fixes (sèrie de control, sèrie objectiu, cames, velocitat alàctica) i el dia de tècnica amb l'«estructura fixa de 4 blocs» d'AGENTS.md (G3). |
| ADR-013 | Model de taper i recuperació | Una sola definició del taper (periodificació, `taper.py` o F4 exponencial) i del doble pic (C13-C15, C36, P08, P21). |
| ADR-014 | Metodologia per fase o focus | Retirar la metodologia per distància a favor de fase o focus amb límits deterministes (C18, C32, P22, R214). |
| ADR-015 | Formats d'E/S i dades versionades | Si l'Excel de registre és una entrada admesa malgrat «Excel = només sortida» (G8), i si les dades dels nedadors es versionen a git (v1 les ignorava). |
| ADR-016 | Jutge semàntic | Dins o fora de v2, i amb quin paper (filtre o mode ombra) segons R218 i un joc golden més gran (M3). |

---

## 5. Ordre proposat de les primeres specs

Cada spec fa servir la plantilla `specs/_TEMPLATE.md`. Abans de cadascuna s'han de resoldre els ADR i les preguntes que bloquegen.

1. **001 — Model de domini i glossari.**
   - Contingut: entitats Nedador, Prova (clau canònica), Catàleg/Inscripció/Competició, Temporada, Setmana ISO amb any, Fase, Bloc, Microcicle, Sessió/Part/Exercici i Zona. Invariants (R142-R145, R233, R248, R254) i *roundtrip* JSON amb les dades del Jep.
   - Es reutilitzen: `models/calendari`, `franja`, `registre`, `historial`, `resultat`, `utils/*`, i la part pura de `rutes`.
   - Bloquegen: ADR-007 i ADR-009 (C33), P23, P03, G3/ADR-012 (forma de la Sessió).
2. **002 — Calendari, pics i objectius.**
   - Contingut: classes A/B/C, pics, doble pic, espaiat, controls, validacions dels objectius.
   - Es reutilitzen: `proves.py`, `context_competicio.validar_espaiat_pics_a`.
   - Bloquegen: P17 (C13), P18, R230 (abast), R232 (Budapest).
3. **003 — Periodització.**
   - Contingut: fases cap enrere des de cada A, blocs, tipus de setmana, persistència estable del pla.
   - Es reutilitza: `periodificacio.py`, amb R225-R227 caracteritzades.
   - Bloquegen: ADR-008, ADR-013 (P08, P21), P10.
4. **004 — Zones, ritmes i descansos.**
   - Contingut: CSS, zones, marques provisionals o mode RPE, temps d'exercici, descans mínim i màxim per zona.
   - Es reutilitzen: `zones_css.py`, el parser i el temps de `cicles.py`.
   - Bloquegen: ADR-009, ADR-010. Té pocs conflictes, i es pot fer en paral·lel amb la 003.
5. **005 — Volum setmanal i mesocicle.**
   - Contingut: volums per tipus de setmana, terra, descàrrega, B, avisos ACWR i de càrrega sobre l'historial real.
   - Bloquegen: ADR-005, P07, P15 i el grup 4 de §3.2.

Després venen la plantilla setmanal i la sessió (ADR-011 i ADR-012, grups 1, 2 i 5), el verificador i l'exportació, en l'ordre de la guia.

---

## Preguntes obertes

Les preguntes **M1-M7** (`moduls.md`) i **P01-P25** (`regles.md`) continuen obertes. Les que bloquegen les primeres specs són P01, P03, P07, P08, P10, P12, P15, P16, P17, P21 i P23. Les preguntes noves:

- **Q1. Categories.** La tasca en demana 3 i la guia i l'inventari en fan servir 4. He integrat «adaptar» a REUTILITZAR o REESCRIURE segons el criteri de §2. Hi estàs d'acord?
- **Q2 (G1).** Les specs han d'anar a `specs/` (AGENTS.md; ja hi ha la plantilla) o a `docs/spec/` (CLAUDE.md)?
- **Q3 (G2).** La guia diu 3 capes, amb la CLI a infraestructura; AGENTS.md i import-linter en fan 4, amb `interfaces`. Confirmo les 4?
- **Q4 (G8).** AGENTS.md diu «Excel = només sortida», però a v1 el coach omple el full de registre en Excel i el sistema el llegeix. Es manté l'Excel com a entrada, o v2 llegeix el registre en un altre format?
- **Q5.** D'on surten les dades de Lou, Cris i Pere (fitxa, dies, calendari, marques)? Es fa una importació puntual des de `Provisional26-27.xlsx`, o es creen a mà?
- **Q6.** A v2, les dades dels nedadors es versionen a git? A v1 eren a `.gitignore`.
- **Q7.** `resultats_vi.json` (100 L, 78,4 s, de vídeo) és un resultat real que s'ha de migrar a `resultats.json`, tenint en compte R252 («només resultats reals»)?
- **Q8 (C33).** Quin és el significat bo de les zones: A2 = llindar (codi i metodologia) o A3 = llindar (diccionari del coach)?
- **Q9 (G3).** «Estructura fixa: escalfament, tècnica, nucli, tornada a la calma» vol dir que desapareixen les parts fixes de v1 (sèrie de control, sèrie objectiu, cames, velocitat alàctica, recuperació), o que van dins del nucli?
- **Q10.** Quan existeixi la spec del domini, cal repetir aquesta auditoria contra ella, tal com demana l'ordre de la guia?
- **Q11 (C35).** El júnior és fora d'abast (Fase2.md:14)? Si ho és, R033 es simplifica.
- **Q12 (G7).** AGENTS.md diu «zona + descans; cada nedador aplica el seu ritme», però la sèrie objectiu de v1 escriu el ritme explícit a l'execució («38,3 s per 50»). Es manté aquesta excepció?
- **Q13.** Els pendents de v1 entren a l'abast de v2: continuïtat G3 (R260), F3-F6 (R261), historial de plans (B31) i tractament d'absències i lesions (B29)?
