"""Inscripcions d'un nedador en una temporada (data-model.md).

Invariants propis: RN-012, RN-014 i RN-016. La validació creuada amb el catàleg i la temporada
(RN-011, RN-013, RN-015, RN-030) és a `validacio.valida_inscripcions`.
"""

from dataclasses import dataclass
from datetime import date

from blondswim.domain.nedador import ErrorInvariant, Violacio
from blondswim.domain.valors import Classe, Prioritat, Prova


@dataclass(frozen=True)
class Inscripcio:
    prova: Prova
    dia: date
    prioritat: Prioritat


@dataclass(frozen=True)
class Participacio:
    """La participació d'un nedador en una competició del catàleg."""

    id_competicio: str
    classe: Classe
    proves: tuple[Inscripcio, ...]

    def __post_init__(self) -> None:
        violacions: list[Violacio] = []
        if not self.proves:
            violacions.append(
                Violacio(
                    "RN-014",
                    "proves",
                    [],
                    f"la participació a {self.id_competicio!r} no té cap inscripció",
                )
            )
        vistes: set[Prova] = set()
        for i, inscripcio in enumerate(self.proves):
            if inscripcio.prova in vistes:
                prova = f"{inscripcio.prova.distancia} {inscripcio.prova.estil.value}"
                violacions.append(
                    Violacio(
                        "RN-016",
                        f"proves.{i}.prova",
                        prova,
                        f"la prova {prova} és inscrita més d'una vegada a {self.id_competicio!r}",
                    )
                )
            vistes.add(inscripcio.prova)
        if violacions:
            raise ErrorInvariant(tuple(violacions))


@dataclass(frozen=True)
class Inscripcions:
    participacions: tuple[Participacio, ...]

    def __post_init__(self) -> None:
        vistes: set[str] = set()
        violacions: list[Violacio] = []
        for i, participacio in enumerate(self.participacions):
            if participacio.id_competicio in vistes:
                violacions.append(
                    Violacio(
                        "RN-012",
                        f"participacions.{i}.id_competicio",
                        participacio.id_competicio,
                        f"hi ha més d'una participació a {participacio.id_competicio!r}",
                    )
                )
            vistes.add(participacio.id_competicio)
        if violacions:
            raise ErrorInvariant(tuple(violacions))
