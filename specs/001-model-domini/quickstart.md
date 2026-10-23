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
- 45 CA amb almenys un test. CA-001-33, 34 i 38 estan pendents de les specs 004 i 002 i no es comproven.
- `import-linter`: `domain` no importa cap altra capa ni cap dependència externa.
- `mypy --strict` sense errors.

## Escenaris de fum (integration, amb `tmp_path`)
1. Escriure els tres fitxers d'exemple de `contracts/fitxers-json.md`, carregar-los i desar-los: el contingut és equivalent (CA-001-01, 02) i un segon desament és idèntic byte a byte (CA-001-36).
2. Canviar `piscina` a 33 en el catàleg: error que identifica el fitxer, el camp i el valor (CA-001-41).
3. Inscriure `100 Ei` en una competició de 50 m: error RN-030 (CA-001-42).
4. Demanar l'aptitud d'un nedador sense participació A: «no», amb el motiu «falta competició A» (CA-001-15).
