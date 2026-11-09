"""US4 — cas d'ús d'aptitud per planificar (T053), amb registre en memòria i rellotge fix."""

from datetime import date, datetime

import pytest

from blondswim.application.aptitud import aptitud
from blondswim.domain.inscripcions import Inscripcio, Inscripcions, Participacio
from blondswim.domain.valors import Classe, CodiTemporada, Estil, Prioritat, Prova
from tests.unit.fakes import ID_A, RegistreMemoria, RellotgeFix, nedador, un_test

TEMPORADA = CodiTemporada("1999-00")
ARA = datetime(2000, 3, 4, 10, 15)


def amb_a(prioritat: Prioritat = Prioritat.PRINCIPAL) -> Inscripcions:
    prova = Inscripcio(Prova(100, Estil.CR), date(2000, 3, 4), prioritat)
    return Inscripcions((Participacio("c001", Classe.A, (prova,)),))


@pytest.mark.ca("CA-001-13")
def test_participacio_a_sense_principal_registra_l_avis_amb_decisio_null() -> None:
    registre = RegistreMemoria()
    resultat = aptitud(
        ID_A, nedador(), amb_a(Prioritat.SECUNDARIA), TEMPORADA, registre, RellotgeFix(ARA)
    )
    assert resultat.es_valid
    assert [(d, a.rn, i, dec) for d, a, i, dec in registre.linies] == [(ARA, "RN-019", ID_A, None)]


@pytest.mark.ca("CA-001-14")
def test_sense_ritmes_es_apte_i_registra_l_avis_amb_decisio_null() -> None:
    registre = RegistreMemoria()
    n = nedador(tests_css=(un_test(acceptat=False),))
    resultat = aptitud(ID_A, n, amb_a(), TEMPORADA, registre, RellotgeFix(ARA))
    assert resultat.es_valid
    assert [(a.rn, a.missatge, dec) for _, a, _, dec in registre.linies] == [
        ("RN-020", "sense ritmes", None)
    ]


@pytest.mark.ca("CA-001-15")
def test_sense_participacio_a_no_es_apte_i_no_registra_res() -> None:
    registre = RegistreMemoria()
    resultat = aptitud(ID_A, nedador(), None, TEMPORADA, registre, RellotgeFix(ARA))
    assert [e.missatge for e in resultat.errors] == ["falta competició A"]
    assert registre.linies == []


@pytest.mark.ca("CA-001-28")
def test_arxivat_no_es_apte() -> None:
    resultat = aptitud(
        ID_A, nedador(arxivat=True), amb_a(), TEMPORADA, RegistreMemoria(), RellotgeFix(ARA)
    )
    assert [e.missatge for e in resultat.errors] == ["arxivat"]
