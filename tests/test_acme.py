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

import json
from fractions import Fraction
from pathlib import Path

import jsonschema
import pytest
from bakobo.errors import BakoboError

from utina.acme import (
    AMENDMENT_ACTS,
    BOARD_LAW,
    DEV,
    EQUITY_ACTS,
    FOUNDING_LAW,
    GAID,
    MARTA,
    NINA,
    ORDINARY_ACTS,
    SEAT,
    SEAT_OFFICE,
    build,
)
from utina.substrate import ENDORSEMENT_SCHEMA, GCD_RULES, GCD_SCHEMA, canonical_bytes

#: The published GCD as vendored, so the record's own credential is checked
#: against the document rather than against a shape restated here.
GCD_DOCUMENT = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "gcd-2.0.1.json").read_text(
        encoding="utf-8"
    )
)

#: ``d1`` through ``d9`` and the two named coordinates are ``docs/demo-script.md``'s.
#: ``b5`` and ``b11`` are ``docs/demo-2-script.md``'s beats 5 and 11, the two
#: coordinates the carried clause A3 needs; its beat 10 is asked at
#: ``board-seated``, the first coordinate the board law governs, so it needs no
#: label of its own.
ORACLE_LABELS = {
    "inception",
    "board-seated",
    "b5",
    "b8",
    "b11",
    "b13",
    "b15",
    "b16",
    "b17",
    "device-granted",
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
    assert weights(BOARD_LAW, "B1") == dict.fromkeys((MARTA, DEV, SEAT), Fraction(1, 2))
    assert weights(BOARD_LAW, "B2") == dict.fromkeys((MARTA, DEV, SEAT), Fraction(1, 3))


def test_the_amendment_seats_the_office_and_not_the_officer():
    """@z373ew7j: the law slots board seat 3, and Nina is nowhere in it.

    A law that slotted the director would attach a governance power to a person.
    Under the office, a director leaving is a rotation on the seat and the
    committed law does not move at all.
    """
    assert BOARD_LAW["seats"] == (SEAT,)
    assert NINA not in weights(BOARD_LAW, "B1")
    assert NINA not in weights(BOARD_LAW, "B2")


def test_every_slot_names_the_schema_its_evidence_must_satisfy():
    """``custos-4.2.md:1946-1951``, and the SHALL at :1435-1437 that rests on it.

    Every clause here is discharged by endorsements, so every slot names the
    dossier's endorsement schema — and it is committed rather than assumed,
    because the seat credential is a second ACDC kind and a requirement that
    could not say which it wanted would be satisfiable by the wrong one.
    """
    for law in (FOUNDING_LAW, BOARD_LAW):
        for entry in law["clauses"]:
            for one in entry["group"]["slots"]:
                assert one["schema"] == ENDORSEMENT_SCHEMA
    assert GCD_SCHEMA != ENDORSEMENT_SCHEMA, "two kinds, or the case above is vacuous"


# --- A3, the clause the amendment does not reach (@rwo55zyw, tick 6ms6) -------


def test_the_founders_keep_their_own_clause_in_both_editions():
    """Escrowed founder equity is a founders' matter in edition 1 and edition 2 alike."""
    assert weights(FOUNDING_LAW, "A3") == {MARTA: Fraction(1, 2), DEV: Fraction(1, 2)}
    assert weights(BOARD_LAW, "A3") == {MARTA: Fraction(1, 2), DEV: Fraction(1, 2)}


def test_the_carried_clause_is_byte_identical_across_the_amendment():
    """The claim the whole fixture exists to make, checked where it is made.

    A clause is its bytes. Equal weights would not be enough — a difference in
    the governed-act list, the operator, or the order of the slots would give the
    same weights a different digest, and the amendment would then be replacing A3
    with a clause that merely resembles it.
    """
    assert canonical_bytes(clause(FOUNDING_LAW, "A3")) == canonical_bytes(
        clause(BOARD_LAW, "A3")
    )


def test_the_carried_clause_governs_what_no_other_clause_governs():
    """Nothing else may rule the equity act, or A3 would not be the untouched one."""
    assert clause(FOUNDING_LAW, "A3")["governs"] == EQUITY_ACTS
    for law, ordinary in ((FOUNDING_LAW, "A1"), (BOARD_LAW, "B1")):
        assert EQUITY_ACTS[0] not in clause(law, ordinary)["governs"]


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


def test_the_seat_credential_in_the_record_is_a_real_gcd(acme_double):
    """The adoption's whole claim, checked on Acme's own committed bytes.

    Not a lookalike and not a shape restated in a test: the credential the
    record carries validates against the published document under a stranger's
    validator, names the published schema, and is issued under the published
    governance framework.
    """
    issuances = [event for event in acme_double.events if event.kind == "issuance"]
    assert issuances, "the record has to seat its board for any of this to mean anything"
    credential = issuances[0].body["acdc"]

    jsonschema.validate(instance=dict(credential), schema=GCD_DOCUMENT)
    assert credential["s"] == GCD_SCHEMA
    assert credential["r"] == GCD_RULES


def test_the_seat_credential_says_what_authority_the_seat_inherited(acme_double):
    """A seat holds power because a credential says which, never because it is
    delegated: the delegation relationship confers nothing (``this.i`` @cglayqvw).

    ``create commitment`` is what an endorsement and a declination both are, and
    it is the whole of what Acme's law lets the seat do. Every other constraint
    dimension is absent because the fold cannot evaluate it, and GCD's rule 1
    makes a dimension a verifier does not recognize a denial rather than a skip.
    """
    credential = next(
        event.body["acdc"] for event in acme_double.events if event.kind == "issuance"
    )

    assert credential["a"]["i"] == acme_double.aid(SEAT), "issued to the office"
    assert credential["a"]["constraints"] == {"acts": ["create commitment"]}
    assert credential["a"]["facet"]["role"] == SEAT_OFFICE


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


def disp(event):
    """The disposition the event's embedded credential carries, if it carries one.

    ``None`` covers both an event with no credential in it and a credential of
    the other kind: a seat credential has an issuee and an office where an
    endorsement has a disposition and a subject.
    """
    acdc = event.body.get("acdc")
    return acdc["a"].get("disp") if isinstance(acdc, dict) else None


def subject_of(event):
    """The subject the event's embedded endorsement is about, if it is one."""
    acdc = event.body.get("acdc")
    return acdc["a"].get("said") if isinstance(acdc, dict) else None


def test_dev_declines_three_times_and_each_is_a_signed_committed_act(acme_double):
    """A no is never a silence, and three nos are three events.

    D3's office lease, D6's retabled budget, and beat 13's Q2 forecast. The
    third is the same signed no as the first two and the fold draws a different
    consequence from it, which is what beats 13 and 15 are for.
    """
    declinations = [
        event
        for event in acme_double.events
        if disp(event) == "decline" and event.body["i"] == DEV
    ]
    assert len(declinations) == 3
    for event in declinations:
        assert acme_double.substrate.verify(DEV, event.body, event.body["sig"])


def test_the_seat_declines_the_amendment(acme_double):
    """Beat D7: the retained bar bites because the seated organ signs a no."""
    assert [
        event.body["i"]
        for event in acme_double.events
        if disp(event) == "decline"
    ] == [DEV, DEV, SEAT, DEV]


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
    assert (event.body["i"], disp(event)) == (DEV, "endorse")
    assert subject_of(event) == acme_double.said("open-bank-account")


def test_d3_is_dev_s_declination_of_the_office_lease(acme_double):
    """@4tcsbw72: the lease takes the signed no so the hire can stay pending."""
    event = acme_double.events[acme_double.at("d3").seq]
    assert (event.body["i"], disp(event)) == (DEV, "decline")
    assert subject_of(event) == acme_double.said("sign-office-lease")


def test_the_hire_is_left_pending_and_nobody_declines_it(acme_double):
    """Demo 2 beat 9's material: an act whose cure path the amendment will close."""
    hire = acme_double.said("hire-vp-sales")
    acts = [
        (event.body["i"], disp(event))
        for event in acme_double.events
        if disp(event) is not None and subject_of(event) == hire
    ]
    assert acts == [(MARTA, "endorse")]


def test_d6_is_dev_s_declination_of_the_retabled_budget(acme_double):
    """The centerpiece's second half addresses the second act, not the first."""
    event = acme_double.events[acme_double.at("d6").seq]
    assert (event.body["i"], disp(event)) == (DEV, "decline")
    assert subject_of(event) == acme_double.said("approve-budget-retabled")


def test_d9_looks_back_from_after_the_amendment(acme_double):
    assert acme_double.at("d9").seq > acme_double.at("board-seated").seq


def test_the_equity_release_is_tabled_once_and_straddles_the_amendment(acme_double):
    """Beats 5, 10 and 11 are one committed act asked at three coordinates.

    Marta endorses before the board is seated and Dev after it, so the same
    question is pending under A3 on both sides of the amendment and cured on the
    far side of it — under a clause whose bytes the amendment did not touch.
    """
    equity = acme_double.said(EQUITY_ACTS[0])
    assert acme_double.corpus.event(equity).body["act"] == EQUITY_ACTS[0]
    endorsers = [
        (event.body["i"], acme_double.at("board-seated").seq < event.position.seq)
        for event in acme_double.events
        if disp(event) == "endorse" and subject_of(event) == equity
    ]
    assert endorsers == [(MARTA, False), (DEV, True)]
    assert acme_double.at("b5").seq < acme_double.at("board-seated").seq
    assert acme_double.at("b11").seq > acme_double.at("board-seated").seq


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
    assert acme_double.events[0].body["i"] == acme_double.gaid
    assert acme_double.gaid == acme_double.aid(GAID)


def test_a_party_is_addressed_by_the_identifier_inception_returned(acme_double):
    """@crrtzf: the alias is a name for a party, and the identifier is the party.

    They coincide under the facade, which is the coincidence that let callers
    write the alias and appear to be right.
    """
    assert acme_double.aid(MARTA) == MARTA
    founding = acme_double.events[0].body["law"]
    assert set(weights(founding, "A1")) == {
        acme_double.aid(MARTA),
        acme_double.aid(DEV),
    }


def test_an_alias_nobody_incepted_is_named_rather_than_guessed_at(acme_double):
    with pytest.raises(BakoboError) as caught:
        acme_double.aid("acme:mallory")
    assert caught.value.code == "e.state.name-unknown.f"


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
