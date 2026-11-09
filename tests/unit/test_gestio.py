"""US5 — gestió: esborrar nedador, acceptar test i esborrar competició (T028)."""

from dataclasses import replace
from datetime import date

import pytest

from blondswim.application.gestio import (
    accepta_test,
    afegeix_test,
    esborra_competicio,
    esborra_nedador,
)
from blondswim.domain.cataleg import Cataleg
from blondswim.domain.derivats import test_vigent
from blondswim.domain.inscripcions import Inscripcio, Inscripcions, Participacio
from blondswim.domain.valors import Classe, CodiTemporada, Estil, Piscina, Prioritat, Prova
from tests.unit.fakes import (
    ALIAS_A,
    ID_A,
    ID_B,
    CatalegMemoria,
    RepositoriMemoria,
    cataleg_com_a_port,
    com_a_port,
    competicio,
    nedador,
    un_test,
)

TEMPORADA = CodiTemporada("1999-00")


def amb_un_nedador() -> RepositoriMemoria:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador())
    return repositori


@pytest.mark.ca("CA-001-37")
def test_esborrar_un_nedador_sempre_es_error_i_no_el_canvia() -> None:
    repositori = amb_un_nedador()
    abans = repositori.nedadors[ID_A]
    resultat = esborra_nedador(com_a_port(repositori), ID_A)
    assert not resultat.desat
    (error,) = resultat.resultat.errors
    assert error.rn == "RN-004"
    assert "arxiva" in error.missatge or "arxiva" in error.accio
    assert error.nedador == str(ALIAS_A)
    assert repositori.nedadors[ID_A] == abans


@pytest.mark.ca("CA-001-30")
def test_un_test_nou_no_canvia_el_vigent_fins_que_el_coach_l_accepta() -> None:
    repositori = RepositoriMemoria()
    vigent = un_test(data=date(2000, 1, 15), acceptat=True)
    repositori.semina(ID_A, nedador(tests_css=(vigent,)))
    nou = un_test(data=date(2000, 2, 15))
    assert afegeix_test(com_a_port(repositori), ID_A, nou).desat
    assert test_vigent(repositori.nedadors[ID_A], Piscina.CURTA) == vigent
    resultat = accepta_test(com_a_port(repositori), ID_A, date(2000, 2, 15), Piscina.CURTA)
    assert resultat.desat
    assert test_vigent(repositori.nedadors[ID_A], Piscina.CURTA) == replace(nou, acceptat=True)
    assert repositori.nedadors[ID_A].tests_css[0] == vigent


def test_acceptar_un_test_que_no_existeix_es_error() -> None:
    repositori = amb_un_nedador()
    resultat = accepta_test(com_a_port(repositori), ID_A, date(1990, 1, 1), Piscina.CURTA)
    assert not resultat.desat
    assert [e.camp for e in resultat.resultat.errors] == ["tests_css"]


def _amb_inscripcions_a(repositori: RepositoriMemoria, id_competicio: str) -> None:
    prova = Inscripcio(Prova(100, Estil.CR), date(2000, 3, 4), Prioritat.PRINCIPAL)
    inscripcions = Inscripcions((Participacio(id_competicio, Classe.A, (prova,)),))
    repositori.semina_inscripcions(ID_A, TEMPORADA, inscripcions)


def _cataleg() -> CatalegMemoria:
    cataleg = CatalegMemoria()
    cataleg.desa(TEMPORADA, Cataleg((competicio(), competicio(id="c002", nom="Altra"))))
    return cataleg


@pytest.mark.ca("CA-001-21")
def test_esborrar_una_competicio_amb_inscripcions_es_error_rn_010() -> None:
    repositori = amb_un_nedador()
    repositori.semina(ID_B, nedador(alias=None, correu=None))
    _amb_inscripcions_a(repositori, "c001")
    cataleg = _cataleg()
    resultat = esborra_competicio(
        cataleg_com_a_port(cataleg), com_a_port(repositori), TEMPORADA, "c001"
    )
    assert not resultat.desat
    (error,) = resultat.resultat.errors
    assert error.rn == "RN-010"
    assert str(ALIAS_A) in error.missatge
    assert cataleg.catalegs[TEMPORADA].competicio("c001") is not None


def test_esborrar_una_competicio_sense_inscripcions_la_treu_del_cataleg() -> None:
    repositori = amb_un_nedador()
    _amb_inscripcions_a(repositori, "c001")
    cataleg = _cataleg()
    resultat = esborra_competicio(
        cataleg_com_a_port(cataleg), com_a_port(repositori), TEMPORADA, "c002"
    )
    assert resultat.desat
    assert cataleg.catalegs[TEMPORADA].competicio("c002") is None
    assert cataleg.catalegs[TEMPORADA].competicio("c001") is not None


def test_esborrar_una_competicio_que_no_existeix_es_error() -> None:
    resultat = esborra_competicio(
        cataleg_com_a_port(_cataleg()), com_a_port(amb_un_nedador()), TEMPORADA, "c999"
    )
    assert not resultat.desat
    assert [e.camp for e in resultat.resultat.errors] == ["competicions"]
