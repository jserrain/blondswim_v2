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

## Entitats

**Nedador** (`nedador.json`)
- `estils_preferents`: un o més codis, sense repetir. Admesos: Cr, Esq, Br, Pap, Ei.
- `dies_entrenament`: un o més dies de la setmana (dl, dt, dc, dj, dv, ds, dg), sense repetir. Les competicions no hi compten.
- `volum_setmanal`: `{min, max}` en metres, amb 0 < min ≤ max.
- `tests_css`: llista de `{data, t400, t200}`, amb t400 > t200.
  - El coach registra els tests manualment; el sistema no els planifica.
  - El CSS i les zones es calculen (spec 004); no es desen.
  - El test vigent és el de data més recent.
- `millors_registres`: llista de `{estil, distancia, piscina, temps, data, competicio}`.
  - `competicio` és un text lliure, perquè pot ser d'una temporada anterior.
  - Per a cada combinació d'estil, distància i piscina hi ha com a màxim un registre.

**Temporada** (`temporada.json`)
- `inici` i `fi` (dates), amb inici < fi.
- La carpeta es diu `AAAA-AA` i es correspon amb l'any d'inici.

**Competició** (catàleg `competicions/<AAAA-AA>.json`)
- `id`: estable i únic dins del catàleg.
- `nom`, `dates` (un o més dies), `piscina` (25 o 50).
- `seu`: un text, o `null` si no es coneix (amb avís).

**Participació** (dins de `inscripcions.json` del nedador)
- `id_competicio`: ha d'existir al catàleg de la mateixa temporada.
- `classe`: A, B o C.
- `proves`: una o més inscripcions.
- Un nedador no pot tenir dues participacions a la mateixa competició.
- Totes les dates de la competició han de caure dins de la temporada del nedador.

**Inscripció**
- `prova`: `{distancia, estil}`.
- `dia`: ha de ser una de les dates de la competició.
- `prioritat`: principal o secundària.
- No hi pot haver dues inscripcions a la mateixa prova el mateix dia.

**Valors derivats (no es desen mai)**
- Setmana ISO.
- CSS i zones.
- Proves objectiu.
- Classe de cada prova (s'agafa de la participació).

## Validació: dues categories
- **Model vàlid:** compleix els invariants anteriors. Si no els compleix, error de càrrega.
- **Apte per planificar:** a més del model vàlid, té com a mínim un test CSS i com a mínim una participació de classe A. Si no ho és, la planificació queda bloquejada i el missatge indica què falta.
- **Avís (no bloqueja):** participació de classe A sense cap inscripció principal.

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
14. **Donat** un nedador vàlid sense cap test CSS, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «falta test CSS».
15. **Donat** un nedador sense cap participació de classe A, **quan** es demana si és apte per planificar, **aleshores** la resposta és «no» i el motiu és «falta competició A».
16. **Donat** un nedador amb participacions A, B i C, **quan** es demanen les proves objectiu, **aleshores** s'obtenen només les inscripcions de les participacions A.
17. **Donat** un fitxer amb un `versio_esquema` desconegut, **quan** es carrega, **aleshores** dona un error.
18. **Donada** una competició en una data qualsevol, **quan** es demana la setmana, **aleshores** es calcula a partir de la data (any ISO + setmana) i no es llegeix del fitxer.
19. **Donada** una participació amb un `id_competicio` que no és al catàleg, **quan** es carrega, **aleshores** dona un error.
20. **Donats** dos nedadors que participen a la mateixa competició amb classes diferents (A i C), **quan** es carreguen, **aleshores** tots dos són vàlids i cadascun conserva la seva classe.
21. **Donada** una competició del catàleg amb participacions, **quan** s'intenta esborrar, **aleshores** dona un error.
22. **Donat** un canvi de data d'una competició al catàleg, **quan** es consulten les participacions dels nedadors, **aleshores** totes veuen la data nova.
23. **Donat** un nedador amb dues participacions a la mateixa competició, **quan** es carrega, **aleshores** dona un error.
