"""Càrrega de nedadors, inscripcions i catàleg.

Un ERROR d'un fitxer del nedador (també les inscripcions) exclou només aquell nedador
(CA-001-19, 60, 65, 66); un ERROR del catàleg fa fallar TOTA la càrrega (CA-001-11, 17, 41, 71).
"""

from collections.abc import Mapping
from dataclasses import dataclass, field, replace

from blondswim.application.ports import RepositoriCataleg, RepositoriNedadors
from blondswim.domain.cataleg import Cataleg
from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import (
    Avis,
    CatalegAbsent,
    ErrorCarrega,
    ErrorValidacio,
    Identitat,
    Resultat,
    fitxer_nedador,
    valida_cataleg,
    valida_inscripcions,
    valida_nedador,
    valida_unicitat,
)
from blondswim.domain.valors import CodiTemporada, IdNedador


@dataclass(frozen=True)
class ResultatCarrega:
    """`nedadors`: només els que no tenen cap ERROR. `resultats`: tots els llegits.

    `inscripcions`: les dels nedadors carregats, per temporada. `avisos_cataleg`: RN-009.
    """

    nedadors: dict[IdNedador, Nedador]
    resultats: dict[IdNedador, Resultat]
    inscripcions: dict[IdNedador, dict[CodiTemporada, Inscripcions]] = field(default_factory=dict)
    avisos_cataleg: tuple[Avis, ...] = ()


class _Catalegs:
    """Cada catàleg es demana una sola vegada, i només si cal. Un ERROR del catàleg es propaga
    (TOTA la càrrega falla); l'absència es recorda i la tracta qui el demana."""

    def __init__(self, repositori: RepositoriCataleg[Cataleg] | None) -> None:
        self._repositori = repositori
        self._carregats: dict[CodiTemporada, Cataleg | CatalegAbsent] = {}
        self.avisos: list[Avis] = []

    def de(self, temporada: CodiTemporada) -> Cataleg:
        if temporada not in self._carregats:
            if self._repositori is None:
                self._carregats[temporada] = CatalegAbsent(temporada)
            else:
                try:
                    cataleg = self._repositori.carrega(temporada)
                except CatalegAbsent as absent:
                    self._carregats[temporada] = absent
                else:
                    self._carregats[temporada] = cataleg
                    self.avisos.extend(valida_cataleg(temporada, cataleg).avisos)
        carregat = self._carregats[temporada]
        if isinstance(carregat, CatalegAbsent):
            raise carregat
        return carregat


def _carrega_inscripcions(
    repositori: RepositoriNedadors, catalegs: _Catalegs, id_nedador: IdNedador, qui: str
) -> tuple[dict[CodiTemporada, Inscripcions], tuple[ErrorValidacio, ...]]:
    """Les inscripcions validades del nedador; els errors l'exclouen (no els del catàleg)."""
    try:
        temporades = repositori.temporades(id_nedador)
    except ErrorCarrega as excepcio:
        return {}, excepcio.errors
    totes: dict[CodiTemporada, Inscripcions] = {}
    errors: list[ErrorValidacio] = []
    for temporada in temporades:
        try:
            inscripcions = repositori.carrega_inscripcions(id_nedador, temporada)
        except ErrorCarrega as excepcio:
            errors.extend(replace(e, nedador=qui) for e in excepcio.errors)
            continue
        try:
            cataleg = catalegs.de(temporada)
        except CatalegAbsent as absent:
            errors.extend(replace(e, nedador=qui) for e in absent.errors)
            continue
        errors.extend(valida_inscripcions(id_nedador, qui, temporada, inscripcions, cataleg).errors)
        totes[temporada] = inscripcions
    return totes, tuple(errors)


def errors_d_unicitat(
    identitats: Mapping[IdNedador, Identitat], id_nedador: IdNedador
) -> tuple[ErrorValidacio, ...]:
    """Les col·lisions (RN-003, RN-032) en què participa `id_nedador`, a nom seu."""
    qui = identitats[id_nedador].alias or str(id_nedador)
    return tuple(
        replace(error, fitxer=fitxer_nedador(id_nedador), nedador=qui)
        for error in valida_unicitat(identitats)
        if id_nedador in error.implicats
    )


def carrega_nedadors(
    repositori: RepositoriNedadors, cataleg: RepositoriCataleg[Cataleg] | None = None
) -> ResultatCarrega:
    """Valida tots els nedadors, la unicitat i les inscripcions contra el catàleg.

    Una col·lisió exclou tots els implicats. Un ERROR del catàleg llança `ErrorCarrega`.
    """
    identitats = repositori.identitats()
    catalegs = _Catalegs(cataleg)
    nedadors: dict[IdNedador, Nedador] = {}
    resultats: dict[IdNedador, Resultat] = {}
    inscripcions: dict[IdNedador, dict[CodiTemporada, Inscripcions]] = {}
    for id_nedador in repositori.ids():
        try:
            nedador = repositori.carrega(id_nedador)
        except ErrorCarrega as excepcio:
            resultats[id_nedador] = Resultat(errors=excepcio.errors)
            continue
        propi = valida_nedador(id_nedador, nedador)
        col_lisions = errors_d_unicitat(identitats, id_nedador) if id_nedador in identitats else ()
        qui = str(nedador.alias) if nedador.alias is not None else str(id_nedador)
        de_temporada, errors_inscripcions = _carrega_inscripcions(
            repositori, catalegs, id_nedador, qui
        )
        resultat = replace(propi, errors=(*propi.errors, *col_lisions, *errors_inscripcions))
        resultats[id_nedador] = resultat
        if resultat.es_valid:
            nedadors[id_nedador] = nedador
            inscripcions[id_nedador] = de_temporada
    return ResultatCarrega(
        nedadors=nedadors,
        resultats=resultats,
        inscripcions=inscripcions,
        avisos_cataleg=tuple(catalegs.avisos),
    )
