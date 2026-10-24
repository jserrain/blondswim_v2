"""Base dels DTO de lectura i missatges d'error en català (research R1)."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, ValidationError

_MISSATGES = {
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
