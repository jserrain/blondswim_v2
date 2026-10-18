# Mapa d'especificacions BlondSwim v2

Proposta de treball. Res d'aquest document és normatiu fins que no queda en un ADR o en una spec aprovada.
Aquest document és genèric: no conté dades de cap nedador ni de cap temporada concreta.

## Requisits del producte
1. Multi-nedador: cada nedador té el seu espai (perfil, temporades, calendari, plans, registre). No hi ha calendari comú.
2. Cada nedador defineix la seva disponibilitat: dies de natació per setmana i rang de volum setmanal.
3. Cada nedador té un o més estils preferents.
4. Cada nedador té el seu calendari: competicions amb dates i classe (A/B/C). Una competició té diverses proves (estil + distància), i el nedador en pot nedar diverses el mateix dia.
5. Les competicions A són els objectius; les B i les C serveixen per avaluar la progressió.
6. L'objectiu de la planificació és el màxim rendiment en les proves on participa el nedador.
7. Planificació per cicles inspirada en TrainingPeaks: macrocicle (temporada), mesocicles (fases i blocs), microcicle (setmana).
8. Les sessions s'adapten a cada nedador i a les seves proves objectiu, a partir d'una biblioteca de material real; no es generen de zero.

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

```
data/
  biblioteca/
    blocs.json                 # biblioteca comuna de blocs etiquetats (vegeu «Biblioteca»)
  nedadors/
    <id>/
      nedador.json             # perfil: estils preferents, disponibilitat, zones
      temporades/
        <AAAA-AA>/
          calendari.json       # competicions del nedador: dates, classe, proves inscrites per dia
          objectius.json       # proves objectiu: prioritat, marca actual, objectiu
          pla/                 # macrocicle i setmanes, versionats
          registre/            # execució real (RPE, temps, resultats)
      fonts/                   # Excels originals d'entrada, només lectura
```

Convencions de noms:
- **Dins de l'espai del nedador, el nom del fitxer no porta l'id**: la carpeta ja l'identifica (una sola font).
- La temporada és una carpeta (`2026-27`), no un sufix: calendari, objectius, pla i registre d'una temporada van junts i les temporades anteriors es conserven.
- **Els fitxers que surten del sistema** (full de piscina, informe) sí que porten l'id i la setmana: `<tipus>_<id>_<AAAA>-W<ss>.xlsx`, perquè viatgen sols.
- Calendari per nedador, sense catàleg comú: si dos nedadors van a la mateixa competició, cadascun la té al seu calendari. Cost acceptat: un canvi de data s'actualitza a cada calendari.
- La biblioteca és comuna; cada bloc guarda l'origen com a metadada.

## Biblioteca: de sessions a blocs

L'Excel d'entrenaments és d'un sol nedador i està esbiaixat cap a les seves proves. Distribució del volum per estil (anàlisi de l'Excel 25-26):

| Crol | Estils | Papallona | Esquena | Braça | Sense estil (escalfament, recuperació, cames) |
|---|---|---|---|---|---|
| 51% | 12% | 7% | 2,6% | 2,1% | 25% |

Conseqüència: **reutilitzar sessions senceres no serveix** per a un nedador amb un altre estil preferent o amb altres proves. La unitat reutilitzable és el **bloc** (una sèrie amb un objectiu), etiquetat i, quan es pot, parametritzat per estil.

Etiquetes mínimes de cada bloc:
- **Part** de la sessió: escalfament, tècnica, nucli, tornada a la calma.
- **Zona** (A0…TOLA) i, si n'hi ha diverses, el repartiment.
- **Estil:** fix (un exercici tècnic de crol només és de crol), **intercanviable** (`estil = preferent` o `estil = el de la prova objectiu`) o neutre.
- **Forma:** repeticions × distància, descans (`d/`), volum, material.
- **Objectiu:** tècnic o fisiològic (aeròbic, llindar, VO2, velocitat, ritme de cursa, cames).
- **Origen:** nedador, data, sessió.

La sessió es construeix: plantilla (rol + fase) → blocs triats per a les proves objectiu del nedador → estil assignat → volum ajustat. L'LLM només redacta i adapta dins d'aquests límits.

Buit detectat: hi ha molt poc material tècnic d'esquena i braça. Caldrà una font de blocs tècnics per estil (p. ex. la biblioteca tècnica de la v1, revisada) abans de planificar nedadors d'aquests estils.

## Proves objectiu i rendiment

- **Prova** = estil + distància (+ piscina de la competició). Té un **perfil de demanda** derivat de la durada (velocitat, mixt, mig fons, fons) que determina els sistemes energètics a entrenar.
- Cada prova objectiu té **prioritat** (principal / secundària) i el pes de l'entrenament específic en depèn.
- **Diverses proves el mateix dia:** la planificació ha de preparar també la capacitat de repetir esforços (ordre de les proves, recuperació entre elles) i el taper ha de tenir en compte el conjunt de proves, no una de sola.
- La competició té **classe** (A/B/C); la prova té **prioritat**. (Pendent de confirmar.)

## Specs necessàries (ordre proposat)

| # | Spec | Contingut | Decisions que la bloquegen |
|---|---|---|---|
| 000 | Glossari | Zones (A0, A1, A2, A3, Vel, MPLA, TOLA), notació (`c/`, `d/`, `r/N`), abreviatures, termes de cicle (macro, meso, micro, fase, bloc), classes A/B/C | Significat d'A2/A3; A0 com a zona |
| 001 | Model de domini | Nedador (estils preferents, disponibilitat, zones), Temporada, Competició (del nedador), Prova, Inscripció per dia, Prova objectiu (prioritat, marca, objectiu), Setmana (derivada de la data). Invariants i roundtrip JSON | Model temporal; formats d'E/S; classe per competició o per prova |
| 002 | Importació i normalització | Excel de calendari → calendari del nedador; Excel d'entrenaments → blocs. Regles per a cada irregularitat de `fonts_dades.md`. Informe d'errors; mai valors inventats | Excel com a entrada; conversió `c/` → `d/` |
| 002b | Biblioteca de blocs | Etiquetatge de blocs (part, zona, estil fix/intercanviable/neutre, forma, objectiu, origen), regles per decidir si un bloc és intercanviable, cobertura per estil | Quins blocs són intercanviables; font de tècnica per estil |
| 003 | Periodització | Fases cap enrere des de cada A, blocs càrrega:recuperació, doble pic, finestra insuficient, activació quan la competició és en cap de setmana, tractament de B i C, períodes no disponibles | Model de taper; mínims de fase; regla de doble pic |
| 004 | Zones i càrrega | CSS → zones; nedador sense CSS; mesura de càrrega (sTSS/CTL/ATL/TSB o volum + RPE) | Model de càrrega; mode sense zones |
| 005 | Microcicle | Plantilla per nombre de dies, rols de sessió, repartiment del rang de volum per fase i tipus de setmana | Plantilla per dies; tolerància de volum |
| 006 | Composició de sessions | Plantilla (rol + fase) → blocs segons les proves objectiu i la seva prioritat → estil assignat → volum ajustat; l'LLM només redacta i adapta dins de límits | Punts de judici LLM; estructura de la sessió; pes per prioritat |
| 007 | Progressió amb B/C | Resultats, bandes de progressió, alertes | — |
| 008 | Sortides | Full de piscina, resum setmanal, plantilla de registre | Formats d'E/S |

Nucli mínim: 000 → 001 → 002 → 002b → 003 → 005 → 006. El model és multi-nedador des de la 001; la validació inicial es fa amb un nedador real com a cas de prova.

## Decisions preses
- L'històric d'entrenaments és una font de material, no un model de temporada.
- La unitat reutilitzable és el bloc, no la sessió sencera.
- Cada nedador té el seu calendari; no hi ha catàleg comú de competicions.

## Preguntes obertes (genèriques)
1. Si la finestra fins a una A no arriba als mínims de fase: s'escurcen fases (quines primer), s'accepta Base curta, o el coach tria quina A és el pic real?
2. Activació abans d'una competició en diumenge (o en un dia sense natació): a l'aigua, en sec o sense activació?
3. Períodes no disponibles (vacances, festius): com es declaren i com afecten el bloc?
4. B i C: només avaluació o la B porta setmana reduïda?
5. Càrrega: sTSS/CTL estil TrainingPeaks, o volum + RPE?
6. Dades mínimes d'un nedador per poder planificar (dies, rang de volum, estils preferents, CSS o RPE, proves objectiu).
7. La classe A/B/C és de la competició o de cada prova? Proposta: classe per competició i prioritat principal/secundària per prova.
8. Estils preferents i proves objectiu: com es reparteix l'entrenament entre l'estil preferent i els estils de les proves quan no coincideixen?
