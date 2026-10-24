import pytest

from blondswim.domain.valors import Alias, Correu, Dia, Estil, IdNedador, Piscina, Temps


@pytest.mark.ca("CA-001-07")
@pytest.mark.parametrize("text", ["1:05.3", "1:05", "1:5.30", "1:65.30", "1:05,30", "65.30", ""])
def test_temps_rebutja_format_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        Temps.de_text(text)


@pytest.mark.ca("CA-001-07")
def test_temps_format_i_centesimes() -> None:
    temps = Temps.de_text("1:05.30")
    assert temps.centesimes == 6530
    assert str(temps) == "1:05.30"
    assert Temps.de_text("10:00.05") == Temps(60005)


def test_temps_es_compara_per_centesimes() -> None:
    assert Temps.de_text("6:30.00") > Temps.de_text("3:10.00")


@pytest.mark.ca("CA-001-41")
@pytest.mark.parametrize("metres", [25, 50])
def test_piscina_admet_25_i_50(metres: int) -> None:
    assert Piscina(metres).value == metres


@pytest.mark.ca("CA-001-41")
@pytest.mark.parametrize("metres", [0, 33, 100])
def test_piscina_rebutja_altres_valors(metres: int) -> None:
    with pytest.raises(ValueError):
        Piscina(metres)


@pytest.mark.ca("CA-001-39")
@pytest.mark.parametrize("codi", ["Cr", "Esq", "Br", "Pap", "Ei"])
def test_estil_admet_els_cinc(codi: str) -> None:
    assert Estil(codi).value == codi


@pytest.mark.ca("CA-001-39")
@pytest.mark.parametrize("codi", ["Fly", "cr", "Lliure", ""])
def test_estil_rebutja_altres_valors(codi: str) -> None:
    with pytest.raises(ValueError):
        Estil(codi)


@pytest.mark.ca("CA-001-40")
def test_dia_admet_els_set_i_numero_iso() -> None:
    codis = ["dl", "dt", "dc", "dj", "dv", "ds", "dg"]
    assert [Dia(c).numero_iso for c in codis] == [1, 2, 3, 4, 5, 6, 7]
    assert len(Dia) == 7


@pytest.mark.ca("CA-001-40")
@pytest.mark.parametrize("codi", ["dm", "DL", "dll", ""])
def test_dia_rebutja_altres_valors(codi: str) -> None:
    with pytest.raises(ValueError):
        Dia(codi)


@pytest.mark.ca("CA-001-27")
def test_id_nedador_valid() -> None:
    assert str(IdNedador("n0001")) == "n0001"


@pytest.mark.ca("CA-001-27")
@pytest.mark.parametrize("text", ["n001", "n00012", "N0001", "x0001", "n000a", "", "n0001\n"])
def test_id_nedador_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        IdNedador(text)


@pytest.mark.ca("CA-001-44")
@pytest.mark.parametrize("text", ["", "a b@example.com", " ", "a@example.com "])
def test_correu_rebutja_buit_o_amb_espais(text: str) -> None:
    with pytest.raises(ValueError):
        Correu(text)


@pytest.mark.ca("CA-001-44")
def test_correu_igualtat_sense_distingir_majuscules() -> None:
    assert Correu("Nedador@Example.com") == Correu("nedador@example.com")
    assert hash(Correu("Nedador@Example.com")) == hash(Correu("nedador@example.com"))


@pytest.mark.parametrize("text", ["ab", "exemple-1", "a" * 20])
def test_alias_valid(text: str) -> None:
    assert str(Alias(text)) == text


@pytest.mark.parametrize("text", ["a", "a" * 21, "Ab", "a_b", "n0001", ""])
def test_alias_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        Alias(text)
