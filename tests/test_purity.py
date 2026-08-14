"""The quarantines' fitness functions, of which there are two.

The first and older one is the KERI quarantine, described below. The second is the
alias quarantine (this.i @cldspl): a COIA alias is creator-local, carries no security
claim, and must never enter committed bytes, be an input to the fold, or affect a
finding. That is a structural claim, so it is defended structurally — ``utina.fold``,
``utina.enact`` and ``utina.acme`` may not import ``utina.coia`` at all, and the same
AST inspection that catches a lazy KERI import catches a lazy alias import. Unlike the
KERI rule, ``utina.cli`` is exempt rather than covered, because display is the plane
whose whole job is display.

The original docstring follows.

The quarantine's fitness function.

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


def test_the_backend_is_exempt_and_the_exemption_is_not_empty() -> None:
    """The exemption is by filename, and it guards something real.

    A quarantine around a module that imports no KERI library would pass
    forever and mean nothing, so the second assertion is the one that matters:
    the exempt file really does reach for keripy.
    """
    exempt = [
        path
        for path in sorted((SRC / "substrate").rglob("*.py"))
        if path.name.startswith(EXEMPT)
    ]
    assert exempt, "no keri*.py backend; the exemption would be a dead rule"
    assert all(path not in quarantined_modules() for path in exempt)
    assert any(
        offenders_in(path.read_text(encoding="utf-8"), str(path)) for path in exempt
    ), (
        "the exempt backend imports no KERI library, which means the quarantine "
        "guards nothing and the demo is not writing real KERI data"
    )


# --- the alias quarantine (this.i @cldspl) ------------------------------------
#
# A COIA alias is display-only. utina.cli builds it and renders it; nothing below
# the display plane may see one, because an alias that reached the fold would be a
# creator-local nickname with no security claim standing where committed evidence
# belongs. Enforced here rather than by review, for the same reason as above.

#: The display-only module the planes below the CLI may not reach for.
DISPLAY_ONLY = "utina.coia"

#: The planes an alias may not reach. utina.cli is absent on purpose: it is the
#: display plane, and it is the one that is supposed to import this.
ALIAS_QUARANTINED = ("fold", "enact", "acme")


def alias_quarantined_modules() -> list[pathlib.Path]:
    """Every source file the alias quarantine covers."""
    return [path for plane in ALIAS_QUARANTINED for path in sorted((SRC / plane).rglob("*.py"))]


def package_of(path: pathlib.Path) -> str:
    """The dotted package a source file lives in, so relative imports resolve.

    ``utina/fold/clause.py`` and ``utina/fold/__init__.py`` both answer
    ``utina.fold``: dropping the last path component drops the module's own name in
    the first case and ``__init__`` in the second, which is the same answer for the
    same reason.
    """
    parts = list(path.relative_to(SRC.parent).with_suffix("").parts)
    parts.pop()
    return ".".join(parts)


def imported_modules(tree: ast.AST, package: str) -> set[str]:
    """Every module a parsed source file names, with relative imports resolved.

    Absolute dotted names rather than roots, because the forbidden name here is
    inside ``utina`` rather than outside it, so a root would say ``utina`` for every
    import in the package and catch nothing. Each ``from X import y`` contributes
    both ``X`` and ``X.y``, because ``from utina import coia`` names the module in
    the second position and is the shortest way to evade a check that reads only the
    first.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = package
            if node.level == 0:
                base = ""
            elif node.level > 1:
                # level 1 is the module's own package; each level above it climbs one.
                bits = package.split(".")
                base = ".".join(bits[: len(bits) - (node.level - 1)])
            full = f"{base}.{node.module}" if base and node.module else (node.module or base)
            names.add(full)
            for alias in node.names:
                names.add(f"{full}.{alias.name}")
    return names


def alias_offenders_in(source: str, filename: str, package: str) -> set[str]:
    """The display-only modules ``source`` imports."""
    named = imported_modules(ast.parse(source, filename=filename), package)
    within = DISPLAY_ONLY + "."
    return {name for name in named if name == DISPLAY_ONLY or name.startswith(within)}


def test_every_alias_quarantined_plane_has_modules() -> None:
    """A vacuous quarantine would pass forever after a bad refactor."""
    found = {path.parent.name for path in alias_quarantined_modules()}
    assert set(ALIAS_QUARANTINED) <= found


@pytest.mark.parametrize(
    "path", alias_quarantined_modules(), ids=lambda p: f"{p.parent.name}/{p.name}"
)
def test_a_plane_below_the_display_plane_imports_no_alias_machinery(
    path: pathlib.Path,
) -> None:
    offenders = alias_offenders_in(
        path.read_text(encoding="utf-8"), str(path), package_of(path)
    )
    assert not offenders, (
        f"{path.relative_to(SRC.parent)} imports {sorted(offenders)}. A COIA alias is "
        "display-only by decision (this.i @cldspl): it is creator-local, carries no "
        "security claim, and the spec names parsing someone else's alias for strong "
        "meaning as a dangerous antipattern. So it may never enter committed bytes, be "
        "an input to the fold, or affect a finding. Render it in utina.cli, which is the "
        "one exempt plane. If that is genuinely wrong, change this.i first — "
        "not this test."
    )


def test_the_display_plane_really_does_render_aliases() -> None:
    """The exemption guards something, rather than being a dead rule."""
    importers = [
        path
        for path in sorted((SRC / "cli").rglob("*.py"))
        if alias_offenders_in(path.read_text(encoding="utf-8"), str(path), package_of(path))
    ]
    assert importers, (
        "no module in utina.cli imports utina.coia, which means the alias quarantine "
        "guards nothing and the screens are not rendering aliases at all"
    )


def test_the_alias_guard_catches_every_shape_of_the_import_it_forbids() -> None:
    """The guard's own teeth, since a guard that cannot fail guards nothing."""
    for source in (
        "import utina.coia\n",
        "from utina.coia import create_alias\n",
        "from utina import coia\n",
        "def render():\n    from utina.coia import create_alias\n    return create_alias\n",
        "from ..coia import create_alias\n",
        "from .. import coia\n",
    ):
        assert alias_offenders_in(source, "fold/evaluate.py", "utina.fold"), source
    # And does not fire on the imports these planes legitimately make.
    for innocent in (
        "from utina.fold.clause import Clause\n",
        "from . import sibling\n",
        "from .law import GAID\n",
        "import unicodedata\n",
    ):
        assert not alias_offenders_in(innocent, "fold/evaluate.py", "utina.fold"), innocent


def test_package_of_answers_the_same_for_a_module_and_its_package_init() -> None:
    assert package_of(SRC / "fold" / "clause.py") == "utina.fold"
    assert package_of(SRC / "fold" / "__init__.py") == "utina.fold"
    assert package_of(SRC / "coia.py") == "utina"


def test_imported_roots_reads_all_three_import_shapes() -> None:
    """The helper's own branches: absolute, from-import, and relative."""
    tree = ast.parse(
        "import keri.core.coring\n"
        "from hio import help\n"
        "from . import sibling\n"
        "from .relative import thing\n"
    )
    assert imported_roots(tree) == {"keri", "hio"}
