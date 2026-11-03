# Quickstart — validació de la spec 001

Guia per comprovar que la implementació compleix la spec. No inclou codi d'implementació.

## Prerequisits
- `uv` instal·lat i entorn sincronitzat (`uv sync`).

## Validació
```bash
uv run pytest -m ca -q                       # tots els tests lligats a criteris
uv run python scripts/check_tracabilitat.py  # cada CA no pendent té test
bash scripts/verify.sh                       # porta única: ha d'acabar «LLEST PER SEGUIR»
```

## Resultats esperats
- 90 CA amb almenys un test (99 actius; 13 retirats: CA-001-55, 56, 77, 85, 86, 87, 88, 94, 95, 98, 99, 100 i 103). CA-001-33, 34, 38, 58, 63, 64, 68, 72 i 84 estan pendents de les specs 002, 004 i 005 i no es comproven.
- `import-linter`: `domain` no importa cap altra capa ni cap dependència externa.
- `mypy --strict` sense errors.

## Escenaris de fum (integration, amb `tmp_path`)
1. Escriure els tres fitxers d'exemple de `contracts/fitxers-json.md`, carregar-los i desar-los: el contingut és equivalent (CA-001-01, 02) i un segon desament és idèntic byte a byte (CA-001-36).
2. Canviar `piscina` a 33 en el catàleg: error que identifica el fitxer, el camp i el valor (CA-001-41).
3. Inscriure `100 Ei` en una competició de 50 m: error RN-030 (CA-001-42).
4. Demanar l'aptitud d'un nedador sense participació A: «no», amb el motiu «falta competició A» (CA-001-15).
5. Dos nedadors amb el mateix correu, un d'ells amb `estils_preferents` buit: no es carrega cap dels dos i l'error identifica tots dos (CA-001-69).
6. Un `nedador.json` trencat i un de vàlid: el filtre dona un ERROR per a l'UUID del trencat i el vàlid es carrega (CA-001-65, 75).
7. Un nedador sense `canal_preferent`: es carrega i `data/avisos.jsonl` té una línia `RN-035` amb `decisio: null` (CA-001-57).
8. Modificar un nedador amb `volum_setmanal.min > max`: no es desa res (CA-001-80).
9. Afegir un millor registre amb un temps menor que el vigent: s'afegeix a la llista; amb un temps igual o pitjor: no passa res (CA-001-83, 89). Tres marques desordenades en un fitxer: error (CA-001-96). Una marca millor amb data igual o anterior a la vigent: error (CA-001-102).
10. Un correu escrit `  Pere@Exemple.cat `: s'accepta i es desa idèntic (CA-001-104). `usari@gmial.com` també (CA-001-106). `a b@example.com` o `nedador@example`: error (CA-001-105). `a@b@example.com` és vàlid (CA-001-104).
11. Un nedador sense correu és vàlid (CA-001-107); amb `canal_preferent: correu` i sense correu, avís RN-035 a la càrrega (CA-001-110). Modificar un nedador amb `correu: null` el deixa sense correu i en lliura el correu antic (CA-001-112). `A@b.com` i ` a@b.com ` en dos nedadors: col·lisió (CA-001-108).
