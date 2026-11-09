"""US3 — `inscripcions.json`: lectura, escriptura i carpeta de temporada (T021)."""

import json
from pathlib import Path

import pytest

from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.validacio import ErrorCarrega
from blondswim.domain.valors import Classe, CodiTemporada
from blondswim.infrastructure.repositoris import RepositoriNedadorsJson
from tests.integration.ajuts import ID_A, TEMPORADA, escriu_inscripcions, inscripcions_json


def test_carrega_les_inscripcions_de_la_temporada(tmp_path: Path) -> None:
    escriu_inscripcions(tmp_path, inscripcions_json())
    repositori = RepositoriNedadorsJson(tmp_path)
    assert repositori.temporades(ID_A) == [TEMPORADA]
    inscripcions = repositori.carrega_inscripcions(ID_A, TEMPORADA)
    assert isinstance(inscripcions, Inscripcions)
    (participacio,) = inscripcions.participacions
    assert participacio.id_competicio == "c001"
    assert participacio.classe is Classe.A


@pytest.mark.ca("CA-001-02")
def test_carregar_i_desar_dona_contingut_equivalent(tmp_path: Path) -> None:
    cami = escriu_inscripcions(tmp_path, inscripcions_json())
    repositori = RepositoriNedadorsJson(tmp_path)
    repositori.desa_inscripcions(ID_A, TEMPORADA, repositori.carrega_inscripcions(ID_A, TEMPORADA))
    assert json.loads(cami.read_text(encoding="utf-8")) == inscripcions_json()


@pytest.mark.ca("CA-001-36")
def test_fitxer_desat_pel_sistema_es_identic_byte_a_byte(tmp_path: Path) -> None:
    cami = escriu_inscripcions(tmp_path, inscripcions_json())
    repositori = RepositoriNedadorsJson(tmp_path)
    repositori.desa_inscripcions(ID_A, TEMPORADA, repositori.carrega_inscripcions(ID_A, TEMPORADA))
    primer = cami.read_bytes()
    repositori.desa_inscripcions(ID_A, TEMPORADA, repositori.carrega_inscripcions(ID_A, TEMPORADA))
    assert cami.read_bytes() == primer


@pytest.mark.ca("CA-001-17")
@pytest.mark.parametrize("versio", [2, "1", None])
def test_versio_desconeguda_d_inscripcions_dona_error_d_aquell_nedador(
    tmp_path: Path, versio: object
) -> None:
    escriu_inscripcions(tmp_path, {**inscripcions_json(), "versio_esquema": versio})
    with pytest.raises(ErrorCarrega) as exc:
        RepositoriNedadorsJson(tmp_path).carrega_inscripcions(ID_A, TEMPORADA)
    (error,) = exc.value.errors
    assert error.camp == "versio_esquema"
    assert error.fitxer == f"nedadors/{ID_A}/temporades/{TEMPORADA}/inscripcions.json"


@pytest.mark.ca("CA-001-43")
def test_carpeta_de_temporada_que_no_segueix_rn_031_dona_error(tmp_path: Path) -> None:
    escriu_inscripcions(tmp_path, inscripcions_json(), temporada="2026-28")
    with pytest.raises(ErrorCarrega) as exc:
        RepositoriNedadorsJson(tmp_path).temporades(ID_A)
    (error,) = exc.value.errors
    assert error.rn == "RN-031"
    assert error.fitxer == f"nedadors/{ID_A}/temporades/2026-28"


def test_carpeta_de_temporada_sense_inscripcions_no_compta(tmp_path: Path) -> None:
    (tmp_path / "nedadors" / str(ID_A) / "temporades" / "2000-01").mkdir(parents=True)
    assert RepositoriNedadorsJson(tmp_path).temporades(ID_A) == []


def test_nedador_sense_temporades(tmp_path: Path) -> None:
    assert RepositoriNedadorsJson(tmp_path).temporades(ID_A) == []


def test_participacio_sense_proves_dona_error_amb_el_camp(tmp_path: Path) -> None:
    dades = inscripcions_json()
    dades["participacions"][0]["proves"] = []  # type: ignore[index]
    escriu_inscripcions(tmp_path, dades)
    with pytest.raises(ErrorCarrega) as exc:
        RepositoriNedadorsJson(tmp_path).carrega_inscripcions(ID_A, TEMPORADA)
    assert [(e.rn, e.camp) for e in exc.value.errors] == [("RN-014", "participacions.0.proves")]


def test_json_trencat_dona_error(tmp_path: Path) -> None:
    escriu_inscripcions(tmp_path, "{no és json")
    with pytest.raises(ErrorCarrega):
        RepositoriNedadorsJson(tmp_path).carrega_inscripcions(ID_A, CodiTemporada("1999-00"))
