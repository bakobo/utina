"""The quarantine's fitness function.

Custos §1.4 axiom 2 closes the fold's inputs at three committed values, so the
evaluator can be — and by decision must be — free of any KERI library. Once
keripy is a real dependency that claim widens: not only the fold but every plane
above the substrate has to stay free of it, or ``--substrate facade`` is a flag
over an already-loaded dependency rather than a fallback (this.i @343xvm).

So this reads every module of ``utina.fold``, ``utina.enact``, ``utina.acme``
and ``utina.cli`` as source and fails if any imports a KERI package. Inside
``utina.substrate`` the same rule holds with exactly one exemption: the files
named ``keri*.py``, which are the implementation the quarantine exists to
contain.

It inspects the AST rather than the runtime import graph on purpose: a lazy
import inside a function body would evade a runtime check, and a lazy import is
exactly how this boundary would erode.

Derived from bakobo/thesmo's ``tests/test_core_purity.py`` (Apache-2.0); see
NOTICE.
"""

import ast
import pathlib

import pytest

from utina.fold import FORBIDDEN_IMPORTS

SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "utina"

#: Every plane above the substrate. None of these may name a KERI package.
QUARANTINED = ("fold", "enact", "acme", "cli")

#: The one place a KERI package may be imported: the substrate's own backend.
EXEMPT = "keri"


def quarantined_modules() -> list[pathlib.Path]:
    """Every source file the quarantine covers, so new ones need no edit here.

    The four planes entirely, plus the substrate minus its keripy backend —
    ``utina.substrate.protocol`` and the facade are as bound by this as the fold
    is, since a KERI import there would load keripy for the facade path too.
    """
    modules = [path for plane in QUARANTINED for path in sorted((SRC / plane).rglob("*.py"))]
    modules += [
        path
        for path in sorted((SRC / "substrate").rglob("*.py"))
        if not path.name.startswith(EXEMPT)
    ]
    return modules


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


def offenders_in(source: str, filename: str) -> set[str]:
    """The forbidden packages ``source`` imports."""
    return imported_roots(ast.parse(source, filename=filename)) & FORBIDDEN_IMPORTS


def test_every_quarantined_plane_has_modules() -> None:
    """A vacuous purity test would pass forever after a bad refactor."""
    found = {path.parent.name for path in quarantined_modules()}
    assert set(QUARANTINED) <= found, "a plane vanished; the purity test would be vacuous"
    assert (SRC / "substrate").is_dir()


@pytest.mark.parametrize(
    "path", quarantined_modules(), ids=lambda p: f"{p.parent.name}/{p.name}"
)
def test_a_quarantined_module_imports_no_keri_library(path: pathlib.Path) -> None:
    offenders = offenders_in(path.read_text(encoding="utf-8"), str(path))
    assert not offenders, (
        f"{path.relative_to(SRC.parent)} imports {sorted(offenders)}. "
        "Everything above the substrate is pure by decision: the fold's inputs "
        "are closed at three committed values, and the planes above it select a "
        "substrate by name rather than by import, so --substrate facade loads no "
        "KERI library at all. Put the call in utina/substrate/keri*.py, which is "
        "the one exempt place. If that is genuinely wrong, change this.i first — "
        "not this test."
    )


def test_the_guard_catches_a_keri_import_planted_in_a_pure_plane() -> None:
    """The guard's own teeth, since a guard that cannot fail guards nothing."""
    planted = "def evaluate():\n    from keri.core import coring\n    return coring\n"
    assert offenders_in(planted, "fold/evaluate.py") == {"keri"}
    assert offenders_in("import hio\nimport lmdb\n", "fold/corpus.py") == {"hio", "lmdb"}


def test_imported_roots_reads_all_three_import_shapes() -> None:
    """The helper's own branches: absolute, from-import, and relative."""
    tree = ast.parse(
        "import keri.core.coring\n"
        "from hio import help\n"
        "from . import sibling\n"
        "from .relative import thing\n"
    )
    assert imported_roots(tree) == {"keri", "hio"}
