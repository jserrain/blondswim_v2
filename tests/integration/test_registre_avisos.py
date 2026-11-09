"""US6 — registre d'avisos `data/avisos.jsonl` (T030), amb `tmp_path` i rellotge fix."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from blondswim.application.carrega import carrega_nedadors
from blondswim.domain.validacio import Avis
from blondswim.infrastructure.registre_avisos import RegistreAvisosJsonl
from blondswim.infrastructure.repositoris import RepositoriCatalegJson, RepositoriNedadorsJson
from tests.integration.ajuts import (
    ID_A,
    TEMPORADA,
    cataleg_json,
    escriu,
    escriu_cataleg,
    escriu_inscripcions,
    inscripcions_json,
    nedador_json,
)

ARA = datetime(2000, 3, 4, 10, 15)


class RellotgeFix:
    def ara(self) -> datetime:
        return ARA


def linies(arrel: Path) -> list[dict[str, object]]:
    cami = arrel / "avisos.jsonl"
    if not cami.exists():
        return []
    return [json.loads(linia) for linia in cami.read_text(encoding="utf-8").splitlines()]


def carrega(arrel: Path) -> None:
    carrega_nedadors(
        RepositoriNedadorsJson(arrel),
        RepositoriCatalegJson(arrel),
        registre=RegistreAvisosJsonl(arrel / "avisos.jsonl"),
        rellotge=RellotgeFix(),
    )


@pytest.mark.ca("CA-001-47")
def test_seu_null_registra_l_avis_rn_009_amb_decisio_null(tmp_path: Path) -> None:
    escriu(tmp_path, nedador_json())
    escriu_inscripcions(tmp_path, inscripcions_json())
    escriu_cataleg(tmp_path, cataleg_json())  # c001 té `seu: null`
    carrega(tmp_path)
    (linia,) = linies(tmp_path)
    assert linia == {
        "data_hora": "2000-03-04T10:15:00",
        "rn": "RN-009",
        "fitxer": f"competicions/{TEMPORADA}.json",
        "camp": "competicions.0.seu",
        "valor": None,
        "missatge": "la seu de la competició 'c001' és desconeguda",
        "id_nedador": None,
        "decisio": None,
    }


@pytest.mark.ca("CA-001-48")
def test_les_linies_anteriors_es_conserven(tmp_path: Path) -> None:
    cami = tmp_path / "avisos.jsonl"
    anterior = '{"data_hora": "1999-01-01T00:00:00", "rn": "RN-009"}\n'
    cami.write_text(anterior, encoding="utf-8")
    registre = RegistreAvisosJsonl(cami)
    registre.afegeix(ARA, Avis("RN-035", "f", "canal_preferent", None, "absent"), ID_A)
    text = cami.read_text(encoding="utf-8")
    assert text.startswith(anterior)
    assert len(text.splitlines()) == 2


@pytest.mark.ca("CA-001-57")
def test_canal_preferent_absent_registra_rn_035_i_es_carrega(tmp_path: Path) -> None:
    escriu(tmp_path, {**nedador_json(), "canal_preferent": None})
    resultat = carrega_nedadors(
        RepositoriNedadorsJson(tmp_path),
        registre=RegistreAvisosJsonl(tmp_path / "avisos.jsonl"),
        rellotge=RellotgeFix(),
    )
    assert ID_A in resultat.nedadors
    (linia,) = linies(tmp_path)
    assert (linia["rn"], linia["camp"], linia["id_nedador"], linia["decisio"]) == (
        "RN-035",
        "canal_preferent",
        str(ID_A),
        None,
    )


@pytest.mark.ca("CA-001-110")
def test_canal_correu_sense_correu_registra_rn_035_amb_canal_preferent(tmp_path: Path) -> None:
    escriu(tmp_path, {**nedador_json(), "correu": None, "canal_preferent": "correu"})
    carrega(tmp_path)
    (linia,) = linies(tmp_path)
    assert (linia["rn"], linia["camp"], linia["valor"], linia["decisio"]) == (
        "RN-035",
        "canal_preferent",
        "correu",
        None,
    )


def test_sense_avisos_no_es_crea_cap_linia(tmp_path: Path) -> None:
    escriu(tmp_path, nedador_json())
    carrega(tmp_path)
    assert linies(tmp_path) == []
