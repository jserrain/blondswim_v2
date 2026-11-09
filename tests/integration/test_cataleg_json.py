import json
from datetime import date
from pathlib import Path

import pytest

from blondswim.application.ports import RepositoriCataleg
from blondswim.domain.cataleg import Cataleg
from blondswim.domain.validacio import ErrorCarrega
from blondswim.domain.valors import Piscina
from blondswim.infrastructure.repositoris import RepositoriCatalegJson
from tests.integration.ajuts import TEMPORADA, cataleg_json, escriu_cataleg

FITXER = "competicions/1999-00.json"


def _errors_de_carrega(arrel: Path) -> ErrorCarrega:
    with pytest.raises(ErrorCarrega) as excepcio:
        RepositoriCatalegJson(arrel).carrega(TEMPORADA)
    return excepcio.value


def _competicions(dades: dict[str, object]) -> list[dict[str, object]]:
    return dades["competicions"]  # type: ignore[return-value]


def test_el_repositori_compleix_el_port_amb_el_cataleg(tmp_path: Path) -> None:
    port: RepositoriCataleg[Cataleg] = RepositoriCatalegJson(tmp_path)

    assert port is not None


def test_carrega_el_cataleg_de_la_temporada(tmp_path: Path) -> None:
    escriu_cataleg(tmp_path, cataleg_json())

    cataleg = RepositoriCatalegJson(tmp_path).carrega(TEMPORADA)

    primera, segona = cataleg.competicions
    assert (primera.id, primera.nom, primera.piscina, primera.seu) == (
        "c001",
        "Exemple",
        Piscina.CURTA,
        None,
    )
    assert primera.dates == (date(2000, 3, 4), date(2000, 3, 5))
    assert (segona.piscina, segona.seu) == (Piscina.LLARGA, "Seu exemple")


def test_carregar_i_desar_dona_contingut_equivalent(tmp_path: Path) -> None:
    original = cataleg_json()
    cami = escriu_cataleg(tmp_path, original)
    repositori = RepositoriCatalegJson(tmp_path)

    repositori.desa(TEMPORADA, repositori.carrega(TEMPORADA))

    assert json.loads(cami.read_text(encoding="utf-8")) == original


@pytest.mark.ca("CA-001-11")
def test_ids_repetits_fallen_la_carrega_amb_rn_008(tmp_path: Path) -> None:
    dades = cataleg_json()
    _competicions(dades)[1]["id"] = "c001"
    escriu_cataleg(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.rn, e.fitxer, e.camp, e.valor) for e in errors] == [
        ("RN-008", FITXER, "competicions.1.id", "c001")
    ]


@pytest.mark.ca("CA-001-12")
@pytest.mark.parametrize("amb_camp", [True, False])
def test_seu_null_o_absent_es_carrega_com_a_none(tmp_path: Path, amb_camp: bool) -> None:
    dades = cataleg_json()
    if not amb_camp:
        del _competicions(dades)[0]["seu"]
    escriu_cataleg(tmp_path, dades)

    cataleg = RepositoriCatalegJson(tmp_path).carrega(TEMPORADA)

    assert cataleg.competicions[0].seu is None


@pytest.mark.ca("CA-001-17")
@pytest.mark.parametrize("versio", [0, 2, "1", True])
def test_versio_desconeguda_del_cataleg_dona_error(tmp_path: Path, versio: object) -> None:
    dades = cataleg_json()
    dades["versio_esquema"] = versio
    escriu_cataleg(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.valor) for e in errors] == [(FITXER, "versio_esquema", versio)]


@pytest.mark.ca("CA-001-36")
def test_cataleg_desat_pel_sistema_es_identic_byte_a_byte(tmp_path: Path) -> None:
    cami = escriu_cataleg(tmp_path, cataleg_json())
    repositori = RepositoriCatalegJson(tmp_path)
    repositori.desa(TEMPORADA, repositori.carrega(TEMPORADA))
    primer = cami.read_bytes()

    repositori.desa(TEMPORADA, repositori.carrega(TEMPORADA))

    assert cami.read_bytes() == primer
    assert primer.endswith(b"\n")
    assert b'"seu": null' in primer


@pytest.mark.ca("CA-001-41")
@pytest.mark.parametrize("piscina", [0, 30, 100])
def test_piscina_no_admesa_en_una_competicio_falla_tota_la_carrega(
    tmp_path: Path, piscina: int
) -> None:
    dades = cataleg_json()
    _competicions(dades)[1]["piscina"] = piscina
    escriu_cataleg(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.valor) for e in errors] == [
        (FITXER, "competicions.1.piscina", piscina)
    ]


@pytest.mark.ca("CA-001-71")
@pytest.mark.parametrize("nom", ["2026-28.json", "1999.json", "cataleg.json"])
def test_nom_de_fitxer_que_no_segueix_rn_031_falla_tota_la_carrega(
    tmp_path: Path, nom: str
) -> None:
    escriu_cataleg(tmp_path, cataleg_json())
    escriu_cataleg(tmp_path, cataleg_json(), nom)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.rn, e.fitxer) for e in errors] == [("RN-031", f"competicions/{nom}")]


def test_dates_buides_donen_error_amb_el_camp(tmp_path: Path) -> None:
    dades = cataleg_json()
    _competicions(dades)[0]["dates"] = []
    escriu_cataleg(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp) for e in errors] == [(FITXER, "competicions.0.dates")]


def test_camp_obligatori_absent_dona_error_amb_el_camp(tmp_path: Path) -> None:
    dades = cataleg_json()
    del _competicions(dades)[1]["nom"]
    escriu_cataleg(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.missatge) for e in errors] == [
        (FITXER, "competicions.1.nom", "camp obligatori absent")
    ]


def test_json_trencat_falla_la_carrega(tmp_path: Path) -> None:
    escriu_cataleg(tmp_path, "{")

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.missatge) for e in errors] == [(FITXER, "", "JSON invàlid")]
