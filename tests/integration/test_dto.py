import pytest
from pydantic import ValidationError

from blondswim.domain.valors import Piscina
from blondswim.infrastructure.dto import DtoBase, ErrorCamp, errors_en_catala


class _Exemple(DtoBase):
    piscina: Piscina
    acceptat: bool


def _errors(json_text: str) -> list[ErrorCamp]:
    with pytest.raises(ValidationError) as excepcio:
        _Exemple.model_validate_json(json_text)
    return errors_en_catala(excepcio.value)


def test_dto_valid() -> None:
    dto = _Exemple.model_validate_json('{"piscina": 25, "acceptat": true}')
    assert dto.piscina is Piscina.CURTA
    assert dto.acceptat is True


def test_piscina_com_a_text_es_error() -> None:
    assert _errors('{"piscina": "25", "acceptat": true}') == [
        ErrorCamp(camp="piscina", missatge="valor no admès")
    ]


def test_acceptat_com_a_text_es_error() -> None:
    assert _errors('{"piscina": 25, "acceptat": "yes"}') == [
        ErrorCamp(camp="acceptat", missatge="ha de ser true o false")
    ]


def test_camp_desconegut_es_error() -> None:
    assert _errors('{"piscina": 25, "acceptat": true, "extra": 1}') == [
        ErrorCamp(camp="extra", missatge="camp desconegut")
    ]


def test_camp_obligatori_absent_es_error() -> None:
    assert _errors('{"piscina": 25}') == [
        ErrorCamp(camp="acceptat", missatge="camp obligatori absent")
    ]
