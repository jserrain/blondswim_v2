"""Ports de l'aplicació (Protocols). Les entitats són paràmetres de tipus fins que existeixin."""

from datetime import datetime
from typing import Protocol

from blondswim.domain.validacio import Avis
from blondswim.domain.valors import CodiTemporada, IdNedador


class RepositoriNedadors[N, I](Protocol):
    """`N`: `Nedador`; `I`: inscripcions d'una temporada."""

    def ids(self) -> list[IdNedador]: ...

    def carrega(self, id_nedador: IdNedador) -> N: ...

    def desa(self, id_nedador: IdNedador, nedador: N) -> None: ...

    def carrega_inscripcions(self, id_nedador: IdNedador, temporada: CodiTemporada) -> I: ...


class RepositoriCataleg[C](Protocol):
    """`C`: `Cataleg` d'una temporada."""

    def carrega(self, temporada: CodiTemporada) -> C: ...

    def desa(self, temporada: CodiTemporada, cataleg: C) -> None: ...


class RegistreAvisos(Protocol):
    def afegeix(self, data_hora: datetime, avis: Avis, id_nedador: IdNedador | None) -> None: ...


class Rellotge(Protocol):
    def ara(self) -> datetime: ...
