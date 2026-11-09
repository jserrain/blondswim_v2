"""US3 — càrrega del catàleg i de les inscripcions (T051), amb repositoris en memòria."""

from dataclasses import replace
from datetime import date

import pytest

from blondswim.application.carrega import carrega_nedadors
from blondswim.application.filtre import filtra
from blondswim.domain.cataleg import Cataleg
from blondswim.domain.inscripcions import Inscripcio, Inscripcions, Participacio
from blondswim.domain.validacio import ErrorCarrega, ErrorValidacio
from blondswim.domain.valors import Classe, CodiTemporada, Estil, Prioritat, Prova
from tests.unit.fakes import (
    ALIAS_B,
    ID_A,
    ID_B,
    CatalegMemoria,
    RepositoriMemoria,
    cataleg_com_a_port,
    com_a_port,
    competicio,
    nedador,
)

TEMPORADA = CodiTemporada("1999-00")


def inscripcions(id_competicio: str = "c001") -> Inscripcions:
    prova = Inscripcio(Prova(100, Estil.CR), date(2000, 3, 4), Prioritat.PRINCIPAL)
    return Inscripcions((Participacio(id_competicio, Classe.A, (prova,)),))


def error_cataleg(rn: str, camp: str = "") -> ErrorValidacio:
    return ErrorValidacio(rn, f"competicions/{TEMPORADA}.json", camp, None, "error del catàleg")


def dos_nedadors_amb_inscripcions() -> RepositoriMemoria:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador())
    repositori.semina(ID_B, nedador(alias=ALIAS_B, correu=None))
    repositori.semina_inscripcions(ID_A, TEMPORADA, inscripcions())
    repositori.semina_inscripcions(ID_B, TEMPORADA, inscripcions())
    return repositori


def amb_cataleg() -> CatalegMemoria:
    cataleg = CatalegMemoria()
    cataleg.desa(TEMPORADA, Cataleg((competicio(),)))
    return cataleg


def test_nedadors_amb_inscripcions_valides_es_carreguen() -> None:
    resultat = carrega_nedadors(
        com_a_port(dos_nedadors_amb_inscripcions()), cataleg_com_a_port(amb_cataleg())
    )
    assert set(resultat.nedadors) == {ID_A, ID_B}
    assert resultat.inscripcions[ID_A][TEMPORADA] == inscripcions()


@pytest.mark.ca("CA-001-11")
@pytest.mark.ca("CA-001-17")
@pytest.mark.ca("CA-001-41")
@pytest.mark.ca("CA-001-71")
@pytest.mark.parametrize(
    "error",
    [
        error_cataleg("RN-008", "competicions.1.id"),
        error_cataleg("format", "versio_esquema"),
        error_cataleg("format", "competicions.0.piscina"),
        error_cataleg("RN-031"),
    ],
)
def test_un_error_del_cataleg_falla_tota_la_carrega(error: ErrorValidacio) -> None:
    cataleg = CatalegMemoria()
    cataleg.il_legibles[TEMPORADA] = (error,)
    with pytest.raises(ErrorCarrega) as exc:
        carrega_nedadors(com_a_port(dos_nedadors_amb_inscripcions()), cataleg_com_a_port(cataleg))
    assert exc.value.errors == (error,)


@pytest.mark.ca("CA-001-19")
def test_un_error_d_inscripcions_exclou_nomes_aquell_nedador() -> None:
    repositori = dos_nedadors_amb_inscripcions()
    repositori.semina_inscripcions(ID_B, TEMPORADA, inscripcions("c999"))
    resultat = carrega_nedadors(com_a_port(repositori), cataleg_com_a_port(amb_cataleg()))
    assert set(resultat.nedadors) == {ID_A}
    assert [(e.rn, e.nedador) for e in resultat.resultats[ID_B].errors] == [
        ("RN-011", str(ALIAS_B))
    ]


def test_inscripcions_il_legibles_exclouen_nomes_aquell_nedador() -> None:
    repositori = dos_nedadors_amb_inscripcions()
    error = ErrorValidacio("format", "x", "versio_esquema", 2, "versió d'esquema no admesa")
    repositori.semina_inscripcions_il_legibles(ID_B, TEMPORADA, (error,))
    resultat = carrega_nedadors(com_a_port(repositori), cataleg_com_a_port(amb_cataleg()))
    assert set(resultat.nedadors) == {ID_A}
    assert resultat.resultats[ID_B].errors == (replace(error, nedador=str(ALIAS_B)),)


def test_sense_inscripcions_no_es_demana_cap_cataleg() -> None:
    repositori = RepositoriMemoria()
    repositori.semina(ID_A, nedador())
    cataleg = CatalegMemoria()  # cap catàleg: si es demanés, seria CatalegAbsent
    resultat = carrega_nedadors(com_a_port(repositori), cataleg_com_a_port(cataleg))
    assert set(resultat.nedadors) == {ID_A}
    assert cataleg.demanats == []


def test_inscripcions_d_una_temporada_sense_cataleg_exclouen_aquell_nedador() -> None:
    repositori = dos_nedadors_amb_inscripcions()
    resultat = carrega_nedadors(com_a_port(repositori), cataleg_com_a_port(CatalegMemoria()))
    assert resultat.nedadors == {}
    assert "falta el catàleg" in resultat.resultats[ID_A].errors[0].missatge


def test_el_cataleg_de_cada_temporada_es_demana_una_sola_vegada() -> None:
    cataleg = amb_cataleg()
    carrega_nedadors(com_a_port(dos_nedadors_amb_inscripcions()), cataleg_com_a_port(cataleg))
    assert cataleg.demanats == [TEMPORADA]


def test_els_avisos_del_cataleg_es_recullen() -> None:
    cataleg = CatalegMemoria()
    cataleg.desa(TEMPORADA, Cataleg((competicio(seu=None),)))
    resultat = carrega_nedadors(
        com_a_port(dos_nedadors_amb_inscripcions()), cataleg_com_a_port(cataleg)
    )
    assert [a.rn for a in resultat.avisos_cataleg] == ["RN-009"]


def test_el_filtre_dona_el_mateix_resultat_que_la_carrega() -> None:
    repositori = dos_nedadors_amb_inscripcions()
    repositori.semina_inscripcions(ID_B, TEMPORADA, inscripcions("c999"))
    filtre = filtra(com_a_port(repositori), cataleg_com_a_port(amb_cataleg()))
    assert filtre.planificables == (ID_A,)
    assert [e.rn for e in filtre.resultats[ID_B].errors] == ["RN-011"]
