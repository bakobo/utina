"""The fold's purity fitness function.

Custos §1.4 axiom 2 closes the fold's inputs at three committed values, so the
evaluator can be — and by decision must be — free of any KERI library. That is
an architectural claim, and an architectural claim defended only by a comment
decays the first time someone needs a digest in a hurry. So it is defended here.

This reads every module under ``utina.fold`` as source and fails if any imports
the substrate. It inspects the AST rather than the runtime import graph on
purpose: a lazy import inside a function body would evade a runtime check, and a
lazy import is exactly how this boundary would erode.

Derived from bakobo/thesmo's ``tests/test_core_purity.py`` (Apache-2.0); see
NOTICE.
"""

import ast
import pathlib

import pytest

from utina.fold import FORBIDDEN_IMPORTS

FOLD = pathlib.Path(__file__).resolve().parent.parent / "src" / "utina" / "fold"


def fold_modules() -> list[pathlib.Path]:
    """Every source file under fold/, so new ones are covered without edits."""
    return sorted(FOLD.rglob("*.py"))


def imported_roots(tree: ast.AST) -> set[str]:
    """Top-level package name of every import in a parsed module.

    ``import keri.core.coring`` and ``from keri import coring`` both yield
    ``keri``; a relative import yields nothing, since it cannot reach outside
    the package.
    """
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.partition(".")[0])
        # node.module is None for `from . import x`; level > 0 is relative, and a
        # relative import cannot reach outside the package.
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            roots.add(node.module.partition(".")[0])
    return roots


def test_fold_package_exists() -> None:
    """A vacuous purity test would pass forever after a bad refactor."""
    assert FOLD.is_dir()
    assert fold_modules(), "fold/ has no modules; the purity test would be vacuous"


@pytest.mark.parametrize("path", fold_modules(), ids=lambda p: p.name)
def test_fold_module_does_not_import_substrate(path: pathlib.Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    offenders = imported_roots(tree) & FORBIDDEN_IMPORTS
    assert not offenders, (
        f"{path.relative_to(FOLD.parent)} imports {sorted(offenders)}. "
        "fold/ is pure by decision: the fold's inputs are closed at three "
        "committed values, so it needs no substrate. Put the substrate call in "
        "utina.substrate and hand the fold the committed values instead. If that "
        "is genuinely wrong, change this.i first — not this test."
    )


def test_imported_roots_reads_all_three_import_shapes() -> None:
    """The helper's own branches: absolute, from-import, and relative."""
    tree = ast.parse(
        "import keri.core.coring\n"
        "from hio import help\n"
        "from . import sibling\n"
        "from .relative import thing\n"
    )
    assert imported_roots(tree) == {"keri", "hio"}
