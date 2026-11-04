"""Ajuts dels tests d'integració: fixtures JSON del nedador i escriptura a `tmp_path`."""

import json
from pathlib import Path

from blondswim.domain.valors import IdNedador

# UUID v4 fictius; ID_X comparteix els 7 primers caràcters amb ID_A.
ID_A = IdNedador("3f2a9c1e-7b4d-4e8a-9c2f-1d6b5e0a8f47")
ID_B = IdNedador("9b1c2d3e-4f5a-4b6c-8d7e-0a1b2c3d4e5f")
ID_X = IdNedador("3f2a9c1f-0000-4000-8000-000000000000")


def nedador_json(alias: str = "exemple_3f2a9c1") -> dict[str, object]:
    return {
        "versio_esquema": 1,
        "correu": "nedador@example.com",
        "mobil": "+34600000000",
        "canal_preferent": "correu",
        "alias": alias,
        "arxivat": False,
        "estils_preferents": ["Cr", "Ei"],
        "dies_entrenament": ["dl", "dc", "dv"],
        "volum_setmanal": {"min": 8000, "max": 12000},
        "tests_css": [
            {
                "data": "2000-01-15",
                "piscina": 25,
                "t400": "6:30.00",
                "t200": "3:10.00",
                "acceptat": True,
                "detall_400": {"parcials": None, "bracades_per_llarg": None, "sr": None, "rpe": 8},
                "detall_200": {"parcials": None, "bracades_per_llarg": None, "sr": None, "rpe": 9},
                "notes": None,
            }
        ],
        "millors_registres": [
            {
                "estil": "Cr",
                "distancia": 100,
                "piscina": 25,
                "temps": "1:16.00",
                "data": "2000-01-22",
                "competicio": "Exemple anterior",
            },
            {
                "estil": "Cr",
                "distancia": 100,
                "piscina": 25,
                "temps": "1:15.00",
                "data": "2000-03-04",
                "competicio": "Exemple",
            },
        ],
    }


def escriu(arrel: Path, dades: object, id_nedador: IdNedador = ID_A) -> Path:
    """Escriu `nedador.json`; `dades` pot ser un objecte JSON o text cru (fitxer trencat)."""
    cami = arrel / "nedadors" / str(id_nedador) / "nedador.json"
    cami.parent.mkdir(parents=True)
    text = dades if isinstance(dades, str) else json.dumps(dades, indent=2)
    cami.write_text(text, encoding="utf-8")
    return cami
