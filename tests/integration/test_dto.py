import json

import pytest
from pydantic import ValidationError

from blondswim.domain.valors import Canal, Piscina
from blondswim.infrastructure.dto import ErrorCamp, NedadorDto, TestCssDto, errors_en_catala
from tests.integration.ajuts import nedador_json


def _test_css(**canvis: object) -> dict[str, object]:
    return {
        "data": "2000-01-15",
        "piscina": 25,
        "t400": "6:30.00",
        "t200": "3:10.00",
        "acceptat": True,
        **canvis,
    }


def _errors(dades: dict[str, object]) -> list[ErrorCamp]:
    with pytest.raises(ValidationError) as excepcio:
        TestCssDto.model_validate_json(json.dumps(dades))
    return errors_en_catala(excepcio.value)


def _errors_nedador(dades: dict[str, object]) -> list[ErrorCamp]:
    with pytest.raises(ValidationError) as excepcio:
        NedadorDto.model_validate_json(json.dumps(dades))
    return errors_en_catala(excepcio.value)


def test_dto_valid() -> None:
    dto = TestCssDto.model_validate_json(json.dumps(_test_css()))
    assert dto.piscina is Piscina.CURTA
    assert dto.acceptat is True


def test_piscina_com_a_text_es_error() -> None:
    assert _errors(_test_css(piscina="25")) == [ErrorCamp("piscina", "valor no admès")]


def test_acceptat_com_a_text_es_error() -> None:
    assert _errors(_test_css(acceptat="yes")) == [ErrorCamp("acceptat", "ha de ser true o false")]


def test_camp_desconegut_es_error() -> None:
    assert _errors(_test_css(extra=1)) == [ErrorCamp("extra", "camp desconegut")]


def test_camp_obligatori_absent_es_error() -> None:
    dades = _test_css()
    del dades["acceptat"]
    assert _errors(dades) == [ErrorCamp("acceptat", "camp obligatori absent")]


@pytest.mark.ca("CA-001-107")
@pytest.mark.parametrize("absent", [True, False])
def test_correu_absent_equival_a_null(absent: bool) -> None:
    dades = nedador_json()
    if absent:
        del dades["correu"]
    else:
        dades["correu"] = None

    assert NedadorDto.model_validate_json(json.dumps(dades)).correu is None


@pytest.mark.ca("CA-001-57")
@pytest.mark.parametrize("absent", [True, False])
def test_canal_preferent_absent_equival_a_null(absent: bool) -> None:
    dades = nedador_json()
    if absent:
        del dades["canal_preferent"]
    else:
        dades["canal_preferent"] = None

    assert NedadorDto.model_validate_json(json.dumps(dades)).canal_preferent is None


def test_canal_preferent_admet_correu_i_mobil() -> None:
    dades = nedador_json()
    dades["canal_preferent"] = "mobil"
    assert NedadorDto.model_validate_json(json.dumps(dades)).canal_preferent is Canal.MOBIL


@pytest.mark.ca("CA-001-54")
@pytest.mark.parametrize("absent", [True, False])
def test_mobil_absent_o_null_es_error_del_camp(absent: bool) -> None:
    dades = nedador_json()
    if absent:
        del dades["mobil"]
    else:
        dades["mobil"] = None

    assert [e.camp for e in _errors_nedador(dades)] == ["mobil"]


@pytest.mark.ca("CA-001-90")
@pytest.mark.parametrize("absent", [True, False])
def test_competicio_absent_o_null_es_error_del_camp(absent: bool) -> None:
    dades = nedador_json()
    registre = dades["millors_registres"][0]  # type: ignore[index]
    if absent:
        del registre["competicio"]
    else:
        registre["competicio"] = None

    assert [e.camp for e in _errors_nedador(dades)] == ["millors_registres.0.competicio"]
