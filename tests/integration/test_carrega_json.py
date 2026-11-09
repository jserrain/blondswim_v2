"""Càrrega del sistema amb els repositoris JSON reals (revisió de la US3 a US6)."""

from pathlib import Path

import pytest

from blondswim.application.carrega import ResultatCarrega, carrega_nedadors
from blondswim.application.gestio import esborra_competicio
from blondswim.domain.validacio import ErrorCarrega
from blondswim.infrastructure.repositoris import RepositoriCatalegJson, RepositoriNedadorsJson
from tests.integration.ajuts import (
    ID_A,
    ID_B,
    TEMPORADA,
    cataleg_json,
    escriu,
    escriu_cataleg,
    escriu_inscripcions,
    inscripcions_json,
    nedador_json,
)


def carrega(arrel: Path) -> ResultatCarrega:
    return carrega_nedadors(RepositoriNedadorsJson(arrel), RepositoriCatalegJson(arrel))


@pytest.mark.ca("CA-001-11")
@pytest.mark.ca("CA-001-71")
@pytest.mark.parametrize("cas", ["id_repetit", "json_trencat", "nom_rn_031", "altra_temporada"])
def test_un_cataleg_amb_error_falla_tota_la_carrega_encara_que_no_hi_hagi_inscripcions(
    tmp_path: Path, cas: str
) -> None:
    escriu(tmp_path, nedador_json())  # sense inscripcions
    if cas == "id_repetit":
        dades = cataleg_json()
        competicions = dades["competicions"]  # type: ignore[index]
        dades["competicions"] = [competicions[0], competicions[0]]
        escriu_cataleg(tmp_path, dades)
    elif cas == "json_trencat":
        escriu_cataleg(tmp_path, "{no és json")
    elif cas == "nom_rn_031":
        escriu_cataleg(tmp_path, cataleg_json(), nom="2026-28.json")
    else:
        escriu_inscripcions(tmp_path, inscripcions_json())
        escriu_cataleg(tmp_path, cataleg_json())
        escriu_cataleg(tmp_path, "{no és json", nom="2000-01.json")
    with pytest.raises(ErrorCarrega):
        carrega(tmp_path)


@pytest.mark.ca("CA-001-12")
def test_l_avis_rn_009_es_recull_encara_que_no_hi_hagi_inscripcions(tmp_path: Path) -> None:
    escriu(tmp_path, nedador_json())
    escriu_cataleg(tmp_path, cataleg_json())
    assert [a.rn for a in carrega(tmp_path).avisos_cataleg] == ["RN-009"]


@pytest.mark.ca("CA-001-75")
def test_un_nedador_json_que_no_es_utf8_exclou_nomes_aquell_nedador(tmp_path: Path) -> None:
    escriu(tmp_path, nedador_json())
    cami = escriu(tmp_path, nedador_json(alias="altre_9b1c2d3"), ID_B)
    cami.write_bytes(b"\xe9")
    resultat = carrega(tmp_path)
    assert set(resultat.nedadors) == {ID_A}
    assert "no es pot llegir" in resultat.resultats[ID_B].errors[0].missatge


def test_una_carpeta_de_nedador_sense_nedador_json_dona_error_i_no_atura_res(
    tmp_path: Path,
) -> None:
    escriu(tmp_path, nedador_json())
    escriu_inscripcions(tmp_path, inscripcions_json(), id_nedador=ID_B)
    escriu_cataleg(tmp_path, cataleg_json())
    resultat = carrega(tmp_path)
    assert set(resultat.nedadors) == {ID_A}
    assert "no existeix" in resultat.resultats[ID_B].errors[0].missatge


@pytest.mark.ca("CA-001-43")
def test_una_carpeta_de_temporada_mal_anomenada_porta_l_alias_i_exclou_el_nedador(
    tmp_path: Path,
) -> None:
    escriu(tmp_path, nedador_json())
    escriu_inscripcions(tmp_path, inscripcions_json(), temporada="vell")
    resultat = carrega(tmp_path)
    assert resultat.nedadors == {}
    (error,) = resultat.resultats[ID_A].errors
    assert (error.rn, error.nedador) == ("RN-031", "exemple_3f2a9c1")


@pytest.mark.ca("CA-001-27")
def test_una_carpeta_de_nedador_que_no_es_uuid_surt_al_resultat(tmp_path: Path) -> None:
    escriu(tmp_path, nedador_json())
    (tmp_path / "nedadors" / "n0001").mkdir()
    resultat = carrega(tmp_path)
    assert set(resultat.nedadors) == {ID_A}
    assert [e.rn for e in resultat.errors_carpetes] == ["RN-001"]


def test_una_carpeta_de_temporada_mal_anomenada_no_bloqueja_esborrar_una_competicio(
    tmp_path: Path,
) -> None:
    escriu(tmp_path, nedador_json())
    escriu_inscripcions(tmp_path, inscripcions_json())  # només c001
    escriu_inscripcions(tmp_path, inscripcions_json(), temporada="vell")
    escriu_cataleg(tmp_path, cataleg_json())
    resultat = esborra_competicio(
        RepositoriCatalegJson(tmp_path), RepositoriNedadorsJson(tmp_path), TEMPORADA, "c002"
    )
    assert resultat.desat
