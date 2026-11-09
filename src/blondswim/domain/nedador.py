"""Nedador i entitats relacionades (data-model.md)."""

from dataclasses import dataclass, replace
from datetime import date

from blondswim.domain.valors import Alias, Canal, Correu, Dia, Estil, Piscina, Prova, Temps

_PARCIALS_400 = 4
_PARCIALS_200 = 2


@dataclass(frozen=True)
class Violacio:
    """Un invariant violat; `camp` és relatiu a l'entitat."""

    rn: str
    camp: str
    valor: object
    missatge: str


class ErrorInvariant(ValueError):
    """Un o més invariants d'una entitat violats, tots alhora."""

    def __init__(self, violacions: tuple[Violacio, ...]) -> None:
        super().__init__("; ".join(v.missatge for v in violacions))
        self.violacions = violacions


def _verifica(violacions: list[Violacio]) -> None:
    if violacions:
        raise ErrorInvariant(tuple(violacions))


def _repetits[T](valors: tuple[T, ...]) -> list[T]:
    repetits: list[T] = []
    vistos: set[T] = set()
    for valor in valors:
        if valor in vistos and valor not in repetits:
            repetits.append(valor)
        vistos.add(valor)
    return repetits


@dataclass(frozen=True)
class VolumSetmanal:
    """Metres per setmana. El rang és RN-005 i es valida al `Nedador`."""

    min: int
    max: int


@dataclass(frozen=True)
class DetallProva:
    """Tots els camps són informatius."""

    parcials: tuple[Temps, ...] | None = None
    bracades_per_llarg: float | None = None
    sr: float | None = None
    rpe: int | None = None

    def __post_init__(self) -> None:
        violacions: list[Violacio] = []
        for camp in ("bracades_per_llarg", "sr"):
            valor = getattr(self, camp)
            if valor is not None and valor <= 0:
                violacions.append(Violacio("", camp, valor, f"{camp} ha de ser positiu"))
        if self.rpe is not None and not 0 <= self.rpe <= 10:
            violacions.append(Violacio("", "rpe", self.rpe, "rpe ha de ser un enter de 0 a 10"))
        _verifica(violacions)


@dataclass(frozen=True)
class TestCss:
    data: date
    piscina: Piscina
    t400: Temps
    t200: Temps
    acceptat: bool
    detall_400: DetallProva | None = None
    detall_200: DetallProva | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        violacions: list[Violacio] = []
        if self.t400 <= self.t200:
            violacions.append(
                Violacio(
                    "RN-006",
                    "t400",
                    str(self.t400),
                    f"t400 ({self.t400}) ha de ser superior a t200 ({self.t200})",
                )
            )
        for camp, detall, esperats in (
            ("detall_400", self.detall_400, _PARCIALS_400),
            ("detall_200", self.detall_200, _PARCIALS_200),
        ):
            if detall is None or detall.parcials is None:
                continue
            if len(detall.parcials) != esperats:
                violacions.append(
                    Violacio(
                        "",
                        f"{camp}.parcials",
                        len(detall.parcials),
                        f"{camp} ha de tenir {esperats} parcials",
                    )
                )
        _verifica(violacions)


@dataclass(frozen=True)
class MillorRegistre:
    """Una millora de la marca d'una prova i piscina (RN-007); la prova és oficial (RN-030).

    `competicio` és el nom de la competició, informatiu i sense catàleg.
    """

    estil: Estil
    distancia: int
    piscina: Piscina
    temps: Temps
    data: date
    competicio: str

    @property
    def prova(self) -> Prova:
        return Prova(self.distancia, self.estil)

    @property
    def descripcio(self) -> str:
        return f"{self.distancia} {self.estil.value} a piscina de {self.piscina.value} m"


@dataclass(frozen=True)
class Nedador:
    """L'id no hi és: és el nom de la carpeta (RN-001).

    `correu` és opcional (RN-032); `mobil` és obligatori, però el pot deixar buit un fitxer
    editat a mà: ho comprova el validador. `canal_preferent` absent és un avís (RN-035).
    """

    correu: Correu | None
    mobil: str
    canal_preferent: Canal | None
    arxivat: bool
    estils_preferents: tuple[Estil, ...]
    dies_entrenament: tuple[Dia, ...]
    volum_setmanal: VolumSetmanal
    tests_css: tuple[TestCss, ...]
    millors_registres: tuple[MillorRegistre, ...]
    alias: Alias | None = None

    def __post_init__(self) -> None:
        violacions: list[Violacio] = []
        for camp, valors in (
            ("estils_preferents", self.estils_preferents),
            ("dies_entrenament", self.dies_entrenament),
        ):
            if not valors:
                violacions.append(Violacio("", camp, [], f"{camp} ha de tenir almenys un valor"))
            violacions.extend(
                Violacio("", camp, repetit.value, f"{camp}: valor repetit ({repetit.value})")
                for repetit in _repetits(valors)
            )
        volum = self.volum_setmanal
        if not 0 < volum.min <= volum.max:
            violacions.append(
                Violacio(
                    "RN-005",
                    "volum_setmanal",
                    {"min": volum.min, "max": volum.max},
                    "el volum setmanal ha de complir 0 < min ≤ max",
                )
            )
        _verifica(violacions)


class _SenseCanvi:
    """Valor de `CanviNedador.correu` quan el correu no canvia (`None` el treu)."""

    def __repr__(self) -> str:
        return "SENSE_CANVI"


SENSE_CANVI = _SenseCanvi()


@dataclass(frozen=True)
class CanviNedador:
    """Camps modificables (RN-002, RN-003: l'id i l'alias no canvien mai).

    Un camp a `None` no canvia; l'excepció és `correu`, on `None` el treu i
    `SENSE_CANVI` el deixa com és (RN-032). Cap camp de la resta no pot ser `None`.
    """

    correu: Correu | _SenseCanvi | None = SENSE_CANVI
    mobil: str | None = None
    canal_preferent: Canal | None = None
    estils_preferents: tuple[Estil, ...] | None = None
    dies_entrenament: tuple[Dia, ...] | None = None
    volum_setmanal: VolumSetmanal | None = None

    def aplica(self, nedador: Nedador) -> Nedador:
        """El nedador amb el canvi aplicat; `ErrorInvariant` si en trenca un invariant."""
        canvis: dict[str, object] = {
            camp: valor
            for camp in (
                "mobil",
                "canal_preferent",
                "estils_preferents",
                "dies_entrenament",
                "volum_setmanal",
            )
            if (valor := getattr(self, camp)) is not None
        }
        if not isinstance(self.correu, _SenseCanvi):
            canvis["correu"] = self.correu
        return replace(nedador, **canvis)  # type: ignore[arg-type]


def _vigent(
    registres: tuple[MillorRegistre, ...], prova: Prova, piscina: Piscina
) -> MillorRegistre | None:
    for registre in reversed(registres):
        if registre.prova == prova and registre.piscina is piscina:
            return registre
    return None


def marca_vigent(nedador: Nedador, prova: Prova, piscina: Piscina) -> MillorRegistre | None:
    """L'última marca de la llista per a la prova i la piscina (RN-007); no es desa."""
    return _vigent(nedador.millors_registres, prova, piscina)


def afegeix_registre(
    registres: tuple[MillorRegistre, ...], nou: MillorRegistre
) -> tuple[MillorRegistre, ...]:
    """RN-007: afegeix `nou` si és millor que la marca vigent de la prova i la piscina.

    Un temps igual o pitjor no fa res (torna la llista sense canvis). Un temps millor amb
    una data no posterior a la de la vigent és un `ErrorInvariant`. Les piscines no es comparen.
    """
    vigent = _vigent(registres, nou.prova, nou.piscina)
    if vigent is None:
        return (*registres, nou)
    if nou.temps >= vigent.temps:
        return registres
    if nou.data <= vigent.data:
        missatge = (
            f"la data de la marca ({nou.data}) ha de ser posterior a la de la vigent "
            f"({vigent.data}): {nou.descripcio}"
        )
        camp = f"millors_registres.{len(registres)}"
        raise ErrorInvariant((Violacio("RN-007", camp, nou.descripcio, missatge),))
    return (*registres, nou)
