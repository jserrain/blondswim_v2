import json
from pathlib import Path

import pytest

from blondswim.domain.validacio import ErrorCarrega
from blondswim.domain.valors import IdNedador
from blondswim.infrastructure.repositoris import RepositoriNedadorsJson

_ID = IdNedador("n0001")


def _nedador_json() -> dict[str, object]:
    return {
        "versio_esquema": 1,
        "correu": "nedador@example.com",
        "alias": "exemple",
        "arxivat": False,
        "estils_preferents": ["Cr", "Ei"],
        "dies_entrenament": ["dl", "dc", "dv"],
        "volum_setmanal": {"min": 8000, "max": 12000},
        "tests_css": [
            {
                "data": "2000-01-15",
                "piscina": 25,
                "t400": "6:30.00",
                "t200": "3:10.00",
                "acceptat": True,
                "detall_400": {"parcials": None, "bracades_per_llarg": None, "sr": None, "rpe": 8},
                "detall_200": {"parcials": None, "bracades_per_llarg": None, "sr": None, "rpe": 9},
                "notes": None,
            }
        ],
        "millors_registres": [
            {
                "estil": "Cr",
                "distancia": 100,
                "piscina": 25,
                "temps": "1:15.00",
                "data": "2000-02-01",
                "competicio": "Exemple",
            }
        ],
    }


def _escriu(arrel: Path, dades: dict[str, object], id_nedador: str = "n0001") -> Path:
    cami = arrel / "nedadors" / id_nedador / "nedador.json"
    cami.parent.mkdir(parents=True)
    cami.write_text(json.dumps(dades, indent=2), encoding="utf-8")
    return cami


def _errors_de_carrega(arrel: Path) -> ErrorCarrega:
    with pytest.raises(ErrorCarrega) as excepcio:
        RepositoriNedadorsJson(arrel).carrega(_ID)
    return excepcio.value


@pytest.mark.ca("CA-001-01")
def test_carregar_i_desar_dona_contingut_equivalent(tmp_path: Path) -> None:
    original = _nedador_json()
    cami = _escriu(tmp_path, original)
    repositori = RepositoriNedadorsJson(tmp_path)

    repositori.desa(_ID, repositori.carrega(_ID))

    assert json.loads(cami.read_text(encoding="utf-8")) == original


@pytest.mark.ca("CA-001-07")
def test_millor_registre_amb_temps_mal_format_dona_error_de_format(tmp_path: Path) -> None:
    dades = _nedador_json()
    dades["millors_registres"][0]["temps"] = "1:05.3"  # type: ignore[index]
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.valor) for e in errors] == [
        ("nedadors/n0001/nedador.json", "millors_registres.0.temps", "1:05.3")
    ]


@pytest.mark.ca("CA-001-17")
@pytest.mark.parametrize("versio", [0, 2, "1", True])
def test_versio_desconeguda_dona_error(tmp_path: Path, versio: object) -> None:
    dades = _nedador_json()
    dades["versio_esquema"] = versio
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.camp, e.valor) for e in errors] == [("versio_esquema", versio)]


@pytest.mark.ca("CA-001-27")
@pytest.mark.parametrize("nom", ["n001", "n00012", "N0001", "nedador"])
def test_carpeta_amb_nom_sense_el_format_de_l_id_dona_error(tmp_path: Path, nom: str) -> None:
    (tmp_path / "nedadors" / nom).mkdir(parents=True)

    with pytest.raises(ErrorCarrega) as excepcio:
        RepositoriNedadorsJson(tmp_path).ids()

    assert [(e.rn, e.fitxer, e.valor) for e in excepcio.value.errors] == [
        ("RN-001", f"nedadors/{nom}", nom)
    ]


def test_ids_llista_les_carpetes_valides_ordenades(tmp_path: Path) -> None:
    for nom in ["n0002", "n0001"]:
        (tmp_path / "nedadors" / nom).mkdir(parents=True)
    (tmp_path / "nedadors" / ".gitkeep").touch()

    assert RepositoriNedadorsJson(tmp_path).ids() == [IdNedador("n0001"), IdNedador("n0002")]


@pytest.mark.ca("CA-001-31")
def test_detalls_amb_tots_els_camps_a_null_es_conserven(tmp_path: Path) -> None:
    original = _nedador_json()
    tot_null = {"parcials": None, "bracades_per_llarg": None, "sr": None, "rpe": None}
    original["tests_css"][0]["detall_400"] = dict(tot_null)  # type: ignore[index]
    original["tests_css"][0]["detall_200"] = dict(tot_null)  # type: ignore[index]
    cami = _escriu(tmp_path, original)
    repositori = RepositoriNedadorsJson(tmp_path)

    repositori.desa(_ID, repositori.carrega(_ID))

    desat = json.loads(cami.read_text(encoding="utf-8"))
    assert desat == original
    assert desat["tests_css"][0]["detall_400"] == tot_null


@pytest.mark.ca("CA-001-36")
def test_fitxer_desat_pel_sistema_es_idèntic_byte_a_byte(tmp_path: Path) -> None:
    cami = _escriu(tmp_path, _nedador_json())
    repositori = RepositoriNedadorsJson(tmp_path)
    repositori.desa(_ID, repositori.carrega(_ID))
    primer = cami.read_bytes()

    repositori.desa(_ID, repositori.carrega(_ID))

    assert cami.read_bytes() == primer
    assert primer.endswith(b"\n")


@pytest.mark.ca("CA-001-35")
def test_test_sense_acceptat_dona_error_de_carrega(tmp_path: Path) -> None:
    dades = _nedador_json()
    del dades["tests_css"][0]["acceptat"]  # type: ignore[index]
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.camp, e.missatge) for e in errors] == [
        ("tests_css.0.acceptat", "camp obligatori absent")
    ]


@pytest.mark.ca("CA-001-39")
def test_estil_preferent_no_admes_identifica_camp_i_valor(tmp_path: Path) -> None:
    dades = _nedador_json()
    dades["estils_preferents"] = ["Cr", "EP"]
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.camp, e.valor) for e in errors] == [("estils_preferents.1", "EP")]


@pytest.mark.ca("CA-001-41")
@pytest.mark.parametrize("camp", ["tests_css", "millors_registres"])
def test_piscina_no_valida_identifica_fitxer_camp_i_valor(tmp_path: Path, camp: str) -> None:
    dades = _nedador_json()
    dades[camp][0]["piscina"] = 33  # type: ignore[index]
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.valor) for e in errors] == [
        ("nedadors/n0001/nedador.json", f"{camp}.0.piscina", 33)
    ]


@pytest.mark.ca("CA-001-44")
@pytest.mark.parametrize("correu", [None, "", "a b@example.com", "absent"])
def test_correu_absent_null_buit_o_amb_espais_identifica_el_camp(
    tmp_path: Path, correu: str | None
) -> None:
    dades = _nedador_json()
    if correu == "absent":
        del dades["correu"]
    else:
        dades["correu"] = correu
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [e.camp for e in errors] == ["correu"]


@pytest.mark.ca("CA-001-46")
@pytest.mark.parametrize("alias", ["", "n0002", "A", "a_b"])
def test_alias_que_incompleix_rn_003_identifica_el_camp(tmp_path: Path, alias: str) -> None:
    dades = _nedador_json()
    dades["alias"] = alias
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.rn, e.camp, e.valor) for e in errors] == [("RN-003", "alias", alias)]


def test_la_carrega_acumula_tots_els_errors(tmp_path: Path) -> None:
    dades = _nedador_json()
    dades["estils_preferents"] = []
    dades["volum_setmanal"] = {"min": 9, "max": 1}
    dades["tests_css"][0]["t400"] = "3:00.00"  # type: ignore[index]
    _escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert {e.camp for e in errors} == {"estils_preferents", "volum_setmanal", "tests_css.0.t400"}
