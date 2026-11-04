from pathlib import Path

import pytest

from blondswim.domain.validacio import ErrorCarrega
from blondswim.infrastructure.repositoris import RepositoriNedadorsJson
from tests.integration.ajuts import ID_A, escriu, nedador_json


@pytest.mark.ca("CA-000-10")
@pytest.mark.parametrize("absent", [True, False])
def test_millor_registre_sense_piscina_es_error_del_dto_que_identifica_el_camp(
    tmp_path: Path, absent: bool
) -> None:
    dades = nedador_json()
    registre = dades["millors_registres"][0]  # type: ignore[index]
    if absent:
        del registre["piscina"]
    else:
        registre["piscina"] = None
    escriu(tmp_path, dades)

    with pytest.raises(ErrorCarrega) as excepcio:
        RepositoriNedadorsJson(tmp_path).carrega(ID_A)

    assert [e.camp for e in excepcio.value.errors] == ["millors_registres.0.piscina"]
