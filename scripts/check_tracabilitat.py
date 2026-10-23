"""Traçabilitat CA → test (constitució, principi VII). Sense LLM. No modifica res.

Sortida:
- 0: tot correcte.
- 1: marcadors òrfens o errors d'ID (sempre), o criteris sense test en mode bloquejant.
- 2: criteris sense test en mode avís.
"""

import ast
import re
import sys
import tomllib
from pathlib import Path

ARREL = Path(__file__).resolve().parent.parent
SPEC = re.compile(r"^(\d{3}[a-z]?)-")
CRITERI = re.compile(r"^- \*\*(CA-(\d{3}[a-z]?)-\d{2})\*\*( \[PENDENT [^\]]+\])?", re.M)
APROVADA = "**Estat:** Aprovada"
MODES = ("avis", "bloquejant")


def specs() -> list[tuple[str, Path]]:
    trobades = []
    for cami in sorted((ARREL / "specs").iterdir()):
        fitxer = cami / "spec.md" if cami.is_dir() else cami
        m = SPEC.match(cami.name)
        if m and fitxer.suffix == ".md" and fitxer.exists():
            trobades.append((m.group(1), fitxer))
    return trobades


def criteris() -> tuple[set[str], set[str], list[str]]:
    exigits: set[str] = set()
    tots: set[str] = set()
    errors: list[str] = []
    for numero, fitxer in specs():
        text = fitxer.read_text(encoding="utf-8")
        for m in CRITERI.finditer(text):
            id_, prefix, pendent = m.group(1), m.group(2), m.group(3)
            if prefix != numero:
                errors.append(f"{id_} és a la spec {numero}")
            if id_ in tots:
                errors.append(f"{id_} repetit")
            tots.add(id_)
            if APROVADA in text and not pendent:
                exigits.add(id_)
    return exigits, tots, errors


def marcadors() -> set[str]:
    trobats: set[str] = set()
    for fitxer in (ARREL / "tests").rglob("*.py"):
        for node in ast.walk(ast.parse(fitxer.read_text(encoding="utf-8"))):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "ca"
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "mark"
            ):
                trobats |= {a.value for a in node.args if isinstance(a, ast.Constant)}
    return trobats


def main() -> int:
    config = tomllib.loads((ARREL / "pyproject.toml").read_text(encoding="utf-8"))
    mode = config["tool"]["blondswim"]["tracabilitat"]
    if mode not in MODES:
        print(f"tracabilitat = {mode!r}: ha de ser 'avis' o 'bloquejant'")
        return 1
    exigits, tots, errors = criteris()
    tests = marcadors()
    sense_test = sorted(exigits - tests)
    orfes = sorted(tests - tots)
    for id_ in sense_test:
        print(f"sense test: {id_}")
    for id_ in orfes:
        print(f"marcador sense criteri: {id_}")
    for error in errors:
        print(f"error d'ID: {error}")
    if not (sense_test or orfes or errors):
        return 0
    print(
        f"{len(sense_test)} sense test (mode {mode}), {len(orfes)} marcadors òrfens, "
        f"{len(errors)} errors d'ID"
    )
    if orfes or errors or mode == "bloquejant":
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
