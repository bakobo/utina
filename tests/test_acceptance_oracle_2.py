"""The demo-2 acceptance oracle: Acme's governance, beat by beat.

This encodes ``docs/demo-2-script.md`` directly. Every row of its beat tables is a
case here under that row's own number, and the numbering is demo 2's — it does not
correspond to demo 1's ``D1``-``D10``, and ``tests/test_acceptance_oracle.py``
remains the oracle for that script until this one ships.

Each case asserts the verdict *and* that the verdict carries the ground its row
names. The Ground Axiom makes the ground a component of a finding's type rather
than an annotation on it, so a case that checked only the verdict would pass
against an engine returning bare opinions.

**A row whose ground the engine cannot yet carry skips, and names what it owes.**
It never asserts the part it can reach: the script's columns are one contract per
row, and a case that checked a verdict while its ground was unbuilt would report
an engine that does not exist. So this file goes from skipped to passing, row by
row, as the phases land — ``uv run pytest -rs`` reads as the remaining work.

Where a row's *behaviour* is reachable today but its ground is not, the assertion
lives at the seam (``tests/test_seam.py``) until the row itself can carry it.
Nothing here is a substitute for that; nothing there is a substitute for this.
"""

import pytest

pytest.importorskip(
    "utina.fold.evaluate",
    reason="the fold has no evaluate() yet — see docs/demo-2-script.md for what it owes",
)

from bakobo.errors import BakoboError

from utina.acme import (
    CAPITAL_PLAN,
    DEV,
    DEVICE,
    GAID,
    MARTA,
    Q2_FORECAST,
    Q3_BUDGET,
    QUINN,
    SEAT,
)
from utina.enact import Constructor
from utina.fold import Constitution, evaluate
from utina.fold.finding import Affirmed, Defeated, Pending, PendingSpecies
from utina.fold.question import Committed, Proposal
from utina.fold.refusal import Refusal
from utina.substrate import DI2I, ENDORSEMENT_SCHEMA, GCD_SCHEMA, ISSUED, REVOKED

#: Where each beat is asked, in the record's own labels. Demo 2 numbers its beats
#: and the record labels its coordinates, so the mapping is stated once here
#: rather than guessed at each row. Beats whose coordinate the record does not
#: reach yet are absent, and their rows skip.
AT = {
    2: "d1",
    3: "d2",
    4: "d3",
    5: "b5",
    6: "d8",
    9: "board-seated",
    10: "board-seated",
    11: "b11",
    12: "d5",
    13: "b13",
    15: "b15",
    16: "b16",
    17: "b17",
    18: "d5",
    19: "b17",
    21: "b21",
    24: "d9",
    25: "board-seated",
}

BANK = "open-bank-account"
HIRE = "hire-vp-sales"
LEASE = "sign-office-lease"
EQUITY = "release-escrowed-equity"
DIVIDEND = "declare-dividend"
BUDGET = "approve-budget"

#: The record's name for the annual budget, which is beat 12's subject and the
#: one beats 18 and 19 re-ask about. Distinct from the act CLASS above: three
#: acts of one class are tabled, and these rows are about one of them.
BUDGET_ACT = "approve-budget"


def owed(*what: str) -> str:
    """The reason this row skips: what the engine still owes it.

    Phase and tick, so the skip line is a pointer into the plan rather than a
    shrug. A row that skips for a reason nobody can act on is worse than absent.
    The caller raises the skip itself, rather than this helper doing it, so that
    ``pytest -rs`` reports each line against its own row.
    """
    return "owes " + "; ".join(what)


# --- The law -----------------------------------------------------------------


def test_edition_one_is_three_clauses_over_the_two_founders(acme):
    """Every founding clause is two slots at a half, so unity needs both founders."""
    law = Constitution.at(acme.corpus, acme.at("inception"))
    assert [clause.id for clause in law.clauses] == ["A1", "A2", "A3"]
    for identifier in ("A1", "A2", "A3"):
        group = law.clause(identifier).group
        assert {slot.endorser for slot in group.slots} == {acme.aid(MARTA), acme.aid(DEV)}
        assert not group.satisfied_by({acme.aid(MARTA)})
        assert group.satisfied_by({acme.aid(MARTA), acme.aid(DEV)})


def test_edition_two_distributes_ordinary_authority_and_carries_a3_unchanged(acme):
    """The most important row of the script's law section.

    Ordinary authority is distributed and the authority to amend is not — demo
    1's point, retained — and the founders' own clause is re-committed with the
    same bytes, so it is the same clause with the same identifier afterwards.
    """
    before = Constitution.at(acme.corpus, acme.at("inception"))
    after = Constitution.at(acme.corpus, acme.at("board-seated"))

    assert after.clause("B1").group.satisfied_by({acme.aid(MARTA), acme.aid(DEV)})
    assert not after.clause("B2").group.satisfied_by({acme.aid(MARTA), acme.aid(DEV)})
    assert after.clause("A3").said() == before.clause("A3").said()


# --- Act I — law is computed, not asserted (the recorded opener) ---------------


def test_b01_the_constitution_at_inception():
    """Row 1: three clauses with their SAIDs, operators, slots and weights, and
    the pinned dossier-semantics digest."""
    pytest.skip(
        owed(
            "U5.2 the semantics-declaration block and its axiom-4 refusal (tick 2uhi)",
        )
    )


def test_b02_open_a_bank_account_is_affirmed(acme):
    """Row 2: clause A1 and both endorsement SAIDs."""
    finding = evaluate(acme.corpus, Proposal(BANK), at=acme.at(AT[2]))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A1",)
    assert len(finding.endorsements) == 2


def test_b03_the_hire_is_pending_naming_devs_slot(acme):
    """Row 3: a typed requirement naming the required schema, the expected issuer
    and the citing clause, species absent."""
    finding = evaluate(acme.corpus, Proposal(HIRE), at=acme.at(AT[3]))
    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [acme.aid(DEV)]
    assert [element.clause for element in finding.requirement] == ["A1"]
    assert [element.schema for element in finding.requirement] == [ENDORSEMENT_SCHEMA]
    assert [element.species for element in finding.requirement] == [PendingSpecies.ABSENT]


def test_b04_the_office_lease_is_defeated(acme):
    """Row 4: Dev's declination SAID and clause A1; unity unreachable."""
    finding = evaluate(acme.corpus, Proposal(LEASE), at=acme.at(AT[4]))
    assert isinstance(finding, Defeated)
    assert finding.citation.clause == "A1"
    assert finding.citation.declination.endorser == acme.aid(DEV)
    assert finding.citation.declination.said == acme.said(LEASE + "-declined")


def test_b05_the_equity_release_is_pending_under_a3(acme):
    """Row 5: a typed requirement naming Dev's slot under A3, species absent."""
    finding = evaluate(acme.corpus, Proposal(EQUITY), at=acme.at(AT[5]))
    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [acme.aid(DEV)]
    assert [element.clause for element in finding.requirement] == ["A3"]
    assert [element.species for element in finding.requirement] == [PendingSpecies.ABSENT]


def test_b06_a_dividend_is_refused_rather_than_answered(acme):
    """Row 6: the refusal names the missing rule, and is not a finding."""
    outcome = evaluate(acme.corpus, Proposal(DIVIDEND), at=acme.at(AT[6]))
    assert isinstance(outcome, Refusal)
    assert not isinstance(outcome, Affirmed | Defeated | Pending)
    assert DIVIDEND in outcome.missing


# --- Act II — delegation, and the two currents --------------------------------


def test_b07_seating_the_board_is_affirmed_under_the_law_it_replaces():
    """Row 7: judged under A2, plus the delegating seal's coordinate in Acme's
    KEL, the dip in seat 3's KEL, the seat credential's issuance event, and the
    declared disturbance set."""
    pytest.skip(owed(
        "U3.3 the declared disturbance set (tick 7rfv)",
        "a finding that carries the delegation and issuance coordinates as ground",
    ))


def test_b08_the_seat_screen_shows_two_bindings():
    """Row 8: KERI's delegating seal and dip, and the ACDC seat credential with
    its registry state — two bindings on one screen."""
    # Both bindings exist now — the dip and its seal, and the credential with its
    # registry state. What is missing is the screen that shows them side by side.
    pytest.skip(owed("U4.2 the seat screen (tick 27x5)"))


def test_b09_the_hire_re_asked_after_the_amendment_has_no_cure_path(acme):
    """Row 9: pending with species expired/abandoned, ground the amending
    enactment's SAID, cure re-presentation.

    The finding at its own position stands forever, as every finding does. What
    it loses is any path to a terminal value: the clause it cited is not the
    clause in force, so the requirement space it declared at birth is
    unreachable and only re-presentation reaches one.
    """
    finding = evaluate(acme.corpus, Committed(acme.said(HIRE)), at=acme.at(AT[9]))

    assert isinstance(finding, Pending)
    assert [element.clause for element in finding.requirement] == ["A1"]
    assert [element.species for element in finding.requirement] == [
        PendingSpecies.EXPIRED_ABANDONED
    ]
    assert [element.ground for element in finding.requirement] == [
        acme.said("seat-the-board")
    ]
    assert finding.requirement[0].species.cure == "cured by re-presentation"


def test_b10_the_equity_release_re_asked_after_the_amendment_is_still_curable():
    """Row 10: species absent, the same requirement as row 5, and the three-part
    stability check shown — same clause SAID, same requirement space, same
    pinned lens."""
    pytest.skip(owed(
        "U3.1 the three-part stability test (tick 6pdw)",
        "U5.2 the pinned lens (tick 2uhi)",
    ))


def test_b11_the_equity_release_is_cured_across_the_amendment(acme):
    """Row 11: clause A3 and both endorsement SAIDs — cured under the clause that
    never moved."""
    finding = evaluate(acme.corpus, Proposal(EQUITY), at=acme.at(AT[11]))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A3",)
    assert len(finding.endorsements) == 2


def test_b12_the_budget_carries_on_two_slots_of_three(acme):
    """Row 12: unity reached though one party never acted, and seat 3's
    endorsement carries its DI2I edge to the seat credential.

    Dev's slot is not a no and not a yes. Unity is reached without it, which is
    what a threshold means and what a quorum count would have obscured.
    """
    finding = evaluate(acme.corpus, Proposal(BUDGET), at=acme.at(AT[12]))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("B1",)
    assert len(finding.endorsements) == 2, "two of three slots, and no act of Dev's"

    seats = acme.events[acme.at(AT[12]).seq]
    assert seats.body["i"] == acme.aid(SEAT)
    assert seats.body["acdc"]["e"]["qp"]["o"] == DI2I


def test_b13_the_same_signed_no_is_only_pending_under_three_slots(acme):
    """Row 13: seat 3's slot is still reachable, so a declination delays rather
    than defeats. Demo 1's centerpiece, re-cut for the seated board.

    The same signed no as D3's, and the fold draws a different consequence from
    it because the law now has three slots and unity is still within reach of
    the one that has not acted. Nothing about the declination changed.
    """
    finding = evaluate(acme.corpus, Proposal(BUDGET), at=acme.at(AT[13]))
    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [acme.aid(SEAT)]
    assert [element.clause for element in finding.requirement] == ["B1"]
    assert [element.species for element in finding.requirement] == [PendingSpecies.ABSENT]

    declining = acme.events[acme.at(AT[13]).seq]
    assert declining.body["i"] == acme.aid(DEV)
    assert declining.body["acdc"]["a"]["disp"] == "decline"


def test_b14_an_unseated_endorser_fails_credential_verification_before_any_fold(acme):
    """Row 14: the DI2I edge names a seat credential whose issuee Quinn is not,
    and the fold's separate answer is unchanged. The two currents stay unmerged.

    This beat is not a committed event and cannot be: under refusal at
    commitment (``this.i`` @x7crwavm) the attempt never reaches the record, so
    the driver performs it live and the CLI prints the refusal. The row is
    therefore written as the attempt itself — the claim really is made, and
    really is refused.
    """
    constructor = Constructor.resume(
        acme.substrate, acme.gaid, values=acme.values, events=acme.events
    )
    seating = acme.events[acme.at("b8").seq]
    before = len(constructor.emitted)

    with pytest.raises(BakoboError) as refused:
        constructor.endorse(
            acme.aid(QUINN),
            acme.said(Q2_FORECAST),
            qualification=seating.body["acdc"]["d"],
        )

    assert refused.value.code == "e.proof.edge-unvalidated.f"
    assert not refused.value.retryable, "an unseated endorser stays unseated"
    assert len(constructor.emitted) == before, "the record did not move"

    # The fold's own answer, recomputed over the unchanged record: still row
    # 13's. The toolchain's current ran and stopped; the governance current
    # never heard about it.
    finding = evaluate(acme.corpus, Proposal(BUDGET), at=acme.at(AT[13]))
    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [acme.aid(SEAT)]


def test_b15_the_delegated_device_fills_the_seats_slot(acme):
    """Row 15: DI2I validates because the issuer is a delegated AID of the
    issuee. Same slot, different key, no law change.

    The script's "via device" is two committed facts and neither is the
    delegation. The seat's GCD grant is what lets the device act at all, and the
    fold finds it by searching the record rather than by following anything the
    endorsement claims (``this.i`` @cglayqvw). DI2I is the toolchain's separate
    check on the edge to the seat credential, which is what makes the *unseated*
    case of row 14 fail — the two currents, again, on one act.
    """
    before = evaluate(acme.corpus, Proposal(BUDGET), at=acme.at(AT[13]))
    assert isinstance(before, Pending), "row 13's question, which the device carries"

    finding = evaluate(acme.corpus, Proposal(BUDGET), at=acme.at(AT[15]))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("B1",)

    acting = acme.events[acme.at(AT[15]).seq]
    assert acting.body["i"] == acme.aid(DEVICE), "the device signed, not the seat"
    assert acting.body["acdc"]["e"]["qp"]["o"] == DI2I
    seating = acme.events[acme.at("b8").seq]
    assert acting.body["acdc"]["e"]["qp"]["n"] == seating.body["acdc"]["d"]


def test_b15_the_device_acts_under_a_grant_the_seat_can_revoke(acme):
    """The half of row 15 the script does not say out loud, and the reason the
    row is safe: the device's authority is a credential, not a relationship.

    The KERI delegation behind the device is permanent — keripy has no
    un-delegation, and a delegate's interaction events need no approval ever —
    so if the delegation conferred the authority there would be no way to end
    it. The grant is issued by the seat, names the device as issuee, and stands
    in the domain's registry until the seat says otherwise.
    """
    grant = acme.events[acme.at("device-granted").seq].body["acdc"]

    assert grant["s"] == GCD_SCHEMA
    assert grant["i"] == acme.aid(SEAT), "the seat grants what the seat holds"
    assert grant["a"]["i"] == acme.aid(DEVICE)
    assert grant["a"]["constraints"] == {"acts": ["create commitment"]}
    assert grant["ri"] != acme.registry, "the seat's own registry, not the domain's"
    assert acme.substrate.registry_state(grant["ri"], grant["d"]) == ISSUED


# --- Act III — revocation, and what it cannot do ------------------------------


def test_b16_the_registry_screen_shows_the_revocation():
    """Row 16: a rev event against the seat credential, with seat 3's KEL
    untouched and its keys still valid."""
    pytest.skip(owed("U4.2 the registry screen (tick 27x5)"))


def test_b16_the_revocation_moves_the_registry_and_not_the_key_log(acme):
    """The substance the screen will show, which the record already carries.

    "Registry state is evidence. Standing is judgment." What the revocation
    moves is what a registry says about a credential; seat 3's key log is
    untouched, its keys still verify, and nothing about the office changed. A
    demo that could not show those two facts side by side would be showing
    revocation as a punishment rather than as a state transition.
    """
    revocation = acme.events[acme.at(AT[16]).seq]
    credential = acme.events[acme.at("b8").seq].body["acdc"]["d"]

    assert revocation.kind == "revocation"
    assert revocation.body["said"] == credential
    assert revocation.body["ri"] == acme.registry
    assert acme.substrate.registry_state(acme.registry, credential) == REVOKED

    seat = acme.aid(SEAT)
    assert acme.substrate.delegator_of(seat) == acme.aid(GAID), "still a delegate of Acme"
    assert acme.substrate.verify(seat, revocation.body, revocation.body["sig"]) is False
    seating = acme.events[acme.at("b8").seq]
    assert acme.substrate.verify(
        acme.gaid, seating.body, seating.body["sig"]
    ), "the keys that signed before still verify after"


def test_b17_a_new_question_after_the_revocation_is_pending(acme):
    """Row 17: a typed requirement naming seat 3's slot — required schema,
    expected issuer, citing clause.

    The revocation is not a verdict about the Q3 budget and the fold does not
    treat it as one. The slot is simply unfilled, and what the finding owes a
    reader is what *would* fill it, which is the requirement's whole job.
    """
    finding = evaluate(acme.corpus, Proposal(BUDGET), at=acme.at(AT[17]))
    assert isinstance(finding, Pending)

    seat = next(one for one in finding.requirement if one.endorser == acme.aid(SEAT))
    assert seat.clause == "B1"
    assert seat.schema == ENDORSEMENT_SCHEMA
    assert seat.species is PendingSpecies.ABSENT


def test_b18_the_earlier_finding_is_byte_identical_when_re_asked_at_its_position(acme):
    """Row 18: re-asking row 12's question at row 12's position, ground included."""
    budget = acme.said(BUDGET_ACT)
    first = evaluate(acme.corpus, Committed(budget), at=acme.at(AT[12]))
    again = evaluate(acme.corpus, Committed(budget), at=acme.at(AT[18]))

    assert isinstance(again, Affirmed)
    assert again == first, "byte-identical, ground included, and not merely equivalent"


def test_b19_a_prospective_revocation_falsifies_no_cited_ground(acme):
    """Row 19, the surprising half: re-asked at a position *after* the
    revocation, the credential stood at that position and the finding stands.

    This is the claim the whole of Act III turns on, and it is one rule rather
    than a special case: a citation is judged at the coordinate of the act that
    made it. The seat's endorsement cited a credential that stood when it was
    cited, and nothing committed later unmakes that. A revocation that reached
    back would mean any issuer could unmake any past finding at any distance,
    unilaterally.
    """
    budget = acme.said(BUDGET_ACT)
    before = evaluate(acme.corpus, Committed(budget), at=acme.at(AT[12]))
    after = evaluate(acme.corpus, Committed(budget), at=acme.at(AT[19]))

    assert isinstance(after, Affirmed)
    assert after.clauses == before.clauses
    assert after.endorsements == before.endorsements

    # The BUNDLE differs, and it has to. Issue #82's third rule makes registry
    # state a member of the evidence bundle rather than an ambient condition, so
    # a revocation is a new span, a new bundle, and a finding at a new position.
    # Row 18 is byte-identical because it is asked at beat 12's own coordinate;
    # this one is the same answer over demonstrably different evidence, which is
    # the stronger statement of the two.
    assert after.bundle != before.bundle
    assert after != before

    credential = acme.events[acme.at("b8").seq].body["acdc"]["d"]
    assert acme.substrate.registry_state(acme.registry, credential) == REVOKED


def test_b20_duplicity_at_the_signing_position_is_self_convicted():
    """Row 20: the canonical proof package naming the contradictory pair, and the
    statement that superseding recovery does not reconcile it. Revocation and
    undercut never share a code path."""
    pytest.skip(
        owed(
            "U2.3 the undercut, via bearing, structurally separate from revocation (tick 3h6k)",
        )
    )


# --- Act IV — the amendment that lies -----------------------------------------


def test_b21_a_second_question_is_pending_under_b1(acme):
    """Row 21: the capital plan, pending alongside row 17's Q3 budget.

    Two acts in flight under one clause, which is what makes beat 23's
    computed disturbance set a set rather than a singleton — and therefore what
    makes an amendment naming only one of them falsifiable.
    """
    finding = evaluate(acme.corpus, Committed(acme.said(CAPITAL_PLAN)), at=acme.at(AT[21]))
    assert isinstance(finding, Pending)
    assert {one.clause for one in finding.requirement} == {"B1"}
    assert {one.endorser for one in finding.requirement} == {acme.aid(DEV), acme.aid(SEAT)}

    q3 = evaluate(acme.corpus, Committed(acme.said(Q3_BUDGET)), at=acme.at(AT[21]))
    assert isinstance(q3, Pending), "and beat 17's is still pending beside it"


def test_b22_the_second_amendment_declares_a_disturbance_set_that_under_declares():
    """Row 22: the enactment's declared set names only the Q3 budget, and not the
    capital plan."""
    pytest.skip(owed("U3.3 the declared disturbance set on the amending enactment (tick 7rfv)"))


def test_b23_the_under_declaring_amendment_is_convicted_on_its_own_bytes():
    """Row 23: declared set against computed set, side by side; the computed set
    contains both B1 questions, and the mismatch is the proof."""
    pytest.skip(owed(
        "U3.3 the fold's computed disturbance set and self-convicted on mismatch (tick 7rfv)",
        "the finding value an under-declaring amendment returns, owed to Custos (tick 7xe6)",
    ))


# --- Coda ---------------------------------------------------------------------


def test_b24_the_past_is_recomputed_under_the_law_in_force_then(acme):
    """Row 24: row 2's question, asked from the end of the log, still under A1."""
    finding = evaluate(acme.corpus, Committed(acme.said(BANK)), at=acme.at(AT[24]))
    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A1",)


def test_b25_permuted_arrival_folds_to_a_byte_identical_constitution(acme):
    """Row 25: binding at custos-4.2.md:3101 — byte-identical, not equivalent."""
    straight = Constitution.at(acme.corpus, acme.at(AT[25]))
    shuffled = Constitution.at(acme.permuted_corpus(seed=7), acme.at(AT[25]))
    assert straight.canonical_bytes() == shuffled.canonical_bytes()


# --- The script's own completeness check --------------------------------------


def test_every_beat_of_the_script_has_a_row_here():
    """Twenty-five beats, twenty-five cases, and the numbering is contiguous.

    The failure this guards against is a row of the script with no case at all,
    which is invisible: a missing test does not fail, and an oracle that is
    quietly short of its script is the one artifact whose silence lies.
    """
    cases = {
        int(name[6:8])
        for name in globals()
        if name.startswith("test_b") and name[6:8].isdigit()
    }
    assert cases == set(range(1, 26))
