# Inventari de regles de planificació — BlondSwim v1

*Fase 0 · 2026-10-14 · Font: `../ws_blondswim` (només lectura, `main` a 565792c, 2026-10-06).*

## Com llegir aquest document

**Fonts revisades:** tot el codi de `src/blondswim/` i `scripts/`, el prompt `prompts/generar_microcicle.md`, la biblioteca i el diccionari de tècnica (`tecnica/*.json`), la fitxa i el calendari del Jep (`data/nedadors/jep/`), el `README.md` i els documents de `data/raw/docs/`. La v1 **no té `CLAUDE.md`**. Els tests de v1 (676) passen.

**Rutes d'origen** (relatives a `../ws_blondswim/`):
- `agents/…`, `models/…`, `utils/…`, `export/…`, `ingestion/…`: dins de `src/blondswim/`.
- `prompt:N`: `src/blondswim/prompts/generar_microcicle.md`, línia N.
- `biblioteca` / `diccionari`: `src/blondswim/tecnica/biblioteca_tecnica.json` / `diccionari.json`.
- `Fase3.md:N`, `Manual.md:N`, etc.: dins de `data/raw/docs/`.
- `scripts/…` i `README.md`: a l'arrel.

**Tipus proposat** (és una proposta per a v2; pot no coincidir amb com ho fa v1, i quan no hi coincideix s'indica a les notes):
- **dura**: s'ha de complir sempre. Si no es compleix, el pla és invàlid i el codi l'ha de rebutjar o corregir.
- **tova**: és un objectiu, un rang orientatiu o un avís. Es pot incomplir per decisió del coach.
- **judici_LLM**: demana judici semàntic. Avui només és una instrucció al prompt o al jutge i cap codi no la comprova.

**Abast** (només els tres valors demanats):
- **global**: igual per a tots els nedadors i totes les fases. També hi entren les regles que depenen del rol de la sessió o del dia; vegeu la pregunta P02.
- **per_nedador**: depèn de paràmetres de la fitxa del nedador.
- **per_fase**: depèn de la fase o del tipus de setmana.

**Estat** (a les notes): *v1: només doc* = escrita però no implementada; *v1: només prompt* = l'LLM la rep però el codi no la comprova; *pendent* = decisió presa però no implementada; *mort* = el codi existeix però no es crida.

---

## 1. Principis i arquitectura

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R001 | L'LLM només redacta els exercicis de les sessions de natació; volums, zones, rols, pressupost d'intensitat i validacions són deterministes. | README.md:82; Architecture.md:7; Fase2.md:20 | dura | global | |
| R002 | El sistema valida i avisa; mai aplica sol un canvi de pla: les decisions de canvi són del coach. | README.md:83; Architecture.md:11; Fase2.md:26 | dura | global | Vegeu C09: el guard ACWR la incompleix. |
| R003 | L'estructura de la temporada es calcula sencera i el contingut es genera setmana a setmana. | Architecture.md:10; Fase3.md:424 | dura | global | |
| R004 | La planificació comença sempre en dilluns (mai a mitja setmana) i cada microcicle és una setmana ISO de dilluns a diumenge. | agents/generar_macrocicle.py:594; utils/dates.py:12-19; agents/periodificacio.py:8 | dura | global | |
| R005 | L'LLM pot ampliar el text de la justificació de la metodologia i el de la `fase_objectiu`, però no canvia cap camp determinista; si falla, es manté el text original. | agents/seleccio_model.py:50-173; agents/generar_macrocicle.py:167-265, 681-683; Fase2.md:25 | judici_LLM | global | |
| R006 | Si falla la crida que genera el contingut d'una sessió, la generació s'atura amb error: no hi ha alternativa determinista. | agents/generar_microcicle.py:1711-1718; Fase2.md:25 | dura | global | |

## 2. Calendari i competicions

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R007 | Les competicions són comunes (catàleg) i la classe A/B/C la fixa cada nedador al seu calendari. | models/calendari.py:1-13; README.md:33 | dura | per_nedador | |
| R008 | El calendari del nedador només conté les competicions on va. | Disseny_proves_objectius.md:23 | dura | per_nedador | |
| R009 | Hi ha d'haver com a màxim 3 competicions A per temporada (si no, avís). | agents/context_competicio.py:80-89; Fase1.md:30 | tova | global | |
| R010 | Entre dues A consecutives hi ha d'haver almenys 8 setmanes; si n'hi ha menys (i més de 4), es recomana tractar la segona com a B. | agents/context_competicio.py:108-117; Fase1.md:31-32 | tova | global | Avís; no reclassifica. |
| R011 | Dues A a 4 setmanes o menys formen un doble pic: un sol període competitiu, sense Transició entre elles, setmanes entremig de Build2 i Peak d'1 setmana abans de la segona. | agents/periodificacio.py:26-29, 147-155, 197-202; agents/context_competicio.py:98-107; Fase3.md:513 | dura | global | La distància es mesura diferent a cada mòdul (C13). |
| R012 | Un pic és una competició A o un grup de doble pic, i les proves del pic són les que el nedador neda a les A. | agents/proves.py:4-8, 67-81, 56-64 | dura | per_nedador | |
| R013 | El pic actiu és el primer pic que encara no s'ha acabat a la data de referència. | agents/proves.py:84-89 | dura | global | |
| R014 | Les simulacions (contrarellotge en entrenament) no alteren la planificació (sense mini-taper ni setmana post-competició), però compten com a punts de control de la progressió. | models/calendari.py:15-18, 166-168; scripts/generar_temporada.py:243-245; README.md:71 | dura | per_nedador | |
| R015 | Una simulació no pot ser de classe A. | models/calendari.py:76-77 | dura | global | |
| R016 | Només les competicions A i B canvien l'organització de la setmana; una C es tracta com un dia normal. | agents/pla_setmanal.py:266, 276-277 | dura | global | |
| R017 | Una setmana és de competició només si una A/B comença dissabte o diumenge; si n'hi ha els dos dies, compta el dissabte. | agents/pla_setmanal.py:280-283; Fase3.md:90 | dura | global | Les competicions que comencen entre setmana no es tracten (B04). |
| R018 | Una setmana és post-competició si una A/B va acabar el dissabte o el diumenge anteriors. | agents/pla_setmanal.py:284-285 | dura | global | |
| R019 | Es competeix en dissabte o diumenge, i els dos dies només en competicions A. | Fase3.md:165 | tova | global | v1: només doc. |
| R020 | Re-taper: si una B prioritzada cau 4 setmanes o menys després d'una A, s'hi aplica un re-taper; la càrrega de la setmana de recàrrega la decideix un control subjectiu 4-5 dies després de l'A. | agents/taper.py:71-109; Fase1.md:56; guia_mvp.md:16 | tova | per_nedador | El control subjectiu no està implementat. `detectar_candidats_retaper` és codi mort. |
| R021 | El macrocicle necessita almenys una A; si no n'hi ha, es crea igualment amb un avís. | agents/generar_macrocicle.py:139-148 | tova | per_nedador | |
| R022 | La temporada va del 2026-08-18 al 2027-07-09 per a tots els nedadors. | scripts/generar_temporada.py:64-65; Architecture.md:132 | tova | global | Valor fix; caldria per nedador (P24). |

## 3. Periodització

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R023 | La temporada es periodifica cap enrere des de cada A: Cursa, Peak de 2 setmanes, Build2 de 4, Build1 de 4 i Base la resta; les fases es retallen si la finestra és curta. | agents/periodificacio.py:24-31, 166-195; Architecture.md:87 | dura | global | |
| R024 | Després de cada Cursa hi ha 1 setmana de Transició, excepte en doble pic. | agents/periodificacio.py:204-210 | dura | global | |
| R025 | La finestra d'una A comença la setmana següent a la Transició de l'A anterior; una A que cau dins la finestra d'una altra s'ignora. | agents/periodificacio.py:143-164 | dura | global | |
| R026 | Les setmanes posteriors a l'última A es planifiquen com a Base, amb avís. | agents/periodificacio.py:212-223 | dura | global | |
| R027 | Les fases Base, Build1 i Build2 es divideixen en blocs de 4 setmanes com a màxim, tan equilibrats com es pugui i amb els llargs primer. | agents/periodificacio.py:62-74, 241-243 | dura | global | |
| R028 | L'última setmana de cada bloc és de descàrrega, excepte en un bloc d'1 setmana, que és de càrrega. | agents/periodificacio.py:256-257; Fase3.md:80 | dura | per_fase | |
| R029 | Un bloc de menys de 3 setmanes genera un avís. | agents/periodificacio.py:247-253 | tova | global | |
| R030 | Les competicions B i C no canvien la fase de la setmana. | agents/periodificacio.py:11 | dura | global | |
| R031 | Tipus de setmana segons la fase: Base = càrrega, Build = qualitat, última del bloc = descàrrega, Peak i Cursa = taper, Transició = transició. | agents/generar_macrocicle.py:275-304 | dura | per_fase | «qualitat» té dos significats (P23). |
| R032 | El test CSS es fa la primera setmana de cada bloc de Base. | agents/generar_macrocicle.py:293-294 | tova | per_fase | Freqüència contradictòria entre fonts (C30). |
| R033 | Com a màxim 3 setmanes de càrrega seguides abans d'una descàrrega en màster i absolut, i 2 en júnior (avís). | agents/validacio.py:57-127 (línia 88); Fase1.md:77 | tova | per_nedador | Depèn de la categoria. |
| R034 | La periodització es recalcula des de la setmana de generació: les setmanes passades no es replanifiquen. | agents/generar_macrocicle.py:599-607 | dura | global | Fa que el volum interpolat depengui de la data de generació (B17). |

## 4. Volum

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R035 | Volum de les setmanes de càrrega: Base 13.600-15.000 m i Build1/Build2 12.000-13.600 m, interpolat linealment al llarg de totes les setmanes de càrrega de la fase; si només n'hi ha una, el mínim. | agents/generar_macrocicle.py:21-25, 56-72; Fase3.md:84 | dura | per_fase | |
| R036 | Una setmana de descàrrega té 0,7 vegades el volum de la setmana de càrrega anterior del bloc. | agents/generar_macrocicle.py:31-32, 326-330 | dura | per_fase | |
| R037 | Peak = 13.000 × 0,60 i × 0,45 (setmanes 1 i 2), i Cursa i Transició = 13.000 × 0,5. | agents/generar_macrocicle.py:38-45, 333-338; Fase3.md:84 | dura | per_fase | |
| R038 | Una setmana amb una prova B té el volum × 0,8; si també és de descàrrega, s'aplica el menor dels dos factors (no el producte). | agents/generar_macrocicle.py:34-36, 340-347 | dura | global | |
| R039 | Terra de volum: cap setmana de càrrega, qualitat o descàrrega per sota de `volum_setmanal_min` (12.000 m per defecte); no s'aplica a taper, transició ni setmanes amb B. | agents/generar_macrocicle.py:27-29, 436-451; models/nedador.py:199; Fase3.md:86 | dura | per_nedador | |
| R040 | Si el terra aixeca una descàrrega, s'avisa (`descarrega_insuficient`): la descàrrega s'ha de fer per intensitat. | agents/generar_macrocicle.py:441-450 | tova | per_nedador | |
| R041 | La setmana posterior a una competició té com a objectiu el mínim setmanal. | agents/generar_macrocicle.py:432-434; Fase3.md:88 | dura | per_nedador | |
| R042 | Guard ACWR: el volum planificat es limita a 1,3 × la mitjana de les 4 setmanes anteriors (avís `acwr_limitat`), però mai per sota del terra. | agents/generar_macrocicle.py:47-48, 475-547 | tova (v1: aplicat) | per_nedador | Modifica el pla automàticament (C09). Té un defecte de càlcul (vegeu moduls.md). |
| R043 | ACWR del volum planificat: 0,8-1,3 és segur; per sobre d'1,3 i per sota de 0,8, avís; per sobre d'1,5, avís de risc de lesió. | agents/validacio.py:130-226; Fase1.md:76 | tova | global | |
| R044 | Dins d'una finestra de taper no hi hauria d'haver setmanes de càrrega o qualitat (avís). | agents/validacio.py:229-290 | tova | per_fase | En el flux real no salta mai (el camp que fa servir no s'omple; vegeu moduls.md). |
| R045 | Rangs setmanals per tipus: càrrega 13.600-15.000, qualitat 12.000-13.600, descàrrega 12.000-12.400, taper A setmana 1 8.400-9.800, taper A setmana 2 5.600-8.200, taper B 10.400-12.000. | Fase3.md:408 | tova | per_fase | v1: només doc. Discrepa del codi (C22). |
| R046 | El volum d'una sessió és el volum setmanal × el pes del rol / la suma de pesos de la setmana completa (una setmana parcial no concentra volum). | agents/esquelet_sessions.py:290-307 | dura | global | |
| R047 | Pesos de volum per rol: aeròbica 1,0, llarga 1,05, qualitat 0,95, tècnica 0,65, recuperació 0,6, activació 0,5. | agents/pla_setmanal.py:32-40; Fase3.md:499 | dura | global | |
| R048 | El rang de volum de cada sessió és l'objectiu ± 5%. | agents/pla_setmanal.py:42-43; agents/esquelet_sessions.py:308-314 | dura | global | |
| R049 | El volum d'una sessió no pot passar de `minuts_max_sessio` × 40 m/min. | agents/pla_setmanal.py:45-46; agents/esquelet_sessions.py:292, 306 | dura | per_nedador | Aproximació pendent de treure (FulldeRuta_1002.md:87). |
| R050 | Els volums de sessió i de part s'arrodoneixen a 100 m (conveni de l'entrenador). | agents/pla_setmanal.py:336-342; agents/esquelet_sessions.py:47-53; Manual.md:166 | dura | global | |
| R051 | El volum generat d'una sessió ha de quedar dins de [volum_min × 0,95, volum_max × 1,05]; si no, és un problema i hi ha reintent. | agents/generar_microcicle.py:41-42, 1060-1071 | dura | global | Se suma al ±5% de R048 (C08). |
| R052 | Si el volum de la setmana es desvia més d'un 5% de l'objectiu, s'avisa. | scripts/generar_temporada.py:404-408 | tova | global | |
| R053 | Esquelet antic (nedadors que no entrenen de dilluns a divendres): rols fixos per dia (dl mitjana, dt qualitat, dc mitjana, dj llarga); als altres dies, l'últim és llarga, el penúltim qualitat i la resta mitjana. | agents/esquelet_sessions.py:22-28, 56-82 | dura | per_nedador | Lògica anterior a la Fase H. |
| R054 | Esquelet antic: rangs per rol (llarga 3.800-4.500, mitjana 3.000-3.500, qualitat 2.800-3.200) escalats pel volum de la setmana, i limitats a 2.800-4.500 en setmanes de càrrega i qualitat. | agents/esquelet_sessions.py:31-38, 178-213 | dura | per_nedador | |
| R055 | Esquelet antic: 5 parts estàndard amb percentatges per tipus de setmana (escalfament 10/10/15, tècnica 20/15/15, aeròbic 50/30/20, específic 10/35/40, calma 10/10/10). | agents/esquelet_sessions.py:237-277; models/sessio.py:64-75 | dura | per_nedador | |
| R056 | Esquelet antic: en setmana de qualitat totes les sessions són de tipus qualitat; en setmana de càrrega amb `dies_qualitat`, el dimecres és de qualitat. | agents/esquelet_sessions.py:115-120, 189-200 | dura | per_nedador | Xoca amb R068 (C21). |

## 5. Taper, competició i recuperació posterior

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R057 | Taper i recuperació per classe: A, taper progressiu de 14 dies i 14 de recuperació activa; B, 3 i 3 dies; C, cap taper i 1 dia de recuperació. | agents/taper.py:1-68; Fase1.md:50-54; Architecture.md:91 | tova | global | Només el fa servir R044. Vegeu P21. |
| R058 | En el taper es manté la intensitat, el volum baixa un 40-60% i la freqüència com a molt un 20%. | Fase3.md:48, 225 | tova | per_fase | El volum s'implementa a R037. |
| R059 | El dia abans de competir hi ha activació (24 h abans): el divendres si es competeix dissabte, o el dissabte si es competeix diumenge (i aleshores el divendres és descans). | agents/pla_setmanal.py:289-296; Fase3.md:167 | dura | global | |
| R060 | Els dies de descans no es neda (descans total a l'aigua) i el cap de setmana no es neda. | Fase3.md:167, 481; agents/pla_setmanal.py:4-7 | dura | global | Xoca amb R059 si es competeix diumenge (C16). |
| R061 | Setmana post-competició: dilluns recuperació activa, dimarts aeròbica, dimecres tècnica, dijous qualitat i divendres llarga. | agents/pla_setmanal.py:303-307 | dura | global | |
| R062 | Una setmana post-competició amb una altra competició aquell cap de setmana no té dia de qualitat (les curses fan d'estímul intens). | agents/pla_setmanal.py:297-302; Fase3.md:182 | dura | global | |
| R063 | El dia de competició no hi ha sessions de gimnàs. | agents/esquelet_sessions.py:383-384 | dura | global | |
| R064 | Rutina d'espatlla opcional de 15 min fora de l'aigua el dia de descans de la fitxa (dissabte per al Jep); no surt si aquell dia hi ha competició o sessió. | export/mesocicle_excel.py:34-42, 105-117; Fase3.md:114, 482 | tova | per_nedador | El contingut de la rutina és fix. |

## 6. Organització setmanal

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R065 | La plantilla setmanal és de 5 sessions, de dilluns a divendres; si el nedador té uns altres dies, es fa servir l'esquelet antic. | agents/pla_setmanal.py:24-26, 319-321; agents/esquelet_sessions.py:151-154 | dura | per_nedador | |
| R066 | Setmana normal: dl aeròbica, dt qualitat, dc tècnica, dj aeròbica i dv aeròbica llarga. | agents/pla_setmanal.py:313-316; Fase3.md:488-497 | dura | global | |
| R067 | Setmana de competició: dl aeròbica, dt qualitat, dc tècnica, dj aeròbica i activació el dia abans (sense sessió llarga). | agents/pla_setmanal.py:308-312 | dura | global | |
| R068 | Hi ha un sol dia de qualitat per setmana. | agents/pla_setmanal.py:6; Fase3.md:162 | dura | global | |
| R069 | Es pot afegir un segon dia de qualitat al Build si hi ha 2 blocs sense alertes i el CSS millora. | Fase3.md:216, 357 | tova | per_fase | Pendent. |
| R070 | El dimecres és el dia de tècnica en estat fresc: volum baix (~2.000 m), Recuperació/A1 i sense qualitat. | Fase3.md:481; agents/pla_setmanal.py:4-5, 222-227 | dura | global | |
| R071 | Com a màxim 3 sessions al dia, una per franja (matí, migdia, tarda), i com a molt una de natació. | models/franja.py:29-30; models/nedador.py:231-256; Fase3.md:239, 355 | dura | per_nedador | |
| R072 | El gimnàs és informatiu: compta a la càrrega (sRPE) però no al volum, i l'LLM no en genera contingut. | Fase3.md:241; agents/esquelet_sessions.py:365-410 | dura | global | |
| R073 | Gimnàs en una franja contigua a la natació de qualitat → avís `separacio_insuficient` (es recomanen 6 h). | agents/validacio.py:374-401; Fase3.md:337 | tova | per_nedador | |
| R074 | Gimnàs el dia de tècnica, d'activació o de recuperació → avís `gimnas_dia_no_recomanat`. | agents/validacio.py:361-411 | tova | global | Vegeu C17. |
| R075 | «Dies durs, durs»: el gimnàs, millor el mateix dia que la qualitat. | Fase3.md:337, 358 | tova | global | v1: només doc. |
| R076 | Sense `setmana_tipus`, la natació es fa a la tarda. | models/franja.py:32-34; models/nedador.py:258-271 | tova | per_nedador | |
| R077 | No es generen sessions anteriors a `sessions_des_de`. | agents/esquelet_sessions.py:165-173, 297-300, 385-389 | dura | global | |

## 7. Estructura de la sessió

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R078 | Ordre de les parts: escalfament → tècnica → bloc o blocs principals → tornada a la calma; el treball exigent va en fresc, just després de la tècnica. | agents/pla_setmanal.py:48-56; prompt:76; Fase3.md:374 | dura | global | |
| R079 | Parts i percentatges de cada rol: aeròbica 20/15/5 vel/50/10; llarga 15/10/5 vel/60/10; qualitat 15/15/25/30/15; tècnica 15/50/25/10; activació 30/25/10/20/15; recuperació 20/20/50/10. | agents/pla_setmanal.py:57-82; Manual.md:209-217 | dura | global | Difereix de Fase3.md:376-383 (C26). |
| R080 | Cada part té un bloc (Escalfament, Tècnica, Bloc principal, Tornada a la calma, Sèrie de control); el dia de tècnica, la tècnica és el bloc principal. | agents/pla_setmanal.py:84-133 | dura | global | |
| R081 | Els metres de cada part són múltiples de 100 i sumen exactament els metres no fixos (mètode del residu més gran); l'última part fa la resta i cap part es queda a 0. | agents/pla_setmanal.py:353-383; Manual.md:166 | dura | global | |
| R082 | L'LLM ha de fer que cada part sumi exactament els seus metres i escriure'ls a `metres_part`, sense canviar els percentatges. | prompt:56, 74, 89 | judici_LLM | global | El codi només informa de les desviacions de més de 100 m. |
| R083 | Cada exercici va a la part que correspon al seu objectiu: l'escalfament només prepara, la tècnica només porta exercicis tècnics i el seu nedar complet, cada bloc principal només el seu objectiu, i no hi ha sèries principals a l'escalfament ni a la calma. | prompt:76; agents/jutge.py:53 | judici_LLM | global | |
| R084 | Sèrie de control fixa cada dimecres després de la tècnica: 4x100 crol A2 d/0:20, igual per a tothom i per a totes les setmanes perquè sigui comparable. | agents/pla_setmanal.py:28-29, 389-405, 523-545; agents/esquelet_sessions.py:318-338; Manual.md:221 | dura | global | |
| R085 | Les parts fixes (control, sèrie objectiu, recuperació, cames A3) no les genera ni les modifica l'LLM, no compten al pressupost (però l'A3 i el làctic fixos el descompten) i no porten material. | models/sessio.py:54-56; agents/generar_microcicle.py:990-993; agents/pla_setmanal.py:551-582, 956-957 | dura | global | |
| R086 | L'escalfament inclou 200 m de cames suaus o progressives (100 m si l'escalfament fa menys de 400 m; cap si en fa menys de 200). | agents/pla_setmanal.py:408-411, 439-445; agents/generar_microcicle.py:1290-1292 | dura | global | |
| R087 | Cada sessió té com a molt un bloc de cames intens, A2 o A3, mai tots dos. | agents/pla_setmanal.py:412-413; Manual.md:218 | dura | global | |
| R088 | Cames A3 (part fixa): només en sessions aeròbiques o llargues sense sèrie fixa al bloc principal, en fresc, mai en dies seguits ni a 2 dies o menys d'una competició; la dosi va per fase (Base 1 sessió 4x50; Build 2 sessions 6x50; Peak i descàrrega 1 sessió 3x50; d/1:00; Cursa i Transició cap). | agents/pla_setmanal.py:414-436, 461-509 | dura | per_fase | |
| R089 | Cames A2 (10% de la sessió): a la resta de sessions aeròbiques o llargues, abans de la tornada a la calma; només cames, en sèries de 100-200 m amb descans, sense braçada. | agents/pla_setmanal.py:418-425, 510-518; agents/generar_microcicle.py:1293-1297 | dura | global | |
| R090 | Les sessions de qualitat, tècnica, activació i recuperació només tenen les cames de l'escalfament. | agents/pla_setmanal.py:420, 425 | dura | global | Contradiu Fase3.md:485 (C27). |
| R091 | La tornada a la calma és nedar suau a l'estil complet (recuperació activa), sense cames ni intensitat. | agents/pla_setmanal.py:54-55; prompt:76; Manual.md:220 | judici_LLM | global | |
| R092 | Cap exercici de farciment («placeholder», «N.A.», metres solts per quadrar); el codi els descarta. | prompt:102, 124; agents/generar_microcicle.py:924-971 | dura | global | |
| R093 | Totes les parts no fixes han de tenir exercicis; una part buida és un problema i provoca reintent. | prompt:100; agents/generar_microcicle.py:1127-1133 | dura | global | |
| R094 | El nom de cada part retornada ha de ser exactament el de l'estructura (enum). | prompt:100; agents/generar_microcicle.py:755-757, 939-952 | dura | global | |
| R095 | No s'ha de repetir el conjunt principal de les sessions ja generades aquella setmana. | prompt:129-132; agents/generar_microcicle.py:853-882 | judici_LLM | global | |
| R096 | L'LLM rep les altres sessions del dia (p. ex. gimnàs a la tarda) per tenir-les en compte. | agents/generar_microcicle.py:832-850 | judici_LLM | per_nedador | No es diu com les ha de tenir en compte (B20). |

## 8. Pressupost d'intensitat

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R097 | Grups d'intensitat: Recuperació i A1 = baixa; A2; A3 i AeM; Velocitat; MPLA i TOLA = làctic. | agents/pla_setmanal.py:148-157 | dura | global | |
| R098 | Pressupost de la sessió de qualitat segons el tipus de setmana: Base A2 ≤20%, A3 ≤25%, velocitat ≤300 m, làctic 0; Build A3 ≤20%, vel ≤300, làctic ≤200; descàrrega A3 ≤10%, vel ≤200, làctic 0; taper A3 ≤15%, vel ≤300, làctic ≤200; transició A3 0, vel ≤100, làctic 0. | agents/pla_setmanal.py:159-167; Manual.md:226 | dura | per_fase | Fase3.md:192-198 dona uns altres valors (C25). |
| R099 | Pressupost dels altres rols: aeròbica A2 ≤25%, A3 ≤5%, vel ≤150; llarga A2 ≤25%, A3 ≤5%, vel ≤200; tècnica tot 0; activació A3 0, vel ≤150; recuperació tot 0 (A2 inclosa). | agents/pla_setmanal.py:169-179 | dura | global | |
| R100 | Els percentatges del pressupost s'arrodoneixen a 100 m cap amunt, i l'A3 o el làctic de les parts fixes el descompten. | agents/pla_setmanal.py:559-582 | dura | global | Si la part fixa en gasta més, el pressupost queda a 0 sense avís (C02, B14). |
| R101 | L'A1 és l'eix de l'entrenament (dues terceres parts del volum a l'històric) i la resta del volum no pressupostat ha de ser Recuperació o A1. | prompt:110; agents/pla_setmanal.py:169-171; Manual.md:226 | tova | global | |
| R102 | El codi retalla sèries de la intensitat que passa del pressupost (primer l'exercici amb més volum, mai els de la biblioteca); si el pressupost és 0, no retalla i l'LLM ho ha de refer. | agents/generar_microcicle.py:1174-1201; Manual.md:171 | dura | global | |
| R103 | A la Base no hi ha làctic. | agents/pla_setmanal.py:162, 243; Fase3.md:194; Disseny_proves_objectius.md:102 | dura | per_fase | Duplicat de R098 (D01). |
| R104 | Una sessió de tolerància làctica a la setmana sol ser suficient, amb ≥48 h de recuperació completa. | Fase3.md:220 | tova | global | v1: només doc. |
| R105 | Una dosi curta de velocitat gairebé cada dia, en fresc (històric: 6,7% del volum). | agents/pla_setmanal.py:169-171, 206-213; Manual.md:219 | tova | global | |
| R106 | Els esprints (Velocitat) que l'LLM posa després de la part de velocitat es mouen a aquesta part. | agents/generar_microcicle.py:1150-1167; Manual.md:172 | dura | global | |
| R107 | La tècnica es fa en Recuperació/A1: un exercici A2, A3 o AeM d'una part de bloc Tècnica (excepte «sortides») baixa a A1. | agents/generar_microcicle.py:1136-1147; Manual.md:172 | dura | global | No toca la part principal del dia de tècnica (C01). |
| R108 | Descripció qualitativa de cada rol al prompt; per exemple, aeròbica amb cada repetició al mateix temps (±1") i la primera mai la més ràpida, llarga amb velocitat alàctica 4-6x15-25 d/45", activació amb 4-6x25 a ritme de cursa d/1'. | agents/pla_setmanal.py:206-238 | judici_LLM | global | |
| R109 | Descripció de la qualitat per fase: Base A3 (VO2 màx, 50-100 m 1:1) o A2 i velocitat alàctica; Build VO2 i ritme de cursa de 100 m amb poc làctic; descàrrega alàctic i ritme curt; taper ritme de cursa; transició sense qualitat. | agents/pla_setmanal.py:239-254 | judici_LLM | per_fase | |

## 9. Descansos i cicles

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R110 | Les sessions generades fan servir descans `d/m:ss` (zona + descans) i no cicles; un `c/` rebut es converteix en `d/` si se'n coneix el ritme. | agents/cicles.py:3-11, 269-314; prompt:82; Manual.md:153-156 | dura | global | |
| R111 | Descans per zona: A1 5-10 s (≤100 m), 10-20 (≤200), 15-20 (≤400), 15-30 (més); A2 10-15 (≤50), 15-25 (≤100), 20-30 (més); A3/AeM 1:1 amb el temps nedat (0,8-1,2×); Velocitat 45 s per cada 25 m; MPLA 1:3; TOLA 1:1; Recuperació 0. | agents/cicles.py:168-211; Manual.md:154 | dura | global | |
| R112 | Les sèries A2 o més intenses de més d'una repetició han de portar descans. | agents/cicles.py:185-186, 338-347; prompt:119 | dura | global | |
| R113 | Un descans per sota del mínim de la zona (tolerància 20%) el puja el codi al mínim, arrodonit a 5 s, sense reintent; només es valida quan el ritme és conegut (estil complet, sense aletes, fora de la biblioteca). | agents/cicles.py:148-157, 269-314; Manual.md:168 | dura | global | |
| R114 | La velocitat i el ritme de cursa es fan amb recuperació completa (d/0:45 o més per cada 25 m). | prompt:118; agents/pla_setmanal.py:217, 229-231 | dura | global | Duplicat de R111 (D02). |
| R115 | La durada estimada d'una sessió no pot passar del 110% de `minuts_max_sessio` (o de la durada del slot). | agents/cicles.py:356-362; agents/generar_microcicle.py:1083-1088 | dura | per_nedador | |
| R116 | Un `c/` de 30 s o menys més curt que el temps nedat s'interpreta com a descans. | agents/cicles.py:265-299 | dura | global | |
| R117 | La durada d'un exercici surt del ritme de la zona × la distància × els factors d'estil i d'aletes de la fitxa. | agents/cicles.py:138-165; models/nedador.py:62-76 | dura | per_nedador | |

## 10. Papallona i estils

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R118 | Màxim de papallona per sessió: tècnica 300 m; qualitat, llarga i aeròbica 150; activació 50; recuperació 0. | agents/pla_setmanal.py:181-193; Manual.md:170 | dura | global | Valors diferents a Fase3.md:205 (C24). |
| R119 | La setmana ha de tenir entre 600 i 900 m de papallona (avís si en surt). | agents/pla_setmanal.py:194, 808-815; Manual.md:170 | tova | global | Tres valors diferents segons la font (C24). |
| R120 | La papallona sola es fa en repeticions de 25 o 50 m (els estils de 100/200 no hi compten). | agents/pla_setmanal.py:195-196, 883-891 | dura | global | |
| R121 | La papallona mai va a la tornada a la calma ni al final de la sessió. | agents/pla_setmanal.py:892-896, 712-714 | dura | global | |
| R122 | Còmput: un exercici d'estils compta un 25% com a papallona; els trossos explícits («25 pap + 25 esq») compten els seus metres; les cames de dofí i els estils sense papallona no compten. | agents/pla_setmanal.py:628-705; prompt:127 | dura | global | |
| R123 | Si la sessió passa del màxim de papallona, el codi en retalla sèries sense reintent (els exercicis de la biblioteca, els últims). | agents/generar_microcicle.py:1209-1232; Manual.md:228 | dura | global | |
| R124 | La papallona no es retalla per quadrar el volum si la sessió no passa del seu màxim. | agents/generar_microcicle.py:1334-1340 | dura | global | |
| R125 | Mínim orientatiu de papallona: 2/3 del màxim de la sessió (si el màxim és de 150 m o més). | agents/pla_setmanal.py:825-828 | tova | global | |
| R126 | La tècnica de papallona va a la sessió de tècnica (coordinació i ondulació seguides de nedar complet). | agents/pla_setmanal.py:718-731 | tova | global | |
| R127 | La papallona amb aletes alterna 40/60 i 60/40 (amb/sense) entre sessions consecutives amb papallona, dins del mateix màxim. | agents/pla_setmanal.py:734-757, 1012-1025; Manual.md:228 | tova | global | |
| R128 | Repartiment orientatiu per estils: esquena i braça un 15% cadascun (20% el dia de tècnica), la papallona fins al màxim i el crol la resta; avís si l'esquena o la braça de la setmana no arriben a la meitat. | agents/pla_setmanal.py:198-204, 760-816; Manual.md:169 | tova | global | |
| R129 | El treball d'estils es reparteix segons les proves objectiu (un 100 IM són 25 m de cada estil). | prompt:10 | judici_LLM | per_nedador | |
| R130 | Les sessions sense papallona només poden tenir estils si són suaus i curts. | agents/pla_setmanal.py:716-717 | judici_LLM | global | Contradiu el còmput de R122 (C04). |

## 11. Material

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R131 | Material per fase: Base, pales petites amb pull (una sèrie de 200-400 m) i aletes a cames, papallona i velocitat; Build, pales grans (màx. 300 m per sessió); Peak, tub i pull i pales petites i poques; Cursa, sense pales; Transició, lliure. | agents/pla_setmanal.py:927-947; Manual.md:227 | judici_LLM | per_fase | v1: només prompt; el límit de 300 m no es comprova. |
| R132 | Mai pales a la papallona ni a la braça; cap material a les parts fixes; després d'una sèrie amb aletes, nedar sense material amb el mateix focus. | agents/pla_setmanal.py:955-960; Manual.md:227 | judici_LLM | global | v1: només prompt (P19). |
| R133 | La qualitat i la velocitat, sense pales; activació i recuperació, aletes i tub amb poc volum; tècnica, material tècnic. | agents/pla_setmanal.py:963-979 | judici_LLM | global | |
| R134 | Si el material principal de la fase (pales a Base i Build, tub al Peak) no surt a la setmana, s'avisa. | agents/pla_setmanal.py:948-954, 1001-1009 | tova | per_fase | |

## 12. Tècnica

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R135 | Premisses tècniques de l'entrenador (posició, braçada, subaquàtic ≥5 m, viratges, arribada, acceleració, progressiu, respiració), també dins les sèries aeròbiques. | prompt:18-26; Manual.md:229 | judici_LLM | global | |
| R136 | Selecció determinista d'exercicis de tècnica: famílies segons el rol; 3 a la tècnica, 2 a aeròbica, llarga i qualitat, 1 a activació i recuperació; puntuació = proves objectiu cobertes + 2 si la família és a `prioritats_tecniques`. | agents/tecnica.py:30-58, 98-140; Fase3.md:507 | dura | per_nedador | |
| R137 | La família es manté durant el bloc (rotació pel número de mesocicle) i la variant canvia cada setmana segons la fase (Base → Build → Peak). | agents/tecnica.py:10-11, 60-66, 118-139 | dura | per_fase | En v1 el bloc sempre és «meso_1», de manera que la rotació no funciona (B17). |
| R138 | Els exercicis de tècnica obligatoris hi han de ser tots, amb el seu `id_biblioteca`, a la part de tècnica (els de cames a l'escalfament si fa 300 m o més i no és el dia de tècnica), seguits de nedar l'estil complet; l'LLM només en decideix la dosi dins dels metres de la part. | prompt:112-113; agents/tecnica.py:12-13; agents/generar_microcicle.py:1204-1206 | dura | global | |
| R139 | Si en falta algun, és un problema (reintent), i a més el codi l'afegeix amb la dosi mínima de la biblioteca i a A1. | agents/generar_microcicle.py:1074-1082, 1235-1285; Manual.md:173 | dura | global | |
| R140 | Les restriccions de cada exercici de la biblioteca (p. ex. «compta per al límit de papallona») es passen al prompt. | agents/tecnica.py:150; biblioteca | judici_LLM | global | |
| R141 | Els ajustos automàtics de pressupost i de volum no toquen els exercicis de la biblioteca. | agents/generar_microcicle.py:1190, 1345 | dura | global | |

## 13. Format de l'exercici i regles de natació

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R142 | Cada exercici és una entrada estructurada (sèries, distància, execució, descans, material, intensitat, objectiu), mai text lliure; el volum el calcula el codi. | prompt:78-85; models/sessio.py:8-35 | dura | global | |
| R143 | Les distàncies han de ser vàlides per a la piscina (25 m: 25…800; 50 m: 50…800); una distància no vàlida es descarta i provoca reintent, i els esforços més curts es descriuen dins de l'execució. | agents/generar_microcicle.py:734-742, 790-793, 1012-1025; prompt:80 | dura | per_nedador | Contradiu R146 (C05). |
| R144 | `distancia_m` ha de ser múltiple de 25. | models/sessio.py:26-31 | dura | global | |
| R145 | Intensitats vàlides: Recuperació, A1, A2, A3, Velocitat, MPLA, TOLA i AeM. | prompt:70, 84; models/sessio.py:19-21 | dura | global | |
| R146 | Mai cap número de ritme ni de volum dins de l'execució ni de cap camp de text. | prompt:28, 81, 87, 155 | judici_LLM | global | El prompt diu que es descarta, però cap codi no ho comprova (C06). |
| R147 | Uns estils complets (IM) són de 100 o 200 m, mai de 125 o 150 m; els estils en repeticions de 25 m són vàlids. | prompt:116; agents/pla_setmanal.py:898-907 | dura | global | El codi accepta 300 i 400 (C07). |
| R148 | L'A3 només en repeticions de 50 m o més (en 25 m no s'arriba al llindar). | prompt:117; agents/pla_setmanal.py:909-913, 427-428 | dura | global | |
| R149 | Només termes de natació reals; si una expressió no és estàndard, cal descriure l'acció. | prompt:125; agents/jutge.py:55 | judici_LLM | global | |
| R150 | Prohibits els exercicis d'arrossegar el polze o els dits a la recuperació de crol (carreguen l'espatlla). | prompt:126; diccionari (terme prohibit); agents/pla_setmanal.py:843-847 | dura | global | |
| R151 | Prohibida l'abreviatura «Ei» al pla: cal escriure Estils, o DPS / recompte de braçades. | prompt:69; diccionari (terme prohibit) | dura | global | Significat ambigu (P03). |
| R152 | Abreviatures estàndard: N, C, E, B, Pap, IM; Ps, AL, Pull, Tub, Palites. | prompt:66-68 | tova | global | |
| R153 | Per allargar la braçada, cal indicar DPS o recompte de braçades a l'objectiu. | prompt:69 | judici_LLM | global | |
| R154 | El `sessio_id` es retorna exactament igual. | prompt:98 | dura | global | |
| R155 | La resposta no inclou mai `percentatge` ni `volum_m`. | prompt:155 | dura | global | |

## 14. Generació, reintents i correccions automàtiques

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R156 | Una crida a l'LLM per sessió de natació, amb tool-use forçat i `max_tokens` = 4096. | agents/generar_microcicle.py:37-38, 886-894; Fase3.md:100 | dura | global | |
| R157 | Si la resposta es talla per `max_tokens`, hi ha un reintent amb «màxim 3 exercicis per part»; si es torna a tallar, la sessió queda buida (avís). | agents/generar_microcicle.py:1596-1619 | dura | global | Sessió buida: B01. |
| R158 | Si `parts` arriba buit, hi ha un reintent; si torna buit, la sessió queda buida. | agents/generar_microcicle.py:1629-1641 | dura | global | |
| R159 | Fins a 2 reintents dirigits amb la llista de problemes; es queda la versió amb menys problemes i, si encara en té, s'avisa. | agents/generar_microcicle.py:39-40, 1645-1687; Manual.md:168 | dura | global | La documentació diu 1 reintent (C28). |
| R160 | Ordre de les correccions automàtiques: aplicar → tècnica a A1 → moure la velocitat → detectar parts buides → corregir descansos → afegir la biblioteca → retallar el pressupost → retallar la papallona → quadrar el volum. | agents/generar_microcicle.py:1092-1119 | dura | global | |
| R161 | Ajust de volum: si n'hi ha de més, treu sèries de la part més desviada (primer el bloc principal); si n'hi ha de menys, afegeix sèries a exercicis Rec/A1; mínim 2 sèries o la meitat de les originals, una repetició única mai a menys de la meitat de la distància, i no toca rotacions d'estils, biblioteca ni parts fixes. | agents/generar_microcicle.py:1319-1415; prompt:104; Manual.md:167 | dura | global | |
| R162 | Few-shot: 5 sèries de l'historial; primer les que coincideixen amb paraules del nom de la metodologia, i després les més recents. | agents/generar_microcicle.py:163-223 | tova | per_nedador | Criteri improvisat (B21). |
| R163 | L'LLM ha de seguir el vocabulari i el nivell de detall del few-shot, repartit en els camps estructurats. | prompt:62, 91 | judici_LLM | per_nedador | |
| R164 | En generar un mesocicle sencer, l'error d'una setmana no atura les altres. | agents/generar_microcicle.py:642-645, 722-728 | tova | global | |

## 15. Zones de ritme

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R165 | CSS/100 = (T400 − T200) / 2. | agents/zones_css.py:64-90; Architecture.md:113 | dura | global | |
| R166 | Zones a partir del CSS: Recuperació = CSS + 12", A1 = CSS + 6", A2 = CSS, A3 = CSS − 4", Velocitat = CSS × 0,85 (offsets ajustables per nedador). | agents/zones_css.py:13-32; models/nedador.py:50, 57-60; metodologia_ritmes.md:30-36 | dura | per_nedador | |
| R167 | Sense test CSS, les zones surten de la marca de 100 lliure (Rec +20%, A1 +13%, A2 +6,5%, A3 +1,5%) i la Velocitat de la marca de 50 lliure × 2,02 (mai del 100). | agents/zones_css.py:35-61; models/nedador.py:46-51; metodologia_ritmes.md:40-48 | dura | per_nedador | |
| R168 | El test CSS té prioritat sobre la marca. | agents/zones_css.py:93-157; metodologia_ritmes.md:26 | dura | per_nedador | `determinar_zones_nedador` és codi mort. «Recent» no està definit (B18). |
| R169 | La Velocitat calculada ha de ser més lenta que el ritme del 100 de cursa. | Fase3.md:396 | tova | per_nedador | v1: comprovació manual (B19). |
| R170 | Al test CSS, cada 100 com a molt 2" més ràpid que la mitjana. | Fase3.md:521 | tova | per_nedador | v1: només doc. |
| R171 | El test CSS es repeteix cada 6-8 setmanes. | metodologia_ritmes.md:22 | tova | per_nedador | Contradiu R032 (C30). |
| R172 | Els nedadors sense marca ni test treballen per RPE (`mode_ritme = rpe`) fins al primer test. | models/nedador.py:186; metodologia_ritmes.md:66; Fase3.md:473 | tova | per_nedador | Cap codi no fa servir `mode_ritme` (B03). |
| R173 | Ritme de les zones sense taula: AeM = A3, MPLA = Velocitat, TOLA = la mitjana entre A3 i Velocitat. | agents/cicles.py:111-127 | dura | per_nedador | No documentat (B11). |

## 16. Sèries de ritme objectiu

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R174 | Hi ha una sèrie fixa per cada prova P que es repeteix cada setmana; per defecte, la primera el dimarts i la segona el dijous, en repeticions de 50 m. | agents/ritme_objectiu.py:1-5, 51, 64-72; models/nedador.py:79-87; Manual.md:187-189 | dura | per_nedador | |
| R175 | L'objectiu va de l'estimació pessimista fins al realista × (1 + guany del taper), sense fer-se mai més lent que l'inici; al Peak i a la Cursa és el realista. | agents/ritme_objectiu.py:6-9, 251-259 | dura | per_nedador | |
| R176 | Els passos són les setmanes de Base i Build sense descàrrega des de l'inici de la sèrie fins al Peak, i l'objectiu s'interpola entre l'inici i el final. | agents/ritme_objectiu.py:10-11, 133-151 | dura | per_fase | |
| R177 | Progressió: dins de l'objectiu (+1% de marge), avança un pas; un 2,5% o més ràpid, dos; per sobre, repeteix; dues setmanes seguides per sobre, retrocedeix un pas i avisa; sense registre, repeteix i avisa. | agents/ritme_objectiu.py:13-18, 53, 78-127, 240-249 | dura | per_nedador | |
| R178 | Forma per fase: Base 6 → 8 repeticions (estils 4 → 6) d/1:00; Build1 8 (6) d/1:00, i d/0:45 des de la 3a setmana; Build2 d/0:45; descàrrega 4; Peak i Cursa 4 d/1:30. | agents/ritme_objectiu.py:23-31, 154-165 | dura | per_fase | |
| R179 | La sèrie objectiu és una part fixa A3 (gasta pressupost A3), va després de la tècnica i de la velocitat alàctica, i la segueixen 200 m de recuperació activa fixos. | agents/ritme_objectiu.py:295-327, 350-369; Manual.md:222 | dura | global | Etiqueta A3 discutible (C20). |
| R180 | Si el dia de la sèrie no hi ha natació o la sessió és d'activació o de recuperació, aquella setmana no es fa (avís). | agents/ritme_objectiu.py:340-349 | dura | global | |
| R181 | No es fa a la Transició ni si falta el pic, el nivell actual o l'objectiu. | agents/ritme_objectiu.py:220-226 | dura | per_nedador | |
| R182 | Només compten els registres posteriors al pic anterior i anteriors a la setmana. | agents/ritme_objectiu.py:228-233 | dura | global | |
| R183 | En el 100 IM, 50 alternant papallona-esquena i braça-crol, amb el temps repartit segons la fracció de la primera meitat dels parcials (0,47 si no n'hi ha). | agents/ritme_objectiu.py:53-56, 168-175, 263-271 | dura | per_nedador | |
| R184 | Si la sessió no té part de velocitat i el seu pressupost de velocitat és més gran que 0, s'insereix una part «Velocitat alàctica» (5%) abans de la sèrie objectiu. | agents/ritme_objectiu.py:356-366 | dura | global | |

## 17. Càrrega i recuperació

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R185 | Càrrega d'una sessió = RPE (CR-10) × minuts; una sessió sense RPE no compta. | models/historial.py:49-54; agents/carrega.py:53-59; Fase3.md:240 | dura | global | |
| R186 | La càrrega del dia suma totes les sessions (aigua i gimnàs); la càrrega aguda i la crònica són mitjanes exponencials de 7 i 28 dies. | agents/carrega.py:1-14, 75-99; Fase3.md:338 | dura | global | |
| R187 | Alerta si la càrrega setmanal passa d'1,15 × la mitjana de les 4 setmanes anteriors (mínim 2; excloent descàrrega, taper i transició; ajustat per l'increment planificat). | agents/carrega.py:23-27, 102-150; Fase3.md:338 | tova | per_nedador | Les exclusions i l'increment planificat no es passen mai (B16). |
| R188 | Alerta de benestar (SRSS): la línia base són els últims 28 registres (mínim 10; DE mínima 0,25); alerta si la recuperació és inferior a la base − 1 DE o l'estrès superior a la base + 1 DE, 2 registres seguits. | agents/recuperacio.py:28-33, 47-87; Fase3.md:339 | tova | per_nedador | |
| R189 | Alerta de la sèrie de control: el temps mitjà no és més d'1"/100 més ràpid que la referència (mitjana de les 3 anteriors) i l'RPE puja ≥1 o les braçades ≥1. | agents/recuperacio.py:35-38, 90-135; Fase3.md:340 | tova | per_nedador | |
| R190 | Regla de decisió: 2 alertes o més en una setmana → recomanació per a la setmana següent (mantenir el mínim i qualitat només alàctica); mai s'aplica sola. | agents/recuperacio.py:13-16, 166-177; Fase3.md:216, 341 | tova | global | |
| R191 | Avís de dades incompletes si hi ha sessions sense RPE o dies d'entrenament sense SRSS. | agents/recuperacio.py:179-196 | tova | global | |
| R192 | L'SRSS es registra cada dia d'entrenament abans de la primera sessió, i l'RPE es pot registrar al vespre. | models/registre.py:68-69; Fase3.md:242, 254 | tova | global | |
| R193 | Si el CSS s'estanca 2 blocs, alerta. | Fase3.md:214 | tova | per_nedador | v1: només doc. |

## 18. Objectius i progressió

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R194 | Cada prova objectiu té prioritat P o S, amb pesos 2 i 1 dins del pic. | agents/proves.py:23, 121-140; Disseny_proves_objectius.md:9 | dura | per_nedador | |
| R195 | El perfil de la prova es classifica per la durada (estimació pessimista): menys de 45 s, velocitat; 45-120 s, mixt; 120-240 s, mig fons; més, fons. | agents/proves.py:25-26, 92-106; Disseny_proves_objectius.md:85-96 | dura | per_nedador | Encara no s'utilitza per planificar. |
| R196 | Les competicions de control d'un pic són les B/C posteriors al pic anterior i anteriors a l'A, a la mateixa piscina i on es neda la prova. | agents/proves.py:143-163; Disseny_proves_objectius.md:26 | dura | global | |
| R197 | Validacions dels objectius (avisos): A sense proves, pic sense prova P, 100 IM en piscina de 50 m, prova que no és a la fitxa, sense nivell, sense objectiu, menys de 2 controls, exigència de més d'un 4% i resultat pendent. | agents/proves.py:174-258; Disseny_proves_objectius.md:192-199 | tova | per_nedador | |
| R198 | El nivell actual és un rang (millor marca ≤ estimació pessimista) i l'objectiu també (ambiciós ≤ realista). | models/nedador.py:99-141; Disseny_proves_objectius.md:16, 20 | dura | per_nedador | |
| R199 | Banda prevista: una línia ràpida (de la millor marca a l'ambiciós) i una de lenta (de la pessimista al realista), fins al temps sense taper a la data de la primera A. | agents/progressio.py:6-10, 65-80 | dura | per_nedador | |
| R200 | Zona d'un resultat: blava (més ràpid que la banda), verda (dins), groga (fins a un `marge` més lent) o vermella. | agents/progressio.py:11-13, 83-91 | dura | per_nedador | |
| R201 | Amb 2 resultats o més, es projecta la marca a l'A per regressió lineal amb un interval de ±1 error estàndard (soroll mínim = `marge`). | agents/progressio.py:14-17, 118-157 | dura | per_nedador | |
| R202 | Ritme de cursa de referència: el realista si no hi ha projecció; si n'hi ha, la projecció com a molt l'ambiciós; un sol resultat no mou el ritme. | agents/progressio.py:160-177; Disseny_proves_objectius.md:184-190 | dura | per_nedador | No el fa servir la sèrie objectiu (que va de pessimista a realista). |
| R203 | Avisos: objectiu exigent després del calibratge, nova millor marca (no amb simulacions) i sense millora (2 resultats vermells seguits, sense simulacions). | agents/progressio.py:252-296 | tova | per_nedador | |
| R204 | Mai es compara una competició amb l'anterior (la variabilitat és més gran que el progrés). | agents/progressio.py:26-27 | dura | global | |
| R205 | En un doble pic, l'objectiu de la primera A val per a la segona. | Disseny_proves_objectius.md:16, 54; models/nedador.py:156-162 | dura | per_nedador | |
| R206 | Paràmetres de progressió: guany del taper 2%, marge 1%, exigència màxima 4% i mínim 2 controls, calibrables per nedador. | models/nedador.py:165-175; Disseny_proves_objectius.md:22 | tova | per_nedador | |
| R207 | Els parcials de 25 m han de sumar el temps final (±0,5 s). | models/resultat.py:9-47 | dura | global | |
| R208 | El 50 papallona queda fora de les proves objectiu. | Disseny_proves_objectius.md:21 | tova | per_nedador | Fase3.md:484 diu el contrari (C29). |
| R209 | Les B i C tenen objectius progressius cap a l'A i serveixen per avaluar i modificar l'entrenament. | Disseny_proves_objectius.md:17 | tova | per_nedador | Implementat parcialment a les bandes; la modificació és manual. |

## 19. Metodologia

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R210 | Metodologia segons la distància de la prova: AAOO específic; IM escola Bowman; fins a 100 m Sprint/Tècnica (USRPT no); 200-400 m polaritzat (evidència moderada en màsters); fins a 1500 m polaritzat + USRPT; més, polaritzat amb volum. | agents/seleccio_model.py:176-442; Fase2.md:41-43 | dura | per_nedador | Superada pel disseny (R213). |
| R211 | La metodologia es tria per la primera prova de la fitxa, un cop per mesocicle. | agents/generar_microcicle.py:278-288, 686-689 | dura | per_nedador | Fase3.md:438 la reconeix provisional. |
| R212 | L'LLM ha d'integrar la metodologia principal a les sessions de qualitat i fer servir les complementàries quan sigui apropiat. | prompt:47-54, 93 | judici_LLM | per_nedador | Xoca amb el pressupost (C18). |
| R213 | La metodologia depèn de la fase: Base polaritzat, tècnica dels 4 estils i alàctic sense làctic; Build ritme de cursa de les proves P; Peak ritme de cursa amb poc volum. | Disseny_proves_objectius.md:13, 98-106 | tova | per_fase | Pendent. |
| R214 | Un planificador setmanal LLM triaria el focus de cada sessió dins de límits: només proves del pic, cap ritme de cursa a Base ni el dia de tècnica, focus a ±10 punts dels pesos en 3-4 setmanes, cap prova P sense focus més de 2 setmanes, i aprovació del coach. | Disseny_proves_objectius.md:14, 108-130 | judici_LLM | per_fase | Pendent. |
| R215 | El redactor de sessions rebria el focus i el ritme de cursa de la sessió en lloc de la metodologia. | Disseny_proves_objectius.md:132-135 | judici_LLM | per_nedador | Pendent. |

## 20. Jutge semàntic (fora del flux de generació)

| id | Regla | Origen | Tipus | Abast | Notes |
|---|---|---|---|---|---|
| R216 | El jutge classifica cada exercici en correcte, no_natacio, insegur, part_incorrecta, intensitat, terminologia o farciment, amb presumpció de validesa, i no jutja volums, descansos ni ritmes. | agents/jutge.py:1-20, 38-57, 196-206 | judici_LLM | global | Només s'usa a scripts/avaluar_jutge.py. |
| R217 | La intensitat és vàlida per a qualsevol estil: un IM a A1 és correcte. | agents/jutge.py:112-116; diccionari (terme «Estils») | judici_LLM | global | |
| R218 | El jutge és apte com a primer filtre si detecta ≥85% dels errors amb ≤10% de falsos positius; si no, només mode ombra. | scripts/avaluar_jutge.py:26-27, 48-49 | tova | global | |
| R219 | Són insegurs les apnees llargues repetides i els gestos que carreguen l'espatlla. | agents/jutge.py:51-52, 86-90 | judici_LLM | global | |

---

## Duplicats

Regles que diuen el mateix (o gairebé) en llocs diferents. A v2 haurien de tenir una sola font.

| # | Regles | On es repeteix | Observació |
|---|---|---|---|
| D01 | R098, R103 | `_PRESSUPOST_QUALITAT` (làctic 0 a Base), `_DESCRIPCIO_QUALITAT["carrega"]`, Fase3.md:194, Disseny_proves_objectius.md:102 | «Sense làctic a Base» és en 4 llocs. |
| D02 | R111, R114, R108 | `DESCANS_VELOCITAT_25`, prompt:118-119, descripció de la llarga (d/45") i de l'activació (d/1') | Recuperació completa a la velocitat, amb xifres diferents segons el lloc (45 s/25 m o 1'). |
| D03 | R148, R109 | prompt:117, `problemes_contingut`, comentari de `CAMES_A3_FASE`, descripció de la qualitat («50-100 m») | A3 ≥ 50 m. |
| D04 | R092 | prompt:102 i 124, `TEXTOS_FARCIMENT` / `_RE_FARCIMENT`, categoria `farciment` del jutge | Sense farciment, quatre vegades. |
| D05 | R150, R219 | prompt:126, diccionari (prohibit), restricció de `cap_recuperacio` a la biblioteca, jutge («gestos que carreguen l'espatlla») | Polze arrossegant. |
| D06 | R151 | prompt:69 i diccionari (prohibit) | «Ei». |
| D07 | R070, R099, R107, R108 | H2 decisió 1, descripció del rol tècnica, pressupost tècnica = 0, `tecnica_a_a1` | La tècnica en Rec/A1 surt en 4 formes, però no s'apliquen igual (C01). |
| D08 | R011 | `periodificacio.SETMANES_DOBLE_PIC`, `context_competicio.validar_espaiat_pics_a` (`setmanes <= 4`), `proves.pics_temporada` | Mateix concepte, dues mesures (C13). |
| D09 | R084 | `pla_setmanal.part_serie_control`, `RegistreSerieControl`, README.md:57, Fase3.md:168, export del registre | 4x100 A2 del dimecres. |
| D10 | R091, R121, R083 | prompt:76, comentari de `PARTS_ROL`, exemple del jutge, regla de papallona | Tornada a la calma suau i sense treball. |
| D11 | R041 | `generar_microcicles_mesocicle`, docstring de `pla_setmanal`, Fase3.md:88, Fase3.md:166 | Post-competició = mínim. |
| D12 | R111 | `cicles.DESCANS_ZONA`, taula del prompt (generada amb `taula_cicles`), Manual.md:154, docstring de `cicles` | Descans per zona (la taula del prompt es genera, però el Manual la copia a mà). |
| D13 | R042, R043, R187 | `ACWR_MAX = 1.3` (guard), `ratio_max = 1.3` (validació), `LLINDAR_INCREMENT_SETMANAL = 1.15` (càrrega real) | Tres llindars d'increment de càrrega, amb dues constants iguals per separat. |
| D14 | R122 | prompt:127, `_RE_CAMES`/`_RE_PAP_DOFI`, restricció de `cam_dofi` a la biblioteca, Fase3.md:484 | El dofí de cames no compta com a papallona. |
| D15 | R032, R171, R193 | `test_css` a `_tipus_base_i_notes`, metodologia_ritmes.md:22, Fase3.md:214 | Freqüència del test CSS, en tres versions (C30). |
| D16 | R166, R167 | `zones_css`, metodologia_ritmes.md:30-36, Architecture.md:113, docstring de scripts/registrar_test_css.py | Offsets de les zones. |
| D17 | R057, R037/R038/R059 | `taper.calcular_taper` (dies de taper) i la planificació real (factors de Peak, × 0,8 per a B, activació) | El taper s'expressa de dues maneres que no estan connectades (C23). |
| D18 | R216, R217, R149 | `jutge.REGLA_INTENSITAT`, significat d'«Estils» al diccionari | Un IM a qualsevol intensitat és vàlid. |

---

## Conflictes

### A. Entre regles vigents de v1 (codi ↔ codi, codi ↔ prompt)

| # | Regles | Per què no es poden complir alhora | Situació concreta |
|---|---|---|---|
| C01 | R070, R099, R107 ↔ R138, R136 | La tècnica ha d'anar a Rec/A1 i el rol tècnica té pressupost A2 = 0 i velocitat = 0, però la biblioteca obliga a incloure exercicis amb dosi A2 o Velocitat. A més, `tecnica_a_a1` només actua en parts de bloc «Tècnica», i la part principal del dia de tècnica («Tècnica i papallona») és de bloc «Bloc principal». | Dimecres (tècnica), família «Canvis d'estil a estils»: `im_esq_bra` «4x25 (12,5 esq + 12,5 bra) A2 d/0:30». L'LLM la posa a A2 → «A2: 100 m per sobre del màxim de 0 m» → el codi no retalla (pressupost 0 i exercici de biblioteca) → reintents fins a esgotar-los. |
| C02 | R174, R179 ↔ R099, R100 | La sèrie objectiu per defecte va el dijous (aeròbica) i és A3 fixa, però el pressupost A3 de l'aeròbica és del 5%. | Jep, dijous, Base: sessió de ~2.900 m → A3 ≤ 200 m; sèrie del 100 IM 6x50 A3 = 300 m. El pressupost queda a max(200 − 300, 0) = 0 sense cap avís, i la sessió supera el seu límit A3 per construcció. |
| C03 | R088 ↔ R174, R057 | Les cames A3 no es poden fer a 2 dies o menys d'una competició i la B té 3 dies de taper, però la sèrie objectiu A3 del dijous es manté. | W50 (CNSF, B, dissabte 12/12): el dijous 10/12 porta 6x50 A3 fix (sèrie objectiu 100 IM) a 2 dies de competir i dins dels 3 dies de taper B. |
| C04 | R130 ↔ R122, R118 | El prompt de les sessions amb màxim de papallona 0 diu que s'hi poden fer estils «suaus i curts», però cada estil compta un 25% com a papallona contra un màxim de 0. | Dilluns post-competició (recuperació): «4x100 estils suau» → 100 m de papallona > 0 → el codi retalla fins a 1x100 (no pot baixar de 2 sèries a 0) → continua el problema → reintent. |
| C05 | R143 ↔ R146 | Un punt del prompt diu que els esforços curts s'escriuen dins de l'execució amb la seva distància, i un altre diu que mai hi ha d'haver cap número de volum en cap camp de text. | prompt:80 posa d'exemple `"execucio": "15 m subaquàtic + 10 suau"`, i el missatge de reintent suggereix «12,5 pap + 12,5 esq»; prompt:87 ho prohibeix. La mateixa sèrie objectiu fixa del codi escriu «38,3 s per 50» a l'execució. |
| C06 | R146 (prompt) ↔ codi | El prompt diu que un exercici amb un número de ritme o una distància no vàlida «serà descartat», però per als números de l'execució no hi ha cap comprovació. | Un «Crol a 1:32/100» a l'execució passa sense cap problema. |
| C07 | R147 (prompt) ↔ R147 (codi) | El prompt diu que els estils complets només són de 100 o 200 m; la validació només exigeix múltiples de 100. | «2x300 estils A1» no és cap problema per al codi. |
| C08 | R082, R048, R051 ↔ R052 | El prompt demana els metres exactes; la sessió té un rang de ±5% i la validació hi suma un altre 5% (~±10% respecte a l'objectiu), mentre que la setmana avisa a partir del 5%. | Objectiu de 2.900 m → volum_max arrodonit a 3.000 → s'accepten 3.150 m (+8,6%). Cinc sessions així: cap problema per sessió, però la setmana surt a +8% i avisa. |
| C09 | R002, R043 ↔ R042 | La documentació diu que l'ACWR és un avís i mai una regla, i que el sistema mai canvia el pla sol; el guard modifica `volum_objectiu` automàticament. | Historial de pretemporada de ~9.000 m/setmana i Base de 13.600 → límit 1,3 × 9.000 = 11.700 → aixecat al terra → la setmana queda a 12.000 sense decisió del coach. |
| C10 | R043 ↔ R036, R037 | La validació ACWR avisa de «descàrrega massa pronunciada» per sota de 0,8, però el taper de Bosquet i la descàrrega demanen baixar el volum un 30-55%. | Peak setmana 1 = 7.800 m amb una crònica de ~13.000 → ACWR 0,6 → avís `carrega_fora_de_rang` en totes les setmanes de taper planificades. |
| C11 | R036 ↔ R039 | La descàrrega ha de ser 0,7 × la càrrega, però cap descàrrega pot quedar per sota del terra de 12.000. | Build1 amb la primera càrrega a 12.000 → descàrrega de 8.400 → aixecada a 12.000 = mateix volum que la càrrega. El codi ho resol amb un avís, però la regla de descàrrega no es compleix mai a Build. |
| C12 | R028 ↔ R033 | Un bloc d'1 setmana és de càrrega (sense descàrrega), però com a molt hi pot haver 3 setmanes de càrrega seguides. | Finestra que deixa Build1 d'1 setmana + Build2 de 4 ([C, C, C, D]) → 4 setmanes de càrrega seguides → avís `descarrega_periodica` per una periodització generada pel mateix sistema. |
| C13 | R011 (periodificacio) ↔ R011 (context_competicio) | El doble pic es mesura com a ≤ 28 dies entre les dates d'inici (periodificació i pics), però l'avís el mesura com a ≤ 4 setmanes entre la data de fi de la primera i l'inici de la segona. | A1 del divendres 1 al diumenge 3; A2 el dissabte 2 del mes següent (29-30 dies entre inicis, ~27 dies des de la fi): l'avís diu «es planifiquen com un sol període competitiu», però la periodificació hi posa Transició i un Peak de 2 setmanes. |
| C14 | R057 ↔ R024, R011 | Després d'una A hi ha 14 dies de recuperació activa, però la periodificació posa 1 setmana de Transició (i cap en doble pic) i després setmanes de càrrega. | Catalunya (A, 16-17/01) → doble pic → les setmanes fins a Espanya (06/02) són Build2 (post-competició, mínim de 12.000) i Peak, sense els 14 dies de recuperació activa. |
| C15 | R057 ↔ R011 | Taper progressiu de 14 dies per a tota A, però en doble pic la segona A només té un Peak d'1 setmana. | Espanya (A, 06/02/2027): 7 dies de taper. |
| C16 | R060 ↔ R059 | El cap de setmana no es neda, però si es competeix diumenge l'activació és el dissabte. | Competició diumenge: sessió de natació el dissabte, que a més el Jep no té a `setmana_tipus` (vegeu B07). |
| C17 | R074 ↔ R066/R070 + `setmana_tipus` del Jep | La plantilla fixa la tècnica el dimecres i la fitxa del Jep té gimnàs el dimecres a la tarda; la regla diu que no hi hagi gimnàs el dia de tècnica. | Cada setmana surt l'avís `gimnas_dia_no_recomanat` (Fase3.md:541 el qualifica de fals positiu, però la regla no ha canviat). |
| C18 | R210-R212 ↔ R101, R103, R099 | El prompt demana aplicar la metodologia «Sprint/Tècnica» (sèries curtes a alta intensitat) a les sessions de qualitat, alhora que diu que l'A1 és l'eix, que a Base no hi ha làctic i que l'A3 està limitada. | Qualitat de Base del Jep: «Metodologia principal: Sprint/Tècnica… alta intensitat» i, al mateix prompt, «MPLA/TOLA: màxim 0 m». Disseny_proves_objectius.md:33 ja reconeix que per al Jep el 100 L és mixt, no esprint. |
| C19 | R214, R213 ↔ R174/R178, R136 | El disseny diu que a Base no hi ha ritme de cursa, però la sèrie objectiu (ritme de cursa) es fa des de la primera setmana de Base i la família «Ritme de cursa» és la primera candidata de l'aeròbica. | W41 (Base): dimarts amb 6x50 a ritme del 100 L, i dilluns i dijous amb `rit_mateix_temps` / `rit_descendent` com a exercici obligatori. |
| C20 | R179 ↔ R166, R111 | La sèrie objectiu s'etiqueta A3, però el seu ritme és el de cursa, molt més ràpid que l'A3, i el descans que porta no és l'1:1 de l'A3. | 100 L: objectiu de ~38-40"/50 contra un A3 del Jep de 47"/50 (94"/100); d/1:00 ≈ 1,5:1. El pressupost i la taula de descansos el tracten com a A3. |
| C21 | R053, R056 ↔ R068 | A l'esquelet antic, el dimarts té rol qualitat i, en setmanes de càrrega amb `dies_qualitat` o en setmanes de Build, el dimecres també és de tipus qualitat; la regla és un sol dia de qualitat. | Un nedador nou amb el valor per defecte de `dies_disponibles` (dl-dj, 4 dies; models/nedador.py:195) en una setmana de Build: totes les sessions tenen `tipus_sessio = "qualitat"`. |
| C22 | R045 ↔ R037 | El rang documentat per a la primera setmana de taper A és de 8.400-9.800 m; el codi en dona 13.000 × 0,60 = 7.800. | Primera setmana de Peak abans de Catalunya. |
| C23 | R057 ↔ R038, R059 | El taper B és «lleuger de 3 dies», però la planificació aplica × 0,8 a tota la setmana i activació el dia abans. | B en dissabte: dilluns i dimarts ja tenen el volum reduït, tot i quedar fora dels 3 dies de taper. |

### B. Entre fonts (documentació ↔ codi)

Gairebé tots provenen del fet que el codi del 06/10 (commits 478ca16, 98850ec, e4cc568, 565792c) és posterior a `Fase3.md` (05/10). `Manual.md` (06/10) coincideix amb el codi. Vegeu P01.

| # | Regles | Font 1 | Font 2 | Situació concreta |
|---|---|---|---|---|
| C24 | R118, R119 | Fase3.md:205: per sessió, tècnica ≤350, qualitat ≤150, la resta ≤50, setmana ≤600. Fase3.md:484: 300-600/setmana. Disseny_proves_objectius.md:106: 150-400/setmana. | Codi i Manual.md:170: tècnica 300, qualitat/llarga/aeròbica 150, activació 50; 600-900/setmana. | Una setmana de 750 m de papallona és correcta per al codi i un excés per a les altres tres fonts. |
| C25 | R098, R099 | Fase3.md:192-203: qualitat Build làctic ≤400; aeròbica velocitat 0; llarga velocitat ≤200 alàctic; A2 sense límit. | Codi: làctic ≤200 a Build; aeròbica velocitat ≤150; A2 ≤25% (aeròbica, llarga) i ≤20% (qualitat de Base). | Qualitat de Build amb 300 m de TOLA: vàlida segons Fase3 i retallada pel codi. |
| C26 | R079, R084 | Fase3.md:376-383: l'aeròbica no té velocitat; hi ha part «Cames» a aeròbica, llarga, tècnica i recuperació; al dia de tècnica, la sèrie de control va abans de la tècnica. FulldeRuta_1002.md:101: cames dins de l'escalfament (~150 m) i sense part pròpia. | Codi i Manual.md:209-218: velocitat del 5% a l'aeròbica; Cames A2/A3 només a aeròbica i llarga; 200 m de cames a l'escalfament; control després de la tècnica. | El dimecres, la sèrie de control va després de «Tècnica i papallona» (codi) o abans (Fase3). |
| C27 | R090 | Fase3.md:485 (H2, decisió 5): cames de tots els estils a les sessions aeròbiques, llargues, de tècnica i de recuperació. | Codi: tècnica i recuperació només tenen les cames de l'escalfament. | Dimecres de tècnica sense bloc de cames. |
| C28 | R159 | Architecture.md:82 i Fase3.md:101: un sol reintent. | Codi i Manual.md:168: fins a 2 reintents dirigits. | |
| C29 | R208 | Fase3.md:484 (H2, 01/10): el 50 papallona continua sent prova objectiu. | Disseny_proves_objectius.md:21 (04/10): el 50 papallona queda fora. | La biblioteca encara etiqueta 18 exercicis amb «50 papallona» (no afecta el Jep perquè ja no és a la seva fitxa). |
| C30 | R032, R171 | Fase3.md:214: test CSS a l'inici de cada bloc (~4 setmanes). metodologia_ritmes.md:22: cada 6-8 setmanes. | Codi: només a la primera setmana dels blocs de Base. | Un Build de 8 setmanes no té cap test. |
| C31 | R020 | `_recalcular_taper_i_pics`: els pics prioritzats són totes les A. | scripts/generar_temporada.py:338: el camp `pics_prioritzats` de la fitxa (buit per al Jep). | Amb la fitxa del Jep el re-taper no s'activa mai; amb les primitives d'ajust sí. |
| C32 | R211 ↔ R213 | Codi: metodologia per la primera prova de la fitxa. | Disseny_proves_objectius.md:13: metodologia per fase. | Decisió presa i no implementada. |

---

## Buits

Situacions en què cap regla diu què fer i el codi o el prompt improvisen.

| # | Situació | Què fa v1 (improvisació) | Origen |
|---|---|---|---|
| B01 | La resposta es talla dues vegades o `parts` arriba buit dues vegades. | La sessió queda buida, s'avisa al log i s'exporta igualment a l'Excel. | agents/generar_microcicle.py:1614-1641 |
| B02 | Després dels reintents, la sessió encara té problemes. | Es queda la versió amb menys problemes i s'exporta. Cap regla diu quins problemes són bloquejants. | agents/generar_microcicle.py:1680-1687 |
| B03 | Nedador sense zones o en mode RPE (Cris, Pere). | El prompt rep «N/A» a les zones; no es poden calcular els descansos 1:1 ni la durada; `mode_ritme` no es fa servir enlloc. | agents/generar_microcicle.py:1044-1046; agents/cicles.py:111-127 |
| B04 | Competició que comença entre setmana o que acaba en dilluns. | No es classifica la setmana: no hi ha activació ni setmana post-competició. Fase3.md:90 ho reconeix i ho resol corregint el calendari a mà. | agents/pla_setmanal.py:280-285 |
| B05 | Competició A amb proves els dos dies del cap de setmana. | Activació abans del primer dia; el segon dia i el que passa entre els dos dies no tenen cap regla. | agents/pla_setmanal.py:280-296 |
| B06 | Les dues proves de Budapest (aigües obertes 29-30/06 i piscina 03-09/07) com un sol bloc. | Pendent; tampoc hi ha regles de periodització per a aigües obertes. | FulldeRuta_1002.md:130 |
| B07 | Activació en un dia sense franja a `setmana_tipus` (el dissabte del Jep). | Franja «tarda» per defecte. El gimnàs només es bloqueja el dia de competició, no el d'activació. | models/nedador.py:266-271; agents/esquelet_sessions.py:383-384 |
| B08 | Nedadors que no entrenen de dilluns a divendres (Lou, Cris, Pere, o qualsevol amb 3, 4 o 6 dies). | Esquelet antic: sense sèrie de control, cames, biblioteca ni rols de la Fase H; el pressupost surt de rols «mitjana» o «llarga». El valor per defecte del model és de 4 dies. | agents/esquelet_sessions.py:160-234; models/nedador.py:195 |
| B09 | Límit d'A2 en activació i a la qualitat de Build, descàrrega, taper i transició. | Sense clau `a2` → sense límit. | agents/pla_setmanal.py:161-179 |
| B10 | Exercici sense intensitat. | Es tracta com a A1 al pressupost i al càlcul de temps. | agents/pla_setmanal.py:614-624; agents/cicles.py:116 |
| B11 | Ritmes d'AeM, MPLA i TOLA (la metodologia de zones no els defineix). | AeM = A3, MPLA = Velocitat, TOLA = la mitjana entre A3 i Velocitat. | agents/cicles.py:117-126 |
| B12 | La sessió és curta i no hi ha cap exercici Rec/A1 amb més d'una sèrie per allargar. | L'ajust s'atura; la sessió queda fora de rang amb avís. | agents/generar_microcicle.py:1403-1410 |
| B13 | La setmana canvia de rols (post-competició: dimarts aeròbica, dijous qualitat) i la sèrie objectiu té el dia fixat. | S'insereix igualment el dia fixat, sigui quin sigui el rol (només s'exclouen l'activació i la recuperació). | agents/ritme_objectiu.py:340-349 |
| B14 | Les parts fixes gasten més A3 que el pressupost de la sessió. | El pressupost A3 de l'LLM queda a 0 sense avís; no hi ha prioritat entre la part fixa i el pressupost. | agents/pla_setmanal.py:576 |
| B15 | El coach accepta la recomanació de la regla de decisió (≥2 alertes). | No té efecte a la planificació: cap regla diu com es tradueix (volum, rols, qualitat alàctica). | agents/recuperacio.py:166-177 |
| B16 | Base de comparació de l'alerta de càrrega. | L'script no passa ni les setmanes excloses ni l'increment planificat: es compara amb les 4 setmanes anteriors sense excloure res. | scripts/generar_temporada.py:155-157 |
| B17 | Què del pla ha de ser estable d'una setmana a l'altra. | El macrocicle es regenera a cada execució: el mesocicle sempre és «meso_1» (la rotació de famílies no canvia mai) i el volum interpolat de la fase depèn de la data de generació. | scripts/generar_temporada.py:290-322; agents/generar_macrocicle.py:599-623; agents/tecnica.py:93-95 |
| B18 | Antiguitat del test CSS. | «Test recent» no està definit: n'hi ha prou amb `font = css_test`. | agents/zones_css.py:115-121 |
| B19 | La Velocitat calculada surt més ràpida que el ritme del 100 de cursa. | Res (comprovació manual recomanada). | Fase3.md:396 |
| B20 | Interacció del gimnàs amb la natació. | Només avisos de franja; cap regla diu com afecta el volum, els rols o el contingut (l'LLM rep «el mateix dia també hi ha gimnàs» sense cap instrucció). | agents/generar_microcicle.py:832-850 |
| B21 | Selecció del few-shot. | Coincidència de paraules entre el nom de la metodologia i la intensitat o l'objectiu de les sèries de l'historial. | agents/generar_microcicle.py:187-221 |
| B22 | La papallona de les parts fixes (sèrie objectiu del 100 IM). | No compta al màxim de la sessió, però sí al resum i a l'avís setmanal. | agents/pla_setmanal.py:662-671, 781 |
| B23 | Proves S o del pic 2 sense nivell ni objectiu (200 L del Jep). | No tenen sèrie objectiu ni cap treball específic; només n'hi ha per a les P. | agents/ritme_objectiu.py:64-72 |
| B24 | Quan s'entrena en piscina de 50 m. | Ho decideix l'usuari a cada execució (`--piscina`); cap regla (p. ex. abans d'una A de 50 m). | scripts/generar_temporada.py:202-208 |
| B25 | Dues sessions de natació el mateix dia. | No està suportat (error de validació). | models/nedador.py:246-250 |
| B26 | La dosi obligatòria de la biblioteca no cap als metres de la part (p. ex. `rit_mateix_temps` 8x100 = 800 m en una tècnica de 400 m). | El prompt diu «redueix-la», sense cap mínim; el codi afegeix amb la dosi mínima del format si l'exercici falta. | prompt:89; agents/generar_microcicle.py:1275-1283 |
| B27 | Veredicte invàlid del jutge. | El jutge no és al flux de generació; no hi ha cap regla d'acció (mode ombra). | scripts/avaluar_jutge.py:26-27 |
| B28 | Temporades i dates de cada nedador. | Dates fixes per a tothom. | scripts/generar_temporada.py:64-65 |

---

## Preguntes obertes

- **P01. Quina font mana quan la documentació i el codi divergeixen?** El codi del 06/10 i el `Manual.md` (06/10) són posteriors a `Fase3.md` (05/10) i coincideixen entre ells (C24-C28). No ho he decidit: totes dues versions queden recollides.
- **P02. Abast «per rol».** Moltes regles depenen del rol de la sessió (qualitat, tècnica…) i les he classificat com a `global`. Cal afegir el valor `per_rol` (o `per_sessio`)?
- **P03. Què vol dir «Ei»?** El diccionari diu que és l'abreviatura d'Estils a l'historial; el prompt el relaciona amb la longitud de braçada («fes servir DPS… mai Ei»); el comentari de `ritme_objectiu.py:309` cita «Rp 200 Ei» de l'històric.
- **P04.** El 50 papallona és prova objectiu o no (C29)?
- **P05.** Quins són els límits de papallona vigents, per sessió i per setmana (C24)?
- **P06.** Quin és el pressupost d'intensitat vigent (C25)? Cal definir el límit d'A2 als casos que no en tenen (B09)?
- **P07.** El guard ACWR pot retallar el pla sol o només ha d'avisar (C09)? I la validació ACWR ha d'excloure les setmanes de taper i de descàrrega (C10)?
- **P08.** Recuperació després d'una A: 14 dies o 1 setmana de Transició? I quin taper té la segona A d'un doble pic (C14, C15)?
- **P09.** Si es competeix diumenge, hi ha activació a l'aigua el dissabte, en sec, o no n'hi ha (C16)?
- **P10.** Cada quant es fa el test CSS, i a quines fases (C30)?
- **P11.** El gimnàs del dimecres del Jep és acceptable (i cal canviar la regla) o s'ha de moure (C17)?
- **P12.** Sèrie objectiu: és A3 o una zona pròpia (ritme de cursa)? Com conviu amb el pressupost de l'aeròbica i amb les setmanes de competició, i quin dia va quan la plantilla canvia de rols (C02, C03, C20, B13)?
- **P13.** Les intensitats de la biblioteca (A2, Velocitat) prevalen sobre «la tècnica a Rec/A1» o al revés? També el dia de tècnica (C01)?
- **P14.** Es permeten estils complets de 300 o 400 m (C07)?
- **P15.** Quina tolerància de volum es vol per sessió i per setmana (C08)?
- **P16.** L'esquelet antic s'ha de mantenir per a nedadors amb uns altres dies, o cal una plantilla per a 3, 4 i 6 dies (B08, C21)?
- **P17.** Com es mesura la proximitat d'un doble pic: entre inicis o des de la fi de la primera (C13)?
- **P18.** Els pics prioritzats són totes les A o un camp de la fitxa? El re-taper és vigent (C31, R020)?
- **P19.** Les regles de material (R131-R133) han de ser dures i comprovades o només orientatives?
- **P20.** Es poden escriure distàncies parcials dins de l'execució («15 m subaquàtic + 10 suau») (C05)?
- **P21.** `taper.py` (14/3/1 dies) és una regla vigent o un vestigi substituït per la periodificació i la plantilla (R057, D17)?
- **P22.** La metodologia es tria per distància, per fase o per durada (R210-R213, C18, C32)?
- **P23.** «Qualitat» és alhora un tipus de setmana (Build) i un rol de sessió, i al prompt una sessió aeròbica de Build surt com a «tipus: qualitat». Cal separar els termes al glossari?
- **P24.** Les dates de temporada han de ser per nedador (R022, B28)?
- **P25.** Algunes regles de dades de la fitxa (identificador = carpeta, fitxers que no se sobreescriuen) no les he considerat «de planificació» i no hi són. Cal incloure-les?
