"""Nedador i entitats relacionades (data-model.md)."""

from dataclasses import dataclass
from datetime import date

from blondswim.domain.valors import Alias, Correu, Dia, Estil, Piscina, Prova, Temps

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
    """Únic per (estil, distància, piscina) (RN-007); la prova és oficial (RN-030)."""

    estil: Estil
    distancia: int
    piscina: Piscina
    temps: Temps
    data: date
    competicio: str

    @property
    def prova(self) -> Prova:
        return Prova(self.distancia, self.estil)


@dataclass(frozen=True)
class Nedador:
    """L'id no hi és: és el nom de la carpeta (RN-001)."""

    correu: Correu
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
