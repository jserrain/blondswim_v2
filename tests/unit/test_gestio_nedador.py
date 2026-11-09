from dataclasses import FrozenInstanceError, replace
from datetime import date

import pytest

from blondswim.application import gestio
from blondswim.application.gestio import (
    NouNedador,
    afegeix_millor_registre,
    afegeix_test,
    alta,
    arxiva,
    desarxiva,
    modifica,
)
from blondswim.domain.nedador import CanviNedador, VolumSetmanal, marca_vigent
from blondswim.domain.valors import Alias, Canal, Correu, Dia, Estil, IdNedador, Piscina, Prova
from tests.unit.fakes import (
    ALIAS_B,
    ID_A,
    ID_B,
    ID_C,
    ID_X,
    GeneradorFix,
    RepositoriMemoria,
    com_a_port,
    nedador,
    registre,
    temps,
    un_test,
)

_CR100 = Prova(100, Estil.CR)


def _nou(**canvis: object) -> NouNedador:
    base = NouNedador(
        part_alias="marc",
        correu=Correu("nou@example.com"),
        mobil="+34600000001",
        canal_preferent=Canal.CORREU,
        estils_preferents=(Estil.CR,),
        dies_entrenament=(Dia.DL,),
        volum_setmanal=VolumSetmanal(min=8000, max=12000),
    )
    return replace(base, **canvis)


def _repositori(*ids: IdNedador) -> RepositoriMemoria:
    """ID_A (alias exemple_3f2a9c1) i, si es demana, ID_B (arxivat, altre_9b1c2d3)."""
    repositori = RepositoriMemoria()
    if ID_A in ids:
        repositori.semina(ID_A, nedador())
    if ID_B in ids:
        repositori.semina(
            ID_B, nedador(correu=Correu("b@example.com"), alias=ALIAS_B, arxivat=True)
        )
    return repositori


# --- Alta ---


@pytest.mark.ca("CA-001-45")
def test_alta_dona_un_id_diferent_dels_existents_arxivats_inclosos() -> None:
    repositori = _repositori(ID_A, ID_B)
    generador = GeneradorFix([ID_A, ID_B, ID_C])  # els dos primers ja existeixen

    resultat = alta(com_a_port(repositori), generador, _nou())

    assert resultat.desat
    assert resultat.id_nedador == ID_C
    assert set(repositori.nedadors) == {ID_A, ID_B, ID_C}


@pytest.mark.ca("CA-001-52")
def test_alta_genera_l_alias_amb_la_part_i_el_sufix_de_l_id() -> None:
    repositori = RepositoriMemoria()

    resultat = alta(com_a_port(repositori), GeneradorFix([ID_A]), _nou(part_alias="marc"))

    assert resultat.desat and resultat.resultat.errors == ()
    desat = repositori.nedadors[ID_A]
    assert desat.alias is not None and str(desat.alias) == "marc_3f2a9c1"
    assert desat.arxivat is False
    assert desat.tests_css == () and desat.millors_registres == ()
    assert desat.correu == Correu("nou@example.com")


@pytest.mark.ca("CA-001-61")
def test_alta_amb_alias_existent_genera_un_id_nou_i_un_alias_nou() -> None:
    repositori = RepositoriMemoria()
    # ID_X té l'alias marc_3f2a9c1: el primer id generat (ID_A) donaria el mateix alias.
    repositori.semina(ID_X, nedador(alias=Alias("marc_3f2a9c1"), correu=Correu("x@example.com")))
    generador = GeneradorFix([ID_A, ID_C])

    resultat = alta(com_a_port(repositori), generador, _nou(part_alias="marc"))

    assert resultat.desat
    assert resultat.id_nedador == ID_C
    assert ID_A not in repositori.nedadors
    desat = repositori.nedadors[ID_C]
    assert desat.alias is not None and str(desat.alias) == "marc_a1b2c3d"


@pytest.mark.ca("CA-001-62")
def test_alta_amb_un_error_no_es_desa_i_el_missatge_dona_alias_rn_i_accio() -> None:
    repositori = RepositoriMemoria()

    resultat = alta(
        com_a_port(repositori),
        GeneradorFix([ID_A]),
        _nou(correu=Correu("nedador.example.com")),
    )

    assert not resultat.desat
    assert repositori.nedadors == {}
    error = resultat.resultat.errors[0]
    assert (error.rn, error.camp, error.valor) == ("RN-032", "correu", "nedador.example.com")
    assert error.nedador == "marc_3f2a9c1"
    assert error.accio


@pytest.mark.ca("CA-001-70")
def test_alta_amb_el_correu_d_un_nedador_amb_error_en_un_altre_camp_es_rebutja() -> None:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador(mobil="", correu=Correu("x@example.com")))  # fitxer llegible

    resultat = alta(
        com_a_port(repositori), GeneradorFix([ID_C]), _nou(correu=Correu("X@example.com"))
    )

    assert not resultat.desat
    assert [(e.rn, e.camp) for e in resultat.resultat.errors] == [("RN-032", "correu")]
    assert ID_C not in repositori.nedadors


@pytest.mark.ca("CA-001-108")
def test_alta_amb_un_correu_en_col_lisio_es_error_i_no_es_desa_res() -> None:
    repositori = _repositori(ID_A)
    repositori.semina(ID_A, nedador(correu=Correu("A@b.com")))

    resultat = alta(com_a_port(repositori), GeneradorFix([ID_C]), _nou(correu=Correu(" a@b.com ")))

    assert not resultat.desat
    assert [(e.rn, e.camp) for e in resultat.resultat.errors] == [("RN-032", "correu")]
    assert set(repositori.nedadors) == {ID_A}


@pytest.mark.ca("CA-001-104")
def test_alta_desa_el_correu_tal_com_s_ha_entrat() -> None:
    repositori = RepositoriMemoria()

    resultat = alta(
        com_a_port(repositori), GeneradorFix([ID_A]), _nou(correu=Correu("  Pere@Exemple.cat "))
    )

    assert resultat.desat
    assert repositori.nedadors[ID_A].correu == Correu("  Pere@Exemple.cat ")


# --- Modificació ---


@pytest.mark.ca("CA-001-25")
def test_modificar_el_correu_no_canvia_l_id() -> None:
    repositori = _repositori(ID_A)

    resultat = modifica(
        com_a_port(repositori), ID_A, CanviNedador(correu=Correu("nou@example.com"))
    )

    assert resultat.desat
    assert resultat.id_nedador == ID_A
    assert set(repositori.nedadors) == {ID_A}
    assert repositori.nedadors[ID_A].correu == Correu("nou@example.com")


@pytest.mark.ca("CA-001-53")
@pytest.mark.parametrize("camp", ["id", "alias", "versio_esquema"])
def test_el_canvi_no_pot_portar_id_alias_ni_versio_d_esquema(camp: str) -> None:
    with pytest.raises(TypeError):
        CanviNedador(**{camp: "x"})  # type: ignore[arg-type]


@pytest.mark.ca("CA-001-53")
def test_modificar_conserva_l_id_i_l_alias() -> None:
    repositori = _repositori(ID_A)
    original = repositori.nedadors[ID_A]

    resultat = modifica(com_a_port(repositori), ID_A, CanviNedador(mobil="+34600000009"))

    assert resultat.desat and resultat.id_nedador == ID_A
    desat = repositori.nedadors[ID_A]
    assert desat.alias == original.alias
    assert desat == replace(original, mobil="+34600000009")  # res més no canvia


@pytest.mark.ca("CA-001-79")
@pytest.mark.parametrize("arxivat", [False, True])
def test_modificar_el_correu_amb_el_d_un_altre_nedador_es_error(arxivat: bool) -> None:
    repositori = _repositori(ID_A)
    repositori.semina(ID_B, nedador(correu=Correu("b@example.com"), alias=ALIAS_B, arxivat=arxivat))

    resultat = modifica(com_a_port(repositori), ID_A, CanviNedador(correu=Correu("B@example.com")))

    assert not resultat.desat
    assert [(e.rn, e.camp) for e in resultat.resultat.errors] == [("RN-032", "correu")]
    assert repositori.nedadors[ID_A] == nedador()


@pytest.mark.ca("CA-001-80")
def test_modificar_amb_un_valor_que_dona_error_no_desa_res() -> None:
    repositori = _repositori(ID_A)

    resultat = modifica(
        com_a_port(repositori), ID_A, CanviNedador(volum_setmanal=VolumSetmanal(12000, 8000))
    )

    assert not resultat.desat
    assert [(e.rn, e.camp) for e in resultat.resultat.errors] == [("RN-005", "volum_setmanal")]
    assert repositori.nedadors[ID_A] == nedador()


@pytest.mark.ca("CA-001-80")
def test_modificar_amb_un_mobil_buit_no_desa_res() -> None:
    repositori = _repositori(ID_A)

    resultat = modifica(com_a_port(repositori), ID_A, CanviNedador(mobil="\t"))

    assert not resultat.desat
    assert [e.camp for e in resultat.resultat.errors] == ["mobil"]
    assert repositori.nedadors[ID_A] == nedador()


@pytest.mark.ca("CA-001-109")
def test_modificar_el_correu_es_desa_tal_qual_i_l_antic_queda_lliure() -> None:
    repositori = _repositori(ID_A)

    resultat = modifica(
        com_a_port(repositori), ID_A, CanviNedador(correu=Correu("  Nou@Exemple.cat "))
    )

    assert resultat.desat and resultat.id_nedador == ID_A
    assert repositori.nedadors[ID_A].correu == Correu("  Nou@Exemple.cat ")
    # L'antic (nedador@example.com) queda lliure per a un nedador nou.
    nou = alta(
        com_a_port(repositori), GeneradorFix([ID_C]), _nou(correu=Correu("nedador@example.com"))
    )
    assert nou.desat


@pytest.mark.ca("CA-001-112")
def test_modificar_amb_correu_null_treu_el_correu_i_el_deixa_lliure() -> None:
    repositori = _repositori(ID_A)

    resultat = modifica(
        com_a_port(repositori),
        ID_A,
        CanviNedador(correu=None, canal_preferent=Canal.MOBIL),
    )

    assert resultat.desat and resultat.id_nedador == ID_A
    assert repositori.nedadors[ID_A].correu is None
    nou = alta(
        com_a_port(repositori), GeneradorFix([ID_C]), _nou(correu=Correu("nedador@example.com"))
    )
    assert nou.desat


@pytest.mark.ca("CA-001-112")
def test_un_canvi_sense_correu_no_treu_el_correu() -> None:
    repositori = _repositori(ID_A)

    modifica(com_a_port(repositori), ID_A, CanviNedador(mobil="+34600000009"))

    assert repositori.nedadors[ID_A].correu == Correu("nedador@example.com")


# --- Arxivar i desarxivar ---


@pytest.mark.ca("CA-001-81")
def test_desarxivar_i_arxivar() -> None:
    repositori = _repositori(ID_A, ID_B)
    original = repositori.nedadors[ID_B]

    desarxiva(com_a_port(repositori), ID_B)
    assert repositori.nedadors[ID_B] == replace(original, arxivat=False)

    arxiva(com_a_port(repositori), ID_B)
    assert repositori.nedadors[ID_B].arxivat is True
    assert repositori.nedadors[ID_B] == original


# --- Tests CSS ---


@pytest.mark.ca("CA-001-82")
def test_afegir_un_test_el_desa_amb_acceptat_false_i_conserva_els_anteriors() -> None:
    repositori = _repositori(ID_A)
    anterior = repositori.nedadors[ID_A].tests_css[0]
    nou = un_test(data=date(2000, 6, 1), acceptat=True)

    resultat = afegeix_test(com_a_port(repositori), ID_A, nou)

    assert resultat.desat
    desats = repositori.nedadors[ID_A].tests_css
    assert desats == (anterior, replace(nou, acceptat=False))


@pytest.mark.ca("CA-001-82")
def test_no_hi_ha_cap_operacio_d_edicio_i_un_test_desat_no_es_pot_canviar() -> None:
    publiques = [nom for nom in dir(gestio) if not nom.startswith("_")]
    prefixos = ("edita", "canvia_test", "canvia_registre")
    assert [nom for nom in publiques if nom.startswith(prefixos)] == []
    with pytest.raises(FrozenInstanceError):
        nedador().tests_css[0].acceptat = False  # type: ignore[misc]


# --- Millors registres (RN-007) ---


@pytest.mark.ca("CA-001-83")
def test_afegir_una_marca_millor_s_afegeix_i_conserva_el_desat() -> None:
    repositori = _repositori(ID_A)
    desat = repositori.nedadors[ID_A].millors_registres[0]
    millor = registre(temps=temps("1:14.00"), data=date(2000, 3, 1))

    resultat = afegeix_millor_registre(com_a_port(repositori), ID_A, millor)

    assert resultat.desat and resultat.resultat.errors == ()
    assert repositori.nedadors[ID_A].millors_registres == (desat, millor)


@pytest.mark.ca("CA-001-83")
def test_les_piscines_no_es_comparen_mai() -> None:
    repositori = _repositori(ID_A)  # 100 Cr a 25 m: 1:15.00
    pitjor_a_50 = registre(piscina=Piscina.LLARGA, temps=temps("1:30.00"), data=date(2000, 1, 1))

    resultat = afegeix_millor_registre(com_a_port(repositori), ID_A, pitjor_a_50)

    assert resultat.desat
    assert repositori.nedadors[ID_A].millors_registres[-1] == pitjor_a_50


@pytest.mark.ca("CA-001-83")
def test_un_registre_desat_no_es_pot_editar() -> None:
    with pytest.raises(FrozenInstanceError):
        nedador().millors_registres[0].temps = temps("1:00.00")  # type: ignore[misc]


@pytest.mark.ca("CA-001-89")
@pytest.mark.parametrize("text", ["1:15.00", "1:16.00"])
def test_un_temps_igual_o_pitjor_no_fa_res(text: str) -> None:
    repositori = _repositori(ID_A)
    pitjor = registre(temps=temps(text), data=date(2000, 3, 1))

    resultat = afegeix_millor_registre(com_a_port(repositori), ID_A, pitjor)

    assert not resultat.desat
    assert resultat.resultat.errors == () and resultat.resultat.avisos == ()
    assert repositori.nedadors[ID_A] == nedador()


@pytest.mark.ca("CA-001-89")
def test_un_temps_pitjor_amb_data_anterior_continua_sense_fer_res() -> None:
    repositori = _repositori(ID_A)
    pitjor = registre(temps=temps("1:20.00"), data=date(1999, 1, 1))

    resultat = afegeix_millor_registre(com_a_port(repositori), ID_A, pitjor)

    assert not resultat.desat
    assert resultat.resultat.errors == ()
    assert repositori.nedadors[ID_A] == nedador()


@pytest.mark.ca("CA-001-90")
def test_afegir_un_registre_sense_competicio_no_l_afegeix_i_identifica_el_camp() -> None:
    repositori = _repositori(ID_A)
    millor = registre(temps=temps("1:14.00"), data=date(2000, 3, 1), competicio="")

    resultat = afegeix_millor_registre(com_a_port(repositori), ID_A, millor)

    assert not resultat.desat
    assert [e.camp for e in resultat.resultat.errors] == ["millors_registres.1.competicio"]
    assert repositori.nedadors[ID_A] == nedador()


@pytest.mark.ca("CA-001-97")
def test_la_marca_vigent_despres_d_afegir_marques_es_l_ultima_de_la_llista() -> None:
    repositori = _repositori(ID_A)
    for text, dia in (("1:14.00", date(2000, 3, 1)), ("1:13.00", date(2000, 4, 1))):
        afegeix_millor_registre(com_a_port(repositori), ID_A, registre(temps=temps(text), data=dia))
    afegeix_millor_registre(
        com_a_port(repositori), ID_A, registre(piscina=Piscina.LLARGA, temps=temps("1:20.00"))
    )

    n = repositori.nedadors[ID_A]
    vigent = marca_vigent(n, _CR100, Piscina.CURTA)

    assert vigent is not None and vigent.temps == temps("1:13.00")
    assert vigent == [r for r in n.millors_registres if r.piscina is Piscina.CURTA][-1]


@pytest.mark.ca("CA-001-102")
@pytest.mark.parametrize("data_nova", [date(2000, 2, 1), date(1999, 12, 31)])
def test_una_marca_millor_amb_data_igual_o_anterior_a_la_vigent_es_error(data_nova: date) -> None:
    repositori = _repositori(ID_A)  # marca vigent: 1:15.00 amb data 2000-02-01
    millor = registre(temps=temps("1:14.00"), data=data_nova)

    resultat = afegeix_millor_registre(com_a_port(repositori), ID_A, millor)

    assert not resultat.desat
    assert [e.rn for e in resultat.resultat.errors] == ["RN-007"]
    assert all(text in resultat.resultat.errors[0].missatge for text in ("100", "Cr", "25"))
    assert repositori.nedadors[ID_A].millors_registres == nedador().millors_registres
