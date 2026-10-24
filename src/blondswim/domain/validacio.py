"""Resultat de la validació (research R5) i validació del nedador."""

from collections.abc import Mapping
from dataclasses import dataclass

from blondswim.domain.definicions import es_prova_oficial
from blondswim.domain.nedador import Nedador
from blondswim.domain.valors import IdNedador


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


class ErrorCarrega(Exception):
    """La càrrega ha trobat un o més errors; els acumula tots."""

    def __init__(self, errors: tuple[ErrorValidacio, ...]) -> None:
        super().__init__("; ".join(f"{e.fitxer}: {e.camp}: {e.missatge}" for e in errors))
        self.errors = errors


def _fitxer_nedador(id_nedador: IdNedador) -> str:
    return f"nedadors/{id_nedador}/nedador.json"


def valida_nedador(nedador: Nedador, fitxer: str) -> Resultat:
    """RN-007 i RN-030 dels millors registres d'un nedador."""
    errors: list[ErrorValidacio] = []
    vistos: set[tuple[object, int, object]] = set()
    for i, registre in enumerate(nedador.millors_registres):
        camp = f"millors_registres.{i}"
        descripcio = (
            f"{registre.distancia} {registre.estil.value} a piscina de {registre.piscina} m"
        )
        if not es_prova_oficial(registre.prova, registre.piscina):
            missatge = f"prova no oficial: {descripcio}"
            errors.append(ErrorValidacio("RN-030", fitxer, camp, descripcio, missatge))
        clau = (registre.estil, registre.distancia, registre.piscina)
        if clau in vistos:
            missatge = f"millor registre repetit: {descripcio}"
            errors.append(ErrorValidacio("RN-007", fitxer, camp, descripcio, missatge))
        vistos.add(clau)
    return Resultat(errors=tuple(errors))


def valida_entre_nedadors(nedadors: Mapping[IdNedador, Nedador]) -> Resultat:
    """RN-003 (alias únic) i RN-032 (correu únic, arxivats inclosos)."""
    errors: list[ErrorValidacio] = []
    ordenats = sorted(nedadors.items(), key=lambda element: element[0].valor)
    for rn, camp in (("RN-003", "alias"), ("RN-032", "correu")):
        grups: dict[object, list[IdNedador]] = {}
        for id_nedador, nedador in ordenats:
            valor = getattr(nedador, camp)
            if valor is not None:
                grups.setdefault(valor, []).append(id_nedador)
        for valor, ids in grups.items():
            if len(ids) > 1:
                llista = ", ".join(str(i) for i in ids)
                missatge = f"{camp} repetit als nedadors {llista}"
                errors.append(
                    ErrorValidacio(rn, _fitxer_nedador(ids[0]), camp, str(valor), missatge)
                )
    return Resultat(errors=tuple(errors))
