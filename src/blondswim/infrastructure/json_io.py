"""Escriptura estable de JSON (research R3)."""

import json
from pathlib import Path

from pydantic import BaseModel


def serialitza(model: BaseModel) -> str:
    """Ordre de claus del model, `null` explícits, salt de línia final."""
    dades = model.model_dump(mode="json", exclude_none=False)
    return json.dumps(dades, indent=2, ensure_ascii=False) + "\n"


def escriu(cami: Path, model: BaseModel) -> None:
    cami.parent.mkdir(parents=True, exist_ok=True)
    cami.write_text(serialitza(model), encoding="utf-8", newline="\n")
