"""Consultes sobre dades desades (data-model.md § Consultes). Cap d'aquests valors es desa.

La temporada és una definició (`definicions.Temporada`, RN-031) i la marca vigent és a
`nedador.marca_vigent` (RN-007).
"""

from datetime import date

from blondswim.domain.inscripcions import Inscripcio, Inscripcions
from blondswim.domain.nedador import Nedador, TestCss
from blondswim.domain.valors import Classe, Piscina


def setmana_iso(data: date) -> tuple[int, int]:
    """Any ISO i setmana ISO de la data (CA-001-18)."""
    calendari = data.isocalendar()
    return calendari.year, calendari.week


def test_vigent(nedador: Nedador, piscina: Piscina) -> TestCss | None:
    """L'acceptat de data més recent de la piscina (CA-001-05, 30); `None` si no n'hi ha."""
    acceptats = [t for t in nedador.tests_css if t.acceptat and t.piscina is piscina]
    return max(acceptats, key=lambda t: t.data, default=None)


test_vigent.__test__ = False  # type: ignore[attr-defined]  # no és un test de pytest


def proves_objectiu(inscripcions: Inscripcions) -> tuple[Inscripcio, ...]:
    """Les inscripcions de les participacions de classe A (CA-001-16)."""
    return tuple(
        inscripcio
        for participacio in inscripcions.participacions
        if participacio.classe is Classe.A
        for inscripcio in participacio.proves
    )
