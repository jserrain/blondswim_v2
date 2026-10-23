# Contracte — fitxers JSON de la spec 001

Interfície externa: fitxers que el coach edita i que genera la importació (spec 002). Els camps, els tipus i les regles són a `data-model.md`; aquí hi ha l'estructura i un exemple de cada fitxer. Els valors són exemples.

## Regles comunes
- UTF-8, `indent=2`, salt de línia final, ordre de claus del data model (research R3).
- `versio_esquema: 1`. Qualsevol altre valor és error (CA-001-17).
- Dates `AAAA-MM-DD` i temps `m:ss.cc`.
- Un camp obligatori absent és error. Un opcional desconegut s'escriu `null`.

## `data/nedadors/<id>/nedador.json`
```json
{
  "versio_esquema": 1,
  "correu": "nedador@example.com",
  "alias": "exemple",
  "arxivat": false,
  "estils_preferents": ["Cr", "Ei"],
  "dies_entrenament": ["dl", "dc", "dv"],
  "volum_setmanal": {"min": 8000, "max": 12000},
  "tests_css": [
    {
      "data": "2000-01-15",
      "piscina": 25,
      "t400": "6:30.00",
      "t200": "3:10.00",
      "acceptat": true,
      "detall_400": {"parcials": null, "bracades_per_llarg": null, "sr": null, "rpe": 8},
      "detall_200": {"parcials": null, "bracades_per_llarg": null, "sr": null, "rpe": 9},
      "notes": null
    }
  ],
  "millors_registres": [
    {"estil": "Cr", "distancia": 100, "piscina": 25, "temps": "1:15.00", "data": "2000-02-01", "competicio": "Exemple"}
  ]
}
```

## `data/competicions/<AAAA-AA>.json`
```json
{
  "versio_esquema": 1,
  "competicions": [
    {"id": "c001", "nom": "Exemple", "dates": ["2000-03-04", "2000-03-05"], "piscina": 25, "seu": null}
  ]
}
```

## `data/nedadors/<id>/temporades/<AAAA-AA>/inscripcions.json`
```json
{
  "versio_esquema": 1,
  "participacions": [
    {
      "id_competicio": "c001",
      "classe": "A",
      "proves": [
        {"prova": {"distancia": 100, "estil": "Cr"}, "dia": "2000-03-04", "prioritat": "principal"}
      ]
    }
  ]
}
```

## `data/avisos.jsonl`
Una línia per avís; només s'hi afegeix.
```json
{"data_hora": "2000-03-04T10:15:00", "rn": "RN-009", "fitxer": "competicions/1999-00.json", "camp": "competicions.0.seu", "valor": null, "missatge": "Seu desconeguda", "id_nedador": null}
```
