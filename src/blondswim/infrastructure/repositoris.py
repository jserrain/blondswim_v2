"""Repositoris sobre fitxers JSON."""

from pathlib import Path

from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import ErrorValidacio, Identitat, fitxer_nedador
from blondswim.domain.valors import IdNedador
from blondswim.infrastructure.json_io import escriu
from blondswim.infrastructure.mappers import a_dto, llegeix_identitat, llegeix_nedador


class RepositoriNedadorsJson:
    """`<arrel>/nedadors/<id>/nedador.json`. L'id és el nom de la carpeta (RN-001).

    `carrega_inscripcions` del port arriba amb la US3 (T024).
    """

    def __init__(self, arrel: Path) -> None:
        self._arrel = arrel

    def _carpetes(self) -> list[Path]:
        carpeta = self._arrel / "nedadors"
        if not carpeta.is_dir():
            return []
        return sorted(p for p in carpeta.iterdir() if p.is_dir())

    def ids(self) -> list[IdNedador]:
        """Les carpetes amb un nom vàlid (RN-001); les altres són a `errors_carpetes`."""
        ids: list[IdNedador] = []
        for cami in self._carpetes():
            try:
                ids.append(IdNedador(cami.name))
            except ValueError:
                continue
        return ids

    def errors_carpetes(self) -> list[ErrorValidacio]:
        """Un ERROR (RN-001) per cada carpeta el nom de la qual no és un UUID v4."""
        errors: list[ErrorValidacio] = []
        for cami in self._carpetes():
            try:
                IdNedador(cami.name)
            except ValueError:
                errors.append(
                    ErrorValidacio(
                        "RN-001",
                        f"nedadors/{cami.name}",
                        "",
                        cami.name,
                        "el nom de la carpeta ha de ser un UUID v4 en minúscules",
                        "Reanomena o treu la carpeta",
                        cami.name,
                    )
                )
        return errors

    def carrega(self, id_nedador: IdNedador) -> Nedador:
        return llegeix_nedador(self._llegeix(id_nedador), id_nedador)

    def identitats(self) -> dict[IdNedador, Identitat]:
        """Correu i alias dels fitxers llegibles; un fitxer il·legible no hi és (D1)."""
        identitats: dict[IdNedador, Identitat] = {}
        for id_nedador in self.ids():
            cami = self._arrel / fitxer_nedador(id_nedador)
            if not cami.is_file():
                continue
            identitat = llegeix_identitat(cami.read_text(encoding="utf-8"))
            if identitat is not None:
                identitats[id_nedador] = identitat
        return identitats

    def desa(self, id_nedador: IdNedador, nedador: Nedador) -> None:
        escriu(self._arrel / fitxer_nedador(id_nedador), a_dto(nedador))

    def _llegeix(self, id_nedador: IdNedador) -> str:
        return (self._arrel / fitxer_nedador(id_nedador)).read_text(encoding="utf-8")
