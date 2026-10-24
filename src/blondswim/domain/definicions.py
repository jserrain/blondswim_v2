"""Definicions fixades a les regles de negoci (research R2). Únic lloc amb aquests valors."""

from blondswim.domain.valors import Estil, Piscina, Prova

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
