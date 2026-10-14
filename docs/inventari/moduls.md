# Inventari de mòduls — BlondSwim v1

*Fase 0 · 2026-10-14 · Font: `../ws_blondswim` (només lectura, `main` a 565792c). Rutes relatives a `src/blondswim/` llevat que s'indiqui.*

## Criteris de les columnes

- **Lògica + IO**: el mateix mòdul calcula i també llegeix o escriu fitxers, crida una API o la xarxa. «Només IO» vol dir que no hi ha lògica de domini que separar.
- **Cadena de regles**: el mòdul conté (com a constants o branques) regles de planificació de `regles.md`. Entre parèntesis, les principals.
- **Tests**: «sí (N)» = fitxer de test propi amb N tests; «indirectes» = no en té de propi però el proven els tests d'altres mòduls; «buit» = el fitxer de test existeix però és buit. Els 676 tests de v1 passen (`pytest -q`, executat sense escriure res a v1).
- **Proposta** (criteris del `ClaudeGuides/…Pla d'acció…`, §3): barreja lògica i IO → separar-los; depèn de la cadena de regles i les regles hi estan entrellaçades → reescriure; és pur, té tests i les regles són constants que es poden extreure a l'especificació → adaptar o reutilitzar. Vegeu la pregunta oberta M1.

---

## 1. Nucli de planificació (cadena de regles)

| Fitxer | Què fa | Lògica + IO | Cadena de regles | Tests | Proposta | Motiu |
|---|---|---|---|---|---|---|
| `agents/pla_setmanal.py` (1.025 l.) | Organitza la setmana: tipus de setmana, rols per dia, pesos, parts i metres, cames, sèrie de control, pressupost d'intensitat, papallona, estils, material i els textos del prompt. | no | sí (R016-R018, R047, R059-R068, R078-R134) | sí (59 + 25 de `test_noms_parts`) | **reescriure** | És la cadena de regles mateixa. Hi barreja valors, heurístiques de text (regex de papallona) i redacció del prompt, i els valors xoquen amb la documentació (C24-C27). Després de l'auditoria es poden aprofitar `assignar_metres_parts` (residu més gran) i els casos de test del comptador de papallona. |
| `agents/esquelet_sessions.py` | Construeix les sessions buides de la setmana (plantilla de 5 dies o esquelet antic): volum de cada sessió, parts, sèrie de control, exercicis de tècnica i sessions de gimnàs. | no | sí (R046-R049, R053-R056, R063, R065, R077) | sí (14 + 11 de `test_sessions_multiples`) | **reescriure** | Conté dues lògiques amb regles incompatibles (C21). L'esquelet antic és anterior a la Fase H i és el que s'aplicaria a Lou, Cris i Pere (B08). |
| `agents/generar_microcicle.py` (1.718 l.) | Orquestra la generació: construeix el prompt, fa una crida a l'LLM per sessió, aplica la resposta, fa les correccions automàtiques i les validacions, reintenta i desa logs. També conté les primitives d'ajust del coach. | **sí** (API d'Anthropic, lectura del prompt, escriptura de logs) | sí (R092-R095, R102, R106-R107, R139, R156-R164, R211) | sí (45) | **reescriure** | És un monòlit que barreja domini, aplicació i infraestructura. Té codi mort: `actualitzar_classe_competicio`, `eliminar_competicio`, `actualitzar_volum_microcicle` i `guardar_log_ajust` no es criden enlloc. Peces candidates a adaptar amb especificació: detecció de farciment, normalització de noms de part i `ajustar_volum`. |
| `agents/generar_macrocicle.py` | Crea el macrocicle de la temporada i el mesocicle del bloc actual amb els volums setmanals (taula per fase, descàrrega, B, terra, post-competició), el guard ACWR i l'enriquiment LLM de `fase_objectiu`. | **sí** (crida LLM) | sí (R021, R031-R042) | sí (24) | **reescriure** | Regles de volum en conflicte (C09-C11, C22). **Defecte**: al guard ACWR, `micro.setmana` és la setmana ISO sense any, de manera que `micro.setmana // 100` sempre val 0 i l'historial real no es consulta mai (línies 507-527). A més, el macrocicle es regenera a cada execució (B17). |
| `agents/periodificacio.py` | Assigna la fase de cada setmana ISO comptant enrere des de cada A (doble pic inclòs) i agrupa les setmanes en blocs amb descàrrega. | no (només llegeix el rellotge a `avui()`) | sí (R011, R023-R030) | sí (14) | **adaptar** | Funció pura, acotada i provada. Cal alinear-la amb l'especificació (mesura del doble pic C13, bloc d'1 setmana C12, Transició C14) i treure `avui()` del domini. |
| `agents/taper.py` | Calcula els dies de taper i de recuperació per classe i detecta els candidats a re-taper. | no | sí (R020, R057) | sí (11) | **descartar** | Només el fa servir `validar_coherencia_taper`, que en el flux real no salta mai (vegeu `validacio.py`). Els seus dies (14/3/1) no governen la planificació (D17, P21). Si l'especificació els manté, cal reescriure'l. |
| `agents/context_competicio.py` | Valida l'espaiat entre competicions A (màxim 3, ≥8 setmanes, doble pic), detecta candidats a re-taper i resumeix el calendari. | no | sí (R009-R011) | sí (9) | **adaptar** | `validar_espaiat_pics_a` és útil, però mesura el doble pic diferent que la periodificació (C13). `detectar_candidats_retaper` i `classificar_pics` són codi mort. |
| `agents/validacio.py` | Genera avisos de descàrrega periòdica, d'ACWR del volum planificat, de coherència amb el taper i de franges natació/gimnàs. | no | sí (R033, R043, R044, R073, R074) | sí (13) | **adaptar** | El patró (funcions pures que retornen avisos) encaixa amb el verificador de v2. Però l'ACWR avisa en tot taper (C10) i només avalua el mesocicle generat sense historial; `validar_coherencia_taper` depèn de `competicio_test_oficial`, que només omple la ingestió d'Excel; i `calcular_volums_setmanals_historial` és codi mort. |
| `agents/cicles.py` | Llegeix la notació de descans, calcula el temps per exercici i per sessió, aplica el descans mínim per zona, corregeix i valida descansos i genera la taula per al prompt. | no | sí (R110-R117, R173) | sí (28) | **adaptar** | El càlcul pur (parser, temps) està ben provat i és reutilitzable. Les taules de descans han de sortir de l'especificació i la taula per al prompt, de la capa d'aplicació. |
| `agents/ritme_objectiu.py` | Prescriu cada setmana les sèries de ritme objectiu (objectiu, forma, progressió segons els registres) i les insereix com a part fixa. | no | sí (R174-R184) | sí (10) | **adaptar** | Lògica pura, recent i provada. Cal resoldre l'etiqueta A3 i la interacció amb el pressupost i les competicions (C02, C03, C20). La inserció a les sessions depèn de `pla_setmanal`. |
| `agents/tecnica.py` | Tria de manera determinista els exercicis de la biblioteca per rol, fase i proves del nedador. | **sí** (llegeix el JSON de la biblioteca, amb memòria cau) | sí (R136-R137) | sí (9) | **adaptar** | Cal separar la càrrega del JSON. La rotació per bloc no funciona perquè depèn de l'id del mesocicle, que sempre és `meso_1` (B17). Hi ha conflicte d'intensitats amb la tècnica (C01). |
| `agents/seleccio_model.py` | Tria la metodologia segons la distància de la prova i amplia la justificació amb l'LLM. | **sí** (crida LLM) | sí (R005, R210) | sí (30) | **descartar** | El disseny la substitueix per una metodologia per fase o per focus de sessió (R213-R215). Els llindars són d'elit i contradiuen el pressupost al prompt (C18, C32). |
| `agents/zones_css.py` | Calcula el CSS i les zones de ritme (a partir del test CSS o de la marca). | no | sí (R165-R168) | sí (13) | **reutilitzar** | Càlcul pur, petit i provat; els offsets ja són paràmetres de la fitxa. `determinar_zones_nedador` és codi mort. |
| `agents/carrega.py` | Calcula la càrrega sRPE diària i setmanal, les mitjanes exponencials aguda i crònica i l'alerta del +15%. | no | sí (R185-R187) | sí (21, compartit amb recuperació) | **reutilitzar** | Pur i provat; els llindars passen a paràmetres. Cal cablejar les exclusions de la base (B16). |
| `agents/recuperacio.py` | Genera les alertes de SRSS i de sèrie de control, la regla de decisió i l'avís de dades incompletes. | no | sí (R188-R191) | sí (a `test_carrega_recuperacio`) | **reutilitzar** | Pur i provat; els llindars són provisionals i han d'anar a l'especificació. |
| `agents/proves.py` | Calcula els pics del calendari, els pesos P/S, el perfil per durada i les competicions de control, i valida els objectius. | no | sí (R012-R013, R194-R197) | sí (17) | **reutilitzar** | Pur, provat i d'un disseny recent. Depèn de `SETMANES_DOBLE_PIC` de la periodificació (s'ha d'unificar amb C13). |
| `agents/progressio.py` | Calcula les bandes, les zones, el calibratge, la projecció i el ritme de cursa de referència, i genera el text de l'informe. | no (genera text, sense IO) | sí (R199-R204) | sí (17) | **adaptar** | El càlcul és reutilitzable; cal separar `format_informe` (presentació). |
| `agents/jutge.py` | Jutge semàntic dels exercicis a través d'una API compatible amb OpenAI (llama.cpp local): prompt, esquema i lectura de la resposta. | **sí** (HTTP amb `urllib`) | sí (R216-R219) | sí (10) | **adaptar** | Cal posar el client HTTP darrere un `LLMClient` i separar-ne la construcció del prompt. Avui no forma part del flux de generació (M3). |
| `agents/referencies.py` | Construeix el corpus de referències per al jutge (biblioteca, historial, JSONL), en desplega les abreviatures i hi fa cerca BM25. | **sí** (llegeix fitxers) | sí (normes R150 i abreviatures) | sí (11) | **adaptar** | La normalització i el BM25 són reutilitzables; cal separar la lectura de fitxers. Només té sentit si es manté el jutge. |
| `agents/diccionari.py` | Carrega el diccionari de l'entrenador: glossari, abreviatures, normes prohibides i vocabulari conegut. | **sí** (llegeix el JSON) | sí (R150, R151) | sí (7) | **adaptar** | Cal separar la lectura del JSON. El contingut és una bona base per al glossari de l'especificació. |

## 2. Infraestructura

| Fitxer | Què fa | Lògica + IO | Cadena de regles | Tests | Proposta | Motiu |
|---|---|---|---|---|---|---|
| `llm/client.py` | Crea el client d'Anthropic amb la clau de l'entorn i el model per defecte (`LLM_MODEL`). | només IO | no | no | **adaptar** | Cal posar-lo darrere un port `LLMClient`, comú amb el client del jutge. |
| `config.py` | Carrega `.env` i llança un error si falta `ANTHROPIC_API_KEY`. | només IO | no | no | **descartar** | No l'importa cap mòdul i duplica `llm/client.py`. |
| `rutes.py` | Deriva les rutes de les dades de cada nedador, carrega i desa JSON i valida l'identificador (= carpeta). | **sí** | no | sí (10) | **adaptar** | L'estructura de carpetes per nedador és vàlida (el Pla d'acció preveu reutilitzar les dades), però cal separar les rutes (pures) de la lectura i escriptura (infraestructura). |

## 3. Models de dades

| Fitxer | Què fa | Lògica + IO | Cadena de regles | Tests | Proposta | Motiu |
|---|---|---|---|---|---|---|
| `models/nedador.py` | Fitxa del nedador: proves, nivell i objectius, ritmes i paràmetres, factors de temps, setmana tipus, paràmetres de progressió i validacions. | no | sí (R039, R049, R071, R166, R198, R206 com a valors per defecte i validacions) | sí (1 de `test_nedador`, 17 de `test_proves_objectiu`, a més de `test_franja_registre`) | **adaptar** | Té camps obsolets o que no es fan servir (`dia_opcional`, `pics_prioritzats`, `ritmes_cursa_objectiu`, `mode_ritme`) i un valor per defecte de 4 dies que porta a l'esquelet antic (B08); hi ha regles incrustades als valors per defecte. |
| `models/sessio.py` | Exercici, part, estructura i sessió. | no | sí (R144, R145) | buit (`test_sessio.py`); indirectes | **adaptar** | Cada part té tres percentatges redundants (càrrega, qualitat, descàrrega) i el camp antic `contingut`; el docstring de 5 parts és obsolet. |
| `models/macrocicle.py` | Macrocicle, mesocicle i microcicle. | no | sí (R031) | buit (`test_macrocicle.py`); indirectes | **adaptar** | Té camps heretats de l'Excel (`competicio_test_oficial`, `test_avaluacio`, `focus_especific`, `tancament`…), `dies_qualitat` amb un comentari obsolet i dates com a text. |
| `models/calendari.py` | Catàleg comú, inscripció del nedador, competició resolta i simulacions. | no | sí (R007, R014, R015) | sí (12 de `test_calendari_capes`; `test_calendari.py` buit) | **reutilitzar** | Model en dues capes, recent i provat. |
| `models/franja.py` | Franges del dia, modalitats i slot de la setmana tipus. | no | sí (R071, R076) | sí (a `test_franja_registre`, 20) | **reutilitzar** | Petit i provat. |
| `models/registre.py` | Escala CR-10, SRSS, sèrie de control i sèrie objectiu. | no | sí (R185, R192) | sí (a `test_franja_registre` i `test_registre_objectiu_roundtrip`) | **reutilitzar** | Petit i provat. |
| `models/historial.py` | Sessió i sèrie realitzades, càrrega sRPE. | no | sí (R185) | sí (6 de `ingestion/test_historial`) | **reutilitzar** | |
| `models/resultat.py` | Resultat de competició amb parcials i braçades. | no | sí (R207) | indirectes | **reutilitzar** | |
| `models/decisio.py` | Decisió de metodologia. | no | sí | indirectes | **descartar** | Va lligat a `seleccio_model.py`. |

## 4. Utilitats

| Fitxer | Què fa | Lògica + IO | Cadena de regles | Tests | Proposta | Motiu |
|---|---|---|---|---|---|---|
| `utils/dates.py` | Dilluns de la setmana, següent dilluns i lectura del rang de dates del microcicle. | no | sí (R004) | sí (6) | **reutilitzar** | Si el model de v2 fa servir dates reals en lloc de text, la lectura del rang sobra. |
| `utils/temps.py` | Llegeix i formata temps de natació. | no | no | indirectes | **reutilitzar** | |
| `utils/proves.py` | Clau canònica de prova («100m Lliure» = «100 crol»). | no | no | indirectes | **reutilitzar** | |

## 5. Ingestió i exportació

| Fitxer | Què fa | Lògica + IO | Cadena de regles | Tests | Proposta | Motiu |
|---|---|---|---|---|---|---|
| `ingestion/xlsx_to_json.py` (1.069 l.) | Converteix els Excel del Jep (calendari, macrocicle de referència, microcicles, ritmes, pretemporada) a JSON. | **sí** | sí (font dels ritmes, mapatge de tipus de setmana, `mode_ritme`) | sí (21 + 9 de `test_microcicles`) | **descartar** | És una migració d'un sol ús amb adreces de cel·la fixes, i v1 ja té JSON com a font de veritat. Si cal tornar a importar l'historial, només s'hauria d'adaptar `convertir_pretemporada` (M4). |
| `ingestion/registre_setmana.py` | Llegeix el full de registre setmanal (sessions, SRSS, control, sèries objectiu) i valida les files. | **sí** | no | sí (7 + roundtrip) | **adaptar** | Cal separar la interpretació de les files (pura) de la lectura de l'Excel. |
| `ingestion/migracio.py` | Copia `data/processed/` a carpetes per nedador. | **sí** | no | sí (7) | **descartar** | La migració ja està feta. |
| `export/mesocicle_excel.py` | Genera el full de la piscina (setmana o mesocicle) amb parts, temps i rutina d'espatlla. | **sí** | sí (R064: on va la rutina d'espatlla; temps de `cicles`) | sí (11) | **adaptar** | Cal separar dades i format; la regla de la rutina d'espatlla ha d'anar al domini. |
| `export/registre_excel.py` | Genera el full de registre en blanc i la pestanya de sèries objectiu. | **sí** | no | indirectes (`test_registre_setmana`, roundtrip) | **adaptar** | Cal separar format i dades. |

## 6. Prompts i dades de configuració

| Fitxer | Què fa | Lògica + IO | Cadena de regles | Tests | Proposta | Motiu |
|---|---|---|---|---|---|---|
| `prompts/generar_microcicle.md` | Plantilla del prompt del redactor de sessions. | — | sí (R082-R155, ~40 regles) | indirectes | **reescriure** | Té regles incrustades que dupliquen el codi, contradiccions internes (C05-C07), una metodologia obsoleta (C18) i afirmacions sobre el que fa el codi que no són certes (C06). |
| `tecnica/biblioteca_tecnica.json` | 64 exercicis en 18 famílies amb format, proves, fases, nivell, restriccions i font. | — | sí (R136-R140) | indirectes (`test_tecnica`) | **adaptar** | La revisió del coach està pendent (Fase3.md:445); les intensitats de les dosis xoquen amb la tècnica a A1 (C01) i hi ha etiquetes de 50 papallona (C29). |
| `tecnica/diccionari.json` | Termes vàlids, prohibits (amb patró i motiu) i pendents. | — | sí (R150, R151) | sí (`test_diccionari`) | **reutilitzar** | És la base del glossari. Abans cal resoldre «Ei» (P03) i els termes pendents. |
| `data/raw/jutge/casos.jsonl` (arrel) | Casos etiquetats pel coach per avaluar el jutge. | — | sí (categories del jutge) | — | **reutilitzar** | Joc golden per a qualsevol verificador semàntic. |
| `data/competicions.json`, `data/nedadors/jep/*.json` (arrel) | Catàleg comú, fitxa, calendari, historial i macrocicle del Jep. | — | no (són dades) | — | **reutilitzar** | Coincideix amb la previsió del Pla d'acció; cal validar-les contra el model de v2. |

## 7. Scripts (arrel)

| Fitxer | Què fa | Lògica + IO | Cadena de regles | Tests | Proposta | Motiu |
|---|---|---|---|---|---|---|
| `scripts/generar_temporada.py` | Punt d'entrada principal: carrega les dades, avalua la recuperació i la progressió, periodifica, genera el mesocicle i la setmana, i exporta el full de la piscina i el registre. | **sí** | sí (R022 dates fixes, orquestració de R174, avisos) | no | **reescriure** | Barreja orquestració, sortida per consola i regles; regenera el macrocicle a cada execució (B17). |
| `scripts/registrar_test_css.py` | Registra un test CSS i actualitza les zones de la fitxa (amb còpia `.bak`). | **sí** | sí (a través de `zones_css`) | no | **adaptar** | Ha de quedar com una CLI prima sobre el cas d'ús. |
| `scripts/registrar_resultat.py` | Registra un resultat a `resultats.json`, comprovant el calendari. | **sí** | no | no | **adaptar** | Ha de quedar com una CLI prima. |
| `scripts/informe_progressio.py` | Mostra l'informe de progressió del pic actiu. | **sí** | no (delega) | no | **reutilitzar** | Ja és una CLI prima. |
| `scripts/avaluar_jutge.py` | Avalua el jutge contra els casos etiquetats i desa el detall. | **sí** | sí (R218) | no | **adaptar** | Només si es manté el jutge (M3). |
| `scripts/prova_generacio_microcicle.py` | Prova manual de generació amb dades reals del Jep. | **sí** | no | no | **descartar** | És una prova manual antiga. |
| `scripts/migrar_a_carpetes.py` | CLI de la migració a carpetes per nedador. | **sí** | no | no | **descartar** | La migració ja està feta. |

## 8. Tests (arrel)

| Fitxer | Què fa | Proposta | Motiu |
|---|---|---|---|
| `tests/` (676 tests en 37 fitxers) | Proves unitàries amb l'LLM simulat. | **adaptar** | Són una font de casos de caracterització per al patró strangler: molts codifiquen regles de v1 i s'han de revisar contra l'especificació abans de portar-los. Hi ha 3 fitxers buits (`models/test_calendari.py`, `test_macrocicle.py`, `test_sessio.py`). |

---

## Resum

| Proposta | Nombre | Fitxers |
|---|---|---|
| reutilitzar | 16 | zones_css, carrega, recuperacio, proves, models calendari/franja/registre/historial/resultat, utils dates/temps/proves, diccionari.json, casos.jsonl, dades JSON, informe_progressio |
| adaptar | 22 | periodificacio, context_competicio, validacio, cicles, ritme_objectiu, tecnica, progressio, jutge, referencies, diccionari.py, llm/client, rutes, models nedador/sessio/macrocicle, registre_setmana, mesocicle_excel, registre_excel, biblioteca_tecnica.json, registrar_test_css, registrar_resultat, avaluar_jutge (i els tests) |
| reescriure | 6 | pla_setmanal, esquelet_sessions, generar_microcicle, generar_macrocicle, prompt generar_microcicle.md, generar_temporada |
| descartar | 8 | taper, seleccio_model, models/decisio, config, xlsx_to_json, migracio, prova_generacio_microcicle, migrar_a_carpetes |

**Codi mort detectat** (no es crida des de `src/` ni `scripts/`): `config.py`, `context_competicio.detectar_candidats_retaper`, `context_competicio.classificar_pics`, `generar_microcicle.actualitzar_classe_competicio`, `eliminar_competicio`, `actualitzar_volum_microcicle`, `guardar_log_ajust`, `zones_css.determinar_zones_nedador`, `validacio.calcular_volums_setmanals_historial`. A més, `validar_coherencia_taper` només salta amb dades importades d'Excel.

**Defectes observats** (no són regles, però afecten la reutilització): el guard ACWR no consulta mai l'historial real (`generar_macrocicle.py:507-527`); la rotació de famílies de tècnica és sempre la del bloc 1, i el volum interpolat de cada fase canvia segons la data de generació (B17).

---

## Preguntes obertes

- **M1. Criteri de reescriptura.** El Pla d'acció diu «depèn de regles de la cadena antiga → reescriure», però també preveu reutilitzar els «càlculs purs: ritmes, zones, temps». He proposat **adaptar o reutilitzar** els mòduls purs i provats on les regles són constants extraïbles (cicles, zones_css, carrega, recuperacio, proves, ritme_objectiu, periodificacio) i **reescriure** on estan entrellaçades amb la lògica (pla_setmanal, esquelet, generar_*). És el criteri que es vol?
- **M2. Excel.** Es manté l'Excel com a sortida (full de la piscina) i com a entrada (full de registre), o v2 canvia de format? Això decideix si `export/*` i `ingestion/registre_setmana.py` s'adapten o es descarten.
- **M3. Jutge.** El Pla d'acció parla d'un «client de llama.cpp»; a v1 només el fa servir el jutge (`agents/jutge.py`, API compatible amb OpenAI), que no forma part del flux de generació. Entra a v2, i amb quin paper (filtre o mode ombra)?
- **M4. Historial a reutilitzar.** El Pla d'acció parla del «registre d'entrenaments 2025-26». A v1, l'historial (`historial.json`) és la pretemporada del 18/08 al 25/09/2026 (`PretemporadaSep26-27.xlsx`); les pestanyes de 2025-26 de `Provisional26-27.xlsx` no s'importen com a historial (Fase3.md:406 diu que barregen temporades i que «Gen» és una còpia de «Desc»). Quin registre s'ha de reutilitzar?
- **M5. Primitives d'ajust del coach.** `actualitzar_volum_microcicle`, `actualitzar_classe_competicio`, `eliminar_competicio` i `guardar_log_ajust` són codi mort, però responen al principi de «pla dinàmic» (Fase2.md:25-26). És un requisit de v2 o es descarten?
- **M6. Log de decisions.** Avui `guardar_log_decisio` només desa la metodologia. La guia del MVP (guia_mvp.md:86) demanava un log amb l'entrada i la regla activada. Cal especificar-lo per a v2?
- **M7. Esquelet antic.** Depèn de P16 (`regles.md`): si v2 ha de suportar nedadors amb uns altres dies, cal especificar-ne la plantilla en lloc de portar l'esquelet antic.
