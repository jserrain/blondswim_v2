# Mapa d'especificacions BlondSwim v2

Proposta de treball. Res d'aquest document és normatiu fins que no queda en un ADR o en una spec aprovada.
Aquest document és genèric: no conté dades de cap nedador ni de cap temporada concreta.

## Requisits del producte
1. Multi-nedador: cada nedador té el seu espai (perfil, temporades, inscripcions, plans, registre). Hi ha un catàleg comú de competicions per temporada (ADR-0006).
2. Cada nedador defineix la seva disponibilitat: dies de natació per setmana i rang de volum setmanal.
3. Cada nedador té un o més estils preferents.
4. Cada nedador té les seves inscripcions a competicions del catàleg, amb classe (A/B/C) per participació. Una competició té diverses proves (estil + distància), i el nedador en pot nedar diverses el mateix dia.
5. Les competicions A són els objectius; les B i les C serveixen per avaluar la progressió.
6. L'objectiu de la planificació és el màxim rendiment en les proves on participa el nedador.
7. Planificació per cicles inspirada en TrainingPeaks: macrocicle (temporada), mesocicles (fases i blocs), microcicle (setmana).
8. Les sessions s'adapten a cada nedador i a les seves proves objectiu. Es composen amb plantilla i metodologia; la tècnica surt de la biblioteca d'exercicis del coach (ADR-0005). L'històric d'entrenaments no s'importa (ADR-0013).

## Principis (lliçons de la v1)

| Principi | Error de la v1 que evita |
|---|---|
| Un valor derivat no es desa mai (setmana ISO, volum d'una sèrie, temps estimat) | Setmana sense any, columnes desplaçades, ordenació errònia al canvi d'any |
| Cap valor per defecte que amagui una dada que falta: dada desconeguda = `null` + avís | Metres buits → 0, fitxa amb valors per defecte que activaven lògica antiga |
| Els paràmetres són del nedador o de la spec, mai constants al codi | Temporada i volums fixos per a tothom |
| Cada regla té una sola font | 18 grups de regles duplicades amb valors diferents |
| Tota regla té tipus: bloquejant, avís o judici LLM | Regles «dures» que no es comprovaven o que esgotaven reintents |
| Abans d'acceptar una regla nova, es comprova contra les existents | Regles apilades que es bloquejaven entre elles |
| El sistema avisa; el coach decideix | Guards que retallaven el pla sense avisar |
| El pla es persisteix i es versiona; no es regenera ni se sobreescriu | Macrocicle regenerat a cada execució, ids de bloc inestables |
| El rellotge i l'LLM s'injecten | Funcions «pures» que llegien la data o carregaven secrets |
| Documents normatius sense història: l'estat actual a la spec, el perquè a l'ADR, la història a git | Documents de la v1 que es contradeien entre ells |

## Organització de dades

L'organització vigent és la de la spec 001. Aquí només s'hi afegeix el que encara no està especificat.

```
data/
  competicions/<AAAA-AA>.json     # catàleg comú de la temporada (spec 001)
  biblioteca/                     # exercicis de tècnica per estil (spec 002b)
  nedadors/<id>/
    nedador.json                  # spec 001
    temporades/<AAAA-AA>/
      temporada.json              # spec 001
      inscripcions.json           # spec 001
      pla/                        # macrocicle i setmanes, versionats (specs 003-006)
      registre/                   # execució real (spec 007)
```

Convencions de noms:
- **Dins de l'espai del nedador, el nom del fitxer no porta l'id**: la carpeta ja l'identifica (una sola font).
- La temporada és una carpeta (`2026-27`), no un sufix: inscripcions, pla i registre d'una temporada van junts i les temporades anteriors es conserven.
- **Els fitxers que surten del sistema** (full de piscina, informe) sí que porten l'id i la setmana: `<tipus>_<id>_<AAAA>-W<ss>.xlsx`, perquè viatgen sols.
- On es desen els CSV d'entrada (ADR-0012) ho decideix la spec 002.

## Composició de sessions

- L'històric d'entrenaments no s'importa, no és font de sessions ni es passa a l'LLM (ADR-0013).
- La sessió es construeix: plantilla (rol + fase) → parts segons l'ADR-0004 → tècnica de la biblioteca del coach (ADR-0005) → principals segons les proves objectiu i la seva prioritat → volum ajustat. L'LLM només redacta i adapta dins d'aquests límits.
- Abans de planificar un nedador, la biblioteca de tècnica ha de cobrir els seus estils (ADR-0005).

## Proves objectiu i rendiment

- **Prova** = estil + distància (+ piscina de la competició). Té un **perfil de demanda** derivat de la durada (velocitat, mixt, mig fons, fons) que determina els sistemes energètics a entrenar.
- Cada prova objectiu té **prioritat** (principal / secundària) i el pes de l'entrenament específic en depèn.
- **Diverses proves el mateix dia:** la planificació ha de preparar també la capacitat de repetir esforços (ordre de les proves, recuperació entre elles) i el taper ha de tenir en compte el conjunt de proves, no una de sola.
- La participació en una competició té **classe** (A/B/C); cada prova inscrita té **prioritat** (ADR-0006).

## Specs necessàries (ordre proposat)

| # | Spec | Contingut | Decisions que la bloquegen |
|---|---|---|---|
| 000 | Glossari | Zones (A0, A1, A2, A3, Vel, MPLA, TOLA), notació (`c/`, `d/`, `r/N`), abreviatures, termes de cicle (macro, meso, micro, fase, bloc), classes A/B/C | — (aprovada) |
| 001 | Model de domini | Nedador (estils preferents, disponibilitat, zones), Temporada, Competició (del nedador), Prova, Inscripció per dia, Prova objectiu (prioritat, marca, objectiu), Setmana (derivada de la data). Invariants i roundtrip JSON | — (aprovada) |
| 002 | Importació i normalització | CSV de calendari → catàleg; CSV d'inscripcions → inscripcions del nedador (ADR-0012). Regles per a cada irregularitat de `fonts_dades.md`. Informe d'errors; mai valors inventats | Ubicació dels CSV d'entrada; format del CSV (codificació, separadors); identificació del nedador en importar (id o alias com a argument) i, si el CSV porta el nom, validar-lo contra `nedador.json` i avisar si no coincideix |
| 002b | Biblioteca d'exercicis de tècnica | Exercicis per estil confeccionats pel coach, format, metres per exercici, cobertura per estil (ADR-0005) | Format de l'exercici; com es tria per a les proves objectiu |
| 003 | Periodització | Fases cap enrere des de cada A, blocs càrrega:recuperació, doble pic, finestra insuficient, activació quan la competició és en cap de setmana, tractament de B i C, períodes no disponibles | Model de taper; mínims de fase; regla de doble pic |
| 004 | Zones i càrrega | CSS → zones; nedador sense CSS; càrrega per RPE de sessió (pendent d'ADR-0009) | Model de càrrega; mode sense zones |
| 005 | Microcicle | Plantilla per nombre de dies, rols de sessió, repartiment del rang de volum per fase i tipus de setmana | Plantilla per dies; tolerància de volum |
| 006 | Composició de sessions | Plantilla (rol + fase) → parts (ADR-0004) → tècnica de la biblioteca → principals segons les proves objectiu i la seva prioritat → volum ajustat; l'LLM només redacta i adapta dins de límits | Punts de judici LLM; activació del principal II; pes per prioritat |
| 007 | Progressió amb B/C | Resultats, bandes de progressió, alertes | — |
| 008 | Sortides | Full de piscina, resum setmanal, plantilla de registre | Formats d'E/S |

Nucli mínim: 000 → 001 → 002 → 002b → 003 → 005 → 006. El model és multi-nedador des de la 001; la validació inicial es fa amb un nedador real com a cas de prova.

## Decisions preses
Les decisions vigents són als ADR de `docs/decisions/`. Aquest mapa no en repeteix cap.

## Preguntes obertes (genèriques)
1. Si la finestra fins a una A no arriba als mínims de fase: s'escurcen fases (quines primer), s'accepta Base curta, o el coach tria quina A és el pic real?
2. Activació abans d'una competició en diumenge (o en un dia sense natació): a l'aigua, en sec o sense activació?
3. Períodes no disponibles (vacances, festius): com es declaren i com afecten el bloc?
4. B i C: només avaluació o la B porta setmana reduïda?
5. **Resolta (pendent d'ADR-0009).** Càrrega: només RPE de sessió, al registre. Sense sTSS/CTL/ATL/TSB fins a tenir dispositius fiables. L'RPE també alimenta avisos de revisió de ritmes i de recuperació (spec 004 i `docs/regles.md`).
6. **Resolta per la spec 001.** Dades mínimes per planificar: model vàlid i una participació de classe A. Els ritmes són opcionals (vegeu la pregunta 8).
7. Estils preferents i proves objectiu: com es reparteix l'entrenament entre l'estil preferent i els estils de les proves quan no coincideixen?
8. Ritmes de zona (spec 004), model híbrid. Sense test CSS, el coach entra els ritmes; amb test CSS, el sistema els calcula. Proposta, pendent de confirmar a l'ADR-0010:
   a) Deriven del CSS: A0–A3. TOLA: ritme de prova objectiu o millor marca de la piscina del bloc. MPLA: [NEEDS CLARIFICATION] (proposta: ritme de prova o millor marca de 50/100, com TOLA). Vel: sense ritme.
   b) Precedència: valor del coach (per zona) > calculat CSS > estimat. L'estimat sempre requereix confirmació del coach.
   c) Avís de test caducat a les 8 setmanes: resolt (RN-028). Les zones surten de l'últim test acceptat de la piscina del període (spec 001).
   d) Ritmes per piscina: un conjunt per a 25 m i un per a 50 m. Sense conjunt de la piscina del bloc → estimat amb factor configurable i avís.
   e) Estils diferents del lliure: offset a partir de les millors marques de 100, sobreescrivible pel coach.
   f) Validació del test (ràtio T400/T200, 200 no màxim): avís, no bloqueig.
   g) Render sense ritme: A0–A2 també es mostra amb `d/` i el descriptor RPE de la zona (spec 004).
   - Nota per a la spec 004: offsets orientatius sobre T_CSS per 100 m, configurables: A0 +15/+20 s, A1 +8/+12 s, A2 −1/+2 s, A3 −2/−5 s.
9. Piscina per bloc (hivern 25 m, estiu 50 m). On es defineix: spec de blocs/calendari. Pendent.
10. Regles de sèries: repeticions de 400 m segons proves inscrites i fase (a A1–A2; mai a A3 o superior), distribució de zones per prova, límit de sessions de qualitat per a màsters. Destí: `docs/regles.md`.
