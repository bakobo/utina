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


# --- the functional-dependency declaration (custos-4.2.md:2850-2858, tick 3uv4) ----
#
# A Constitution commits the revision of every external specification its fold
# consumes and names the superseding-recovery rules it consumes, each consumed or
# expressly excluded, never in silence (this.i @ehrgtmuj).

_EVERY_RULE_CONSUMED = {rule: semantics.CONSUMED for rule in semantics.RECOVERY_RULES}


def _law(keri: object) -> dict[str, object]:
    return {
        semantics.SEMANTICS_FIELD: {
            semantics.DOSSIER_KEY: semantics.DOSSIER,
            semantics.KERI_KEY: keri,
        }
    }


def _declaring(spec: str = semantics.KERI, **recovery: str) -> dict[str, object]:
    return _law(
        {
            semantics.KERI_SPEC_KEY: spec,
            semantics.RECOVERY_KEY: {**_EVERY_RULE_CONSUMED, **recovery},
        }
    )


def test_the_recovery_rules_are_the_eight_the_pinned_revision_names():
    assert semantics.RECOVERY_RULES == ("A0", "A1", "A2", "B1", "B2", "B3", "C", "C1")


def test_a_law_that_declares_its_keri_dependency_reads_back_as_that_declaration():
    dependency = semantics.dependency(_declaring())

    assert dependency == semantics.IMPLEMENTED
    assert dependency is not None
    assert dependency.spec == semantics.KERI


def test_the_engine_implements_every_rule_consumed():
    """Excluding any rule would leave a duplicity observation ordinary evidence
    rather than a conviction, so the engine consumes all of them (@ehrgtmuj)."""
    assert dict(semantics.IMPLEMENTED.recovery) == _EVERY_RULE_CONSUMED


@pytest.mark.parametrize(
    "law",
    [
        {},
        {semantics.SEMANTICS_FIELD: {semantics.DOSSIER_KEY: semantics.DOSSIER}},
        _law(None),
        _law("the KERI specification"),
        _law({}),
        _law({semantics.KERI_SPEC_KEY: "", semantics.RECOVERY_KEY: _EVERY_RULE_CONSUMED}),
        _law({semantics.KERI_SPEC_KEY: semantics.KERI}),
        _law({semantics.KERI_SPEC_KEY: semantics.KERI, semantics.RECOVERY_KEY: "all"}),
        _law(
            {
                semantics.KERI_SPEC_KEY: semantics.KERI,
                semantics.RECOVERY_KEY: {**_EVERY_RULE_CONSUMED, "A0": 1},
            }
        ),
    ],
    ids=[
        "no-block",
        "dossier-only",
        "null",
        "not-a-block",
        "empty",
        "empty-spec",
        "no-recovery",
        "recovery-not-a-mapping",
        "disposition-not-a-string",
    ],
)
def test_a_dependency_this_fold_cannot_read_is_no_declaration(law):
    assert semantics.dependency(law) is None


def test_the_implemented_declaration_is_applicable():
    assert semantics.dependency_refusal_for(semantics.IMPLEMENTED) is None


def test_an_absent_declaration_is_refused_and_says_what_is_missing():
    refusal = semantics.dependency_refusal_for(None)

    assert isinstance(refusal, Refusal)
    assert refusal.seal_kind is SealKind.DIGEST
    assert "functional-dependency declaration" in refusal.missing


def test_an_unrecognized_keri_revision_is_refused_and_names_it():
    refusal = semantics.dependency_refusal_for(semantics.dependency(_declaring(spec="f" * 64)))

    assert isinstance(refusal, Refusal)
    assert refusal.seal_kind is SealKind.DIGEST
    assert "ffffffffffffffff" in refusal.missing


def test_a_rule_left_in_silence_is_refused_and_named():
    """'Each consumed or expressly excluded, never in silence' (:2855-2856)."""
    recovery = {k: v for k, v in _EVERY_RULE_CONSUMED.items() if k not in {"B2", "C"}}
    law = _law({semantics.KERI_SPEC_KEY: semantics.KERI, semantics.RECOVERY_KEY: recovery})

    refusal = semantics.dependency_refusal_for(semantics.dependency(law))

    assert isinstance(refusal, Refusal)
    assert refusal.seal_kind is SealKind.DIGEST
    assert "B2" in refusal.missing and "C" in refusal.missing


@pytest.mark.parametrize(
    "recovery",
    [{"B1": semantics.EXCLUDED}, {"A0": "partly"}, {"D1": semantics.CONSUMED}],
    ids=["excluded", "unknown-disposition", "unknown-rule"],
)
def test_a_declaration_this_engine_does_not_implement_is_refused(recovery):
    """An engine that answered under an exclusion it cannot honour would be
    assuming at exactly the moment axiom 4 forbids it."""
    refusal = semantics.dependency_refusal_for(semantics.dependency(_declaring(**recovery)))

    assert isinstance(refusal, Refusal)
    assert refusal.seal_kind is SealKind.DIGEST
    assert "recovery" in refusal.missing


def test_the_four_dependency_failures_refuse_differently():
    silent = _law({semantics.KERI_SPEC_KEY: semantics.KERI, semantics.RECOVERY_KEY: {}})
    refusals = [
        semantics.dependency_refusal_for(declaration)
        for declaration in (
            None,
            semantics.dependency(_declaring(spec="f" * 64)),
            semantics.dependency(silent),
            semantics.dependency(_declaring(B1=semantics.EXCLUDED)),
        )
    ]

    assert all(isinstance(refusal, Refusal) for refusal in refusals)
    assert len({refusal.missing for refusal in refusals if refusal is not None}) == 4
