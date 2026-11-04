import pytest

from blondswim.domain.valors import Alias, IdNedador

_ID = IdNedador("3f2a9c1e-7b4d-4e8a-9c2f-1d6b5e0a8f47")


@pytest.mark.parametrize(
    "text", ["marc_3f2a9c1", "ab_3f2a9c1", "abcdefghijkl_3f2a9c1", "a-b_0123abc"]
)
def test_alias_valid(text: str) -> None:
    assert str(Alias(text)) == text


@pytest.mark.ca("CA-001-46")
@pytest.mark.parametrize(
    "text",
    [
        "",
        "marc",  # sense sufix
        "Marc_3f2a9c1",  # majúscula
        "marc_cognom_3f2a9c1",  # dos guions baixos
        "a_3f2a9c1",  # part massa curta
        "abcdefghijklm_3f2a9c1",  # part de 13 caràcters
        "marc_3f2a9c",  # sufix de 6
        "marc_3F2A9C1",  # sufix en majúscules
    ],
)
def test_alias_que_incompleix_rn_003_es_rebutja(text: str) -> None:
    with pytest.raises(ValueError):
        Alias(text)


@pytest.mark.ca("CA-001-51")
def test_alias_amb_sufix_que_no_coincideix_amb_l_id() -> None:
    assert not Alias("marc_0000000").coincideix_amb(_ID)
    assert Alias("marc_3f2a9c1").coincideix_amb(_ID)


@pytest.mark.ca("CA-001-52")
def test_genera_l_alias_amb_els_7_primers_caracters_de_l_id() -> None:
    alias = Alias.genera("marc", _ID)
    assert alias == Alias("marc_3f2a9c1")
    assert alias.coincideix_amb(_ID)


@pytest.mark.ca("CA-001-46")
@pytest.mark.parametrize("part", ["", "m", "Marc", "marc_cognom", "abcdefghijklm"])
def test_genera_rebutja_una_part_que_incompleix_rn_003(part: str) -> None:
    with pytest.raises(ValueError):
        Alias.genera(part, _ID)
