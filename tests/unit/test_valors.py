import pytest

from blondswim.domain.valors import Canal, Correu, Dia, Estil, IdNedador, Piscina, Temps


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
@pytest.mark.parametrize("codi", ["Fly", "cr", "Lliure", "EP", ""])
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


# --- IdNedador (RN-001, ADR-0014) ---


@pytest.mark.ca("CA-001-27")
def test_id_nedador_accepta_un_uuid_v4_en_minuscules() -> None:
    text = "3f2a9c1e-7b4d-4e8a-9c2f-1d6b5e0a8f47"
    assert str(IdNedador(text)) == text


@pytest.mark.ca("CA-001-27")
@pytest.mark.parametrize(
    "text",
    [
        "n0001",
        "3F2A9C1E-7B4D-4E8A-9C2F-1D6B5E0A8F47",  # majúscules
        "3f2a9c1e-7b4d-1e8a-9c2f-1d6b5e0a8f47",  # UUID v1
        "3f2a9c1e-7b4d-4e8a-cc2f-1d6b5e0a8f47",  # variant fora de 8-b
        "3f2a9c1e7b4d4e8a9c2f1d6b5e0a8f47",  # sense guions
        "3f2a9c1e-7b4d-4e8a-9c2f-1d6b5e0a8f47\n",
        "",
    ],
)
def test_id_nedador_rebutja_el_que_no_es_uuid_v4_canonic(text: str) -> None:
    with pytest.raises(ValueError):
        IdNedador(text)


# --- Correu (RN-032, ADR-0020) ---


@pytest.mark.ca("CA-001-104")
@pytest.mark.parametrize(
    "text",
    [
        "a@b.c",
        "  Pere@Exemple.cat ",
        "\tpere@exemple.cat",
        "pere@exemple.cat\n",
        "a@b@example.com",
    ],
)
def test_correu_de_format_basic_s_accepta_i_es_conserva_identic(text: str) -> None:
    correu = Correu(text)
    assert correu.format_valid
    assert correu.valor == text
    assert str(correu) == text


@pytest.mark.ca("CA-001-105")
@pytest.mark.parametrize(
    "text",
    [
        "nedador.example.com",  # sense @
        "@example.com",  # sense part local
        "nedador@",  # sense domini
        "nedador@example",  # domini sense punt
        "a b@example.com",  # espai al mig
        "a\tb@example.com",  # tabulador al mig
    ],
)
def test_correu_amb_format_no_valid_es_rebutja(text: str) -> None:
    assert not Correu(text).format_valid


@pytest.mark.ca("CA-001-44")
@pytest.mark.parametrize("text", ["", " ", " \t\n "])
def test_correu_buit_o_nomes_amb_espais_en_blanc_es_rebutja(text: str) -> None:
    assert not Correu(text).format_valid


@pytest.mark.ca("CA-001-106")
def test_correu_amb_error_tipografic_s_accepta_tal_qual() -> None:
    correu = Correu("usari@gmial.com")
    assert correu.format_valid
    assert correu.valor == "usari@gmial.com"


@pytest.mark.ca("CA-001-108")
@pytest.mark.parametrize(
    "a, b",
    [
        ("A@b.com", " a@b.com "),
        ("a@b.com", "\ta@B.com\n"),
        ("Pere@Exemple.cat", "pere@exemple.cat"),
    ],
)
def test_clau_de_comparacio_en_minuscules_i_sense_espais_en_blanc_als_extrems(
    a: str, b: str
) -> None:
    assert Correu(a).clau == Correu(b).clau
    # El valor desat no canvia.
    assert Correu(a).valor == a
    assert Correu(b).valor == b


@pytest.mark.ca("CA-001-108")
def test_clau_de_correus_diferents_es_diferent() -> None:
    assert Correu("a@b.com").clau != Correu("a@c.com").clau


# --- Canal (RN-035) ---


@pytest.mark.ca("CA-001-59")
def test_canal_nomes_admet_correu_i_mobil() -> None:
    assert {c.value for c in Canal} == {"correu", "mobil"}
    assert Canal("correu") is Canal.CORREU
    assert Canal("mobil") is Canal.MOBIL


@pytest.mark.ca("CA-001-59")
@pytest.mark.parametrize("text", ["whatsapp", "Correu", "", "sms"])
def test_canal_rebutja_altres_valors(text: str) -> None:
    with pytest.raises(ValueError):
        Canal(text)
