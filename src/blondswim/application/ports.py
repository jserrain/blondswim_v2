"""Ports de l'aplicació (Protocols)."""

from datetime import datetime
from typing import Protocol

from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import Avis, Identitat
from blondswim.domain.valors import CodiTemporada, IdNedador


class RepositoriNedadors(Protocol):
    """Nedadors i les seves inscripcions per temporada."""

    def ids(self) -> list[IdNedador]: ...

    def carrega(self, id_nedador: IdNedador) -> Nedador: ...

    def identitats(self) -> dict[IdNedador, Identitat]:
        """Correu i alias dels fitxers llegibles, valguin o no (D1)."""
        ...

    def desa(self, id_nedador: IdNedador, nedador: Nedador) -> None: ...

    def temporades(self, id_nedador: IdNedador) -> list[CodiTemporada]:
        """Les temporades amb inscripcions; `ErrorCarrega` si una carpeta incompleix RN-031."""
        ...

    def carrega_inscripcions(
        self, id_nedador: IdNedador, temporada: CodiTemporada
    ) -> Inscripcions: ...

    def desa_inscripcions(
        self, id_nedador: IdNedador, temporada: CodiTemporada, inscripcions: Inscripcions
    ) -> None: ...


class RepositoriCataleg[C](Protocol):
    """`C`: `Cataleg` d'una temporada."""

    def carrega(self, temporada: CodiTemporada) -> C: ...

    def desa(self, temporada: CodiTemporada, cataleg: C) -> None: ...


class GeneradorId(Protocol):
    """Genera ids de nedador nous (D2)."""

    def nou(self) -> IdNedador: ...


class RegistreAvisos(Protocol):
    """`decisio`: `confirmat` o `rebutjat` a l'entrada (spec 002); `None` a la càrrega i a la
    planificació."""

    def afegeix(
        self,
        data_hora: datetime,
        avis: Avis,
        id_nedador: IdNedador | None,
        decisio: str | None = None,
    ) -> None: ...


class Rellotge(Protocol):
    def ara(self) -> datetime: ...
