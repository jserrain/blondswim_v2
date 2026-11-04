"""Càrrega de nedadors: un ERROR exclou només aquell nedador (CA-001-60, 65, 66)."""

from collections.abc import Mapping
from dataclasses import dataclass, replace

from blondswim.application.ports import RepositoriNedadors
from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import (
    ErrorCarrega,
    ErrorValidacio,
    Identitat,
    Resultat,
    fitxer_nedador,
    valida_nedador,
    valida_unicitat,
)
from blondswim.domain.valors import IdNedador


@dataclass(frozen=True)
class ResultatCarrega:
    """`nedadors`: només els que no tenen cap ERROR. `resultats`: tots els llegits."""

    nedadors: dict[IdNedador, Nedador]
    resultats: dict[IdNedador, Resultat]


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


def carrega_nedadors(repositori: RepositoriNedadors[object]) -> ResultatCarrega:
    """Valida tots els nedadors i la unicitat; una col·lisió exclou tots els implicats."""
    identitats = repositori.identitats()
    nedadors: dict[IdNedador, Nedador] = {}
    resultats: dict[IdNedador, Resultat] = {}
    for id_nedador in repositori.ids():
        try:
            nedador = repositori.carrega(id_nedador)
        except ErrorCarrega as excepcio:
            resultats[id_nedador] = Resultat(errors=excepcio.errors)
            continue
        propi = valida_nedador(id_nedador, nedador)
        col_lisions = errors_d_unicitat(identitats, id_nedador) if id_nedador in identitats else ()
        resultat = replace(propi, errors=(*propi.errors, *col_lisions))
        resultats[id_nedador] = resultat
        if resultat.es_valid:
            nedadors[id_nedador] = nedador
    return ResultatCarrega(nedadors=nedadors, resultats=resultats)
