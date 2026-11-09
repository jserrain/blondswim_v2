"""Generador d'ids de nedador (D2)."""

from uuid import uuid4

from blondswim.domain.valors import IdNedador


class GeneradorUuid4:
    def nou(self) -> IdNedador:
        return IdNedador(str(uuid4()))
