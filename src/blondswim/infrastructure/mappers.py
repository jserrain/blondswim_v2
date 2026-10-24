"""Mapper DTO ↔ domini del nedador."""

import json
from collections.abc import Callable

from pydantic import ValidationError

from blondswim.domain.nedador import (
    DetallProva,
    ErrorInvariant,
    MillorRegistre,
    Nedador,
    TestCss,
    VolumSetmanal,
)
from blondswim.domain.validacio import ErrorCarrega, ErrorValidacio, valida_nedador
from blondswim.domain.valors import Alias, Correu, Temps
from blondswim.infrastructure.dto import (
    DetallProvaDto,
    MillorRegistreDto,
    NedadorDto,
    TestCssDto,
    VolumSetmanalDto,
    errors_en_catala,
)

VERSIO_ESQUEMA = 1


def _camp(prefix: str, camp: str) -> str:
    return f"{prefix}.{camp}" if prefix and camp else prefix or camp


def _valor_a(brut: object, camp: str) -> object:
    """El valor del JSON brut a la ruta `a.0.b`; `None` si no hi és."""
    for part in camp.split(".") if camp else []:
        if isinstance(brut, dict):
            brut = brut.get(part)
        elif isinstance(brut, list) and part.isdigit() and int(part) < len(brut):
            brut = brut[int(part)]
        else:
            return None
    return brut


class _Acumulador:
    """Recull els errors de construcció del domini sense aturar-se al primer."""

    def __init__(self, fitxer: str) -> None:
        self.fitxer = fitxer
        self.errors: list[ErrorValidacio] = []

    def valor[T](self, camp: str, rn: str, brut: str, fabrica: Callable[[str], T]) -> T | None:
        try:
            return fabrica(brut)
        except ValueError as excepcio:
            self.errors.append(ErrorValidacio(rn, self.fitxer, camp, brut, str(excepcio)))
            return None

    def entitat[T](self, prefix: str, fabrica: Callable[[], T]) -> T | None:
        try:
            return fabrica()
        except ErrorInvariant as excepcio:
            self.errors.extend(
                ErrorValidacio(v.rn, self.fitxer, _camp(prefix, v.camp), v.valor, v.missatge)
                for v in excepcio.violacions
            )
            return None


def llegeix_nedador(text: str, fitxer: str) -> Nedador:
    """Llegeix `nedador.json`; si no és vàlid, `ErrorCarrega` amb tots els errors."""
    try:
        brut = json.loads(text)
    except json.JSONDecodeError:
        raise ErrorCarrega((ErrorValidacio("", fitxer, "", None, "JSON invàlid"),)) from None
    if not isinstance(brut, dict):
        raise ErrorCarrega((ErrorValidacio("", fitxer, "", None, "ha de ser un objecte"),))
    if "versio_esquema" in brut:
        versio = brut["versio_esquema"]
        if type(versio) is not int or versio != VERSIO_ESQUEMA:
            missatge = f"versió d'esquema no admesa (cal {VERSIO_ESQUEMA})"
            raise ErrorCarrega((ErrorValidacio("", fitxer, "versio_esquema", versio, missatge),))
    try:
        dto = NedadorDto.model_validate_json(text)
    except ValidationError as excepcio:
        raise ErrorCarrega(
            tuple(
                ErrorValidacio("", fitxer, e.camp, _valor_a(brut, e.camp), e.missatge)
                for e in errors_en_catala(excepcio)
            )
        ) from None
    return de_dto(dto, fitxer)


def de_dto(dto: NedadorDto, fitxer: str) -> Nedador:
    acc = _Acumulador(fitxer)
    correu = acc.valor("correu", "RN-032", dto.correu, Correu)
    alias = acc.valor("alias", "RN-003", dto.alias, Alias) if dto.alias is not None else None
    tests = [_de_test(acc, f"tests_css.{i}", t) for i, t in enumerate(dto.tests_css)]
    registres = [
        _de_registre(acc, f"millors_registres.{i}", r) for i, r in enumerate(dto.millors_registres)
    ]
    nedador = None
    if correu is not None:
        nedador = acc.entitat(
            "",
            lambda: Nedador(
                correu=correu,
                arxivat=dto.arxivat,
                estils_preferents=tuple(dto.estils_preferents),
                dies_entrenament=tuple(dto.dies_entrenament),
                volum_setmanal=VolumSetmanal(dto.volum_setmanal.min, dto.volum_setmanal.max),
                tests_css=tuple(t for t in tests if t is not None),
                millors_registres=tuple(r for r in registres if r is not None),
                alias=alias,
            ),
        )
    if nedador is not None:
        acc.errors.extend(valida_nedador(nedador, fitxer).errors)
    if acc.errors or nedador is None:
        raise ErrorCarrega(tuple(acc.errors))
    return nedador


def _de_detall(acc: _Acumulador, prefix: str, dto: DetallProvaDto | None) -> DetallProva | None:
    if dto is None:
        return None
    parcials = None
    if dto.parcials is not None:
        convertits = [
            acc.valor(f"{prefix}.parcials.{i}", "", text, Temps.de_text)
            for i, text in enumerate(dto.parcials)
        ]
        if any(temps is None for temps in convertits):
            return None
        parcials = tuple(temps for temps in convertits if temps is not None)
    return acc.entitat(
        prefix, lambda: DetallProva(parcials, dto.bracades_per_llarg, dto.sr, dto.rpe)
    )


def _de_test(acc: _Acumulador, prefix: str, dto: TestCssDto) -> TestCss | None:
    t400 = acc.valor(f"{prefix}.t400", "", dto.t400, Temps.de_text)
    t200 = acc.valor(f"{prefix}.t200", "", dto.t200, Temps.de_text)
    detall_400 = _de_detall(acc, f"{prefix}.detall_400", dto.detall_400)
    detall_200 = _de_detall(acc, f"{prefix}.detall_200", dto.detall_200)
    if t400 is None or t200 is None:
        return None
    return acc.entitat(
        prefix,
        lambda: TestCss(
            dto.data, dto.piscina, t400, t200, dto.acceptat, detall_400, detall_200, dto.notes
        ),
    )


def _de_registre(acc: _Acumulador, prefix: str, dto: MillorRegistreDto) -> MillorRegistre | None:
    temps = acc.valor(f"{prefix}.temps", "", dto.temps, Temps.de_text)
    if temps is None:
        return None
    return MillorRegistre(dto.estil, dto.distancia, dto.piscina, temps, dto.data, dto.competicio)


def a_dto(nedador: Nedador) -> NedadorDto:
    return NedadorDto(
        versio_esquema=VERSIO_ESQUEMA,
        correu=nedador.correu.valor,
        alias=None if nedador.alias is None else nedador.alias.valor,
        arxivat=nedador.arxivat,
        estils_preferents=list(nedador.estils_preferents),
        dies_entrenament=list(nedador.dies_entrenament),
        volum_setmanal=VolumSetmanalDto(
            min=nedador.volum_setmanal.min, max=nedador.volum_setmanal.max
        ),
        tests_css=[_test_a_dto(t) for t in nedador.tests_css],
        millors_registres=[
            MillorRegistreDto(
                estil=r.estil,
                distancia=r.distancia,
                piscina=r.piscina,
                temps=str(r.temps),
                data=r.data,
                competicio=r.competicio,
            )
            for r in nedador.millors_registres
        ],
    )


def _test_a_dto(test: TestCss) -> TestCssDto:
    return TestCssDto(
        data=test.data,
        piscina=test.piscina,
        t400=str(test.t400),
        t200=str(test.t200),
        acceptat=test.acceptat,
        detall_400=_detall_a_dto(test.detall_400),
        detall_200=_detall_a_dto(test.detall_200),
        notes=test.notes,
    )


def _detall_a_dto(detall: DetallProva | None) -> DetallProvaDto | None:
    if detall is None:
        return None
    return DetallProvaDto(
        parcials=None if detall.parcials is None else [str(t) for t in detall.parcials],
        bracades_per_llarg=detall.bracades_per_llarg,
        sr=detall.sr,
        rpe=detall.rpe,
    )
