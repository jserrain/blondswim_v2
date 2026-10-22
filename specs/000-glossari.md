# Spec 000 — Glossari

**Estat:** Aprovada

## Objectiu
Fixar els termes, els codis i la notació canònica del sistema. Cada codi té un sol significat.

Fora d'abast:
- Àlies i irregularitats d'importació: spec 002.
- Ritme de cada zona per nedador: spec 004.
- Tractament de cada classe de competició i noms de fases: spec 003.

## 1. Zones d'intensitat

| Codi | Nom | Ús |
|---|---|---|
| A0 | Recuperació | Recuperació activa, entre sèries o entre principals |
| A1 | Aeròbic extensiu | Volum aeròbic de base |
| A2 | Llindar | Ritme CSS |
| A3 | VO2 màx | Aeròbic intensiu |
| TOLA | Tolerància al lactat | Esforços submàxims amb descans mitjà o incomplet; mantenir la velocitat amb fatiga |
| MPLA | Màxima producció de lactat | Esforços màxims de 25–50 m amb descans molt llarg |
| Vel | Velocitat (alàctica) | Esforços màxims de ≤ 25 m amb recuperació completa |

**Màx**: marcador d'esforç màxim a la distància de la repetició. No és una zona de l'escala i no es solapa amb Vel. On és vàlid: RN-027.

**CSS** (Critical Swim Speed): ritme que s'aproxima a la frontera entre el domini intens i el sever, per sobre del llindar anaerobi. No és el llindar aeròbic. Es calcula a partir del test CSS (§9) a la spec 004.

## 2. Patró de ritme dins d'una sèrie
El patró s'aplica sempre dins d'una sola zona.
- **Constant** (sense codi): el mateix ritme de la zona durant tota la sèrie. Quan no s'indica cap patró, el patró és constant; és semàntica de la notació, no una dada que falta.
- **Progressiu** (`prog`): la velocitat augmenta gradualment, bloc a bloc (dins d'una distància o entre repeticions). Comença per sota del ritme de la zona i acaba per sobre, sense arribar al ritme de la zona superior.
  - *Exemple:* `4x100 Cr A2 prog d/0:20`.
- **Negatiu** (`neg`): la distància es divideix en dues meitats iguals, i la segona és més ràpida que la primera.
  - *Exemple:* `1x400 Cr A2 neg d/1:00`.
- Els marges de ritme de `prog` i `neg` no es defineixen en aquesta versió.

**Trams:** canvis de zona dins d'una repetició, per simular els canvis de ritme d'una prova.
- *Exemple:* `4x100 Cr trams(25 A2, 25 A3, 25 A2, 25 Vel) d/0:30`.
- Cada tram té una distància i una zona de l'escala (mai `Màx`). La suma dels trams és la distància de la repetició.
- Una sèrie amb trams no porta patró.

**AeM (Aeròbic mix):** sèrie progressiva per zones. Cada repetició té la seva zona, en ordre creixent, i la seqüència té tantes zones com repeticions. No és un patró, ni una zona, ni trams.
- És una forma només d'entrada: pot aparèixer en dades importades, però el sistema no la prescriu. La conversió és de la spec 002.
- *Exemple:* `4x100 Cr AeM (A1-A2-A3-Màx) c/2:00`. Són quatre repeticions de 100 m de crol: la primera a A1, la segona a A2, la tercera a A3 i la quarta al màxim. Cada repetició comença cada 2 minuts.

## 3. Descans
- **`d/m:ss`**: descans fix entre repeticions.
  - *Exemple:* `12x25 Cr (subaquàtic 15 m) A1 d/0:45`.
- **`d/×N`**: ràtio treball:descans. El descans és N vegades la durada de la repetició, amb N enter positiu. Zones on s'admet: RN-024. La conversió a segons és de la spec 004.
  - *Exemple:* `6x50 Cr TOLA d/×2`.
- `d/m:ss` i `d/×N` són les úniques formes de descans que prescriu el sistema (RN-023).
- **`c/m:ss`**: cicle. Cada repetició comença a l'interval indicat, i el descans és el temps que sobra. Si el nedador va més ràpid, descansa més; si va més lent, descansa menys.
  - *Exemple:* `4x100 Cr A1 c/1:45`. Si el nedador fa cada 100 m en 1:27, descansa 18 s.
  - El sistema només l'accepta en dades importades o introduïdes pel coach.
  - El render el pot mostrar a A0–A2 (ADR-0008).
- **Durades:** sempre en format `m:ss`.
- **Temps de registre** (marques): format `m:ss.cc`, amb centèsimes; per exemple, `1:05.32`.

## 4. Estils i combinacions

| Codi | Significat |
|---|---|
| Cr | Crol |
| Esq | Esquena |
| Br | Braça |
| Pap | Papallona |
| Ei | Estils individuals (Pap-Esq-Br-Cr). Prova d'estils; també es pot fer servir com a estil preferent |
| Ei inv | Estils en ordre invers (Cr-Br-Esq-Pap) |
| FRIM | Estils amb crol en lloc de papallona (Cr-Esq-Br-Cr) |
| PEB | Papallona-Esquena-Braça |
| EP | Estil preferent del nedador. Es resol per a cada nedador (spec 006) |

**Seqüències d'escalfament:** cada lletra és un tram de la sèrie, en l'ordre escrit (per exemple, `4x100 NPBN`: cada 100 m es fa d'una manera diferent).
- **N**: nedar, a ritme suau, normalment a crol.
- **P**: nedar amb pales.
- **B**: nedar amb pull i pales; només treballa el tren superior.
- **T**: tècnica.
- Codis canònics: **NPB**, **NPT**, **NPBT**, **NPBN**. S'escriuen sencers; dins d'aquests codis, P i B no són estils.

**Execució:**
- **N** = nedar (estil complet).
- **Ps + estil** = només peus; per exemple, `Ps Cr`. Un `Ps` sense estil no és vàlid.

Les lletres soltes C/E/B/P i «IM» (= Ei) no són codis canònics; només són àlies d'importació (spec 002).

## 5. Material i respiració

| Codi | Significat |
|---|---|
| AL | Aletes |
| Pp | Pales petites |
| Pal | Pales |
| Pb | Pull |
| Tub | Tub frontal |
| Pilotes | Pilotes |
| r/N | Respiració cada N braçades |
| hypox | Treball en hipòxia |

## 6. Prescripció d'una sèrie

`<rep>x<dist> <estil|Ps estil> [(detall)] <zona [patró]|trams(…)> <d/m:ss|d/×N> [r/N] [material]`

- La zona i el descans són obligatoris.
- Les dades importades poden portar una seqüència AeM en lloc de la zona (§2).
- *Exemple:* `8x50 Cr A2 prog d/0:20 Pb`.

## 7. Competició i proves
- **Competició**: element del catàleg comú; té data o dates, piscina (25 m o 50 m) i seu. Té un programa de proves, que el sistema no desa.
- **Participació**: la presència d'un nedador en una competició, amb una classe.
- **Classe** de la participació (inspirada en TrainingPeaks; ADR-0006):
  - **A**: objectiu de temporada. Pic de forma amb taper complet.
  - **B**: competició exigent. Taper breu.
  - **C**: es tracta com un entrenament de qualitat. Sense descàrrega prèvia.
- **Prova**: distància + estil; per exemple, `100 Ei`. Al programa d'una competició, cada prova apareix una sola vegada per sexe. Al sistema s'identifica per distància i estil; el sexe el determina el nedador.
- **Inscripció**: la participació d'un nedador en una prova individual del programa, dins d'una participació, en un dia concret i amb una prioritat. Tota participació porta les proves que s'hi volen nedar.
- **Relleu**: prova per equips. No es modela: no és una inscripció individual ni una prova objectiu.
- **Prioritat**: principal o secundària.
- **Prova objectiu**: prova inscrita en una participació de classe A. No hi ha proves objectiu sense competició.
- **Prova d'avaluació**: prova inscrita en una participació de classe B o C.
- **Millor registre**: temps per a un estil i una distància, amb la piscina on es va fer.

## 8. Cicles
- **Macrocicle**: la temporada.
- **Mesocicle**: una fase, formada per un o més blocs.
- **Bloc**: un grup de setmanes amb un patró de càrrega i recuperació.
- **Microcicle**: la setmana. Es deriva de la data i no es desa.

## 9. Sessió
- **Part**: escalfament, tècnica, principal I, principal II (opcional) o tornada a la calma (ADR-0004).
- **Sèrie**: la unitat de prescripció dins d'una part.
- **Exercici de tècnica**: un element de la biblioteca de tècnica del coach (ADR-0005).
- **Sessió de test CSS**: segueix l'estructura de l'ADR-0004 sense bloc de tècnica (ADR-0011). El sistema n'ofereix la plantilla fixa (spec 006) quan el coach la insereix al pla del nedador (spec 001).
  - **Escalfament:** 400–800 m suau amb tècnica i 2–4 progressions de 25 m. El contingut el fixa el coach a la plantilla de test i es repeteix igual a cada test. La tècnica forma part de l'escalfament; no hi ha bloc de tècnica.
  - **Principal I:** 400 Cr Màx, al màxim ritme que es pot mantenir de manera constant.
  - **Recuperació entre principals:** A0, 10 min.
  - **Principal II:** 200 Cr Màx.
  - **Tornada a la calma:** 100–200 m molt suau.
  - Els rangs de l'escalfament i de la tornada a la calma són orientatius; el sistema no els valida.
  - Sortida des de l'aigua, sense salt.

## Criteris d'acceptació
1. **Donat** el catàleg de zones, **quan** es llista, **aleshores** conté exactament A0, A1, A2, A3, TOLA, MPLA i Vel.
2. **Donat** qualsevol codi canònic, **quan** es converteix a text i es torna a llegir, **aleshores** s'obté el mateix valor.
3. **Donat** un codi no canònic (per exemple, `Mpla` o `C`), **quan** el domini el llegeix, **aleshores** el rebutja amb un error, sense interpretar-lo ni assignar-li cap valor per defecte.
4. **Donats** tots els codis del glossari, **quan** es comparen, **aleshores** no n'hi ha dos d'iguals amb significats diferents.
5. **Donada** una sèrie sense zona (ni seqüència AeM) o sense descans, **quan** es valida, **aleshores** és invàlida (error bloquejant).
6. **Donada** una sèrie generada pel sistema, **quan** es valida, **aleshores** el descans és de tipus `d/`.
7. **Donada** la durada `1:45`, **quan** es llegeix, **aleshores** val 105 s. **Donada** la durada `45`, **quan** es llegeix, **aleshores** es rebutja.
8. **Donada** una sèrie `Ps` sense estil, **quan** es valida, **aleshores** és invàlida.
9. **Donada** una sèrie sense patró de ritme, **quan** es llegeix, **aleshores** el patró és constant.
10. **Donat** un millor registre sense piscina, **quan** es valida, **aleshores** és invàlid.
11. **Donada** una sèrie AeM de 4 repeticions amb una seqüència de 3 zones, **quan** es valida, **aleshores** és invàlida.
12. **Donada** una sèrie AeM amb una seqüència que no és creixent (per exemple, A2-A1-A3-Màx), **quan** es valida, **aleshores** és invàlida.
13. **Donada** una sèrie amb `Màx` fora d'una seqüència AeM i fora de la sessió de test CSS, **quan** es valida, **aleshores** és invàlida.
14. **Donada** una sèrie generada pel sistema amb una seqüència AeM, **quan** es valida, **aleshores** és invàlida.
15. **Donada** una sèrie a A0, A1, A2 o A3 amb descans `d/×N`, **quan** es valida, **aleshores** és invàlida.
16. **Donat** el descans `d/×0`, **quan** es llegeix, **aleshores** es rebutja.
