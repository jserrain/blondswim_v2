"""Base dels DTO de lectura i missatges d'error en català (research R1)."""

from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel, ConfigDict, ValidationError

from blondswim.domain.valors import Dia, Estil, Piscina

_MISSATGES = {
    "model_type": "ha de ser un objecte",
    "date_type": "ha de ser una data",
    "date_parsing": "data invàlida (format AAAA-MM-DD)",
    "missing": "camp obligatori absent",
    "extra_forbidden": "camp desconegut",
    "int_type": "ha de ser un enter",
    "float_type": "ha de ser un nombre",
    "string_type": "ha de ser un text",
    "bool_type": "ha de ser true o false",
    "list_type": "ha de ser una llista",
    "enum": "valor no admès",
    "json_invalid": "JSON invàlid",
}


class DtoBase(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class VolumSetmanalDto(DtoBase):
    min: int
    max: int


class DetallProvaDto(DtoBase):
    parcials: list[str] | None = None
    bracades_per_llarg: float | None = None
    sr: float | None = None
    rpe: int | None = None


class TestCssDto(DtoBase):
    __test__ = False  # no és un test de pytest

    data: date
    piscina: Piscina
    t400: str
    t200: str
    acceptat: bool
    detall_400: DetallProvaDto | None = None
    detall_200: DetallProvaDto | None = None
    notes: str | None = None


class MillorRegistreDto(DtoBase):
    estil: Estil
    distancia: int
    piscina: Piscina
    temps: str
    data: date
    competicio: str


class NedadorDto(DtoBase):
    """`nedador.json`. L'ordre dels camps és el de l'escriptura (research R3)."""

    versio_esquema: int
    correu: str
    alias: str | None = None
    arxivat: bool
    estils_preferents: list[Estil]
    dies_entrenament: list[Dia]
    volum_setmanal: VolumSetmanalDto
    tests_css: list[TestCssDto]
    millors_registres: list[MillorRegistreDto]


@dataclass(frozen=True)
class ErrorCamp:
    camp: str
    missatge: str


def errors_en_catala(excepcio: ValidationError) -> list[ErrorCamp]:
    """Un `ErrorCamp` per error, amb la ruta del camp (`tests_css.0.t400`)."""
    return [
        ErrorCamp(
            camp=".".join(str(part) for part in error["loc"]),
            missatge=_MISSATGES.get(error["type"], error["msg"]),
        )
        for error in excepcio.errors()
    ]
