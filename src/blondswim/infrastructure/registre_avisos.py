"""Registre d'avisos `data/avisos.jsonl` (una línia JSON per avís).

Només s'hi afegeix: les línies anteriors no es toquen (CA-001-48).
"""

import json
from datetime import date, datetime
from pathlib import Path

from blondswim.domain.validacio import Avis
from blondswim.domain.valors import IdNedador


def _json(valor: object) -> object:
    if isinstance(valor, date):
        return valor.isoformat()
    return str(valor)


class RegistreAvisosJsonl:
    def __init__(self, cami: Path) -> None:
        self._cami = cami

    def afegeix(
        self,
        data_hora: datetime,
        avis: Avis,
        id_nedador: IdNedador | None,
        decisio: str | None = None,
    ) -> None:
        """`decisio`: `confirmat` o `rebutjat` a l'entrada (spec 002); `None` a la càrrega i a la
        planificació."""
        linia = {
            "data_hora": data_hora.isoformat(timespec="seconds"),
            "rn": avis.rn,
            "fitxer": avis.fitxer,
            "camp": avis.camp,
            "valor": avis.valor,
            "missatge": avis.missatge,
            "id_nedador": None if id_nedador is None else str(id_nedador),
            "decisio": decisio,
        }
        self._cami.parent.mkdir(parents=True, exist_ok=True)
        with self._cami.open("a", encoding="utf-8", newline="\n") as fitxer:
            fitxer.write(json.dumps(linia, ensure_ascii=False, default=_json) + "\n")
