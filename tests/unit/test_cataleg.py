import pytest

from blondswim.domain.cataleg import Cataleg
from blondswim.domain.nedador import ErrorInvariant
from blondswim.domain.validacio import valida_cataleg
from blondswim.domain.valors import CodiTemporada
from tests.unit.fakes import competicio

TEMPORADA = CodiTemporada("1999-00")


@pytest.mark.ca("CA-001-11")
def test_ids_de_competicio_repetits_son_un_error_rn_008() -> None:
    with pytest.raises(ErrorInvariant) as excepcio:
        Cataleg((competicio(id="c001"), competicio(id="c002"), competicio(id="c001")))

    assert [(v.rn, v.camp, v.valor) for v in excepcio.value.violacions] == [
        ("RN-008", "competicions.2.id", "c001")
    ]


def test_ids_diferents_formen_un_cataleg() -> None:
    cataleg = Cataleg((competicio(id="c001"), competicio(id="c002")))

    assert [c.id for c in cataleg.competicions] == ["c001", "c002"]


def test_cataleg_buit_es_valid() -> None:
    assert Cataleg(()).competicions == ()


def test_competicio_sense_dates_es_un_error() -> None:
    with pytest.raises(ErrorInvariant) as excepcio:
        competicio(dates=())

    assert [(v.camp, v.valor) for v in excepcio.value.violacions] == [("dates", ())]


@pytest.mark.ca("CA-001-12")
def test_seu_desconeguda_es_un_avis_rn_009_i_no_un_error() -> None:
    cataleg = Cataleg((competicio(id="c001", seu=None), competicio(id="c002", seu="Seu")))

    resultat = valida_cataleg(TEMPORADA, cataleg)

    assert resultat.es_valid
    assert [(a.rn, a.fitxer, a.camp, a.valor) for a in resultat.avisos] == [
        ("RN-009", "competicions/1999-00.json", "competicions.0.seu", None)
    ]
    assert "c001" in resultat.avisos[0].missatge


def test_seu_coneguda_no_dona_cap_avis() -> None:
    resultat = valida_cataleg(TEMPORADA, Cataleg((competicio(seu="Seu"),)))

    assert resultat.errors == ()
    assert resultat.avisos == ()
