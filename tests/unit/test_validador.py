from datetime import date

import pytest

from blondswim.domain.validacio import Identitat, Resultat, valida_nedador, valida_unicitat
from blondswim.domain.valors import Alias, Canal, Correu, Piscina
from tests.unit.fakes import (
    ALIAS_A,
    ALIAS_B,
    ALIAS_C,
    ID_A,
    ID_B,
    ID_C,
    nedador,
    registre,
    temps,
)


def _camps(resultat: Resultat) -> list[str]:
    return [e.camp for e in resultat.errors]


# --- Unicitat (CA-001-24, 26, 69, 76, 108) ---


@pytest.mark.ca("CA-001-24")
def test_col_lisio_de_correu_amb_majuscules_diferents_i_un_arxivat() -> None:
    identitats = {
        ID_A: Identitat.de(nedador(correu=Correu("Nedador@Example.com"))),
        ID_B: Identitat.de(
            nedador(correu=Correu("nedador@example.com"), arxivat=True, alias=ALIAS_B)
        ),
    }
    errors = valida_unicitat(identitats)
    assert [(e.rn, e.camp) for e in errors] == [("RN-032", "correu")]
    assert set(errors[0].implicats) == {ID_A, ID_B}


@pytest.mark.ca("CA-001-26")
def test_col_lisio_d_alias_identifica_tots_dos_nedadors() -> None:
    identitats = {
        ID_A: Identitat.de(nedador(correu=Correu("a@example.com"))),
        ID_B: Identitat.de(nedador(correu=Correu("b@example.com"), arxivat=True)),
    }
    errors = valida_unicitat(identitats)
    assert [(e.rn, e.camp) for e in errors] == [("RN-003", "alias")]
    assert set(errors[0].implicats) == {ID_A, ID_B}


@pytest.mark.ca("CA-001-69")
def test_col_lisio_de_correu_amb_un_error_en_un_altre_camp() -> None:
    amb_error = nedador(mobil="", correu=Correu("x@example.com"))
    altre = nedador(correu=Correu("X@example.com"), alias=ALIAS_B)
    assert not valida_nedador(ID_A, amb_error).es_valid

    errors = valida_unicitat({ID_A: Identitat.de(amb_error), ID_B: Identitat.de(altre)})

    assert [(e.rn, e.camp) for e in errors] == [("RN-032", "correu")]
    assert set(errors[0].implicats) == {ID_A, ID_B}


@pytest.mark.ca("CA-001-76")
def test_col_lisio_d_alias_amb_un_error_en_un_altre_camp() -> None:
    amb_error = nedador(mobil=" ")
    altre = nedador(correu=Correu("b@example.com"))
    assert not valida_nedador(ID_A, amb_error).es_valid

    errors = valida_unicitat({ID_A: Identitat.de(amb_error), ID_B: Identitat.de(altre)})

    assert [(e.rn, e.camp) for e in errors] == [("RN-003", "alias")]
    assert set(errors[0].implicats) == {ID_A, ID_B}


@pytest.mark.ca("CA-001-108")
def test_col_lisio_de_correus_que_nomes_difereixen_en_majuscules_i_espais() -> None:
    a = nedador(correu=Correu("A@b.com"))
    b = nedador(correu=Correu(" a@b.com "), arxivat=True, alias=ALIAS_B)

    errors = valida_unicitat({ID_A: Identitat.de(a), ID_B: Identitat.de(b)})

    assert [(e.rn, e.camp) for e in errors] == [("RN-032", "correu")]
    assert set(errors[0].implicats) == {ID_A, ID_B}
    # El valor de cada nedador no canvia.
    assert a.correu is not None and a.correu.valor == "A@b.com"
    assert b.correu is not None and b.correu.valor == " a@b.com "


@pytest.mark.ca("CA-001-107")
def test_els_nedadors_sense_correu_no_participen_a_la_unicitat() -> None:
    identitats = {
        ID_A: Identitat.de(nedador(correu=None, canal_preferent=Canal.MOBIL)),
        ID_B: Identitat.de(nedador(correu=None, canal_preferent=Canal.MOBIL, alias=ALIAS_B)),
    }
    assert valida_unicitat(identitats) == ()


@pytest.mark.ca("CA-001-101")
def test_el_mobil_no_participa_a_la_unicitat() -> None:
    identitats = {
        ID_A: Identitat.de(nedador(mobil="+34600000000")),
        ID_B: Identitat.de(
            nedador(mobil="+34600000000", correu=Correu("b@example.com"), alias=ALIAS_B)
        ),
        ID_C: Identitat.de(
            nedador(mobil="600 00 00 00", correu=Correu("c@example.com"), alias=ALIAS_C)
        ),
    }
    assert valida_unicitat(identitats) == ()


@pytest.mark.ca("CA-001-92")
def test_un_camp_d_identitat_il_legible_no_participa_a_la_unicitat_d_aquell_camp() -> None:
    # `correu` no és text: no hi ha clau de correu, però l'alias sí que compta.
    identitats = {
        ID_A: Identitat(correu=None, alias=str(ALIAS_A)),
        ID_B: Identitat(correu="b@example.com", alias=str(ALIAS_A)),
    }
    errors = valida_unicitat(identitats)
    assert [(e.rn, e.camp) for e in errors] == [("RN-003", "alias")]
    assert set(errors[0].implicats) == {ID_A, ID_B}


# --- Errors del nedador ---


@pytest.mark.ca("CA-001-44")
def test_correu_buit_es_error_de_format_del_camp() -> None:
    resultat = valida_nedador(ID_A, nedador(correu=Correu("")))
    assert [(e.rn, e.camp) for e in resultat.errors] == [("RN-032", "correu")]


@pytest.mark.ca("CA-001-50")
def test_alias_absent_es_error_que_identifica_el_camp() -> None:
    resultat = valida_nedador(ID_A, nedador(alias=None))
    assert [(e.rn, e.camp) for e in resultat.errors] == [("RN-003", "alias")]
    assert resultat.errors[0].nedador == str(ID_A)  # sense alias, s'identifica per l'UUID


@pytest.mark.ca("CA-001-51")
def test_alias_amb_sufix_que_no_coincideix_amb_l_id_es_error() -> None:
    resultat = valida_nedador(ID_A, nedador(alias=Alias("marc_0000000")))
    assert [(e.rn, e.camp, e.valor) for e in resultat.errors] == [
        ("RN-003", "alias", "marc_0000000")
    ]


@pytest.mark.ca("CA-001-93")
@pytest.mark.parametrize("mobil", ["", " ", "     "])
def test_mobil_buit_o_nomes_amb_espais_es_error_de_format(mobil: str) -> None:
    resultat = valida_nedador(ID_A, nedador(mobil=mobil))
    assert [(e.rn, e.camp, e.valor) for e in resultat.errors] == [("format", "mobil", mobil)]


@pytest.mark.ca("CA-001-111")
@pytest.mark.parametrize("mobil", ["\t", "\n", " \t\n "])
def test_mobil_amb_nomes_un_tabulador_o_un_salt_de_linia_es_error(mobil: str) -> None:
    resultat = valida_nedador(ID_A, nedador(mobil=mobil))
    assert [(e.rn, e.camp) for e in resultat.errors] == [("format", "mobil")]


@pytest.mark.ca("CA-001-101")
@pytest.mark.parametrize("mobil", ["600 00 00 00", "+34600000000", "abc"])
def test_el_mobil_no_te_format_ni_genera_avisos(mobil: str) -> None:
    resultat = valida_nedador(ID_A, nedador(mobil=mobil))
    assert resultat.errors == ()
    assert resultat.avisos == ()


@pytest.mark.ca("CA-001-105")
@pytest.mark.parametrize(
    "text",
    [
        "nedador.example.com",
        "@example.com",
        "nedador@",
        "nedador@example",
        "a b@example.com",
    ],
)
def test_correu_amb_format_no_valid_es_error_que_identifica_camp_i_valor(text: str) -> None:
    resultat = valida_nedador(ID_A, nedador(correu=Correu(text)))
    assert [(e.rn, e.camp, e.valor) for e in resultat.errors] == [("RN-032", "correu", text)]


@pytest.mark.ca("CA-001-105")
@pytest.mark.parametrize(
    "text", ["a@b.c", "  Pere@Exemple.cat ", "\tpere@exemple.cat", "a@b@example.com"]
)
def test_correu_de_format_basic_no_dona_error(text: str) -> None:
    assert valida_nedador(ID_A, nedador(correu=Correu(text))).es_valid


@pytest.mark.ca("CA-001-107")
def test_sense_correu_i_amb_canal_mobil_es_valid_sense_errors_ni_avisos() -> None:
    resultat = valida_nedador(ID_A, nedador(correu=None, canal_preferent=Canal.MOBIL))
    assert resultat.errors == ()
    assert resultat.avisos == ()


@pytest.mark.ca("CA-001-91")
def test_competicio_que_no_es_al_cataleg_no_dona_error_ni_avis() -> None:
    n = nedador(millors_registres=(registre(competicio="No existeix"),))
    resultat = valida_nedador(ID_A, n)
    assert resultat.errors == ()
    assert resultat.avisos == ()


@pytest.mark.ca("CA-001-96")
def test_llista_de_marques_no_ordenada_es_error_que_identifica_prova_i_piscina() -> None:
    registres = (
        registre(temps=temps("1:10.00"), data=date(2000, 1, 1)),
        registre(temps=temps("1:08.00"), data=date(2000, 2, 1)),
        registre(temps=temps("1:09.00"), data=date(2000, 3, 1)),
    )
    resultat = valida_nedador(ID_A, nedador(millors_registres=registres))
    assert [(e.rn, e.camp) for e in resultat.errors] == [("RN-007", "millors_registres.2")]
    assert all(text in resultat.errors[0].missatge for text in ("100", "Cr", "25"))


@pytest.mark.ca("CA-001-102")
@pytest.mark.parametrize("data_segona", [date(2000, 1, 1), date(1999, 12, 31)])
def test_marca_amb_data_igual_o_anterior_a_la_de_l_anterior_es_error(data_segona: date) -> None:
    registres = (
        registre(temps=temps("1:10.00"), data=date(2000, 1, 1)),
        registre(temps=temps("1:08.00"), data=data_segona),
    )
    resultat = valida_nedador(ID_A, nedador(millors_registres=registres))
    assert [(e.rn, e.camp) for e in resultat.errors] == [("RN-007", "millors_registres.1")]
    assert all(text in resultat.errors[0].missatge for text in ("100", "Cr", "25"))


@pytest.mark.ca("CA-001-102")
def test_la_data_es_compara_dins_de_cada_prova_i_piscina() -> None:
    registres = (
        registre(temps=temps("1:10.00"), data=date(2000, 6, 1)),
        registre(piscina=Piscina.LLARGA, temps=temps("1:20.00"), data=date(2000, 1, 1)),
    )
    assert valida_nedador(ID_A, nedador(millors_registres=registres)).es_valid


# --- Avisos (RN-035) ---


@pytest.mark.ca("CA-001-57")
def test_canal_preferent_absent_dona_un_avis_rn_035_que_no_bloqueja() -> None:
    resultat = valida_nedador(ID_A, nedador(canal_preferent=None))
    assert resultat.es_valid
    assert [(a.rn, a.camp, a.nedador) for a in resultat.avisos] == [
        ("RN-035", "canal_preferent", str(ALIAS_A))
    ]


@pytest.mark.ca("CA-001-110")
def test_canal_correu_sense_correu_dona_un_avis_rn_035_que_no_bloqueja() -> None:
    resultat = valida_nedador(ID_A, nedador(correu=None, canal_preferent=Canal.CORREU))
    assert resultat.es_valid
    assert [(a.rn, a.camp, a.nedador) for a in resultat.avisos] == [
        ("RN-035", "canal_preferent", str(ALIAS_A))
    ]


@pytest.mark.ca("CA-001-110")
def test_canal_correu_amb_correu_no_dona_avis() -> None:
    assert valida_nedador(ID_A, nedador(canal_preferent=Canal.CORREU)).avisos == ()


# --- Resultat: errors i avisos per separat, amb tots els camps (CA-001-67, 73) ---


@pytest.mark.ca("CA-001-67")
def test_el_resultat_separa_errors_i_avisos_amb_alias_camp_valor_rn_i_accio() -> None:
    resultat = valida_nedador(ID_A, nedador(mobil="", canal_preferent=None))

    assert [e.camp for e in resultat.errors] == ["mobil"]
    assert [a.camp for a in resultat.avisos] == ["canal_preferent"]
    for element in (*resultat.errors, *resultat.avisos):
        assert element.nedador == str(ALIAS_A)
        assert element.rn
        assert element.fitxer == f"nedadors/{ID_A}/nedador.json"
        assert element.accio
        assert element.missatge
    assert resultat.errors[0].valor == ""
    assert resultat.errors[0].rn == "format"


@pytest.mark.ca("CA-001-67")
def test_cada_nedador_te_el_seu_resultat() -> None:
    bo = valida_nedador(ID_B, nedador(alias=ALIAS_B))
    dolent = valida_nedador(ID_C, nedador(alias=ALIAS_C, mobil=""))
    assert bo.es_valid and not dolent.es_valid
    assert dolent.errors[0].nedador == str(ALIAS_C)


@pytest.mark.ca("CA-001-73")
def test_un_nedador_amb_diversos_errors_els_llista_tots() -> None:
    registres = (
        registre(temps=temps("1:08.00"), data=date(2000, 1, 1)),
        registre(temps=temps("1:09.00"), data=date(2000, 2, 1)),
    )
    n = nedador(correu=Correu("nedador.example.com"), mobil=" ", millors_registres=registres)

    resultat = valida_nedador(ID_A, n)

    assert sorted(_camps(resultat)) == ["correu", "millors_registres.1", "mobil"]
    for error in resultat.errors:
        assert error.rn and error.accio and error.nedador == str(ALIAS_A)
