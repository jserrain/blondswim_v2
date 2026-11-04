"""Objectes de valor del domini (data-model.md)."""

import re
from dataclasses import dataclass
from enum import Enum, IntEnum

_RE_ID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")
_RE_PART_ALIAS = re.compile(r"[a-z0-9-]{2,12}")
_RE_ALIAS = re.compile(r"[a-z0-9-]{2,12}_[0-9a-f]{7}")
_MIDA_SUFIX_ALIAS = 7
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


class Canal(Enum):
    """RN-035."""

    CORREU = "correu"
    MOBIL = "mobil"


# Espais en blanc dels extrems que no compten (RN-032): espais, tabuladors i salts de línia.
BLANCS = " \t\n"


@dataclass(frozen=True)
class IdNedador:
    """RN-001: UUID v4 canònic en minúscules (ADR-0014)."""

    valor: str

    def __post_init__(self) -> None:
        if not _RE_ID.fullmatch(self.valor):
            raise ValueError(f"id de nedador invàlid: {self.valor!r}")

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Correu:
    """RN-032. Conserva el valor tal com s'ha entrat; no es corregeix ni es normalitza.

    El format es consulta amb `format_valid` (l'ERROR el dona el validador); la unicitat
    es valida entre nedadors amb `clau`.
    """

    valor: str

    @property
    def clau(self) -> str:
        """Clau de comparació: en minúscules i sense blancs als extrems."""
        return self.valor.strip(BLANCS).lower()

    @property
    def format_valid(self) -> bool:
        net = self.valor.strip(BLANCS)
        local, arroba, domini = net.rpartition("@")
        return bool(
            arroba and local and domini and "." in domini and not any(c.isspace() for c in net)
        )

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class Alias:
    """RN-003 (format `<part>_<sufix>`). La unicitat es valida entre nedadors."""

    valor: str

    def __post_init__(self) -> None:
        if not _RE_ALIAS.fullmatch(self.valor):
            raise ValueError(f"alias invàlid: {self.valor!r}")

    @classmethod
    def genera(cls, part: str, id_nedador: IdNedador) -> "Alias":
        """L'alias definitiu: la part del coach i els 7 primers caràcters de l'id."""
        if not _RE_PART_ALIAS.fullmatch(part):
            raise ValueError(f"part d'alias invàlida: {part!r}")
        return cls(f"{part}_{id_nedador.valor[:_MIDA_SUFIX_ALIAS]}")

    def coincideix_amb(self, id_nedador: IdNedador) -> bool:
        """El sufix és els 7 primers caràcters de l'id."""
        return self.valor.rpartition("_")[2] == id_nedador.valor[:_MIDA_SUFIX_ALIAS]

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
