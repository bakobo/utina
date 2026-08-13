"""Acme's committed law and corpus: built by driving enact, never hand-written.

Two things are checked here and nowhere else. The corpus has to be a real
product of the constructor's verb — if the fixture were a literal, the demo
would prove that a hand-written log folds the way its author intended, which is
not a claim about anything. And the corpus has to reach every position label
``docs/demo-script.md`` names, meaning what that table says it means, because
the acceptance oracle addresses the log through those labels alone.

The verdicts themselves are not asserted here. They belong to the fold, and the
oracle asserts them.
"""

from __future__ import annotations

from fractions import Fraction

import pytest
from bakobo.errors import BakoboError

from utina.acme import (
    AMENDMENT_ACTS,
    BOARD_LAW,
    DEV,
    FOUNDING_LAW,
    GAID,
    MARTA,
    NINA,
    ORDINARY_ACTS,
    build,
)
from utina.substrate import canonical_bytes

ORACLE_LABELS = {
    "inception",
    "board-seated",
    "d1",
    "d2",
    "d3",
    "d4",
    "d5",
    "d6",
    "d7",
    "d8",
    "d9",
}


def clause(law, clause_id):
    return next(entry for entry in law["clauses"] if entry["id"] == clause_id)


def weights(law, clause_id):
    """The clause's weights, parsed. Committed as exact rational strings."""
    slots = clause(law, clause_id)["group"]["slots"]
    return {slot["endorser"]: Fraction(slot["weight"]) for slot in slots}


# --- The law, in both states -------------------------------------------------


def test_state_one_gives_each_founder_half_of_both_clauses():
    assert weights(FOUNDING_LAW, "A1") == {MARTA: Fraction(1, 2), DEV: Fraction(1, 2)}
    assert weights(FOUNDING_LAW, "A2") == {MARTA: Fraction(1, 2), DEV: Fraction(1, 2)}


def test_state_two_distributes_ordinary_authority_but_not_amendment_authority():
    """The retained higher bar at B2 is the point of the whole demo."""
    assert weights(BOARD_LAW, "B1") == dict.fromkeys((MARTA, DEV, NINA), Fraction(1, 2))
    assert weights(BOARD_LAW, "B2") == dict.fromkeys((MARTA, DEV, NINA), Fraction(1, 3))


def test_the_amendment_seats_nina():
    assert BOARD_LAW["seats"] == (NINA,)


@pytest.mark.parametrize(
    ("law", "ordinary", "amendment"),
    [(FOUNDING_LAW, "A1", "A2"), (BOARD_LAW, "B1", "B2")],
    ids=["state-one", "state-two"],
)
def test_each_state_governs_ordinary_acts_and_amendment_separately(law, ordinary, amendment):
    assert clause(law, ordinary)["governs"] == ORDINARY_ACTS
    assert clause(law, amendment)["governs"] == AMENDMENT_ACTS


def test_no_clause_governs_a_distribution():
    """Beat D8 needs the law to be silent, and silence has to be real."""
    governed = {
        act
        for law in (FOUNDING_LAW, BOARD_LAW)
        for entry in law["clauses"]
        for act in entry["governs"]
    }
    assert "declare-dividend" not in governed


@pytest.mark.parametrize("law", [FOUNDING_LAW, BOARD_LAW], ids=["state-one", "state-two"])
def test_every_weight_is_an_exact_rational(law):
    """@ta7vle — a float in the committed bytes would make unity undecidable.

    The committed form is the exact rational *string* ``docs/interfaces.md``
    rules for the law body, because the fold parses the committed value and not
    the committed bytes. A float would not survive the round trip and is what
    this guards against; a Fraction object would survive the encoder and then
    fail to read as law, which is the seam integration had to close.
    """
    for entry in law["clauses"]:
        for slot in entry["group"]["slots"]:
            assert isinstance(slot["weight"], str)
            assert Fraction(slot["weight"]).denominator in (2, 3)


def test_a_weight_commits_as_a_rational_string_not_a_decimal():
    assert b'"weight":"1/2"' in canonical_bytes(FOUNDING_LAW)
    assert b"0.5" not in canonical_bytes(FOUNDING_LAW)


# --- The corpus --------------------------------------------------------------


def test_the_corpus_is_what_the_constructor_emitted(acme_double):
    """Driven, not written. Every event carries a signature it earned."""
    assert acme_double.events
    for event in acme_double.events:
        assert acme_double.substrate.verify(event.body["i"], event.body, event.body["sig"])


def test_the_founding_law_is_committed_at_inception(acme_double):
    inception = acme_double.events[0]
    assert inception.kind == "inception"
    assert inception.body["law"] == FOUNDING_LAW


def test_the_successor_law_is_committed_by_the_amendment(acme_double):
    enactment = acme_double.corpus.event(acme_double.said("seat-the-board"))
    assert enactment.kind == "enactment"
    assert enactment.body["law"] == BOARD_LAW


def test_the_amendment_anchors_in_an_establishment_event(acme_double):
    """custos-4.2.md:2085-2087, and the reason Substrate has a rotate at all."""
    assert acme_double.substrate.anchoring_event(acme_double.said("seat-the-board")) is not None


def test_every_committed_event_has_a_distinct_identifier(acme_double):
    saids = [event.said for event in acme_double.events]
    assert len(set(saids)) == len(saids)


def test_the_budget_is_tabled_twice(acme_double):
    """@w5yqab — D5 needs Nina endorsed and D6 needs her untouched, so two acts."""
    first = acme_double.said("approve-budget")
    retabled = acme_double.said("approve-budget-retabled")
    assert first != retabled
    for said in (first, retabled):
        assert acme_double.corpus.event(said).body["act"] == "approve-budget"


def test_dev_declines_twice_and_both_are_signed_committed_acts(acme_double):
    """A no is never a silence, and two nos are two events."""
    declinations = [
        event
        for event in acme_double.events
        if event.body.get("disp") == "decline" and event.body["i"] == DEV
    ]
    assert len(declinations) == 2
    for event in declinations:
        assert acme_double.substrate.verify(DEV, event.body, event.body["sig"])


def test_nina_declines_the_amendment(acme_double):
    """Beat D7: the retained bar bites because a seated director signs a no."""
    assert [
        event.body["i"]
        for event in acme_double.events
        if event.body.get("disp") == "decline"
    ] == [DEV, DEV, NINA]


# --- The position labels the oracle addresses the log through -----------------


def test_every_label_the_oracle_uses_resolves(acme_double):
    for label in ORACLE_LABELS:
        assert acme_double.at(label).seq >= 0


def test_the_labels_are_exactly_the_ones_the_demo_script_names(acme_double):
    assert set(acme_double.labels) == ORACLE_LABELS


def test_the_beats_run_in_the_order_the_demo_script_tells_them(acme_double):
    order = ["inception", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"]
    seqs = [acme_double.at(label).seq for label in order]
    assert seqs == sorted(seqs)


def test_the_board_is_seated_at_the_amendment_s_own_beat(acme_double):
    assert acme_double.at("board-seated").seq == acme_double.at("d4").seq


def test_d1_is_the_second_founder_s_endorsement_of_the_bank_account(acme_double):
    event = acme_double.events[acme_double.at("d1").seq]
    assert (event.body["i"], event.body["disp"]) == (DEV, "endorse")
    assert event.body["said"] == acme_double.said("open-bank-account")


def test_d3_is_dev_s_declination_of_the_hire(acme_double):
    event = acme_double.events[acme_double.at("d3").seq]
    assert (event.body["i"], event.body["disp"]) == (DEV, "decline")
    assert event.body["said"] == acme_double.said("hire-vp-sales")


def test_d6_is_dev_s_declination_of_the_retabled_budget(acme_double):
    """The centerpiece's second half addresses the second act, not the first."""
    event = acme_double.events[acme_double.at("d6").seq]
    assert (event.body["i"], event.body["disp"]) == (DEV, "decline")
    assert event.body["said"] == acme_double.said("approve-budget-retabled")


def test_d9_looks_back_from_after_the_amendment(acme_double):
    assert acme_double.at("d9").seq > acme_double.at("board-seated").seq


def test_an_unknown_label_is_named_rather_than_guessed_at(acme_double):
    with pytest.raises(BakoboError) as caught:
        acme_double.at("d99")
    assert caught.value.code == "e.state.label-unknown.f"
    assert "d99" in str(caught.value)


def test_an_unknown_name_is_named_rather_than_guessed_at(acme_double):
    with pytest.raises(BakoboError) as caught:
        acme_double.said("buy-a-yacht")
    assert caught.value.code == "e.state.name-unknown.f"
    assert "buy-a-yacht" in str(caught.value)


def test_every_named_event_is_in_the_corpus(acme_double):
    for name in acme_double.saids:
        assert acme_double.corpus.event(acme_double.said(name)) is not None


def test_the_gaid_signs_for_the_domain(acme_double):
    assert acme_double.events[0].body["i"] == GAID


# --- Determinism and permutation ---------------------------------------------


def test_two_builds_agree_down_to_the_byte(acme_double, values):
    """The replay beat dies if any identifier or signature varies between runs."""
    again = build(values=values)
    assert [event.said for event in again.events] == [
        event.said for event in acme_double.events
    ]
    assert [canonical_bytes(event.body) for event in again.events] == [
        canonical_bytes(event.body) for event in acme_double.events
    ]


def test_a_permutation_really_permutes(acme_double):
    """A shuffle that returned the log unchanged would make beat D10 vacuous."""
    permuted = acme_double.permuted_events(seed=7)
    assert permuted != acme_double.events
    assert sorted(event.said for event in permuted) == sorted(
        event.said for event in acme_double.events
    )


def test_a_permuted_corpus_holds_the_same_committed_events(acme_double):
    permuted = acme_double.permuted_corpus(seed=7)
    last = acme_double.at("d9")
    assert permuted.upto(last) == acme_double.corpus.upto(last)


def test_the_permutation_is_a_function_of_its_seed(acme_double):
    assert acme_double.permuted_events(seed=7) == acme_double.permuted_events(seed=7)
    assert acme_double.permuted_events(seed=7) != acme_double.permuted_events(seed=8)
