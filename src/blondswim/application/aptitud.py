"""Cas d'ús d'aptitud per planificar (T054): aplica `valida_aptitud` i registra els avisos
RN-019 i RN-020 amb `decisio: null`, sense confirmació."""

from blondswim.application.ports import RegistreAvisos, Rellotge
from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.nedador import Nedador
from blondswim.domain.validacio import Resultat, valida_aptitud
from blondswim.domain.valors import CodiTemporada, IdNedador


def aptitud(
    id_nedador: IdNedador,
    nedador: Nedador,
    inscripcions: Inscripcions | None,
    temporada: CodiTemporada,
    registre: RegistreAvisos,
    rellotge: Rellotge,
) -> Resultat:
    qui = str(id_nedador) if nedador.alias is None else str(nedador.alias)
    resultat = valida_aptitud(id_nedador, qui, nedador, inscripcions, temporada)
    ara = rellotge.ara()
    for avis in resultat.avisos:
        registre.afegeix(ara, avis, id_nedador)
    return resultat
