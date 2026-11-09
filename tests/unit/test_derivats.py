"""US4 — consultes (no es desen) i aptitud per planificar (T025)."""

from datetime import date

import pytest

from blondswim.domain.derivats import proves_objectiu, setmana_iso, test_vigent
from blondswim.domain.inscripcions import Inscripcio, Inscripcions, Participacio
from blondswim.domain.validacio import valida_aptitud
from blondswim.domain.valors import Classe, CodiTemporada, Estil, Piscina, Prioritat, Prova
from tests.unit.fakes import ALIAS_A, ID_A, nedador, un_test

TEMPORADA = CodiTemporada("1999-00")


def participacio(
    id_competicio: str, classe: Classe, prioritat: Prioritat = Prioritat.PRINCIPAL
) -> Participacio:
    prova = Inscripcio(Prova(100, Estil.CR), date(2000, 3, 4), prioritat)
    return Participacio(id_competicio, classe, (prova,))


def amb_a(prioritat: Prioritat = Prioritat.PRINCIPAL) -> Inscripcions:
    return Inscripcions((participacio("c001", Classe.A, prioritat),))


@pytest.mark.ca("CA-001-05")
def test_el_test_vigent_es_l_acceptat_mes_recent_de_la_piscina() -> None:
    antic = un_test(data=date(2000, 1, 10), acceptat=True)
    recent = un_test(data=date(2000, 2, 10), acceptat=True)
    no_acceptat = un_test(data=date(2000, 3, 10), acceptat=False)
    altra_piscina = un_test(data=date(2000, 4, 10), piscina=Piscina.LLARGA, acceptat=True)
    n = nedador(tests_css=(recent, no_acceptat, antic, altra_piscina))
    assert test_vigent(n, Piscina.CURTA) == recent
    assert test_vigent(n, Piscina.LLARGA) == altra_piscina
    assert test_vigent(nedador(tests_css=(no_acceptat,)), Piscina.CURTA) is None


@pytest.mark.ca("CA-001-16")
def test_les_proves_objectiu_son_les_inscripcions_de_les_participacions_a() -> None:
    inscripcions = Inscripcions(
        (
            participacio("c001", Classe.A),
            participacio("c002", Classe.B),
            participacio("c003", Classe.C),
        )
    )
    assert proves_objectiu(inscripcions) == inscripcions.participacions[0].proves


@pytest.mark.ca("CA-001-18")
@pytest.mark.parametrize(
    ("data", "esperat"),
    [
        (date(2000, 3, 4), (2000, 9)),
        (date(2000, 1, 1), (1999, 52)),
        (date(2026, 12, 31), (2026, 53)),
    ],
)
def test_la_setmana_es_calcula_a_partir_de_la_data(data: date, esperat: tuple[int, int]) -> None:
    assert setmana_iso(data) == esperat


@pytest.mark.ca("CA-001-13")
def test_participacio_a_sense_prova_principal_dona_avis_i_no_bloqueja() -> None:
    resultat = valida_aptitud(ID_A, str(ALIAS_A), nedador(), amb_a(Prioritat.SECUNDARIA))
    assert resultat.es_valid
    assert [(a.rn, a.camp) for a in resultat.avisos] == [("RN-019", "participacions.0")]


@pytest.mark.ca("CA-001-14")
def test_sense_test_acceptat_es_apte_amb_l_avis_sense_ritmes() -> None:
    n = nedador(tests_css=(un_test(acceptat=False),))
    resultat = valida_aptitud(ID_A, str(ALIAS_A), n, amb_a())
    assert resultat.es_valid
    assert [(a.rn, a.missatge) for a in resultat.avisos] == [("RN-020", "sense ritmes")]


@pytest.mark.ca("CA-001-15")
@pytest.mark.parametrize(
    "inscripcions",
    [None, Inscripcions((participacio("c002", Classe.B), participacio("c003", Classe.C)))],
)
def test_sense_participacio_a_no_es_apte(inscripcions: Inscripcions | None) -> None:
    resultat = valida_aptitud(ID_A, str(ALIAS_A), nedador(), inscripcions)
    assert not resultat.es_valid
    assert [(e.rn, e.missatge) for e in resultat.errors] == [("RN-018", "falta competició A")]


@pytest.mark.ca("CA-001-28")
def test_un_nedador_arxivat_no_es_apte() -> None:
    resultat = valida_aptitud(ID_A, str(ALIAS_A), nedador(arxivat=True), amb_a())
    assert [(e.rn, e.missatge) for e in resultat.errors] == [("RN-017", "arxivat")]


def test_nedador_apte_sense_avisos() -> None:
    resultat = valida_aptitud(ID_A, str(ALIAS_A), nedador(), amb_a())
    assert resultat.es_valid and resultat.avisos == ()
