# Fonts de dades d'entrada

Formats dels Excels que el sistema ha d'importar i irregularitats que la spec 002 ha de convertir en regles. Document genèric: descriu formats, no dades de cap nedador.

## Excel de calendari (un per nedador i temporada)
Columnes: núm., classe (A/B/C), data, competició, piscina (25m/50m), modalitat, seu.

Cada fila és una competició del calendari del nedador amb la seva classe. Falta la informació de proves: quines proves neda el nedador, en quin dia de la competició i amb quina prioritat.

Irregularitats a resoldre:
- **Data en dos formats:** un dia com a data (AAAA-MM-DD); diversos dies com a text «DD/MM/AAAA» separat per salt de línia.
- **Valors marcadors:** «pendent» a la seu = dada desconeguda (`null`), no un valor.
- **Proves:** no s'indiquen per competició; s'han de poder afegir després (competició sense proves = «encara no decidit», avís).
- **Setmana:** no hi ha de ser; es deriva de la data.

## Excel d'entrenaments (font de blocs per a la biblioteca)
Prové d'un sol nedador: el volum està concentrat en els seus estils (crol 51%, estils 12%, papallona 7%, esquena 2,6%, braça 2,1%, sense estil explícit 25%). Repeticions més freqüents: 50 m, 100 m i 25 m.

Una pestanya per mes. Capçalera de setmana («Setmana N»), fila de dia («Dilluns 4») i una fila «Total» per sessió.
Columnes: Dia | Treball | Execució | Descans | Material | Intensitat | Objectiu | Temps (min) | Volum (m).

Irregularitats a resoldre:
- **Descans:** majoritàriament cicle `c/m:ss`; minoritàriament descans `d/m:ss`; també «-». El sistema prescriu `d/`.
- **Intensitat:** zones simples (A0, A1, A2, A3, Vel, MPLA, TOLA, AeM), variants d'escriptura (MPLA/Mpla) i combinacions en una fila («A1 + A2», «A1-A2-A3», «Vel / A1»).
- **Files compostes:** blocs repartits en diverses files (`1) … 2) …`, `3x` amb subfiles) que formen un sol exercici o bloc.
- **Capçaleres repetides** dins del full («Intensitat», «Material», «Descans»).
- **Material:** combinacions i ordres diferents («Palites + AL», «AL + Palites», «- / AL»).
- **Abreviatures** a l'execució: C, E, B, Pap/P, Ei, EP, Ps (peus), PEB, N, Frim, NPB/NPT, AL (aletes), Palites, Pales, Pull, Tub, Pilotes, r/N (respiració cada N), hypox.

Evidència per al glossari (spec 000), segons l'ús real a l'objectiu de cada fila:
- A2 s'usa per a «resistència aeròbica / umbral» → llindar (CSS).
- A3 s'usa per a «VO2 màx / High Endurance Performance».
- A0 s'usa per a recuperació activa.
- «Ei» = Estils.
