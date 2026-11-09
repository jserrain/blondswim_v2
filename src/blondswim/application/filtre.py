"""Filtre de validació: passa per tots els nedadors i no planifica els que tenen un ERROR."""

from dataclasses import dataclass

from blondswim.application.carrega import carrega_nedadors
from blondswim.application.ports import RepositoriCataleg, RepositoriNedadors
from blondswim.domain.cataleg import Cataleg
from blondswim.domain.validacio import Resultat
from blondswim.domain.valors import IdNedador


@dataclass(frozen=True)
class ResultatFiltre:
    resultats: dict[IdNedador, Resultat]
    planificables: tuple[IdNedador, ...]


def filtra(
    repositori: RepositoriNedadors, cataleg: RepositoriCataleg[Cataleg] | None = None
) -> ResultatFiltre:
    """Mateix resultat que la càrrega i que l'entrada (CA-001-78); no s'atura al primer error."""
    carregats = carrega_nedadors(repositori, cataleg)
    return ResultatFiltre(
        resultats=carregats.resultats,
        planificables=tuple(carregats.nedadors),
    )
