"""COIA 2.0, held to the specification's own normative vectors.

``src/utina/coia.py`` is the upstream reference implementation, vendored **byte for
byte** from ``~/code/me/coia/coia.py`` along with its ``tables.json``. It is not
utina's code and nothing in utina should edit it: the point of vendoring the reference
rather than writing our own is that six implementations in six languages are held to
one set of vectors, and a local variant would be the seventh that nobody checks.

``tests/coia-vectors.json`` is that vector file, also copied verbatim. Its own header
says what makes it worth running: *"Authored from README.md prose, NOT from
implementation output. Each vector cites the rule it tests. Normative."* So a vector
that fails is the implementation disagreeing with the specification, not with a
previous run of itself.

**What this replaces.** utina carried a 493-line COIA 1.x implementation of its own and
a 463-line hand-written test of it. The cutover is `this.i` @<coia2> and it fixed a bug
no test of ours could have caught, because our tests agreed with our implementation:
every alias in the demo led with flag ``9``, which meant "test environment" in 1.x and
means **compromised — positive evidence that the wrong party controls it** in 2.0. The
test flag in 2.0 is ``6``.

The refresh procedure is a copy, not a merge:

    cp ~/code/me/coia/coia.py      src/utina/coia.py
    cp ~/code/me/coia/tables.json  src/utina/tables.json
    cp ~/code/me/coia/vectors.json tests/coia-vectors.json
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from utina import coia

ROOT = Path(__file__).resolve().parents[1]
VECTORS = json.loads((Path(__file__).parent / "coia-vectors.json").read_text("utf-8"))


def _cases(name: str) -> list:
    return [case for case in VECTORS[name]]


def _id(case) -> str:
    return case[0]


# --- the specification's own vectors -------------------------------------------


@pytest.mark.parametrize("case", _cases("normalize"), ids=_id)
def test_normalize_matches_the_specifications_vector(case):
    _, given, want = case
    assert coia.normalize(given) == want


@pytest.mark.parametrize("case", _cases("generate"), ids=_id)
def test_generate_matches_the_specifications_vector(case):
    _, args, want = case
    lang, who, role, scope, flags, private = args
    subject = coia.ME if who is None else who
    assert coia.create_alias(lang, subject, role, scope, flags, private) == want


@pytest.mark.parametrize("case", _cases("reject"), ids=_id)
def test_a_malformed_alias_is_rejected(case):
    _, args = case
    lang, who, role, scope, flags, private = args
    subject = coia.ME if who is None else who
    with pytest.raises(ValueError):
        coia.create_alias(lang, subject, role, scope, flags, private)


@pytest.mark.parametrize("case", _cases("parse"), ids=_id)
def test_parse_matches_the_specifications_vector(case):
    _, given, want = case
    assert list(coia.parse_alias(given)) == list(want)


@pytest.mark.parametrize("case", _cases("match"), ids=_id)
def test_match_matches_the_specifications_vector(case):
    _, alias, query, want = case
    assert coia.matches(query, alias) is want


@pytest.mark.parametrize("case", _cases("search"), ids=_id)
def test_search_matches_the_specifications_vector(case):
    _, aliases, query, want = case
    assert list(coia.search(query, aliases)) == list(want)


# --- the vendoring discipline ---------------------------------------------------


def test_the_vendored_implementation_is_byte_identical_to_upstream():
    """A local edit would make this the seventh implementation nobody checks.

    Skipped rather than failed when the upstream checkout is absent, because a
    contributor without it should still be able to run the suite — the vectors above
    are the substantive check and they travel with this repo.
    """
    upstream = Path.home() / "code" / "me" / "coia" / "coia.py"
    if not upstream.exists():  # pragma: no cover - depends on the developer's checkout
        pytest.skip("upstream COIA checkout not present")
    assert (ROOT / "src" / "utina" / "coia.py").read_bytes() == upstream.read_bytes()


def test_coia_stands_alone_and_imports_nothing_of_utinas():
    """COIA is a convention, not a part of this engine, and it has to stay liftable.

    The module is display-plane only and `tests/test_purity.py` enforces the other
    half — that no plane below the CLI may import it at all.
    """
    tree = ast.parse((ROOT / "src" / "utina" / "coia.py").read_text("utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "a relative import would tie it to this package"
            if node.module:
                imported.add(node.module)
    assert not [one for one in imported if one.split(".")[0] == "utina"]


def test_the_test_flag_is_six_and_nine_means_compromised():
    """The bug the cutover fixed, pinned so it cannot come back.

    Under COIA 1.x, ``9`` meant a test environment; under 2.0 it means the wrong party
    is known to control the identifier. Every alias in this demo carried it.
    """
    assert coia.create_alias("en", "Bob", "payee", flags="6") == "bob-payee,6"
    assert "6" in coia.ASSIGNED and "9" in coia.ASSIGNED
