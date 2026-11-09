"""Ajuts dels tests unitaris: constants, constructors i dobles en memòria."""

from collections.abc import Sequence
from dataclasses import replace
from datetime import date

from blondswim.application.ports import RepositoriCataleg, RepositoriNedadors
from blondswim.domain.cataleg import Cataleg, Competicio
from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.nedador import MillorRegistre, Nedador, VolumSetmanal
from blondswim.domain.nedador import TestCss as CssTest
from blondswim.domain.validacio import CatalegAbsent, ErrorCarrega, ErrorValidacio, Identitat
from blondswim.domain.valors import (
    Alias,
    Canal,
    CodiTemporada,
    Correu,
    Dia,
    Estil,
    IdNedador,
    Piscina,
    Temps,
)

# UUID v4 fictius. ID_X comparteix els 7 primers caràcters amb ID_A (sufix d'alias igual).
ID_A = IdNedador("3f2a9c1e-7b4d-4e8a-9c2f-1d6b5e0a8f47")
ID_B = IdNedador("9b1c2d3e-4f5a-4b6c-8d7e-0a1b2c3d4e5f")
ID_C = IdNedador("a1b2c3d4-e5f6-4a7b-9c8d-1e2f3a4b5c6d")
ID_X = IdNedador("3f2a9c1f-0000-4000-8000-000000000000")

ALIAS_A = Alias("exemple_3f2a9c1")
ALIAS_B = Alias("altre_9b1c2d3")
ALIAS_C = Alias("tercer_a1b2c3d")


def temps(text: str) -> Temps:
    return Temps.de_text(text)


def un_test(**canvis: object) -> CssTest:
    base = CssTest(
        data=date(2000, 1, 15),
        piscina=Piscina.CURTA,
        t400=temps("6:30.00"),
        t200=temps("3:10.00"),
        acceptat=True,
    )
    return replace(base, **canvis)


def registre(**canvis: object) -> MillorRegistre:
    base = MillorRegistre(
        estil=Estil.CR,
        distancia=100,
        piscina=Piscina.CURTA,
        temps=temps("1:15.00"),
        data=date(2000, 2, 1),
        competicio="Exemple",
    )
    return replace(base, **canvis)


def competicio(**canvis: object) -> Competicio:
    base = Competicio(
        id="c001",
        nom="Exemple",
        dates=(date(2000, 3, 4), date(2000, 3, 5)),
        piscina=Piscina.CURTA,
        seu="Seu exemple",
    )
    return replace(base, **canvis)


def nedador(**canvis: object) -> Nedador:
    base = Nedador(
        correu=Correu("nedador@example.com"),
        mobil="+34600000000",
        canal_preferent=Canal.CORREU,
        arxivat=False,
        estils_preferents=(Estil.CR, Estil.EI),
        dies_entrenament=(Dia.DL, Dia.DC, Dia.DV),
        volum_setmanal=VolumSetmanal(min=8000, max=12000),
        tests_css=(un_test(),),
        millors_registres=(registre(),),
        alias=ALIAS_A,
    )
    return replace(base, **canvis)


class RepositoriMemoria:
    """`RepositoriNedadors` en memòria. Un fitxer il·legible porta els errors de `carrega`."""

    def __init__(self) -> None:
        self.nedadors: dict[IdNedador, Nedador] = {}
        self.il_legibles: dict[IdNedador, tuple[ErrorValidacio, ...]] = {}
        self.inscripcions: dict[tuple[IdNedador, CodiTemporada], Inscripcions] = {}
        self.inscripcions_il_legibles: dict[
            tuple[IdNedador, CodiTemporada], tuple[ErrorValidacio, ...]
        ] = {}

    def semina(self, id_nedador: IdNedador, nedador: Nedador) -> None:
        self.nedadors[id_nedador] = nedador

    def semina_il_legible(self, id_nedador: IdNedador, errors: tuple[ErrorValidacio, ...]) -> None:
        self.il_legibles[id_nedador] = errors

    def ids(self) -> list[IdNedador]:
        return sorted({*self.nedadors, *self.il_legibles}, key=lambda i: i.valor)

    def carrega(self, id_nedador: IdNedador) -> Nedador:
        if id_nedador in self.il_legibles:
            raise ErrorCarrega(self.il_legibles[id_nedador])
        return self.nedadors[id_nedador]

    def identitats(self) -> dict[IdNedador, Identitat]:
        return {i: Identitat.de(n) for i, n in self.nedadors.items()}

    def desa(self, id_nedador: IdNedador, nedador: Nedador) -> None:
        self.nedadors[id_nedador] = nedador

    def semina_inscripcions(
        self, id_nedador: IdNedador, temporada: CodiTemporada, inscripcions: Inscripcions
    ) -> None:
        self.inscripcions[(id_nedador, temporada)] = inscripcions

    def semina_inscripcions_il_legibles(
        self, id_nedador: IdNedador, temporada: CodiTemporada, errors: tuple[ErrorValidacio, ...]
    ) -> None:
        self.inscripcions_il_legibles[(id_nedador, temporada)] = errors

    def temporades(self, id_nedador: IdNedador) -> list[CodiTemporada]:
        claus = {*self.inscripcions, *self.inscripcions_il_legibles}
        return sorted({t for i, t in claus if i == id_nedador}, key=lambda t: t.valor)

    def carrega_inscripcions(self, id_nedador: IdNedador, temporada: CodiTemporada) -> Inscripcions:
        if (id_nedador, temporada) in self.inscripcions_il_legibles:
            raise ErrorCarrega(self.inscripcions_il_legibles[(id_nedador, temporada)])
        return self.inscripcions[(id_nedador, temporada)]

    def desa_inscripcions(
        self, id_nedador: IdNedador, temporada: CodiTemporada, inscripcions: Inscripcions
    ) -> None:
        self.inscripcions[(id_nedador, temporada)] = inscripcions


def com_a_port(repositori: RepositoriMemoria) -> RepositoriNedadors:
    return repositori


class CatalegMemoria:
    """`RepositoriCataleg` en memòria. Una temporada sense catàleg dona `CatalegAbsent`."""

    def __init__(self) -> None:
        self.catalegs: dict[CodiTemporada, Cataleg] = {}
        self.il_legibles: dict[CodiTemporada, tuple[ErrorValidacio, ...]] = {}
        self.demanats: list[CodiTemporada] = []

    def carrega(self, temporada: CodiTemporada) -> Cataleg:
        self.demanats.append(temporada)
        if temporada in self.il_legibles:
            raise ErrorCarrega(self.il_legibles[temporada])
        if temporada not in self.catalegs:
            raise CatalegAbsent(temporada)
        return self.catalegs[temporada]

    def desa(self, temporada: CodiTemporada, cataleg: Cataleg) -> None:
        self.catalegs[temporada] = cataleg


def cataleg_com_a_port(repositori: CatalegMemoria) -> RepositoriCataleg[Cataleg]:
    return repositori


class GeneradorFix:
    """`GeneradorId` que torna els ids donats, en ordre (D2)."""

    def __init__(self, ids: Sequence[IdNedador]) -> None:
        self._ids = list(ids)
        self.demanats = 0

    def nou(self) -> IdNedador:
        self.demanats += 1
        return self._ids.pop(0)


def error_il_legible(id_nedador: IdNedador, camp: str = "", valor: object = None) -> ErrorValidacio:
    return ErrorValidacio(
        rn="format",
        fitxer=f"nedadors/{id_nedador}/nedador.json",
        camp=camp,
        valor=valor,
        missatge="fitxer no vàlid",
        accio="Corregeix el fitxer",
        nedador=str(id_nedador),
    )
