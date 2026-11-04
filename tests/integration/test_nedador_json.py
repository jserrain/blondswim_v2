import json
from pathlib import Path

import pytest

from blondswim.domain.validacio import ErrorCarrega, Identitat
from blondswim.domain.valors import IdNedador
from blondswim.infrastructure.repositoris import RepositoriNedadorsJson
from tests.integration.ajuts import ID_A, ID_B, ID_X, escriu, nedador_json


def _errors_de_carrega(arrel: Path) -> ErrorCarrega:
    with pytest.raises(ErrorCarrega) as excepcio:
        RepositoriNedadorsJson(arrel).carrega(ID_A)
    return excepcio.value


def _desa_i_torna_a_llegir(arrel: Path, cami: Path) -> dict[str, object]:
    repositori = RepositoriNedadorsJson(arrel)
    repositori.desa(ID_A, repositori.carrega(ID_A))
    return json.loads(cami.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


@pytest.mark.ca("CA-001-01")
def test_carregar_i_desar_dona_contingut_equivalent(tmp_path: Path) -> None:
    original = nedador_json()
    cami = escriu(tmp_path, original)

    assert _desa_i_torna_a_llegir(tmp_path, cami) == original


@pytest.mark.ca("CA-001-01")
@pytest.mark.ca("CA-001-104")
@pytest.mark.parametrize(
    "correu",
    ["a@b.c", "  Pere@Exemple.cat ", "\tpere@exemple.cat", "pere@exemple.cat\n", "a@b@example.com"],
)
def test_el_correu_es_desa_i_es_torna_a_llegir_identic_sense_normalitzar(
    tmp_path: Path, correu: str
) -> None:
    original = nedador_json()
    original["correu"] = correu
    cami = escriu(tmp_path, original)

    desat = _desa_i_torna_a_llegir(tmp_path, cami)

    assert desat["correu"] == correu
    assert desat == original


@pytest.mark.ca("CA-001-07")
def test_millor_registre_amb_temps_mal_format_dona_error_de_format(tmp_path: Path) -> None:
    dades = nedador_json()
    dades["millors_registres"][1]["temps"] = "1:05.3"  # type: ignore[index]
    escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.valor) for e in errors] == [
        (f"nedadors/{ID_A}/nedador.json", "millors_registres.1.temps", "1:05.3")
    ]


@pytest.mark.ca("CA-001-17")
@pytest.mark.parametrize("versio", [0, 2, "1", True])
def test_versio_desconeguda_dona_error(tmp_path: Path, versio: object) -> None:
    dades = nedador_json()
    dades["versio_esquema"] = versio
    escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.camp, e.valor) for e in errors] == [("versio_esquema", versio)]


@pytest.mark.ca("CA-001-27")
@pytest.mark.parametrize(
    "nom",
    [
        "n0001",
        "7C4E1A2B-5D6F-4A8B-9C0D-1E2F3A4B5C6D",  # majúscules
        "3f2a9c1e-7b4d-1e8a-9c2f-1d6b5e0a8f47",  # UUID v1
        "nedador",
    ],
)
def test_carpeta_que_no_es_uuid_v4_dona_error_i_no_afecta_els_altres(
    tmp_path: Path, nom: str
) -> None:
    (tmp_path / "nedadors" / nom).mkdir(parents=True)
    escriu(tmp_path, nedador_json())
    repositori = RepositoriNedadorsJson(tmp_path)

    assert repositori.ids() == [ID_A]
    assert [(e.rn, e.fitxer, e.valor) for e in repositori.errors_carpetes()] == [
        ("RN-001", f"nedadors/{nom}", nom)
    ]


def test_ids_llista_les_carpetes_valides_ordenades(tmp_path: Path) -> None:
    for id_nedador in (ID_B, ID_A):
        (tmp_path / "nedadors" / str(id_nedador)).mkdir(parents=True)
    (tmp_path / "nedadors" / ".gitkeep").touch()

    assert RepositoriNedadorsJson(tmp_path).ids() == [ID_A, ID_B]


@pytest.mark.ca("CA-001-31")
def test_detalls_amb_tots_els_camps_a_null_es_conserven(tmp_path: Path) -> None:
    original = nedador_json()
    tot_null = {"parcials": None, "bracades_per_llarg": None, "sr": None, "rpe": None}
    original["tests_css"][0]["detall_400"] = dict(tot_null)  # type: ignore[index]
    original["tests_css"][0]["detall_200"] = dict(tot_null)  # type: ignore[index]
    cami = escriu(tmp_path, original)

    desat = _desa_i_torna_a_llegir(tmp_path, cami)

    assert desat == original
    assert desat["tests_css"][0]["detall_400"] == tot_null  # type: ignore[index]


@pytest.mark.ca("CA-001-36")
def test_fitxer_desat_pel_sistema_es_identic_byte_a_byte(tmp_path: Path) -> None:
    cami = escriu(tmp_path, nedador_json())
    repositori = RepositoriNedadorsJson(tmp_path)
    repositori.desa(ID_A, repositori.carrega(ID_A))
    primer = cami.read_bytes()

    repositori.desa(ID_A, repositori.carrega(ID_A))

    assert cami.read_bytes() == primer
    assert primer.endswith(b"\n")


@pytest.mark.ca("CA-001-35")
def test_test_sense_acceptat_dona_error_de_carrega(tmp_path: Path) -> None:
    dades = nedador_json()
    del dades["tests_css"][0]["acceptat"]  # type: ignore[index]
    escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.camp, e.missatge) for e in errors] == [
        ("tests_css.0.acceptat", "camp obligatori absent")
    ]


@pytest.mark.ca("CA-001-39")
def test_estil_preferent_no_admes_identifica_camp_i_valor(tmp_path: Path) -> None:
    dades = nedador_json()
    dades["estils_preferents"] = ["Cr", "EP"]
    escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.camp, e.valor) for e in errors] == [("estils_preferents.1", "EP")]


@pytest.mark.ca("CA-001-41")
@pytest.mark.parametrize("camp", ["tests_css", "millors_registres"])
def test_piscina_no_valida_identifica_fitxer_camp_i_valor(tmp_path: Path, camp: str) -> None:
    dades = nedador_json()
    dades[camp][0]["piscina"] = 33  # type: ignore[index]
    escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.fitxer, e.camp, e.valor) for e in errors] == [
        (f"nedadors/{ID_A}/nedador.json", f"{camp}.0.piscina", 33)
    ]


@pytest.mark.ca("CA-001-46")
@pytest.mark.parametrize("alias", ["", "marc", "Marc_3f2a9c1", "marc_cognom_3f2a9c1"])
def test_alias_que_incompleix_rn_003_identifica_el_camp(tmp_path: Path, alias: str) -> None:
    escriu(tmp_path, nedador_json(alias=alias))

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.rn, e.camp, e.valor) for e in errors] == [("RN-003", "alias", alias)]


@pytest.mark.ca("CA-001-49")
def test_test_sense_notes_ni_detall_es_carrega_i_es_desa_amb_null(tmp_path: Path) -> None:
    dades = nedador_json()
    for camp in ("notes", "detall_400"):
        del dades["tests_css"][0][camp]  # type: ignore[index]
    cami = escriu(tmp_path, dades)

    desat = _desa_i_torna_a_llegir(tmp_path, cami)

    assert desat["tests_css"][0]["notes"] is None  # type: ignore[index]
    assert desat["tests_css"][0]["detall_400"] is None  # type: ignore[index]


@pytest.mark.ca("CA-001-54")
@pytest.mark.parametrize("absent", [True, False])
def test_mobil_absent_o_null_dona_error_de_format_del_camp(tmp_path: Path, absent: bool) -> None:
    dades = nedador_json()
    if absent:
        del dades["mobil"]
    else:
        dades["mobil"] = None
    escriu(tmp_path, dades)

    assert [e.camp for e in _errors_de_carrega(tmp_path).errors] == ["mobil"]


@pytest.mark.ca("CA-001-57")
def test_canal_preferent_absent_equival_a_null_i_es_desa_com_a_null(tmp_path: Path) -> None:
    dades = nedador_json()
    del dades["canal_preferent"]
    cami = escriu(tmp_path, dades)

    desat = _desa_i_torna_a_llegir(tmp_path, cami)

    assert "canal_preferent" in desat and desat["canal_preferent"] is None


@pytest.mark.ca("CA-001-59")
def test_canal_no_admes_dona_error_amb_alias_camp_valor_i_opcions(tmp_path: Path) -> None:
    dades = nedador_json()
    dades["canal_preferent"] = "whatsapp"
    escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert [(e.rn, e.nedador, e.camp, e.valor) for e in errors] == [
        ("format", "exemple_3f2a9c1", "canal_preferent", "whatsapp")
    ]
    assert "correu" in errors[0].missatge and "mobil" in errors[0].missatge


@pytest.mark.ca("CA-001-107")
def test_correu_absent_equival_a_null_i_es_desa_com_a_null(tmp_path: Path) -> None:
    dades = nedador_json()
    del dades["correu"]
    dades["canal_preferent"] = "mobil"
    cami = escriu(tmp_path, dades)

    desat = _desa_i_torna_a_llegir(tmp_path, cami)

    assert "correu" in desat and desat["correu"] is None


@pytest.mark.ca("CA-001-75")
@pytest.mark.parametrize("contingut", ['{"versio_esquema": 1,', "[1, 2]", ""])
def test_fitxer_il_legible_dona_un_error_propi_amb_l_uuid_i_no_participa_a_la_unicitat(
    tmp_path: Path, contingut: str
) -> None:
    escriu(tmp_path, contingut, ID_A)
    escriu(tmp_path, nedador_json(alias="altre_9b1c2d3"), ID_B)
    repositori = RepositoriNedadorsJson(tmp_path)

    with pytest.raises(ErrorCarrega) as excepcio:
        repositori.carrega(ID_A)

    assert [(e.nedador, e.fitxer) for e in excepcio.value.errors] == [
        (str(ID_A), f"nedadors/{ID_A}/nedador.json")
    ]
    assert set(repositori.identitats()) == {ID_B}


@pytest.mark.ca("CA-001-92")
def test_correu_que_no_es_text_no_participa_a_la_unicitat_del_correu_pero_si_a_la_de_l_alias(
    tmp_path: Path,
) -> None:
    primer = nedador_json()
    primer["correu"] = 12345
    escriu(tmp_path, primer, ID_A)
    escriu(tmp_path, nedador_json(), ID_X)  # mateix alias: mateix sufix, 3f2a9c1
    repositori = RepositoriNedadorsJson(tmp_path)

    identitats = repositori.identitats()

    assert identitats[ID_A] == Identitat(correu=None, alias="exemple_3f2a9c1")
    assert identitats[ID_X] == Identitat(correu="nedador@example.com", alias="exemple_3f2a9c1")
    assert [e.camp for e in _errors_de_carrega(tmp_path).errors] == ["correu"]


@pytest.mark.ca("CA-001-92")
@pytest.mark.parametrize("camp", ["correu", "alias"])
@pytest.mark.parametrize("estat", ["absent", "no_text"])
def test_un_camp_d_identitat_que_falta_o_no_es_text_no_participa_a_la_unicitat_d_aquell_camp(
    tmp_path: Path, camp: str, estat: str
) -> None:
    dades = nedador_json()
    if estat == "absent":
        del dades[camp]
    else:
        dades[camp] = 7
    escriu(tmp_path, dades)

    identitat = RepositoriNedadorsJson(tmp_path).identitats()[ID_A]

    assert getattr(identitat, camp) is None
    altre = "alias" if camp == "correu" else "correu"
    assert getattr(identitat, altre) == nedador_json()[altre]


@pytest.mark.ca("CA-001-92")
def test_identitat_conserva_el_correu_cru_i_no_comprova_la_resta_de_camps(tmp_path: Path) -> None:
    dades = nedador_json()
    dades["correu"] = "  Pere@Exemple.cat "
    dades["estils_preferents"] = []  # error en un altre camp: el fitxer continua sent llegible
    escriu(tmp_path, dades)

    identitat = RepositoriNedadorsJson(tmp_path).identitats()[ID_A]

    assert identitat.correu == "  Pere@Exemple.cat "
    assert identitat.clau_correu == "pere@exemple.cat"


def test_la_carrega_acumula_tots_els_errors(tmp_path: Path) -> None:
    dades = nedador_json()
    dades["estils_preferents"] = []
    dades["volum_setmanal"] = {"min": 9, "max": 1}
    dades["tests_css"][0]["t400"] = "3:00.00"  # type: ignore[index]
    escriu(tmp_path, dades)

    errors = _errors_de_carrega(tmp_path).errors

    assert {e.camp for e in errors} == {"estils_preferents", "volum_setmanal", "tests_css.0.t400"}


def test_un_id_de_nedador_es_el_nom_de_la_carpeta(tmp_path: Path) -> None:
    escriu(tmp_path, nedador_json())

    assert RepositoriNedadorsJson(tmp_path).ids() == [IdNedador(str(ID_A))]
