"""Ports de l'aplicació (Protocols). Les entitats són paràmetres de tipus fins que existeixin."""

from datetime import datetime
from typing import Protocol

from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import Avis, Identitat
from blondswim.domain.valors import CodiTemporada, IdNedador


class RepositoriNedadors[I](Protocol):
    """`I`: inscripcions d'una temporada."""

    def ids(self) -> list[IdNedador]: ...

    def carrega(self, id_nedador: IdNedador) -> Nedador: ...

    def identitats(self) -> dict[IdNedador, Identitat]:
        """Correu i alias dels fitxers llegibles, valguin o no (D1)."""
        ...

    def desa(self, id_nedador: IdNedador, nedador: Nedador) -> None: ...

    def carrega_inscripcions(self, id_nedador: IdNedador, temporada: CodiTemporada) -> I: ...


class RepositoriCataleg[C](Protocol):
    """`C`: `Cataleg` d'una temporada."""

    def carrega(self, temporada: CodiTemporada) -> C: ...

    def desa(self, temporada: CodiTemporada, cataleg: C) -> None: ...


class GeneradorId(Protocol):
    """Genera ids de nedador nous (D2)."""

    def nou(self) -> IdNedador: ...


class RegistreAvisos(Protocol):
    def afegeix(self, data_hora: datetime, avis: Avis, id_nedador: IdNedador | None) -> None: ...


class Rellotge(Protocol):
    def ara(self) -> datetime: ...
