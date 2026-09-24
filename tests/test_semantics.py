"""Axiom 4: an external semantics is pinned by digest, or the fold refuses.

``custos-4.2.md:290``. Acme's composition rule is expressed in the dossier
specification's terms, so that specification is an external semantics and the law
has to say which revision of it the clauses mean. The discipline exists because
pinned artifacts move: three of Custos 4.1's five moved *after* ratification.

The cases below are mostly refusals, and deliberately. A fold that refused the
unpinned law and quietly attempted the unrecognized one would be assuming at
exactly the moment the axiom forbids it, which is the failure that looks most
like success.
"""

from __future__ import annotations

import pytest

from utina.fold import semantics
from utina.fold.refusal import Refusal, SealKind


def test_a_law_that_pins_the_dossier_declares_its_digest():
    law = {semantics.SEMANTICS_FIELD: {semantics.DOSSIER_KEY: semantics.DOSSIER}}

    assert semantics.declared(law) == semantics.DOSSIER


@pytest.mark.parametrize(
    "law",
    [
        {},
        {"semantics": None},
        {"semantics": "the dossier specification"},
        {"semantics": {}},
        {"semantics": {"dossier": ""}},
        {"semantics": {"dossier": None}},
        {"semantics": {"something-else": "E" + "x" * 43}},
    ],
    ids=["absent", "null", "not-a-block", "empty", "empty-pin", "null-pin", "other-key"],
)
def test_a_law_that_pins_nothing_readable_declares_nothing(law):
    """Read fail-closed, like every other committed value: a declaration this
    fold cannot read is one it cannot hold the law to."""
    assert semantics.declared(law) is None


def test_the_recognized_revision_is_applicable():
    assert semantics.refusal_for(semantics.DOSSIER) is None


def test_an_unpinned_semantics_is_refused_and_says_so():
    """Not a pending finding. Nothing is short of evidence; the law never said
    what its clauses mean."""
    refusal = semantics.refusal_for(None)

    assert isinstance(refusal, Refusal)
    assert refusal.seal_kind is SealKind.DIGEST  # @kr7j7d7l
    assert "semantics declaration" in refusal.missing
    assert "digest" in refusal.missing


def test_an_unrecognized_semantics_is_refused_and_names_what_it_pinned():
    """The beat itself: flipping the digest produces a refusal, never a wrong
    answer under whatever revision happens to be installed."""
    refusal = semantics.refusal_for("e" * 64)

    assert isinstance(refusal, Refusal)
    assert refusal.seal_kind is SealKind.DIGEST  # @kr7j7d7l
    assert "an implementation of the semantics this law pins" in refusal.missing
    assert "eeeeeeeeeeeeeeee" in refusal.missing, "and which one, so a reader can go and look"


def test_the_two_failures_refuse_differently():
    """A law that never said what its clauses mean is a different mistake from
    one that said something this engine cannot read, and the refusal says which."""
    assert semantics.refusal_for(None).missing != semantics.refusal_for("e" * 64).missing


def test_the_recognized_set_is_closed_and_holds_the_revision_this_engine_implements():
    """A set, because an engine may implement two revisions during a migration.
    Closed, because anything outside it is refused rather than attempted."""
    assert semantics.DOSSIER in semantics.RECOGNIZED
    assert "e" * 64 not in semantics.RECOGNIZED
