# Spec 001 — Model de domini

**Estat:** Aprovada

## Objectiu
Definir les entitats, els invariants i el format JSON del catàleg de competicions i de l'espai de cada nedador (ADR-0006).

Fora d'abast:
- Pla i registre (specs 003–008).
- Zones derivades del CSS (spec 004).
- Períodes no disponibles i canvis de disponibilitat (spec 003).
- Importació des de l'Excel (spec 002).
- Aigües obertes (AAOO).
- Relleus: no es modelen (spec 000).
- Programa de proves de la competició: no es desa al catàleg.

## Organització

```
data/
  competicions/<AAAA-AA>.json        # catàleg comú de la temporada
  nedadors/<id>/
    nedador.json
    temporades/<AAAA-AA>/
      temporada.json
      inscripcions.json
```

- L'id del nedador és el nom de la carpeta i no es repeteix dins del fitxer.
- Les proves objectiu no es desen enlloc: es deriven de les participacions de classe A.

## Identificador del nedador
- L'id del nedador és el nom de la carpeta (`nedadors/<id>/`); per exemple, `n0001`. Format: RN-001.
- Assignació i immutabilitat: RN-002. Els nedadors no s'esborren, s'arxiven: RN-004.
- El nom i els cognoms són dades de `nedador.json`, no formen part de l'id.
- `nedador.json` pot tenir un `alias` opcional per a ús del coach a la CLI (RN-003).

## Entitats

**Nedador** (`nedador.json`)
- `nom`: text no buit.
- `cognoms`: text no buit. Admet un o dos cognoms en el mateix camp.
- `alias`: text o `null` (RN-003).
- `arxivat`: booleà. En crear el nedador val `false` (RN-017).
- `estils_preferents`: un o més codis, sense repetir. Admesos: Cr, Esq, Br, Pap, Ei.
- `dies_entrenament`: un o més dies de la setmana (dl, dt, dc, dj, dv, ds, dg), sense repetir. Les competicions no hi compten.
- `volum_setmanal`: `{min, max}` en metres (RN-005).
- `tests_css`: llista de `{data, t400, t200}` (RN-006).
  - El coach registra els tests manualment; el sistema no els planifica.
  - El CSS i les zones es calculen (spec 004); no es desen.
  - **Test vigent:** el de data més recent. Es precisarà per piscina del bloc a la spec 004.
- `millors_registres`: llista de `{estil, distancia, piscina, temps, data, competicio}`.
  - `competicio` és un text lliure, perquè pot ser d'una temporada anterior.
  - Unicitat: RN-007.

**Temporada** (`temporada.json`)
- `inici` i `fi` (dates), amb inici < fi.
- La carpeta es diu `AAAA-AA` i es correspon amb l'any d'inici.

**Competició** (catàleg `competicions/<AAAA-AA>.json`)
- `id`: estable (RN-008).
- `nom`, `dates` (un o més dies), `piscina` (25 o 50).
- `seu`: un text, o `null` si no es coneix (RN-009).
- Esborrat: RN-010.

**Participació** (dins de `inscripcions.json` del nedador)
- `id_competicio` (RN-011).
- `classe`: A, B o C.
- `proves`: llista d'inscripcions (RN-014). Sense límit màxim al sistema.
- Regles: RN-012, RN-013.

**Inscripció**
- `prova`: `{distancia, estil}`, una prova individual del programa de la competició.
- `dia`: una data (RN-015).
- `prioritat`: principal o secundària.
- Una sola inscripció per prova i competició: RN-016.

**Valors derivats (no es desen mai)**
- **Setmana:** setmana ISO 8601 (de dilluns a diumenge), identificada per l'any ISO i el número de setmana.
- CSS i zones.
- Proves objectiu.
- Classe de cada prova (s'agafa de la participació).

## Validació: dues categories
- **Model vàlid:** compleix els invariants de format d'aquesta spec i les regles de càrrega RN-001, RN-003, RN-005 a RN-008 i RN-011 a RN-016. Si no els compleix, error de càrrega.
- **Apte per planificar:** a més del model vàlid, compleix RN-017 i RN-018. Si no ho és, la planificació queda bloquejada i el missatge indica què falta.
- **Avisos (no bloquegen):** RN-009, RN-019, RN-020.

## Format JSON
- Cada fitxer porta `versio_esquema`.
- Dates en format `AAAA-MM-DD`.
- Temps de registre en format `m:ss.cc` (spec 000).
- No hi ha valors per defecte: un camp que falta i és obligatori provoca un error. Un camp opcional desconegut es desa com a `null` i genera un avís.

## Criteris d'acceptació
1. **Donat** un `nedador.json` vàlid, **quan** es carrega i es torna a desar, **aleshores** el fitxer resultant és idèntic.
2. **Donat** un catàleg de competicions i un `inscripcions.json` vàlids, **quan** es carreguen i es tornen a desar, **aleshores** els fitxers resultants són idèntics.
3. **Donat** un nedador sense estils preferents, sense dies d'entrenament o amb `volum_setmanal.min > max`, **quan** es carrega, **aleshores** dona un error que identifica el camp.
4. **Donat** un test CSS amb t400 ≤ t200, **quan** es carrega, **aleshores** dona un error.
5. **Donats** dos tests CSS, **quan** es demana el vigent, **aleshores** s'obté el de data més recent.
6. **Donats** dos millors registres amb el mateix estil, distància i piscina, **quan** es carrega, **aleshores** dona un error.
7. **Donat** un millor registre amb temps `1:05.3`, **quan** es carrega, **aleshores** dona un error de format.
8. **Donada** una participació sense inscripcions, **quan** es carrega, **aleshores** dona un error.
9. **Donada** una inscripció amb un dia que no és de la competició, **quan** es carrega, **aleshores** dona un error.
10. **Donada** una participació a una competició amb alguna data fora de la temporada del nedador, **quan** es carrega, **aleshores** dona un error.
11. **Donats** dos ids de competició repetits al catàleg, **quan** es carrega, **aleshores** dona un error.
12. **Donada** una competició amb `seu: null`, **quan** es carrega, **aleshores** es carrega correctament i genera un avís.
13. **Donada** una participació de classe A sense cap inscripció principal, **quan** es valida, **aleshores** genera un avís i no bloqueja la planificació.
14. **Donat** un nedador vàlid, no arxivat, sense cap test CSS i sense ritmes, amb una participació de classe A, **quan** es demana si és apte per planificar, **aleshores** la resposta és «sí» i genera l'avís «sense ritmes».
15. **Donat** un nedador sense cap participació de classe A, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «falta competició A».
16. **Donat** un nedador amb participacions A, B i C, **quan** es demanen les proves objectiu, **aleshores** s'obtenen només les inscripcions de les participacions A.
17. **Donat** un fitxer amb un `versio_esquema` desconegut, **quan** es carrega, **aleshores** dona un error.
18. **Donada** una competició en una data qualsevol, **quan** es demana la setmana, **aleshores** es calcula a partir de la data (any ISO + setmana) i no es llegeix del fitxer.
19. **Donada** una participació amb un `id_competicio` que no és al catàleg, **quan** es carrega, **aleshores** dona un error.
20. **Donats** dos nedadors que participen a la mateixa competició amb classes diferents (A i C), **quan** es carreguen, **aleshores** tots dos són vàlids i cadascun conserva la seva classe.
21. **Donada** una competició del catàleg amb participacions, **quan** s'intenta esborrar, **aleshores** dona un error.
22. **Donat** un canvi de data d'una competició al catàleg, **quan** es consulten les participacions dels nedadors, **aleshores** totes veuen la data nova.
23. **Donat** un nedador amb dues participacions a la mateixa competició, **quan** es carrega, **aleshores** dona un error.
24. **Donats** dos nedadors amb el mateix nom i cognoms, **quan** es creen, **aleshores** reben ids diferents i tots dos són vàlids.
25. **Donat** un nedador existent, **quan** se'n canvia el nom, **aleshores** l'id no canvia.
26. **Donats** dos nedadors amb el mateix `alias`, **quan** es valida el model, **aleshores** dona un error.
27. **Donada** una carpeta de nedador amb un nom que no té el format `n` + 4 dígits, **quan** es carrega, **aleshores** dona un error.
28. **Donat** un nedador arxivat, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «arxivat».
