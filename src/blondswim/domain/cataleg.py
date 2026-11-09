"""Competició i catàleg de la temporada (data-model.md)."""

from dataclasses import dataclass
from datetime import date

from blondswim.domain.nedador import ErrorInvariant, Violacio
from blondswim.domain.valors import Piscina


@dataclass(frozen=True)
class Competicio:
    """`seu` és opcional amb avís (RN-009); l'avís el dona el validador."""

    id: str
    nom: str
    dates: tuple[date, ...]
    piscina: Piscina
    seu: str | None = None

    def __post_init__(self) -> None:
        if not self.dates:
            raise ErrorInvariant(
                (Violacio("", "dates", self.dates, "la competició ha de tenir una data o més"),)
            )


@dataclass(frozen=True)
class Cataleg:
    """Les competicions d'una temporada. RN-008: l'id és únic."""

    competicions: tuple[Competicio, ...]

    def __post_init__(self) -> None:
        vistos: set[str] = set()
        violacions: list[Violacio] = []
        for i, competicio in enumerate(self.competicions):
            if competicio.id in vistos:
                violacions.append(
                    Violacio(
                        "RN-008",
                        f"competicions.{i}.id",
                        competicio.id,
                        f"l'id de competició {competicio.id!r} és repetit",
                    )
                )
            vistos.add(competicio.id)
        if violacions:
            raise ErrorInvariant(tuple(violacions))

    def competicio(self, id_competicio: str) -> Competicio | None:
        """La competició amb aquest id, o `None` si no és al catàleg (RN-011)."""
        return next((c for c in self.competicions if c.id == id_competicio), None)
