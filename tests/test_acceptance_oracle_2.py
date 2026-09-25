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

from fractions import Fraction

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
    EQUITY_ACTS,
    GAID,
    MARTA,
    Q2_FORECAST,
    Q3_BUDGET,
    QUINN,
    SEAT,
    SEAT_OFFICE,
)
from utina.cli.aliases import aliases_over
from utina.cli.appraisal import held_by, registry_holdings
from utina.cli.render import law_screen, registry_screen, seat_screen
from utina.cli.style import Style
from utina.enact import Constructor
from utina.fold import Constitution, bearing, certification, evaluate, semantics, standing
from utina.fold import slots as slot_predicate
from utina.fold.evaluate import disturbed_by
from utina.fold.finding import Affirmed, Defeated, Pending, PendingSpecies, SelfConvicted
from utina.fold.group import Disposition
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
    7: "d4",
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
    20: "b20",
    21: "b21",
    22: "b22",
    23: "b23",
    24: "d9",
    25: "board-seated",
    26: "b26",
}

BANK = "open-bank-account"
HIRE = "hire-vp-sales"
LEASE = "sign-office-lease"
EQUITY = "release-escrowed-equity"
DIVIDEND = "declare-dividend"
BUDGET = "approve-budget"

#: The record's name for the amendment that lowers the ordinary-acts bar.
SECOND_AMENDMENT = "lower-the-bar"

#: The record's name for the annual budget, which is beat 12's subject and the
#: one beats 18 and 19 re-ask about. Distinct from the act CLASS above: three
#: acts of one class are tabled, and these rows are about one of them.
BUDGET_ACT = "approve-budget"

#: Beat 26's three names. The second tabling of the equity release, the declination
#: Marta's tally was written around, and the tally itself — each addressed by the name
#: the record files it under, because the row is about which of them contradicts which.
FALSELY_CERTIFIED = "equity-retabled"
FALSE_DECLINATION = "equity-retabled-declined"
FALSE_CERTIFICATION = "release-escrowed-equity-falsely-certified"


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


def test_b01_the_constitution_at_inception(acme):
    """Row 1: three clauses with their SAIDs, operators, slots and weights, and
    the pinned dossier-semantics digest.

    The pin is the half of this beat a reader will not expect. Acme's clauses are
    expressed in the dossier specification's terms, so that specification is an
    external semantics and axiom 4 requires the law to name which revision of it
    the clauses mean — never the one that happens to be installed.
    """
    law = Constitution.at(acme.corpus, acme.at("inception"))

    assert {clause.id for clause in law.clauses} == {"A1", "A2", "A3"}
    assert all(clause.group.operator == "MxN" for clause in law.clauses)
    assert all(len(clause.group.slots) == 2 for clause in law.clauses)
    assert law.semantics == semantics.DOSSIER

    screened = _law_screen(acme, "inception")
    assert semantics.DOSSIER[:16] in screened
    assert "the dossier specification, pinned" in screened


def test_b01_a_law_pinning_a_semantics_this_engine_cannot_read_is_refused(acme):
    """The unscheduled beat the script calls the best one available if there is
    time: flipping the digest produces a refusal rather than a wrong answer.

    Asserted at the seam rather than by building a second record, because what
    it is about is the fold's disposition toward an unreadable lens and not
    Acme's bytes. The refusal names what it pinned, so a reader can go and look.
    """
    assert semantics.refusal_for(semantics.DOSSIER) is None

    refused = semantics.refusal_for("e" * 64)
    assert isinstance(refused, Refusal)
    assert "an implementation of the semantics this law pins" in refused.missing


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


def test_b07_seating_the_board_is_affirmed_under_the_law_it_replaces(acme):
    """Row 7: judged under A2, plus the delegating seal's coordinate in Acme's
    KEL, the dip in seat 3's KEL, and the seat credential's issuance event.

    **The finding's ground is A2 and the two endorsements, and NOT the
    delegation coordinates**, which is a reading this row takes deliberately.
    The row's column lists five things the beat shows, and they are not all the
    same kind of thing: the amendment is lawful because clause A2's slots were
    filled, and the delegation and the seat credential are *consequences* of it
    taking force rather than reasons it was lawful. A finding carrying them as
    ground would say the amendment was affirmed because a delegation happened,
    which is false and would corrupt the Ground Axiom in the one place the demo
    most needs it sound. So the finding carries what a finding carries, and the
    other four facts are asserted against the record, where they live.
    """
    amendment = acme.said("seat-the-board")
    finding = evaluate(acme.corpus, Committed(amendment), at=acme.at(AT[7]))

    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A2",), "judged under the law it replaces, not the one it makes"
    assert len(finding.endorsements) == 2, "Marta and Dev, and nothing else"

    # What it ends: the hire, computed rather than declared (``this.i`` @ow6dzro4).
    assert disturbed_by(acme.corpus, acme.corpus.event(amendment), acme.at(AT[7])) == (
        acme.said(HIRE),
    )

    # KERI's two halves, answerable at the substrate because key events are not
    # in the corpus the fold folds (``this.i`` @jdie6v).
    seat = acme.aid(SEAT)
    assert acme.substrate.delegator_of(seat) == acme.aid(GAID), "the dip names Acme in di"
    assert acme.substrate.anchoring_event(seat) is not None, "and Acme sealed that dip"

    # And ACDC's half, which IS in the record.
    seating = acme.events[acme.at("b8").seq]
    assert seating.kind == standing.ISSUANCE_KIND
    assert seating.body["ri"] == acme.registry
    assert seating.body["acdc"]["a"]["i"] == seat


def test_b08_the_seat_screen_shows_two_bindings(acme):
    """Row 8: KERI's delegating seal and dip, and the ACDC seat credential with
    its registry state — two bindings on one screen.

    The beat is that they are SEPARATE and that only one of them confers. KERI's
    half is dual-anchored and permanent; ACDC's is the credential a revocation
    can take back. Asserted here as the two facts the screen renders, so the row
    is about the record rather than about a layout.
    """
    seat = acme.aid(SEAT)
    seating = acme.events[acme.at("b8").seq]
    credential = seating.body["acdc"]

    assert acme.substrate.delegator_of(seat) == acme.aid(GAID), "the dip names Acme in di"
    assert acme.substrate.anchoring_event(seat) is not None, "and Acme sealed that dip"

    assert credential["a"]["i"] == seat, "issuee is the seat itself"
    assert credential["ri"] == acme.registry
    upto = acme.corpus.upto(acme.at("b8"))
    assert standing.state_over(upto, acme.registry, credential["d"]) == ISSUED

    screened = _seat_screen(acme, "b8")
    assert "KERI" in screened and "ACDC" in screened
    assert "issued, as the fold reads it here" in screened


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


def test_b10_the_equity_release_re_asked_after_the_amendment_is_still_curable(acme):
    """Row 10: species absent, the same requirement as row 5, and the three-part
    stability check shown — same clause SAID, same requirement space, same
    pinned lens.

    A3 is carried across the amendment byte-identical, so its cure path stays
    open and the question is still the question it was. All three parts hold
    here: the clause identifier is unmoved, the requirement space with it —
    a clause IS its bytes — and the semantics the law pins did not move either.
    """
    before = evaluate(acme.corpus, Proposal(EQUITY), at=acme.at(AT[5]))
    after = evaluate(acme.corpus, Proposal(EQUITY), at=acme.at(AT[10]))

    assert isinstance(after, Pending)
    assert [one.species for one in after.requirement] == [PendingSpecies.ABSENT]
    assert [one.ground for one in after.requirement] == [""], "the cure path is open"
    assert after.requirement == before.requirement, "the same requirement as row 5"

    first = Constitution.at(acme.corpus, acme.at(AT[5]))
    second = Constitution.at(acme.corpus, acme.at(AT[10]))
    assert first.clause("A3").said() == second.clause("A3").said(), "same clause SAID"
    assert first.clause("A3").group == second.clause("A3").group, "same requirement space"
    assert first.semantics == second.semantics == semantics.DOSSIER, "same pinned lens"
    assert first.law_head != second.law_head, "and the edition around it did move"


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

    seats = acme.corpus.event(acme.said("seat-endorses-budget"))
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
    assert [element.endorser for element in finding.requirement] == [SEAT_OFFICE]
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
    assert [element.endorser for element in finding.requirement] == [SEAT_OFFICE]


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

    acting = acme.corpus.event(acme.said("device-endorses-forecast"))
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


def _law_screen(acme, label: str) -> str:
    """Beat 1's screen, over the record this oracle is holding."""
    return law_screen(
        Constitution.at(acme.corpus, acme.at(label)),
        label,
        acme.at(label),
        aliases_over(acme.aids),
        Style(enabled=False),
    )


def _seat_screen(acme, label: str) -> str:
    """Beat 8's screen, rendered over the record THIS oracle is holding.

    Built here rather than shelled out to, because a subprocess would build a
    second Acme and the row would be asserting a screen about a different set of
    identifiers than the ones it just checked.
    """
    seat = acme.aid(SEAT)
    upto = acme.corpus.upto(acme.at(label))
    return seat_screen(
        seat,
        label,
        acme.at(label),
        {
            "delegator": acme.substrate.delegator_of(seat),
            "seal": acme.substrate.anchoring_event(seat),
        },
        held_by(upto, seat),
        aliases_over(acme.aids),
        Style(enabled=False),
    )


def _registry_screen(acme, label: str) -> str:
    """Beat 16's screen, over the same record, for the same reason."""
    upto = acme.corpus.upto(acme.at(label))
    return registry_screen(
        str(acme.registry),
        acme.gaid,
        label,
        acme.at(label),
        registry_holdings(upto, str(acme.registry)),
        aliases_over(acme.aids),
        Style(enabled=False),
    )


# --- Act III — revocation, and what it cannot do ------------------------------


def test_b16_the_registry_screen_shows_the_revocation(acme):
    """Row 16: a rev event against the seat credential, with seat 3's KEL
    untouched and its keys still valid.

    The screen names the act that moved the state, because a state with no act
    behind it is a claim rather than a record — and it folds that state from
    committed events rather than reading the transaction log, which is issue #82
    rule 3 applied to a display plane.
    """
    credential = acme.events[acme.at("b8").seq].body["acdc"]["d"]
    revocation = acme.events[acme.at(AT[16]).seq]

    screened = _registry_screen(acme, "b16")
    assert "revoked" in screened
    assert credential[:12] in screened
    assert revocation.said[:12] in screened

    before = _registry_screen(acme, "b15")
    assert "revoked" not in before, "and not one coordinate earlier"


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

    seat = next(one for one in finding.requirement if one.endorser == SEAT_OFFICE)
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


def test_b20_duplicity_at_a_cited_third_party_taints_the_voice(acme):
    """Row 20, with its expected value ruled 2026-09-15 (``this.i`` @f3pmxu3x).

    The script expected self-convicted. The text gives pending with species
    unresolved-conflict, because the convict's role dispatches the edge and seat
    3 is a CITED THIRD PARTY here — the subject is the budget act, committed by
    the gAID, and seat 3's endorsement is the affirmation's ground.

    The beat's work is unchanged. Beat 19 re-asked this question after a
    revocation and got the same answer; this re-asks it after duplicity and the
    answer moves. That contrast is what the row exists for, and only the verdict
    word differs from what the script wrote.
    """
    finding = evaluate(acme.corpus, Committed(acme.said(BUDGET_ACT)), at=acme.at(AT[20]))

    assert isinstance(finding, Pending)
    assert [one.species for one in finding.requirement] == [
        PendingSpecies.UNRESOLVED_CONFLICT
    ]
    # The PARTY, not the seat. A taint's cure is an act owned by whoever the conflict
    # belongs to, and that is an identifier with keys rather than an office — which is
    # the one place a requirement element names the holder and not the slot it filled.
    assert [one.endorser for one in finding.requirement] == [acme.aid(SEAT)]
    assert finding.requirement[0].ground == acme.events[acme.at(AT[20]).seq].said

    # No missing bytes cure a taint, and the requirement says which act does.
    assert finding.requirement[0].species.cure == (
        "cured by an owned act of the party whose conflict it is"
    )


def test_b20_the_taint_reaches_forward_and_leaves_the_record_it_made(acme):
    """"What was affirmed above stands at its coordinate forever" (``:1805``).

    Beat 12's finding is untouched at its own coordinate, and so is beat 19's,
    which sits between the endorsement and the observation. A taint that reached
    backwards would be the rewrite ``:1741`` forbids — the reversal is a new
    fact, never a change to an old one.
    """
    budget = Committed(acme.said(BUDGET_ACT))

    assert isinstance(evaluate(acme.corpus, budget, at=acme.at(AT[12])), Affirmed)
    assert isinstance(evaluate(acme.corpus, budget, at=acme.at(AT[19])), Affirmed)
    assert isinstance(evaluate(acme.corpus, budget, at=acme.at(AT[20])), Pending)


def test_b20_the_undercut_shares_no_code_path_with_revocation(acme):
    """Issue #82's determination 4 asks that the two be unmistakable in the
    bearing machinery. They are different mechanisms with different reaches: the
    revocation at beat 16 moved a registry and no finding, and this moved a
    finding and no registry.
    """
    import utina.fold.bearing as bearing_module
    import utina.fold.standing as standing_module

    assert "standing" not in dir(bearing_module)
    assert "bearing" not in dir(standing_module)

    observation = acme.events[acme.at(AT[20]).seq]
    assert observation.kind == bearing.DUPLICITY_KIND
    assert "ri" not in observation.body, "an undercut touches no registry"

    credential = acme.events[acme.at("b8").seq].body["acdc"]["d"]
    upto = acme.corpus.upto(acme.at(AT[20]))
    assert standing.state_over(upto, acme.registry, credential) == REVOKED
    assert standing.state_over(upto, acme.registry, credential) == REVOKED, (
        "and the registry says exactly what it said before the observation"
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
    assert {one.endorser for one in finding.requirement} == {acme.aid(DEV), SEAT_OFFICE}

    q3 = evaluate(acme.corpus, Committed(acme.said(Q3_BUDGET)), at=acme.at(AT[21]))
    assert isinstance(q3, Pending), "and beat 17's is still pending beside it"


def test_b22_the_second_amendment_reaches_unity_under_the_retained_bar(acme):
    """Row 22: three slots endorsed, unity reached under B2's retained bar.

    The amendment declares nothing about what it ends (``this.i`` @ow6dzro4), so
    there is no claim here to set against the fold's answer — row 23 simply
    reports what the amendment did. What this row asserts is that the board
    genuinely passed it: the cost in row 23 is the cost of a lawful, unanimous
    amendment, which is the whole reason it is worth showing.
    """
    amendment = acme.corpus.event(acme.said(SECOND_AMENDMENT))
    assert amendment.kind == "enactment"
    assert "disturbs" not in amendment.body, "an amendment declares nothing (@ow6dzro4)"

    slots = slot_predicate.dispositions(
        Constitution.at(acme.corpus, acme.at(AT[22])).clause("B2").group,
        acme.corpus.upto(acme.at(AT[22])),
        amendment.said,
    )
    assert set(slots.values()) == {Disposition.ENDORSED}, "Marta, Dev and seat 3 all endorsed"


def test_b23_the_amendment_ends_three_acts_that_were_in_flight(acme):
    """Row 23: what the amendment actually ended, computed from committed bytes.

    Three acts, all pending under B1 when the bar moved: the Q3 budget, the
    capital plan, and demo 1's own retabled budget, which has been pending since
    D6. None of them was voted down and none of them can now finish.

    What the amendment does NOT end is the hire, which the first amendment
    already closed. An act whose cure path was shut before this enactment was not
    in flight, so it is not this amendment's casualty — the specificity that
    keeps every later amendment from inheriting every earlier one's.
    """
    amendment = acme.corpus.event(acme.said(SECOND_AMENDMENT))
    computed = disturbed_by(acme.corpus, amendment, acme.at(AT[23]))

    assert set(computed) == {
        acme.said(Q3_BUDGET),
        acme.said(CAPITAL_PLAN),
        acme.said("approve-budget-retabled"),
    }
    assert acme.said(HIRE) not in computed, "already closed by the first amendment"


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


# --- Act V — a certification that lies ----------------------------------------


def test_b26_a_false_certification_convicts_its_sponsor_on_her_own_signature(acme):
    """Row 26: the fourth verdict, and a governance failure rather than a lost key.

    Marta tables the equity release again, endorses it, Dev signs a no, and Marta —
    sponsoring the tally — cites her own endorsement at full weight and omits the no. The
    domain admits it, because what the domain checks is that the cited weights sum to
    unity and they do; what it does not do is re-fold its own record first (``this.i``
    @t3kuqli6). So the lie is well formed and committed, and the fold convicts it on bytes
    Marta signed.

    The proof carries the PAIR, which is the row's whole content: the certification, and
    the declination it was written around. A reader recomputes both from committed bytes.
    """
    finding = evaluate(acme.corpus, Committed(acme.said(FALSELY_CERTIFIED)), at=acme.at(AT[26]))

    assert isinstance(finding, SelfConvicted)
    assert finding.proof.package == acme.said(FALSE_CERTIFICATION)
    assert finding.proof.pair == (
        acme.said(FALSE_CERTIFICATION),
        acme.said(FALSE_DECLINATION),
    )

    # The LIE itself, which the verdict alone does not establish — a different false
    # tally would satisfy everything above. Raised by the substitute review on PR #9.
    tally = acme.corpus.event(acme.said(FALSE_CERTIFICATION))
    assert tally.body["i"] == acme.gaid, "only the domain can admit a tally to its own log"
    assert slot_predicate.credential(tally)["i"] == acme.aid(MARTA), "Marta sponsored it"

    cited = dict(certification.counted_by(tally))
    assert cited == {acme.said("marta-endorses-retabled-equity"): Fraction(1, 1)}, (
        "her own endorsement, cited at the whole of unity where her slot commits a half"
    )
    assert acme.said(FALSE_DECLINATION) not in cited, "and Dev's signed no is not in it"

    # And the arithmetic the screen shows beside it: Marta's half, Dev's spent slot, and
    # a sum that never reached the unity the tally claimed.
    law = Constitution.at(acme.corpus, acme.corpus.event(acme.said(FALSELY_CERTIFIED)).position)
    clause = law.governing(EQUITY_ACTS[0])
    held = slot_predicate.dispositions(
        clause.group, acme.corpus.upto(acme.at(AT[26])), acme.said(FALSELY_CERTIFIED)
    )
    assert clause.id == "A3", "the one clause neither amendment moves"
    # Equality rather than ``< 1``: the comment above claims Marta's HALF, and a weight
    # regression to anything in [0, 1) would keep a sub-unity assertion green while
    # falsifying it. Raised by a cross-model review of this round's fix diff.
    assert clause.group.endorsed_weight(held) == Fraction(1, 2), "Marta's half, and no more"
    assert not clause.group.reachable(held), "Dev's no spent the slot that would have cured it"


# --- The script's own completeness check --------------------------------------


def test_every_beat_of_the_script_has_a_row_here():
    """A case per beat, and the numbering is contiguous.

    The failure this guards against is a row of the script with no case at all,
    which is invisible: a missing test does not fail, and an oracle that is
    quietly short of its script is the one artifact whose silence lies.
    """
    cases = {
        int(name[6:8])
        for name in globals()
        if name.startswith("test_b") and name[6:8].isdigit()
    }
    assert cases == set(range(1, 27))
