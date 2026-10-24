from dataclasses import replace
from datetime import date

import pytest

from blondswim.domain.nedador import (
    DetallProva,
    ErrorInvariant,
    MillorRegistre,
    Nedador,
    VolumSetmanal,
)
from blondswim.domain.nedador import TestCss as CssTest  # evita que pytest el reculli
from blondswim.domain.validacio import valida_entre_nedadors, valida_nedador
from blondswim.domain.valors import Alias, Correu, Dia, Estil, IdNedador, Piscina, Temps


def _test(**canvis: object) -> CssTest:
    base = CssTest(
        data=date(2000, 1, 15),
        piscina=Piscina.CURTA,
        t400=Temps.de_text("6:30.00"),
        t200=Temps.de_text("3:10.00"),
        acceptat=True,
    )
    return replace(base, **canvis)


def _registre(**canvis: object) -> MillorRegistre:
    base = MillorRegistre(
        estil=Estil.CR,
        distancia=100,
        piscina=Piscina.CURTA,
        temps=Temps.de_text("1:15.00"),
        data=date(2000, 2, 1),
        competicio="Exemple",
    )
    return replace(base, **canvis)


def _nedador(**canvis: object) -> Nedador:
    base = Nedador(
        correu=Correu("nedador@example.com"),
        arxivat=False,
        estils_preferents=(Estil.CR, Estil.EI),
        dies_entrenament=(Dia.DL, Dia.DC, Dia.DV),
        volum_setmanal=VolumSetmanal(min=8000, max=12000),
        tests_css=(_test(),),
        millors_registres=(_registre(),),
        alias=Alias("exemple"),
    )
    return replace(base, **canvis)


def _violacions(excepcio: pytest.ExceptionInfo[ErrorInvariant]) -> list[tuple[str, object]]:
    return [(v.camp, v.valor) for v in excepcio.value.violacions]


def test_nedador_valid() -> None:
    assert valida_nedador(_nedador(), "nedadors/n0001/nedador.json").es_valid


@pytest.mark.ca("CA-001-03")
def test_sense_estils_preferents_identifica_el_camp() -> None:
    with pytest.raises(ErrorInvariant) as excepcio:
        _nedador(estils_preferents=())
    assert [camp for camp, _ in _violacions(excepcio)] == ["estils_preferents"]


@pytest.mark.ca("CA-001-03")
def test_sense_dies_d_entrenament_identifica_el_camp() -> None:
    with pytest.raises(ErrorInvariant) as excepcio:
        _nedador(dies_entrenament=())
    assert [camp for camp, _ in _violacions(excepcio)] == ["dies_entrenament"]


@pytest.mark.ca("CA-001-03")
@pytest.mark.parametrize("minim, maxim", [(12000, 8000), (0, 8000), (-1, 8000)])
def test_volum_setmanal_fora_de_rang_identifica_el_camp(minim: int, maxim: int) -> None:
    # RN-005: 0 < min ≤ max
    with pytest.raises(ErrorInvariant) as excepcio:
        _nedador(volum_setmanal=VolumSetmanal(min=minim, max=maxim))
    assert [camp for camp, _ in _violacions(excepcio)] == ["volum_setmanal"]
    assert excepcio.value.violacions[0].rn == "RN-005"


@pytest.mark.ca("CA-001-03")
def test_volum_setmanal_min_igual_a_max_es_valid() -> None:
    assert _nedador(volum_setmanal=VolumSetmanal(min=8000, max=8000))


@pytest.mark.ca("CA-001-04")
@pytest.mark.parametrize("t400, t200", [("3:10.00", "3:10.00"), ("3:00.00", "3:10.00")])
def test_t400_no_superior_a_t200_es_error(t400: str, t200: str) -> None:
    with pytest.raises(ErrorInvariant) as excepcio:
        _test(t400=Temps.de_text(t400), t200=Temps.de_text(t200))
    assert excepcio.value.violacions[0].rn == "RN-006"


@pytest.mark.ca("CA-001-06")
def test_millors_registres_repetits_son_error() -> None:
    nedador = _nedador(millors_registres=(_registre(), _registre(temps=Temps.de_text("1:14.00"))))
    resultat = valida_nedador(nedador, "nedadors/n0001/nedador.json")
    assert [(e.rn, e.camp) for e in resultat.errors] == [("RN-007", "millors_registres.1")]


@pytest.mark.ca("CA-001-06")
def test_millors_registres_amb_piscina_diferent_no_son_repetits() -> None:
    nedador = _nedador(millors_registres=(_registre(), _registre(piscina=Piscina.LLARGA)))
    assert valida_nedador(nedador, "nedadors/n0001/nedador.json").es_valid


@pytest.mark.ca("CA-001-24")
def test_correu_repetit_sense_distingir_majuscules_identifica_els_dos_ids() -> None:
    nedadors = {
        IdNedador("n0001"): _nedador(correu=Correu("Nedador@Example.com")),
        IdNedador("n0002"): _nedador(
            correu=Correu("nedador@example.com"), arxivat=True, alias=None
        ),
    }
    errors = valida_entre_nedadors(nedadors).errors
    assert [(e.rn, e.camp) for e in errors] == [("RN-032", "correu")]
    assert "n0001" in errors[0].missatge and "n0002" in errors[0].missatge


@pytest.mark.ca("CA-001-26")
def test_alias_repetit_es_error() -> None:
    nedadors = {
        IdNedador("n0001"): _nedador(correu=Correu("a@example.com")),
        IdNedador("n0002"): _nedador(correu=Correu("b@example.com")),
    }
    errors = valida_entre_nedadors(nedadors).errors
    assert [(e.rn, e.camp, e.valor) for e in errors] == [("RN-003", "alias", "exemple")]
    assert "n0001" in errors[0].missatge and "n0002" in errors[0].missatge


@pytest.mark.ca("CA-001-26")
def test_nedadors_sense_alias_no_es_consideren_repetits() -> None:
    nedadors = {
        IdNedador("n0001"): _nedador(correu=Correu("a@example.com"), alias=None),
        IdNedador("n0002"): _nedador(correu=Correu("b@example.com"), alias=None),
    }
    assert valida_entre_nedadors(nedadors).es_valid


@pytest.mark.ca("CA-001-32")
def test_detalls_i_notes_a_null_no_generen_avisos() -> None:
    detall = DetallProva(parcials=None, bracades_per_llarg=None, sr=None, rpe=None)
    test = _test(detall_400=detall, detall_200=detall, notes="Bon dia")
    resultat = valida_nedador(_nedador(tests_css=(test,)), "nedadors/n0001/nedador.json")
    assert resultat.avisos == ()
    assert resultat.es_valid


@pytest.mark.ca("CA-001-35")
def test_test_sense_acceptat_no_es_pot_construir() -> None:
    with pytest.raises(TypeError):
        CssTest(  # type: ignore[call-arg]
            data=date(2000, 1, 15),
            piscina=Piscina.CURTA,
            t400=Temps.de_text("6:30.00"),
            t200=Temps.de_text("3:10.00"),
        )


@pytest.mark.ca("CA-001-39")
def test_estil_preferent_repetit_identifica_camp_i_valor() -> None:
    with pytest.raises(ErrorInvariant) as excepcio:
        _nedador(estils_preferents=(Estil.CR, Estil.CR))
    assert _violacions(excepcio) == [("estils_preferents", "Cr")]


@pytest.mark.ca("CA-001-39")
def test_estil_preferent_fora_dels_cinc_es_rebutja() -> None:
    with pytest.raises(ValueError):
        Estil("EP")


@pytest.mark.ca("CA-001-40")
def test_dia_d_entrenament_repetit_identifica_camp_i_valor() -> None:
    with pytest.raises(ErrorInvariant) as excepcio:
        _nedador(dies_entrenament=(Dia.DL, Dia.DL))
    assert _violacions(excepcio) == [("dies_entrenament", "dl")]


@pytest.mark.ca("CA-001-40")
def test_dia_d_entrenament_no_valid_es_rebutja() -> None:
    with pytest.raises(ValueError):
        Dia("dm")


@pytest.mark.ca("CA-001-41")
@pytest.mark.parametrize("metres", [0, 33, 100])
def test_piscina_no_valida_es_rebutja_al_test_i_al_millor_registre(metres: int) -> None:
    with pytest.raises(ValueError):
        Piscina(metres)


@pytest.mark.ca("CA-001-42")
def test_millor_registre_amb_prova_no_oficial_identifica_prova_i_piscina() -> None:
    # RN-030: 100 Ei només a 25 m
    registre = _registre(estil=Estil.EI, distancia=100, piscina=Piscina.LLARGA)
    nedador = _nedador(millors_registres=(registre,))
    resultat = valida_nedador(nedador, "nedadors/n0001/nedador.json")
    assert [(e.rn, e.camp) for e in resultat.errors] == [("RN-030", "millors_registres.0")]
    assert "100" in resultat.errors[0].missatge
    assert "Ei" in resultat.errors[0].missatge
    assert "50" in resultat.errors[0].missatge


@pytest.mark.ca("CA-001-42")
def test_millor_registre_amb_prova_oficial_es_valid() -> None:
    registre = _registre(estil=Estil.EI, distancia=100, piscina=Piscina.CURTA)
    assert valida_nedador(_nedador(millors_registres=(registre,)), "f").es_valid


@pytest.mark.ca("CA-001-44")
@pytest.mark.parametrize("text", ["", " ", "a b@example.com"])
def test_correu_buit_o_amb_espais_es_rebutja(text: str) -> None:
    with pytest.raises(ValueError):
        Correu(text)


@pytest.mark.ca("CA-001-46")
@pytest.mark.parametrize("text", ["", "n0002", "A", "a_b"])
def test_alias_que_incompleix_rn_003_es_rebutja(text: str) -> None:
    with pytest.raises(ValueError):
        Alias(text)


def test_detall_prova_rebutja_valors_fora_de_rang() -> None:
    for camp, valor in [("rpe", 11), ("rpe", -1), ("sr", 0.0), ("bracades_per_llarg", -2.0)]:
        with pytest.raises(ErrorInvariant) as excepcio:
            DetallProva(**{camp: valor})  # type: ignore[arg-type]
        assert [c for c, _ in _violacions(excepcio)] == [camp]


def test_parcials_son_4_al_400_i_2_al_200() -> None:
    quatre = tuple(Temps.de_text("1:35.00") for _ in range(4))
    dos = tuple(Temps.de_text("1:35.00") for _ in range(2))
    assert _test(detall_400=DetallProva(parcials=quatre), detall_200=DetallProva(parcials=dos))
    with pytest.raises(ErrorInvariant) as excepcio:
        _test(detall_400=DetallProva(parcials=dos))
    assert [c for c, _ in _violacions(excepcio)] == ["detall_400.parcials"]
    with pytest.raises(ErrorInvariant) as excepcio:
        _test(detall_200=DetallProva(parcials=quatre))
    assert [c for c, _ in _violacions(excepcio)] == ["detall_200.parcials"]
