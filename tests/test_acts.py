"""The act grid: which (effect, state-kind) points a GCD's ``acts`` entries cover.

The grammar under test is the published one. ``gcd-2.0.1.schema.json`` constrains
every ``acts`` entry with a regular expression, and that pattern — not the prose
beside it — is what a conforming verifier has to agree with. So the cases here
are written against the pattern's own vocabulary: the five effects, the six
state-kinds, one space between the halves, one-sided braces only, and separators
of one or more commas or spaces.

Everything the grammar does not admit contributes *no* points rather than
raising. That is GCD's own rule 1 read from the verifier's side — "a verifier
that does not recognize it MUST assume that constraint is unmet and MUST deny" —
and it is also ``fold/slots.py``'s posture, so an entry this module cannot parse
must never widen what a delegate may do.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from utina.fold import acts

GCD_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "gcd-2.0.1.json"


def test_a_bare_point_covers_exactly_itself():
    assert acts.points("create commitment") == frozenset({("create", "commitment")})


def test_every_effect_and_kind_in_the_published_vocabulary_parses():
    """The two axes, exhaustively — a missing token would silently deny forever."""
    for effect in ("observe", "create", "modify", "preserve", "destroy"):
        for kind in ("info", "record", "commitment", "authority", "resource", "relationship"):
            assert acts.points(f"{effect} {kind}") == frozenset({(effect, kind)})


def test_one_effect_over_braced_kinds_covers_the_cross_product():
    assert acts.points("observe {info, record}") == frozenset(
        {("observe", "info"), ("observe", "record")}
    )


def test_braced_effects_over_one_kind_cover_the_cross_product():
    assert acts.points("{create, modify} record") == frozenset(
        {("create", "record"), ("modify", "record")}
    )


@pytest.mark.parametrize(
    "entry",
    [
        "observe {info,record}",
        "observe {info record}",
        "observe {info,  record}",
        "observe {info , record}",
    ],
)
def test_brace_items_separate_on_commas_or_spaces_or_both(entry):
    """``[ ,]+`` in the published pattern, so all four of these are one entry."""
    assert acts.points(entry) == frozenset({("observe", "info"), ("observe", "record")})


def test_a_single_braced_item_is_admitted():
    """The pattern's inner repetition is ``*``, so a brace of one is well formed."""
    assert acts.points("create {commitment}") == frozenset({("create", "commitment")})


@pytest.mark.parametrize(
    "entry",
    [
        "",
        "create",
        "commitment",
        "invent commitment",
        "create fantasy",
        "create  commitment",
        " create commitment",
        "create commitment ",
        "Create commitment",
        "create Commitment",
        "CREATE COMMITMENT",
        "create *",
        "* commitment",
        "{create, modify} {info, record}",
        "create {}",
        "create {info,}",
        "create {,info}",
        "create {info, fantasy}",
        "{create, invent} record",
        "{create, modify} fantasy",
        "create commitment, modify record",
        "create{commitment}",
        "{create}record",
    ],
)
def test_anything_outside_the_grammar_covers_nothing(entry):
    """Fail closed, and never an exception: an unparseable grant grants nothing."""
    assert acts.points(entry) == frozenset()


def test_the_grammar_agrees_with_the_published_pattern():
    """Cross-check every case above against the schema's own regular expression.

    The point is not that two implementations agree — it is that this module's
    idea of the grammar is the *published* one, checked against the document
    rather than against my reading of its prose.
    """
    pattern = re.compile(
        json.loads(GCD_SCHEMA.read_text(encoding="utf-8"))["properties"]["a"]["oneOf"][1][
            "properties"
        ]["constraints"]["properties"]["acts"]["items"]["pattern"]
    )
    admitted = [
        "create commitment",
        "observe {info, record}",
        "{create, modify} record",
        "observe {info,record}",
        "observe {info record}",
        "create {commitment}",
    ]
    refused = [
        "",
        "create",
        "invent commitment",
        "create fantasy",
        "Create commitment",
        "create *",
        "{create, modify} {info, record}",
        "create {}",
        "create {info,}",
        "create  commitment",
        "{create, modify} fantasy",
    ]
    for entry in admitted:
        assert pattern.match(entry), entry
        assert acts.points(entry), entry
    for entry in refused:
        assert not pattern.match(entry), entry
        assert not acts.points(entry), entry


def test_covered_unions_every_entry():
    assert acts.covered(["create commitment", "{observe, modify} record"]) == frozenset(
        {("create", "commitment"), ("observe", "record"), ("modify", "record")}
    )


def test_covered_drops_what_it_cannot_parse_and_keeps_what_it_can():
    """One bad entry denies itself, never the whole grant and never the caller."""
    assert acts.covered(["create commitment", "invent commitment"]) == frozenset(
        {("create", "commitment")}
    )


def test_covered_of_nothing_is_nothing():
    assert acts.covered([]) == frozenset()


def test_an_act_is_permitted_when_every_point_it_occupies_is_covered():
    """"An act is authorized only if EVERY point it occupies is covered here." """
    assert acts.permits(["{create, modify} record", "create commitment"], [
        ("create", "record"),
        ("create", "commitment"),
    ])


def test_an_act_is_refused_when_one_of_its_points_is_uncovered():
    """The schema's own example: filing a return is two points in one move."""
    assert not acts.permits(["create record"], [("create", "record"), ("create", "commitment")])


def test_an_act_occupying_no_points_is_refused():
    """Not vacuous truth. An act that names no point has not said what it is, and
    authorizing it would authorize anything, so the fail-closed answer is no."""
    assert not acts.permits(["create commitment"], [])


def test_an_empty_grant_permits_nothing():
    assert not acts.permits([], [("create", "commitment")])
