"""US3 — inscripcions: invariants i validació creuada amb el catàleg (T020)."""

from dataclasses import replace
from datetime import date

import pytest

from blondswim.domain.cataleg import Cataleg
from blondswim.domain.inscripcions import Inscripcio, Inscripcions, Participacio
from blondswim.domain.nedador import ErrorInvariant
from blondswim.domain.validacio import valida_inscripcions
from blondswim.domain.valors import Classe, CodiTemporada, Estil, Piscina, Prioritat, Prova
from tests.unit.fakes import ALIAS_A, ALIAS_B, ID_A, ID_B, competicio

TEMPORADA = CodiTemporada("1999-00")
CATALEG = Cataleg((competicio(),))  # c001: 2000-03-04 i 2000-03-05, piscina de 25 m


def inscripcio(**canvis: object) -> Inscripcio:
    base = Inscripcio(
        prova=Prova(100, Estil.CR), dia=date(2000, 3, 4), prioritat=Prioritat.PRINCIPAL
    )
    return replace(base, **canvis)


def participacio(**canvis: object) -> Participacio:
    base = Participacio(id_competicio="c001", classe=Classe.A, proves=(inscripcio(),))
    return replace(base, **canvis)


def valida(inscripcions: Inscripcions, cataleg: Cataleg = CATALEG) -> list[tuple[str, str]]:
    resultat = valida_inscripcions(ID_A, str(ALIAS_A), TEMPORADA, inscripcions, cataleg)
    return [(e.rn, e.camp) for e in resultat.errors]


def test_inscripcions_valides_no_donen_errors() -> None:
    assert valida(Inscripcions((participacio(),))) == []


@pytest.mark.ca("CA-001-08")
def test_participacio_sense_inscripcions_es_error_rn_014() -> None:
    with pytest.raises(ErrorInvariant) as exc:
        participacio(proves=())
    assert [v.rn for v in exc.value.violacions] == ["RN-014"]


@pytest.mark.ca("CA-001-09")
def test_dia_que_no_es_de_la_competicio_es_error_rn_015() -> None:
    inscripcions = Inscripcions((participacio(proves=(inscripcio(dia=date(2000, 3, 6)),)),))
    assert valida(inscripcions) == [("RN-015", "participacions.0.proves.0.dia")]


@pytest.mark.ca("CA-001-10")
def test_competicio_amb_una_data_fora_de_la_temporada_es_error_rn_013() -> None:
    cataleg = Cataleg((competicio(dates=(date(2000, 9, 30), date(2000, 10, 1))),))
    inscripcions = Inscripcions((participacio(proves=(inscripcio(dia=date(2000, 9, 30)),)),))
    errors = valida_inscripcions(ID_A, str(ALIAS_A), TEMPORADA, inscripcions, cataleg).errors
    assert [(e.rn, e.camp, e.valor) for e in errors] == [
        ("RN-013", "participacions.0.id_competicio", date(2000, 10, 1))
    ]


@pytest.mark.ca("CA-001-19")
def test_competicio_que_no_es_al_cataleg_es_error_rn_011() -> None:
    errors = valida(Inscripcions((participacio(id_competicio="c999"),)))
    assert errors == [("RN-011", "participacions.0.id_competicio")]


@pytest.mark.ca("CA-001-20")
def test_dos_nedadors_a_la_mateixa_competicio_amb_classes_diferents_son_valids() -> None:
    de_a = Inscripcions((participacio(classe=Classe.A),))
    de_b = Inscripcions((participacio(classe=Classe.C),))
    resultat_a = valida_inscripcions(ID_A, str(ALIAS_A), TEMPORADA, de_a, CATALEG)
    resultat_b = valida_inscripcions(ID_B, str(ALIAS_B), TEMPORADA, de_b, CATALEG)
    assert resultat_a.es_valid and resultat_b.es_valid
    assert de_a.participacions[0].classe is Classe.A
    assert de_b.participacions[0].classe is Classe.C


@pytest.mark.ca("CA-001-22")
def test_un_canvi_de_data_al_cataleg_el_veuen_totes_les_participacions() -> None:
    inscripcions = Inscripcions((participacio(proves=(inscripcio(dia=date(2000, 3, 11)),)),))
    nou = Cataleg((competicio(dates=(date(2000, 3, 11), date(2000, 3, 12))),))
    assert valida(inscripcions, nou) == []
    assert nou.competicio(inscripcions.participacions[0].id_competicio) is not None
    assert nou.competicio("c001").dates == (date(2000, 3, 11), date(2000, 3, 12))  # type: ignore[union-attr]


@pytest.mark.ca("CA-001-23")
def test_dues_participacions_a_la_mateixa_competicio_es_error_rn_012() -> None:
    with pytest.raises(ErrorInvariant) as exc:
        Inscripcions((participacio(), participacio(classe=Classe.B)))
    assert [(v.rn, v.camp) for v in exc.value.violacions] == [
        ("RN-012", "participacions.1.id_competicio")
    ]


@pytest.mark.ca("CA-001-29")
def test_la_mateixa_prova_en_dos_dies_es_error_rn_016() -> None:
    with pytest.raises(ErrorInvariant) as exc:
        participacio(proves=(inscripcio(), inscripcio(dia=date(2000, 3, 5))))
    assert [(v.rn, v.camp) for v in exc.value.violacions] == [("RN-016", "proves.1.prova")]


@pytest.mark.ca("CA-001-42")
def test_inscripcio_a_una_prova_no_oficial_per_a_la_piscina_es_error_rn_030() -> None:
    cataleg = Cataleg((competicio(piscina=Piscina.LLARGA),))
    inscripcions = Inscripcions((participacio(proves=(inscripcio(prova=Prova(100, Estil.EI)),)),))
    errors = valida_inscripcions(ID_A, str(ALIAS_A), TEMPORADA, inscripcions, cataleg).errors
    assert [(e.rn, e.camp) for e in errors] == [("RN-030", "participacions.0.proves.0.prova")]
    assert "100 Ei" in errors[0].missatge and "50" in errors[0].missatge


def test_els_errors_identifiquen_el_fitxer_i_el_nedador() -> None:
    inscripcions = Inscripcions((participacio(id_competicio="c999"),))
    (error,) = valida_inscripcions(ID_A, str(ALIAS_A), TEMPORADA, inscripcions, CATALEG).errors
    assert error.fitxer == f"nedadors/{ID_A}/temporades/{TEMPORADA}/inscripcions.json"
    assert error.nedador == str(ALIAS_A)
