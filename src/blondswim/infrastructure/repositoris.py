"""Repositoris sobre fitxers JSON."""

from pathlib import Path

from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import ErrorCarrega, ErrorValidacio
from blondswim.domain.valors import IdNedador
from blondswim.infrastructure.json_io import escriu
from blondswim.infrastructure.mappers import a_dto, llegeix_nedador


class RepositoriNedadorsJson:
    """`<arrel>/nedadors/<id>/nedador.json`. L'id és el nom de la carpeta (RN-001).

    `carrega_inscripcions` del port arriba amb la US3 (T024).
    """

    def __init__(self, arrel: Path) -> None:
        self._arrel = arrel

    def ids(self) -> list[IdNedador]:
        carpeta = self._arrel / "nedadors"
        if not carpeta.is_dir():
            return []
        ids: list[IdNedador] = []
        errors: list[ErrorValidacio] = []
        for cami in sorted(p for p in carpeta.iterdir() if p.is_dir()):
            try:
                ids.append(IdNedador(cami.name))
            except ValueError:
                errors.append(
                    ErrorValidacio(
                        "RN-001",
                        f"nedadors/{cami.name}",
                        "",
                        cami.name,
                        "el nom de la carpeta ha de ser n + 4 dígits",
                    )
                )
        if errors:
            raise ErrorCarrega(tuple(errors))
        return ids

    def carrega(self, id_nedador: IdNedador) -> Nedador:
        fitxer = self._fitxer(id_nedador)
        return llegeix_nedador((self._arrel / fitxer).read_text(encoding="utf-8"), fitxer)

    def desa(self, id_nedador: IdNedador, nedador: Nedador) -> None:
        escriu(self._arrel / self._fitxer(id_nedador), a_dto(nedador))

    @staticmethod
    def _fitxer(id_nedador: IdNedador) -> str:
        return f"nedadors/{id_nedador}/nedador.json"
