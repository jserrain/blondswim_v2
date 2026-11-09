"""Mappers DTO ↔ domini: nedador, catàleg i inscripcions."""

import json
from collections.abc import Callable

from pydantic import ValidationError

from blondswim.domain.cataleg import Cataleg, Competicio
from blondswim.domain.inscripcions import Inscripcio, Inscripcions, Participacio
from blondswim.domain.nedador import (
    DetallProva,
    ErrorInvariant,
    MillorRegistre,
    Nedador,
    TestCss,
    VolumSetmanal,
)
from blondswim.domain.validacio import (
    ErrorCarrega,
    ErrorValidacio,
    Identitat,
    fitxer_cataleg,
    fitxer_inscripcions,
    fitxer_nedador,
    valida_nedador,
)
from blondswim.domain.valors import Alias, Canal, CodiTemporada, Correu, IdNedador, Prova, Temps
from blondswim.infrastructure.dto import (
    CatalegDto,
    CompeticioDto,
    DetallProvaDto,
    IdentitatDto,
    InscripcioDto,
    InscripcionsDto,
    MillorRegistreDto,
    NedadorDto,
    ParticipacioDto,
    ProvaDto,
    TestCssDto,
    VolumSetmanalDto,
    errors_en_catala,
)

VERSIO_ESQUEMA = 1
_ACCIO = "Corregeix el camp al fitxer del nedador"
_ACCIO_CATALEG = "Corregeix el camp al fitxer del catàleg"
_ACCIO_INSCRIPCIONS = "Corregeix el camp al fitxer d'inscripcions"


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


def _qui(brut: object, id_nedador: IdNedador) -> str:
    """L'alias del JSON si hi és; si no, l'UUID de la carpeta."""
    alias = brut.get("alias") if isinstance(brut, dict) else None
    return alias if isinstance(alias, str) and alias else str(id_nedador)


class _Acumulador:
    """Recull els errors de construcció del domini sense aturar-se al primer."""

    def __init__(self, id_nedador: IdNedador, qui: str) -> None:
        self.id_nedador = id_nedador
        self.qui = qui
        self.errors: list[ErrorValidacio] = []

    def afegeix(self, rn: str, camp: str, valor: object, missatge: str) -> None:
        self.errors.append(
            ErrorValidacio(
                rn or "format",
                fitxer_nedador(self.id_nedador),
                camp,
                valor,
                missatge,
                _ACCIO,
                self.qui,
            )
        )

    def valor[T](self, camp: str, rn: str, brut: str, fabrica: Callable[[str], T]) -> T | None:
        try:
            return fabrica(brut)
        except ValueError as excepcio:
            self.afegeix(rn, camp, brut, str(excepcio))
            return None

    def entitat[T](self, prefix: str, fabrica: Callable[[], T]) -> T | None:
        try:
            return fabrica()
        except ErrorInvariant as excepcio:
            for v in excepcio.violacions:
                self.afegeix(v.rn, _camp(prefix, v.camp), v.valor, v.missatge)
            return None


def llegeix_nedador(text: str, id_nedador: IdNedador) -> Nedador:
    """Llegeix `nedador.json`; si no és vàlid, `ErrorCarrega` amb tots els errors."""
    acc = _Acumulador(id_nedador, str(id_nedador))
    try:
        brut = json.loads(text)
    except json.JSONDecodeError:
        acc.afegeix("format", "", None, "JSON invàlid")
        raise ErrorCarrega(tuple(acc.errors)) from None
    if not isinstance(brut, dict):
        acc.afegeix("format", "", None, "ha de ser un objecte")
        raise ErrorCarrega(tuple(acc.errors))
    acc.qui = _qui(brut, id_nedador)
    if "versio_esquema" in brut:
        versio = brut["versio_esquema"]
        if type(versio) is not int or versio != VERSIO_ESQUEMA:
            missatge = f"versió d'esquema no admesa (cal {VERSIO_ESQUEMA})"
            acc.afegeix("format", "versio_esquema", versio, missatge)
            raise ErrorCarrega(tuple(acc.errors))
    try:
        dto = NedadorDto.model_validate_json(text)
    except ValidationError as excepcio:
        for e in errors_en_catala(excepcio):
            missatge = e.missatge
            if e.camp == "canal_preferent":
                missatge += f" (opcions: {', '.join(c.value for c in Canal)})"
            acc.afegeix("format", e.camp, _valor_a(brut, e.camp), missatge)
        raise ErrorCarrega(tuple(acc.errors)) from None
    return de_dto(dto, id_nedador, acc.qui)


def llegeix_identitat(text: str) -> Identitat | None:
    """El correu i l'alias com a text cru (D1); `None` si el fitxer no és llegible.

    Un camp que falta o no és text queda a `None`: no participa a la unicitat d'aquell camp.
    """
    try:
        dto = IdentitatDto.model_validate_json(text)
    except ValidationError:
        return None
    return Identitat(
        correu=dto.correu if isinstance(dto.correu, str) else None,
        alias=dto.alias if isinstance(dto.alias, str) else None,
    )


def de_dto(dto: NedadorDto, id_nedador: IdNedador, qui: str) -> Nedador:
    acc = _Acumulador(id_nedador, qui)
    correu = None if dto.correu is None else Correu(dto.correu)
    alias = acc.valor("alias", "RN-003", dto.alias, Alias) if dto.alias is not None else None
    tests = [_de_test(acc, f"tests_css.{i}", t) for i, t in enumerate(dto.tests_css)]
    registres = [
        _de_registre(acc, f"millors_registres.{i}", r) for i, r in enumerate(dto.millors_registres)
    ]
    nedador = acc.entitat(
        "",
        lambda: Nedador(
            correu=correu,
            mobil=dto.mobil,
            canal_preferent=dto.canal_preferent,
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
        # Un error amb el mateix camp i la mateixa RN (p. ex. l'alias) ja s'ha informat.
        reportats = {(e.camp, e.rn) for e in acc.errors}
        acc.errors.extend(
            e for e in valida_nedador(id_nedador, nedador).errors if (e.camp, e.rn) not in reportats
        )
    if acc.errors or nedador is None:
        raise ErrorCarrega(tuple(acc.errors))
    return nedador


def _de_detall(acc: _Acumulador, prefix: str, dto: DetallProvaDto | None) -> DetallProva | None:
    if dto is None:
        return None
    parcials = None
    if dto.parcials is not None:
        convertits = [
            acc.valor(f"{prefix}.parcials.{i}", "format", text, Temps.de_text)
            for i, text in enumerate(dto.parcials)
        ]
        if any(temps is None for temps in convertits):
            return None
        parcials = tuple(temps for temps in convertits if temps is not None)
    return acc.entitat(
        prefix, lambda: DetallProva(parcials, dto.bracades_per_llarg, dto.sr, dto.rpe)
    )


def _de_test(acc: _Acumulador, prefix: str, dto: TestCssDto) -> TestCss | None:
    t400 = acc.valor(f"{prefix}.t400", "format", dto.t400, Temps.de_text)
    t200 = acc.valor(f"{prefix}.t200", "format", dto.t200, Temps.de_text)
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
    temps = acc.valor(f"{prefix}.temps", "format", dto.temps, Temps.de_text)
    if temps is None:
        return None
    return MillorRegistre(dto.estil, dto.distancia, dto.piscina, temps, dto.data, dto.competicio)


def llegeix_cataleg(text: str, temporada: CodiTemporada) -> Cataleg:
    """Llegeix `competicions/<AAAA-AA>.json`; si no és vàlid, `ErrorCarrega` (falla TOTA la
    càrrega) amb tots els errors."""
    fitxer = fitxer_cataleg(temporada)
    errors: list[ErrorValidacio] = []

    def afegeix(rn: str, camp: str, valor: object, missatge: str) -> None:
        errors.append(ErrorValidacio(rn or "format", fitxer, camp, valor, missatge, _ACCIO_CATALEG))

    try:
        brut = json.loads(text)
    except json.JSONDecodeError:
        afegeix("format", "", None, "JSON invàlid")
        raise ErrorCarrega(tuple(errors)) from None
    if not isinstance(brut, dict):
        afegeix("format", "", None, "ha de ser un objecte")
        raise ErrorCarrega(tuple(errors))
    if "versio_esquema" in brut:
        versio = brut["versio_esquema"]
        if type(versio) is not int or versio != VERSIO_ESQUEMA:
            afegeix(
                "format",
                "versio_esquema",
                versio,
                f"versió d'esquema no admesa (cal {VERSIO_ESQUEMA})",
            )
            raise ErrorCarrega(tuple(errors))
    try:
        dto = CatalegDto.model_validate_json(text)
    except ValidationError as excepcio:
        for e in errors_en_catala(excepcio):
            afegeix("format", e.camp, _valor_a(brut, e.camp), e.missatge)
        raise ErrorCarrega(tuple(errors)) from None

    competicions: list[Competicio] = []
    for i, c in enumerate(dto.competicions):
        try:
            competicions.append(Competicio(c.id, c.nom, tuple(c.dates), c.piscina, c.seu))
        except ErrorInvariant as excepcio:
            for v in excepcio.violacions:
                afegeix(v.rn, _camp(f"competicions.{i}", v.camp), v.valor, v.missatge)
    if errors:
        raise ErrorCarrega(tuple(errors))
    try:
        return Cataleg(tuple(competicions))
    except ErrorInvariant as excepcio:
        raise ErrorCarrega(
            tuple(
                ErrorValidacio(
                    v.rn or "format", fitxer, v.camp, v.valor, v.missatge, _ACCIO_CATALEG
                )
                for v in excepcio.violacions
            )
        ) from None


def llegeix_inscripcions(
    text: str, id_nedador: IdNedador, temporada: CodiTemporada, qui: str
) -> Inscripcions:
    """Llegeix `inscripcions.json`; si no és vàlid, `ErrorCarrega` amb tots els errors (exclou
    aquell nedador). La validació creuada amb el catàleg és a `valida_inscripcions`."""
    fitxer = fitxer_inscripcions(id_nedador, temporada)
    errors: list[ErrorValidacio] = []

    def afegeix(rn: str, camp: str, valor: object, missatge: str) -> None:
        errors.append(
            ErrorValidacio(rn or "format", fitxer, camp, valor, missatge, _ACCIO_INSCRIPCIONS, qui)
        )

    try:
        brut = json.loads(text)
    except json.JSONDecodeError:
        afegeix("format", "", None, "JSON invàlid")
        raise ErrorCarrega(tuple(errors)) from None
    if not isinstance(brut, dict):
        afegeix("format", "", None, "ha de ser un objecte")
        raise ErrorCarrega(tuple(errors))
    if "versio_esquema" in brut:
        versio = brut["versio_esquema"]
        if type(versio) is not int or versio != VERSIO_ESQUEMA:
            missatge = f"versió d'esquema no admesa (cal {VERSIO_ESQUEMA})"
            afegeix("format", "versio_esquema", versio, missatge)
            raise ErrorCarrega(tuple(errors))
    try:
        dto = InscripcionsDto.model_validate_json(text)
    except ValidationError as excepcio:
        for e in errors_en_catala(excepcio):
            afegeix("format", e.camp, _valor_a(brut, e.camp), e.missatge)
        raise ErrorCarrega(tuple(errors)) from None

    # RN-012 s'avalua sobre el DTO, independentment dels altres errors (els llista tots)
    vistes: set[str] = set()
    for i, p in enumerate(dto.participacions):
        if p.id_competicio in vistes:
            afegeix(
                "RN-012",
                f"participacions.{i}.id_competicio",
                p.id_competicio,
                f"hi ha més d'una participació a {p.id_competicio!r}",
            )
        vistes.add(p.id_competicio)
    participacions: list[Participacio] = []
    for i, p in enumerate(dto.participacions):
        proves = tuple(
            Inscripcio(Prova(x.prova.distancia, x.prova.estil), x.dia, x.prioritat)
            for x in p.proves
        )
        try:
            participacions.append(Participacio(p.id_competicio, p.classe, proves))
        except ErrorInvariant as excepcio:
            for v in excepcio.violacions:
                afegeix(v.rn, _camp(f"participacions.{i}", v.camp), v.valor, v.missatge)
    if errors:
        raise ErrorCarrega(tuple(errors))
    try:
        return Inscripcions(tuple(participacions))
    except ErrorInvariant as excepcio:
        for v in excepcio.violacions:
            afegeix(v.rn, v.camp, v.valor, v.missatge)
        raise ErrorCarrega(tuple(errors)) from None


def inscripcions_a_dto(inscripcions: Inscripcions) -> InscripcionsDto:
    return InscripcionsDto(
        versio_esquema=VERSIO_ESQUEMA,
        participacions=[
            ParticipacioDto(
                id_competicio=p.id_competicio,
                classe=p.classe,
                proves=[
                    InscripcioDto(
                        prova=ProvaDto(distancia=x.prova.distancia, estil=x.prova.estil),
                        dia=x.dia,
                        prioritat=x.prioritat,
                    )
                    for x in p.proves
                ],
            )
            for p in inscripcions.participacions
        ],
    )


def cataleg_a_dto(cataleg: Cataleg) -> CatalegDto:
    return CatalegDto(
        versio_esquema=VERSIO_ESQUEMA,
        competicions=[
            CompeticioDto(id=c.id, nom=c.nom, dates=list(c.dates), piscina=c.piscina, seu=c.seu)
            for c in cataleg.competicions
        ],
    )


def a_dto(nedador: Nedador) -> NedadorDto:
    return NedadorDto(
        versio_esquema=VERSIO_ESQUEMA,
        correu=None if nedador.correu is None else nedador.correu.valor,
        mobil=nedador.mobil,
        canal_preferent=nedador.canal_preferent,
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
