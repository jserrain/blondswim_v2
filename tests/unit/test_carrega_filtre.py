import pytest

from blondswim.application.carrega import carrega_nedadors
from blondswim.application.filtre import filtra
from blondswim.application.gestio import NouNedador, alta
from blondswim.domain.nedador import VolumSetmanal
from blondswim.domain.valors import Canal, Correu, Dia, Estil
from tests.unit.fakes import (
    ALIAS_B,
    ALIAS_C,
    ID_A,
    ID_B,
    ID_C,
    ID_X,
    GeneradorFix,
    RepositoriMemoria,
    com_a_port,
    error_il_legible,
    nedador,
)


def _repositori_amb_tres() -> RepositoriMemoria:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador())
    repositori.semina(ID_B, nedador(correu=Correu("b@example.com"), alias=ALIAS_B))
    repositori.semina(ID_C, nedador(correu=Correu("c@example.com"), alias=ALIAS_C))
    return repositori


@pytest.mark.ca("CA-001-60")
def test_un_nedador_amb_canal_no_admes_no_es_carrega_i_el_valid_si() -> None:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador())
    repositori.semina_il_legible(ID_B, (error_il_legible(ID_B, "canal_preferent", "whatsapp"),))

    resultat = carrega_nedadors(com_a_port(repositori))

    assert set(resultat.nedadors) == {ID_A}
    assert resultat.resultats[ID_B].errors[0].camp == "canal_preferent"
    assert resultat.resultats[ID_A].es_valid


@pytest.mark.ca("CA-001-65")
def test_un_nedador_editat_a_ma_que_ja_no_es_valid_no_es_carrega_i_l_altre_si() -> None:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador(correu=Correu("nedador.example.com")))  # correu sense @
    repositori.semina(ID_B, nedador(correu=Correu("b@example.com"), alias=ALIAS_B))

    resultat = carrega_nedadors(com_a_port(repositori))

    assert set(resultat.nedadors) == {ID_B}
    assert [e.camp for e in resultat.resultats[ID_A].errors] == ["correu"]


@pytest.mark.ca("CA-001-66")
@pytest.mark.parametrize("camp", ["correu", "alias"])
def test_una_col_lisio_exclou_tots_els_implicats_i_la_resta_es_carrega(camp: str) -> None:
    repositori = _repositori_amb_tres()
    if camp == "correu":
        altre = ID_B
        repositori.semina(altre, nedador(correu=Correu(" NEDADOR@example.com "), alias=ALIAS_B))
    else:
        # Mateix alias = mateixos 7 primers caràcters de l'id: ID_X comparteix el prefix d'ID_A.
        altre = ID_X
        repositori.semina(altre, nedador(correu=Correu("x@example.com")))

    resultat = carrega_nedadors(com_a_port(repositori))

    assert ID_A not in resultat.nedadors and altre not in resultat.nedadors
    for id_nedador in (ID_A, altre):
        assert [e.camp for e in resultat.resultats[id_nedador].errors] == [camp]
        assert set(resultat.resultats[id_nedador].errors[0].implicats) == {ID_A, altre}
    assert ID_C in resultat.nedadors
    assert resultat.resultats[ID_C].es_valid


@pytest.mark.ca("CA-001-74")
def test_el_filtre_passa_per_tots_i_no_planifica_el_nedador_amb_error() -> None:
    repositori = _repositori_amb_tres()
    repositori.semina(ID_A, nedador(mobil=""))  # el primer, perquè no pari al primer error
    repositori.semina(ID_B, nedador(correu=Correu("b@x"), alias=ALIAS_B))  # domini sense punt

    resultat = filtra(com_a_port(repositori))

    assert set(resultat.resultats) == {ID_A, ID_B, ID_C}
    assert [e.camp for e in resultat.resultats[ID_A].errors] == ["mobil"]
    assert [e.camp for e in resultat.resultats[ID_B].errors] == ["correu"]
    assert resultat.planificables == (ID_C,)


@pytest.mark.ca("CA-001-74")
def test_el_filtre_llista_tots_els_errors_i_avisos_del_nedador() -> None:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador(mobil="", correu=Correu("sense-arroba"), canal_preferent=None))

    resultat = filtra(com_a_port(repositori)).resultats[ID_A]

    assert sorted(e.camp for e in resultat.errors) == ["correu", "mobil"]
    assert [a.camp for a in resultat.avisos] == ["canal_preferent"]


@pytest.mark.ca("CA-001-75")
def test_un_fitxer_il_legible_es_un_error_propi_identificat_per_l_uuid() -> None:
    repositori = _repositori_amb_tres()
    repositori.semina_il_legible(ID_B, (error_il_legible(ID_B),))
    del repositori.nedadors[ID_B]

    resultat = filtra(com_a_port(repositori))

    assert set(resultat.resultats) == {ID_A, ID_B, ID_C}
    assert [e.nedador for e in resultat.resultats[ID_B].errors] == [str(ID_B)]
    assert resultat.planificables == (ID_A, ID_C)


@pytest.mark.ca("CA-001-78")
def test_entrada_carrega_i_filtre_donen_el_mateix_resultat() -> None:
    # Depèn de T047 (alta). El nedador té un ERROR: correu sense @.
    repositori = RepositoriMemoria()
    nou = NouNedador(
        part_alias="marc",
        correu=Correu("nedador.example.com"),
        mobil="+34600000000",
        canal_preferent=Canal.MOBIL,
        estils_preferents=(Estil.CR,),
        dies_entrenament=(Dia.DL,),
        volum_setmanal=VolumSetmanal(min=8000, max=12000),
    )

    entrada = alta(com_a_port(repositori), GeneradorFix([ID_A]), nou)

    assert not entrada.desat
    assert entrada.nedador is not None and entrada.resultat.errors
    repositori.semina(ID_A, entrada.nedador)  # el mateix fitxer, ara a disc

    carregat = carrega_nedadors(com_a_port(repositori)).resultats[ID_A]
    filtrat = filtra(com_a_port(repositori)).resultats[ID_A]

    assert entrada.resultat == carregat == filtrat
