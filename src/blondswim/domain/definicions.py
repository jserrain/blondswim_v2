"""Definicions fixades a les regles de negoci (research R2). Únic lloc amb aquests valors."""

from dataclasses import dataclass
from datetime import date, timedelta

from blondswim.domain.valors import CodiTemporada, Estil, Piscina, Prova

# RN-030 — proves individuals oficials: estil -> piscina -> distàncies.
_TOTES = {Piscina.CURTA, Piscina.LLARGA}
_PROVES_OFICIALS: dict[Estil, dict[Piscina, frozenset[int]]] = {
    Estil.CR: {p: frozenset({50, 100, 200, 400, 800, 1500}) for p in _TOTES},
    Estil.ESQ: {p: frozenset({50, 100, 200}) for p in _TOTES},
    Estil.BR: {p: frozenset({50, 100, 200}) for p in _TOTES},
    Estil.PAP: {p: frozenset({50, 100, 200}) for p in _TOTES},
    Estil.EI: {
        Piscina.CURTA: frozenset({100, 200, 400}),
        Piscina.LLARGA: frozenset({200, 400}),
    },
}


def es_prova_oficial(prova: Prova, piscina: Piscina) -> bool:
    """RN-030."""
    return prova.distancia in _PROVES_OFICIALS[prova.estil][piscina]


# RN-031 — la temporada comença l'1 d'octubre.
INICI_TEMPORADA_MES = 10
INICI_TEMPORADA_DIA = 1


@dataclass(frozen=True)
class Temporada:
    """RN-031: de l'1 d'octubre d'`AAAA` al 30 de setembre de l'any següent."""

    codi: CodiTemporada
    inici: date
    fi: date

    @classmethod
    def de_codi(cls, text: str) -> "Temporada":
        """`ValueError` si el nom no és `AAAA-AA` coherent."""
        codi = CodiTemporada(text)
        inici = date(codi.any_inici, INICI_TEMPORADA_MES, INICI_TEMPORADA_DIA)
        seguent = date(codi.any_inici + 1, INICI_TEMPORADA_MES, INICI_TEMPORADA_DIA)
        return cls(codi, inici, seguent - timedelta(days=1))
