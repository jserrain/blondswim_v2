"""Resultat de la validació (research R5)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorValidacio:
    rn: str
    fitxer: str
    camp: str
    valor: object
    missatge: str


@dataclass(frozen=True)
class Avis:
    rn: str
    fitxer: str
    camp: str
    valor: object
    missatge: str


@dataclass(frozen=True)
class Resultat:
    errors: tuple[ErrorValidacio, ...] = ()
    avisos: tuple[Avis, ...] = ()

    @property
    def es_valid(self) -> bool:
        return not self.errors
