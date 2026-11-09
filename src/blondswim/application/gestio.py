"""Operacions de gestió (CA-001-21, 25, 30, 37, 45, 52, 53, 61, 62, 70, 79 a 83, 89, 90, 102, 108).

Cap operació d'edició d'un test o d'un registre desat: només se n'afegeixen (CA-001-82, 83).
Un ERROR no es desa; un AVÍS no bloqueja.
"""

from dataclasses import dataclass, replace
from datetime import date

from blondswim.application.carrega import errors_d_unicitat
from blondswim.application.ports import GeneradorId, RepositoriCataleg, RepositoriNedadors
from blondswim.domain.cataleg import Cataleg
from blondswim.domain.nedador import (
    CanviNedador,
    ErrorInvariant,
    MillorRegistre,
    Nedador,
    TestCss,
    VolumSetmanal,
    afegeix_registre,
)
from blondswim.domain.validacio import (
    ErrorCarrega,
    ErrorValidacio,
    Identitat,
    Resultat,
    fitxer_cataleg,
    fitxer_nedador,
    valida_nedador,
)
from blondswim.domain.valors import (
    Alias,
    Canal,
    CodiTemporada,
    Correu,
    Dia,
    Estil,
    IdNedador,
    Piscina,
)

_ACCIO = "Corregeix el valor i torna-ho a provar"


@dataclass(frozen=True)
class NouNedador:
    """Les dades de l'alta. L'id i l'alias els genera el sistema (RN-002, RN-003)."""

    part_alias: str
    correu: Correu | None
    mobil: str
    canal_preferent: Canal | None
    estils_preferents: tuple[Estil, ...]
    dies_entrenament: tuple[Dia, ...]
    volum_setmanal: VolumSetmanal


@dataclass(frozen=True)
class ResultatOperacio:
    """`nedador`: el que s'ha validat (`None` si no s'ha pogut construir)."""

    id_nedador: IdNedador
    resultat: Resultat
    nedador: Nedador | None
    desat: bool


def _fallida(id_nedador: IdNedador, errors: tuple[ErrorValidacio, ...]) -> ResultatOperacio:
    return ResultatOperacio(id_nedador, Resultat(errors=errors), None, False)


def _errors_d_invariant(
    id_nedador: IdNedador, qui: str, excepcio: ErrorInvariant
) -> tuple[ErrorValidacio, ...]:
    return tuple(
        ErrorValidacio(
            v.rn or "format",
            fitxer_nedador(id_nedador),
            v.camp,
            v.valor,
            v.missatge,
            _ACCIO,
            qui,
        )
        for v in excepcio.violacions
    )


def _qui(id_nedador: IdNedador, nedador: Nedador) -> str:
    return str(id_nedador) if nedador.alias is None else str(nedador.alias)


def _valida_i_desa(
    repositori: RepositoriNedadors, id_nedador: IdNedador, nedador: Nedador
) -> ResultatOperacio:
    """El mateix validador que la càrrega: el nedador sencer i la unicitat sobre els llegibles."""
    identitats = dict(repositori.identitats())
    identitats[id_nedador] = Identitat.de(nedador)
    propi = valida_nedador(id_nedador, nedador)
    resultat = replace(propi, errors=(*propi.errors, *errors_d_unicitat(identitats, id_nedador)))
    if resultat.es_valid:
        repositori.desa(id_nedador, nedador)
    return ResultatOperacio(id_nedador, resultat, nedador, resultat.es_valid)


def alta(
    repositori: RepositoriNedadors, generador: GeneradorId, nou: NouNedador
) -> ResultatOperacio:
    """Genera l'id i l'alias; si l'id o l'alias ja existeixen, en genera de nous."""
    existents = set(repositori.ids())
    aliases = {i.alias for i in repositori.identitats().values() if i.alias is not None}
    while True:
        id_nedador = generador.nou()
        if id_nedador in existents:
            continue
        try:
            alias = Alias.genera(nou.part_alias, id_nedador)
        except ValueError as excepcio:
            error = ErrorValidacio(
                "RN-003",
                fitxer_nedador(id_nedador),
                "alias",
                nou.part_alias,
                str(excepcio),
                "Tria una part d'alias de 2 a 12 caràcters [a-z0-9-]",
                str(id_nedador),
            )
            return _fallida(id_nedador, (error,))
        if str(alias) not in aliases:
            break
    qui = str(alias)
    try:
        nedador = Nedador(
            correu=nou.correu,
            mobil=nou.mobil,
            canal_preferent=nou.canal_preferent,
            arxivat=False,
            estils_preferents=nou.estils_preferents,
            dies_entrenament=nou.dies_entrenament,
            volum_setmanal=nou.volum_setmanal,
            tests_css=(),
            millors_registres=(),
            alias=alias,
        )
    except ErrorInvariant as excepcio:
        return _fallida(id_nedador, _errors_d_invariant(id_nedador, qui, excepcio))
    return _valida_i_desa(repositori, id_nedador, nedador)


def _carrega(repositori: RepositoriNedadors, id_nedador: IdNedador) -> Nedador | ResultatOperacio:
    try:
        return repositori.carrega(id_nedador)
    except ErrorCarrega as excepcio:
        return _fallida(id_nedador, excepcio.errors)


def modifica(
    repositori: RepositoriNedadors, id_nedador: IdNedador, canvi: CanviNedador
) -> ResultatOperacio:
    """Valida el nedador sencer; l'id i l'alias no canvien (RN-002, RN-003)."""
    actual = _carrega(repositori, id_nedador)
    if isinstance(actual, ResultatOperacio):
        return actual
    try:
        nou = canvi.aplica(actual)
    except ErrorInvariant as excepcio:
        return _fallida(
            id_nedador, _errors_d_invariant(id_nedador, _qui(id_nedador, actual), excepcio)
        )
    return _valida_i_desa(repositori, id_nedador, nou)


def _canvia_arxivat(
    repositori: RepositoriNedadors, id_nedador: IdNedador, arxivat: bool
) -> ResultatOperacio:
    actual = _carrega(repositori, id_nedador)
    if isinstance(actual, ResultatOperacio):
        return actual
    return _valida_i_desa(repositori, id_nedador, replace(actual, arxivat=arxivat))


def arxiva(repositori: RepositoriNedadors, id_nedador: IdNedador) -> ResultatOperacio:
    """RN-004: un nedador no s'esborra, s'arxiva."""
    return _canvia_arxivat(repositori, id_nedador, True)


def desarxiva(repositori: RepositoriNedadors, id_nedador: IdNedador) -> ResultatOperacio:
    return _canvia_arxivat(repositori, id_nedador, False)


def afegeix_test(
    repositori: RepositoriNedadors, id_nedador: IdNedador, test: TestCss
) -> ResultatOperacio:
    """Els tests es desen tots; un de nou entra amb `acceptat: false` (CA-001-82)."""
    actual = _carrega(repositori, id_nedador)
    if isinstance(actual, ResultatOperacio):
        return actual
    try:
        nou = replace(actual, tests_css=(*actual.tests_css, replace(test, acceptat=False)))
    except ErrorInvariant as excepcio:
        qui = _qui(id_nedador, actual)
        return _fallida(id_nedador, _errors_d_invariant(id_nedador, qui, excepcio))
    return _valida_i_desa(repositori, id_nedador, nou)


def afegeix_millor_registre(
    repositori: RepositoriNedadors, id_nedador: IdNedador, registre: MillorRegistre
) -> ResultatOperacio:
    """RN-007: s'afegeix només si millora la marca vigent; igual o pitjor no fa res."""
    actual = _carrega(repositori, id_nedador)
    if isinstance(actual, ResultatOperacio):
        return actual
    qui = _qui(id_nedador, actual)
    try:
        registres = afegeix_registre(actual.millors_registres, registre)
    except ErrorInvariant as excepcio:
        return _fallida(id_nedador, _errors_d_invariant(id_nedador, qui, excepcio))
    if registres == actual.millors_registres:
        return ResultatOperacio(id_nedador, Resultat(), actual, False)
    return _valida_i_desa(repositori, id_nedador, replace(actual, millors_registres=registres))


def esborra_nedador(repositori: RepositoriNedadors, id_nedador: IdNedador) -> ResultatOperacio:
    """RN-004: un nedador no s'esborra mai; s'arxiva. Sempre error; el nedador no canvia."""
    actual = _carrega(repositori, id_nedador)
    qui = str(id_nedador) if isinstance(actual, ResultatOperacio) else _qui(id_nedador, actual)
    error = ErrorValidacio(
        "RN-004",
        fitxer_nedador(id_nedador),
        "",
        None,
        "un nedador no es pot esborrar: s'arxiva",
        "Arxiva el nedador",
        qui,
    )
    return ResultatOperacio(
        id_nedador,
        Resultat(errors=(error,)),
        None if isinstance(actual, ResultatOperacio) else actual,
        False,
    )


def accepta_test(
    repositori: RepositoriNedadors, id_nedador: IdNedador, data: date, piscina: Piscina
) -> ResultatOperacio:
    """El coach accepta un test desat: passa a ser el vigent si és el més recent (CA-001-30).

    És l'únic canvi admès en un test desat; la resta del test no es toca (CA-001-82).
    """
    actual = _carrega(repositori, id_nedador)
    if isinstance(actual, ResultatOperacio):
        return actual
    index = next(
        (i for i, t in enumerate(actual.tests_css) if t.data == data and t.piscina is piscina),
        None,
    )
    if index is None:
        error = ErrorValidacio(
            "format",
            fitxer_nedador(id_nedador),
            "tests_css",
            f"{data.isoformat()} {int(piscina)} m",
            f"no hi ha cap test del {data.isoformat()} en piscina de {int(piscina)} m",
            "Indica la data i la piscina d'un test registrat",
            _qui(id_nedador, actual),
        )
        return _fallida(id_nedador, (error,))
    tests = list(actual.tests_css)
    tests[index] = replace(tests[index], acceptat=True)
    return _valida_i_desa(repositori, id_nedador, replace(actual, tests_css=tuple(tests)))


@dataclass(frozen=True)
class ResultatCataleg:
    resultat: Resultat
    desat: bool


def esborra_competicio(
    cataleg: RepositoriCataleg[Cataleg],
    repositori: RepositoriNedadors,
    temporada: CodiTemporada,
    id_competicio: str,
) -> ResultatCataleg:
    """RN-010: no es pot esborrar una competició amb participacions; el missatge identifica els
    nedadors afectats. Unes inscripcions que no es poden llegir també ho impedeixen."""
    fitxer = fitxer_cataleg(temporada)
    actual = cataleg.carrega(temporada)
    if actual.competicio(id_competicio) is None:
        error = ErrorValidacio(
            "format",
            fitxer,
            "competicions",
            id_competicio,
            f"la competició {id_competicio!r} no és al catàleg de {temporada}",
            "Indica una competició del catàleg",
        )
        return ResultatCataleg(Resultat(errors=(error,)), False)
    afectats: list[str] = []
    for id_nedador in repositori.ids():
        try:
            qui = _qui(id_nedador, repositori.carrega(id_nedador))
        except ErrorCarrega:
            qui = str(id_nedador)
        try:
            if temporada not in repositori.temporades(id_nedador):
                continue
            inscripcions = repositori.carrega_inscripcions(id_nedador, temporada)
        except ErrorCarrega:
            afectats.append(f"{qui} (inscripcions il·legibles)")
            continue
        if any(p.id_competicio == id_competicio for p in inscripcions.participacions):
            afectats.append(qui)
    if afectats:
        error = ErrorValidacio(
            "RN-010",
            fitxer,
            "competicions",
            id_competicio,
            f"la competició {id_competicio!r} té participacions: {', '.join(afectats)}",
            "Treu primer les participacions d'aquests nedadors",
        )
        return ResultatCataleg(Resultat(errors=(error,)), False)
    restants = tuple(c for c in actual.competicions if c.id != id_competicio)
    cataleg.desa(temporada, Cataleg(restants))
    return ResultatCataleg(Resultat(), True)
