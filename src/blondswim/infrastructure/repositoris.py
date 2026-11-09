"""Repositoris sobre fitxers JSON."""

from pathlib import Path

from blondswim.domain.cataleg import Cataleg
from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import (
    CatalegAbsent,
    ErrorCarrega,
    ErrorValidacio,
    Identitat,
    carpeta_temporada,
    fitxer_cataleg,
    fitxer_inscripcions,
    fitxer_nedador,
)
from blondswim.domain.valors import CodiTemporada, IdNedador
from blondswim.infrastructure.json_io import escriu
from blondswim.infrastructure.mappers import (
    a_dto,
    cataleg_a_dto,
    inscripcions_a_dto,
    llegeix_cataleg,
    llegeix_identitat,
    llegeix_inscripcions,
    llegeix_nedador,
)


class RepositoriNedadorsJson:
    """`<arrel>/nedadors/<id>/nedador.json`. L'id és el nom de la carpeta (RN-001).

    Inscripcions: `<arrel>/nedadors/<id>/temporades/<AAAA-AA>/inscripcions.json` (RN-031).
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

    def temporades(self, id_nedador: IdNedador) -> list[CodiTemporada]:
        """Les temporades amb `inscripcions.json`. Una carpeta que no segueix RN-031 és un
        ERROR d'aquell nedador (CA-001-43)."""
        carpeta = self._arrel / "nedadors" / str(id_nedador) / "temporades"
        if not carpeta.is_dir():
            return []
        temporades: list[CodiTemporada] = []
        errors: list[ErrorValidacio] = []
        for cami in sorted(p for p in carpeta.iterdir() if p.is_dir()):
            try:
                temporada = CodiTemporada(cami.name)
            except ValueError:
                errors.append(
                    ErrorValidacio(
                        "RN-031",
                        carpeta_temporada(id_nedador, cami.name),
                        "",
                        cami.name,
                        "el nom de la carpeta de temporada ha de ser `AAAA-AA`",
                        "Reanomena la carpeta",
                        str(id_nedador),
                    )
                )
                continue
            if (cami / "inscripcions.json").is_file():
                temporades.append(temporada)
        if errors:
            raise ErrorCarrega(tuple(errors))
        return temporades

    def carrega_inscripcions(self, id_nedador: IdNedador, temporada: CodiTemporada) -> Inscripcions:
        text = (self._arrel / fitxer_inscripcions(id_nedador, temporada)).read_text(
            encoding="utf-8"
        )
        return llegeix_inscripcions(text, id_nedador, temporada, str(id_nedador))

    def desa_inscripcions(
        self, id_nedador: IdNedador, temporada: CodiTemporada, inscripcions: Inscripcions
    ) -> None:
        escriu(
            self._arrel / fitxer_inscripcions(id_nedador, temporada),
            inscripcions_a_dto(inscripcions),
        )


class RepositoriCatalegJson:
    """`<arrel>/competicions/<AAAA-AA>.json` (RN-031). Un ERROR falla TOTA la càrrega."""

    def __init__(self, arrel: Path) -> None:
        self._arrel = arrel

    def _errors_noms(self) -> list[ErrorValidacio]:
        """Un ERROR (RN-031) per cada `.json` de la carpeta el nom del qual no és `AAAA-AA`."""
        carpeta = self._arrel / "competicions"
        if not carpeta.is_dir():
            return []
        errors: list[ErrorValidacio] = []
        for cami in sorted(carpeta.glob("*.json")):
            try:
                CodiTemporada(cami.stem)
            except ValueError:
                errors.append(
                    ErrorValidacio(
                        "RN-031",
                        f"competicions/{cami.name}",
                        "",
                        cami.name,
                        "el nom del fitxer del catàleg ha de ser `AAAA-AA.json`",
                        "Reanomena o treu el fitxer",
                    )
                )
        return errors

    def carrega(self, temporada: CodiTemporada) -> Cataleg:
        errors = self._errors_noms()
        if errors:
            raise ErrorCarrega(tuple(errors))
        cami = self._arrel / fitxer_cataleg(temporada)
        if not cami.is_file():
            # La càrrega del sistema només demana el catàleg si hi ha inscripcions d'aquella
            # temporada (T052): l'absència no impedeix carregar nedadors.
            raise CatalegAbsent(temporada)
        return llegeix_cataleg(cami.read_text(encoding="utf-8"), temporada)

    def desa(self, temporada: CodiTemporada, cataleg: Cataleg) -> None:
        escriu(self._arrel / fitxer_cataleg(temporada), cataleg_a_dto(cataleg))
