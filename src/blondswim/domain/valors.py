"""Objectes de valor del domini (data-model.md)."""

import re
from dataclasses import dataclass
from enum import Enum, IntEnum

_RE_ID = re.compile(r"n[0-9]{4}")
_RE_ALIAS = re.compile(r"[a-z0-9-]{2,20}")
_RE_TEMPS = re.compile(r"([0-9]+):([0-5][0-9])\.([0-9]{2})")
_RE_TEMPORADA = re.compile(r"([0-9]{4})-([0-9]{2})")


class Estil(Enum):
    CR = "Cr"
    ESQ = "Esq"
    BR = "Br"
    PAP = "Pap"
    EI = "Ei"


class Dia(Enum):
    DL = "dl"
    DT = "dt"
    DC = "dc"
    DJ = "dj"
    DV = "dv"
    DS = "ds"
    DG = "dg"

    @property
    def numero_iso(self) -> int:
        """dl=1 … dg=7."""
        return list(Dia).index(self) + 1


class Piscina(IntEnum):
    CURTA = 25
    LLARGA = 50


class Classe(Enum):
    A = "A"
    B = "B"
    C = "C"


class Prioritat(Enum):
    PRINCIPAL = "principal"
    SECUNDARIA = "secundària"


@dataclass(frozen=True)
class IdNedador:
    """RN-001."""

    valor: str

    def __post_init__(self) -> None:
        if not _RE_ID.fullmatch(self.valor):
            raise ValueError(f"id de nedador invàlid: {self.valor!r}")

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Correu:
    """RN-032 (format). La unicitat es valida entre nedadors."""

    valor: str

    def __post_init__(self) -> None:
        if not self.valor or any(c.isspace() for c in self.valor):
            raise ValueError(f"correu invàlid: {self.valor!r}")

    def __eq__(self, altre: object) -> bool:
        return isinstance(altre, Correu) and self.valor.casefold() == altre.valor.casefold()

    def __hash__(self) -> int:
        return hash(self.valor.casefold())

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Alias:
    """RN-003 (format). La unicitat es valida entre nedadors."""

    valor: str

    def __post_init__(self) -> None:
        if not _RE_ALIAS.fullmatch(self.valor) or _RE_ID.fullmatch(self.valor):
            raise ValueError(f"alias invàlid: {self.valor!r}")

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True, order=True)
class Temps:
    """Temps en centèsimes enteres, `m:ss.cc` en text (research R4)."""

    centesimes: int

    def __post_init__(self) -> None:
        if self.centesimes < 0:
            raise ValueError(f"temps negatiu: {self.centesimes}")

    @classmethod
    def de_text(cls, text: str) -> "Temps":
        coincidencia = _RE_TEMPS.fullmatch(text)
        if coincidencia is None:
            raise ValueError(f"temps invàlid (format m:ss.cc): {text!r}")
        minuts, segons, centesimes = (int(g) for g in coincidencia.groups())
        return cls((minuts * 60 + segons) * 100 + centesimes)

    def __str__(self) -> str:
        minuts, resta = divmod(self.centesimes, 6000)
        segons, centesimes = divmod(resta, 100)
        return f"{minuts}:{segons:02d}.{centesimes:02d}"


@dataclass(frozen=True)
class Prova:
    """Distància i estil. Que sigui oficial per a la piscina és RN-030."""

    distancia: int
    estil: Estil


@dataclass(frozen=True)
class CodiTemporada:
    """RN-031 (nom `AAAA-AA`). Les dates són a derivats."""

    valor: str

    def __post_init__(self) -> None:
        coincidencia = _RE_TEMPORADA.fullmatch(self.valor)
        if coincidencia is None or int(coincidencia.group(2)) != (self.any_inici + 1) % 100:
            raise ValueError(f"codi de temporada invàlid: {self.valor!r}")

    @property
    def any_inici(self) -> int:
        return int(self.valor[:4])

    def __str__(self) -> str:
        return self.valor
