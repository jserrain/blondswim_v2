"""Ports de l'aplicació (Protocols)."""

from datetime import datetime
from typing import Protocol

from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import Avis, ErrorValidacio, Identitat
from blondswim.domain.valors import CodiTemporada, IdNedador


class RepositoriNedadors(Protocol):
    """Nedadors i les seves inscripcions per temporada."""

    def ids(self) -> list[IdNedador]: ...

    def errors_carpetes(self) -> list[ErrorValidacio]:
        """Carpetes de nedador amb un nom que no és un UUID v4 (RN-001)."""
        ...

    def carrega(self, id_nedador: IdNedador) -> Nedador: ...

    def identitats(self) -> dict[IdNedador, Identitat]:
        """Correu i alias dels fitxers llegibles, valguin o no (D1)."""
        ...

    def desa(self, id_nedador: IdNedador, nedador: Nedador) -> None: ...

    def temporades(self, id_nedador: IdNedador) -> list[CodiTemporada]:
        """Les temporades vàlides amb inscripcions."""
        ...

    def errors_temporades(self, id_nedador: IdNedador) -> list[ErrorValidacio]:
        """Carpetes de temporada que no segueixen RN-031."""
        ...

    def carrega_inscripcions(
        self, id_nedador: IdNedador, temporada: CodiTemporada
    ) -> Inscripcions: ...

    def desa_inscripcions(
        self, id_nedador: IdNedador, temporada: CodiTemporada, inscripcions: Inscripcions
    ) -> None: ...


class RepositoriCataleg[C](Protocol):
    """`C`: `Cataleg` d'una temporada."""

    def temporades(self) -> list[CodiTemporada]:
        """Totes les temporades amb catàleg; `ErrorCarrega` si un nom incompleix RN-031."""
        ...

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
