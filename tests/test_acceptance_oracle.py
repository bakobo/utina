"""The acceptance oracle: Acme's governance, beat by beat.

This is the outer red test. It encodes ``docs/demo-script.md`` directly — every
row of that table is a case here, with the same identifier — and it stays red
until the engine can answer all of them. Unit-level red/green cycles happen
underneath it; this file is what "done" means.

Each case asserts two things, and the second is the one that matters: the
verdict, and that the verdict *carries its ground*. Custos's Ground Axiom makes
the ground a component of the finding's type rather than an annotation on it, so
a case that checks only the verdict would pass against an engine that returns
bare opinions — which is precisely the engine this one must not be.
"""

import pytest

# The oracle is written before the engine, outside-in: it names the API the fold
# must grow, and skips with that reason until the modules exist. Inner unit tests
# are the ones driven red-to-green; this one goes from skipped to passing, and the
# day it can be collected is the day the engine is feature-complete against the
# demo. Do not weaken a case to make it collect sooner.
pytest.importorskip(
    "utina.fold.question",
    reason="the fold has no Constitution yet — see docs/demo-script.md for what it owes",
)

from utina.fold import Constitution, evaluate  # noqa: E402
from utina.fold.finding import Affirmed, Defeated, Pending  # noqa: E402
from utina.fold.question import Committed, Proposal  # noqa: E402
from utina.fold.refusal import Refusal  # noqa: E402


# --- The law -----------------------------------------------------------------


def test_state_one_requires_both_founders(acme):
    """Clause A1: two slots at w=1/2, so unity needs both."""
    law = Constitution.at(acme.corpus, acme.at("inception"))
    group = law.clause("A1").group
    assert {slot.endorser for slot in group.slots} == {"acme:marta", "acme:dev"}
    assert sum(slot.weight for slot in group.slots) == 1
    assert not group.satisfied_by(set())


def test_amendment_redistributes_ordinary_authority_but_not_amendment_authority(acme):
    """The retained higher bar is the point of the whole demo."""
    before = Constitution.at(acme.corpus, acme.at("inception"))
    after = Constitution.at(acme.corpus, acme.at("board-seated"))

    assert len(after.clause("B1").group.slots) == 3
    assert after.clause("B1").group.satisfied_by({"acme:marta", "acme:nina"})

    # Ordinary authority is now distributed; amendment authority is not.
    assert not after.clause("B2").group.satisfied_by({"acme:marta", "acme:nina"})
    assert after.clause("B2").group.satisfied_by({"acme:marta", "acme:dev", "acme:nina"})
    assert before.clause("A2").group.satisfied_by({"acme:marta", "acme:dev"})


# --- The beats ---------------------------------------------------------------


def test_d1_both_founders_endorse_is_affirmed(acme):
    finding = evaluate(acme.corpus, Proposal("open-bank-account"), at=acme.at("d1"))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A1",)
    assert len(finding.endorsements) == 2


def test_d2_one_slot_untouched_is_pending_naming_the_slot(acme):
    """Pending is 'not yet', and it must name what would discharge it."""
    finding = evaluate(acme.corpus, Proposal("hire-vp-sales"), at=acme.at("d2"))
    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == ["acme:dev"]


def test_d3_declination_under_two_slots_makes_unity_unreachable(acme):
    """The centerpiece, first half: a signed no kills a two-slot decision."""
    finding = evaluate(acme.corpus, Proposal("hire-vp-sales"), at=acme.at("d3"))
    assert isinstance(finding, Defeated)
    assert finding.citation.clause == "A1"
    assert finding.citation.declination.endorser == "acme:dev"


def test_d4_the_amendment_is_judged_under_the_law_it_replaces(acme):
    """Succession: the enactment that seats the board clears A2, not B2."""
    finding = evaluate(acme.corpus, Committed(acme.said("seat-the-board")), at=acme.at("d4"))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A2",)


def test_d5_unity_is_reached_though_one_party_never_acted(acme):
    finding = evaluate(acme.corpus, Proposal("approve-budget"), at=acme.at("d5"))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("B1",)


def test_d6_the_same_declination_under_three_slots_is_only_pending(acme):
    """The centerpiece, second half. Same signed no, opposite verdict."""
    finding = evaluate(acme.corpus, Proposal("approve-budget"), at=acme.at("d6"))
    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == ["acme:nina"]


def test_d7_the_retained_amendment_bar_bites(acme):
    finding = evaluate(acme.corpus, Proposal("amend-operating-agreement"), at=acme.at("d7"))
    assert isinstance(finding, Defeated)
    assert finding.citation.clause == "B2"


def test_d8_an_ungoverned_question_is_refused_not_answered(acme):
    """Axiom 3, shown: where committed law runs out, the fold refuses."""
    outcome = evaluate(acme.corpus, Proposal("declare-dividend"), at=acme.at("d8"))
    assert isinstance(outcome, Refusal)
    assert not isinstance(outcome, (Affirmed, Defeated, Pending))
    assert "declare-dividend" in outcome.missing


def test_d9_the_past_is_recomputed_under_the_law_in_force_then(acme):
    """The utility claim. D1 is still affirmed, under A1, from a later position."""
    finding = evaluate(acme.corpus, Committed(acme.said("open-bank-account")), at=acme.at("d9"))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A1",)


def test_d10_permuted_arrival_folds_to_byte_identical_constitutions(acme):
    """Binding at custos-4.2.md:3101 — byte-identical, not merely equivalent."""
    straight = Constitution.at(acme.corpus, acme.at("board-seated"))
    shuffled = Constitution.at(acme.permuted_corpus(seed=7), acme.at("board-seated"))
    assert straight.canonical_bytes() == shuffled.canonical_bytes()


# --- The two contrasts the demo turns on --------------------------------------


@pytest.mark.parametrize(
    ("position", "expected"),
    [("d3", Defeated), ("d6", Pending)],
    ids=["two-slots-unreachable", "three-slots-still-reachable"],
)
def test_one_declination_two_verdicts(acme, position, expected):
    """Dev's signed no is one act. The Constitution decides what it means."""
    act = "hire-vp-sales" if position == "d3" else "approve-budget"
    assert isinstance(evaluate(acme.corpus, Proposal(act), at=acme.at(position)), expected)
