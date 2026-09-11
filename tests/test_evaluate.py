"""The evaluator: the fold's entry point, and the order it works in.

These are the inner tests. They build committed evidence by hand rather than
through ``utina.acme``, so that each rule of the order of operations can be put
under a case of its own — the acceptance oracle exercises the same evaluator
over the demo's real log, and a failure there should have a failure here that
says which rule broke.

The order is ``docs/interfaces.md``'s and it is not an implementation detail:

1. no governing clause is a refusal, never a finding;
2. the complete requirement space is built before anything is returned;
3. every slot is classified from committed evidence at or before the position;
4. unity reached is affirmed;
5. unity unreachable is what ``UNREACHABLE_YIELDS`` says it is;
6. otherwise pending, with the outstanding slots named.
"""

from __future__ import annotations

import importlib
from fractions import Fraction

import pytest

from utina.fold import disturbance
from utina.fold.corpus import Corpus, Event
from utina.fold.evaluate import UNREACHABLE_YIELDS, appraisal_triple, evaluate
from utina.fold.finding import (
    Affirmed,
    Defeated,
    DefeaterClass,
    Pending,
    PendingSpecies,
    SelfConvicted,
    Verdict,
)
from utina.fold.question import Committed, Proposal
from utina.fold.refusal import Refusal
from utina.fold.triple import Position
from utina.substrate import ENDORSEMENT_SCHEMA

MARTA, DEV, NINA = "acme:marta", "acme:dev", "acme:nina"
GAID = "acme:gaid"

#: What every slot below names as the schema its evidence must satisfy.
SCHEMA = ENDORSEMENT_SCHEMA


# --- a committed log, built by hand -------------------------------------------


def slots(*pairs):
    """Committed slots. Each names the schema its evidence must satisfy, which is
    committed law rather than an engine constant (custos-4.2.md:1946-1951)."""
    return [
        {"endorser": who, "weight": weight, "schema": SCHEMA} for who, weight in pairs
    ]


def clause(identifier, governs, *pairs):
    return {
        "id": identifier,
        "governs": list(governs),
        "group": {"operator": "MxN", "slots": slots(*pairs)},
    }


FOUNDERS_LAW = [
    clause("A1", ["hire"], (MARTA, "1/2"), (DEV, "1/2")),
    clause("A2", ["amend"], (MARTA, "1/2"), (DEV, "1/2")),
]

BOARD_LAW = [
    clause("B1", ["hire"], (MARTA, "1/2"), (DEV, "1/2"), (NINA, "1/2")),
    clause("B2", ["amend"], (MARTA, "1/3"), (DEV, "1/3"), (NINA, "1/3")),
]


class Log:
    """A committed log under construction, addressed by the names it gives events."""

    def __init__(self):
        self.events: list[Event] = []
        self.saids: dict[str, str] = {}

    def _add(self, name: str, kind: str, body: dict[str, object]) -> str:
        said = f"E{len(self.events)}-{name}"
        self.events.append(
            Event(said=said, kind=kind, position=Position(len(self.events)), body=body)
        )
        self.saids[name] = said
        return said

    def law(self, name: str, kind: str, clauses: list[dict[str, object]]) -> str:
        return self._add(name, kind, {"t": kind, "i": GAID, "law": {"clauses": clauses}})

    def act(self, name: str, kind: str) -> str:
        return self._add(name, "act", {"t": "act", "i": GAID, "act": kind})

    def amend(self, name: str, clauses, act: str = "amend", disturbs=None) -> str:
        body: dict[str, object] = {
            "t": "enact",
            "i": GAID,
            "act": act,
            "law": {"clauses": clauses},
        }
        if disturbs is not None:
            body["disturbs"] = tuple(disturbs)
        return self._add(name, "enactment", body)

    def dispose(self, who: str, subject: str, disposition: str) -> str:
        name = f"{disposition}-{who}"
        return self._add(
            name,
            "endorsement",
            {
                "t": "end",
                "i": who,
                "acdc": {
                    "v": "ACDCtest",
                    "d": f"E{name}-credential",
                    "i": who,
                    "s": ENDORSEMENT_SCHEMA,
                    "a": {
                        "d": f"E{name}-attributes",
                        "dt": "2026-01-01T00:00:00.000000+00:00",
                        "said": subject,
                        "act": "issue",
                        "disp": disposition,
                    },
                },
                "acdc_sig": f"E{name}-sig",
            },
        )

    def endorse(self, who: str, subject: str) -> str:
        return self.dispose(who, subject, "endorse")

    def decline(self, who: str, subject: str) -> str:
        return self.dispose(who, subject, "decline")

    def retract(self, who: str, target: str) -> str:
        """``who`` withdrawing their own earlier act, which the fold reads and
        nothing in ``utina.enact`` can yet write (ticks ``3z6a``, ``56js``)."""
        body = {"t": "ret", "i": who, "revokes": target}
        return self._add(f"retract-{who}", "retraction", body)

    @property
    def corpus(self) -> Corpus:
        return Corpus.load(self.events)

    @property
    def now(self) -> Position:
        return Position(len(self.events) - 1)

    def said(self, name: str) -> str:
        return self.saids[name]


@pytest.fixture
def founded() -> Log:
    log = Log()
    log.law("inception", "inception", FOUNDERS_LAW)
    return log


# --- 1. the refusal hinge ------------------------------------------------------


def test_an_act_no_clause_governs_is_refused(founded):
    """Axiom 3: where committed law runs out, the fold refuses and names what is missing."""
    outcome = evaluate(founded.corpus, Proposal("declare-dividend"), at=founded.now)

    assert isinstance(outcome, Refusal)
    assert "declare-dividend" in outcome.missing
    assert outcome.detail != ""


def test_a_refusal_is_not_a_finding(founded):
    """It must never be substitutable for one — the separation is the point."""
    outcome = evaluate(founded.corpus, Proposal("declare-dividend"), at=founded.now)

    assert not isinstance(outcome, Affirmed | Defeated | Pending)


def test_a_question_about_bytes_nobody_committed_is_refused(founded):
    outcome = evaluate(founded.corpus, Committed("E-never-committed"), at=founded.now)

    assert isinstance(outcome, Refusal)
    assert "E-never-committed" in outcome.missing


def test_a_question_about_an_act_committed_later_than_the_position_is_refused(founded):
    """Fail closed: an act the position cannot see is not evidence at that position."""
    founded.act("hire", "hire")

    outcome = evaluate(founded.corpus, Committed(founded.said("hire")), at=Position(0))

    assert isinstance(outcome, Refusal)


def test_a_question_about_bytes_that_claim_no_act_class_is_refused(founded):
    """An endorsement is committed bytes, and it is not an act any clause governs.

    Its ``act`` field carries the registry operation rather than a class of act,
    which is exactly the confusion the fold must not make: reading ``"issue"`` as
    an act class would have the endorsement judged instead of the decision.
    """
    hire = founded.act("hire", "hire")
    endorsement = founded.endorse(MARTA, hire)

    outcome = evaluate(founded.corpus, Committed(endorsement), at=founded.now)

    assert isinstance(outcome, Refusal)
    assert "act class" in outcome.missing


def test_a_question_about_the_inception_itself_is_refused(founded):
    """Genesis is constructed rather than judged (``:2272-2274``)."""
    outcome = evaluate(founded.corpus, Committed(founded.said("inception")), at=founded.now)

    assert isinstance(outcome, Refusal)


def test_a_clause_whose_slots_cannot_sum_to_unity_defeats_without_a_declination():
    """Unreachable with nothing spent: the clause itself can never be satisfied.

    No slot declined, so there is no signed no to cite, and the citation carries
    the clause alone. It is still a defeat and not a pending: a pending would
    have to name a cure, and there is none — no arrangement of endorsements
    satisfies a group whose whole weight is less than unity.
    """
    log = Log()
    log.law("inception", "inception", [clause("A1", ["hire"], (MARTA, "1/3"), (DEV, "1/3"))])
    hire = log.act("hire", "hire")
    log.endorse(MARTA, hire)
    log.endorse(DEV, hire)

    finding = evaluate(log.corpus, Proposal("hire"), at=log.now)

    assert isinstance(finding, Defeated)
    assert finding.citation.clause == "A1"
    assert finding.citation.declination is None
    assert finding.citation.reason != ""


def test_an_unsatisfiable_clause_stays_a_defeat_under_the_flipped_reading(monkeypatch):
    """The flip has a floor: with no spent slot to name, ``Pending`` is unbuildable.

    The Ground Axiom, not a convenience — a pending finding carrying an empty
    requirement set is not a pending finding, so where the other reading has
    nothing to say the citation is what the fold has.
    """
    evaluator = importlib.import_module("utina.fold.evaluate")
    log = Log()
    log.law("inception", "inception", [clause("A1", ["hire"], (MARTA, "1/3"), (DEV, "1/3"))])
    hire = log.act("hire", "hire")
    log.endorse(MARTA, hire)
    log.endorse(DEV, hire)
    monkeypatch.setattr(evaluator, "UNREACHABLE_YIELDS", Pending)

    assert isinstance(evaluate(log.corpus, Proposal("hire"), at=log.now), Defeated)


def test_a_domain_with_no_committed_law_refuses_everything(founded):
    outcome = evaluate(Corpus.load([]), Proposal("hire"), at=Position(0))

    assert isinstance(outcome, Refusal)


# --- 4. unity reached ----------------------------------------------------------


def test_unity_reached_is_affirmed_and_carries_its_ground(founded):
    hire = founded.act("hire", "hire")
    first = founded.endorse(MARTA, hire)
    second = founded.endorse(DEV, hire)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A1",)
    assert set(finding.endorsements) == {first, second}
    assert finding.bundle != ""


def test_an_affirmation_carries_every_endorsement_that_reached_unity(founded):
    """Never short-circuit: the whole space is built, so the ground is complete."""
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.endorse(DEV, hire)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert len(finding.endorsements) == 2


def test_the_bundle_identifier_is_a_function_of_the_committed_evidence(founded):
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.endorse(DEV, hire)
    corpus, at = founded.corpus, founded.now

    first = evaluate(corpus, Proposal("hire"), at=at)
    again = evaluate(Corpus.load(list(reversed(founded.events))), Proposal("hire"), at=at)

    assert first.bundle == again.bundle


# --- 6. pending, and the requirement space it names ----------------------------


def test_an_untouched_slot_is_pending_naming_that_slot(founded):
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV]


def test_a_pending_requirement_element_carries_its_kind_and_species(founded):
    """Both fields are populated by the evaluator, never left to a default."""
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)

    element = evaluate(founded.corpus, Proposal("hire"), at=founded.now).requirement[0]

    assert element.clause == "A1"
    assert element.kind == "endorsement"
    assert element.species is PendingSpecies.ABSENT


def test_a_proposal_nobody_has_acted_on_names_every_slot(founded):
    """The complete requirement space, not the first missing element."""
    founded.act("hire", "hire")

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV, MARTA]


def test_a_proposal_with_no_committed_act_at_all_is_pending_on_every_slot(founded):
    """The law governs the class; nothing has been tabled, so nothing is endorsed."""
    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV, MARTA]


def test_the_requirement_set_is_canonically_ordered(founded):
    log = Log()
    log.law("inception", "inception", BOARD_LAW)
    hire = log.act("hire", "hire")
    log.endorse(NINA, hire)

    finding = evaluate(log.corpus, Proposal("hire"), at=log.now)

    keys = [element.sort_key() for element in finding.requirement]
    assert keys == sorted(keys)


# --- 3. dispositions are read at or before the position ------------------------


def test_evidence_after_the_position_does_not_count(founded):
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    before_dev_acts = founded.now
    founded.endorse(DEV, hire)

    assert isinstance(evaluate(founded.corpus, Proposal("hire"), at=founded.now), Affirmed)
    assert isinstance(
        evaluate(founded.corpus, Proposal("hire"), at=before_dev_acts), Pending
    )


def test_an_endorsement_from_someone_the_clause_does_not_slot_adds_nothing(founded):
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.endorse(NINA, hire)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV]


# --- 5. unity unreachable ------------------------------------------------------


def test_unity_unreachable_yields_the_pinned_finding(founded):
    """The demo's centerpiece, and the one reading the maintainer may still flip."""
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.decline(DEV, hire)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, UNREACHABLE_YIELDS)


def test_an_unreachable_defeat_cites_the_clause_and_the_signed_no(founded):
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    said = founded.decline(DEV, hire)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Defeated)
    assert finding.citation.clause == "A1"
    assert finding.citation.declination.endorser == DEV
    assert finding.citation.declination.said == said
    assert finding.citation.defeater_class is DefeaterClass.AUTHORITY
    assert finding.citation.reason != ""


def test_a_declination_that_leaves_unity_reachable_is_only_pending(founded):
    """Three slots at a half: the same signed no, and the arithmetic differs."""
    log = Log()
    log.law("inception", "inception", BOARD_LAW)
    hire = log.act("hire", "hire")
    log.endorse(MARTA, hire)
    log.decline(DEV, hire)

    finding = evaluate(log.corpus, Proposal("hire"), at=log.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [NINA]


def test_a_retraction_after_the_act_settles_leaves_the_affirmation_standing(founded):
    """R1's measurement, at the level it was measured: the finding does not come apart.

    Both founders endorse the hire, and it is affirmed. Dev then withdraws the
    endorsement he gave. Under the unconditional filter the same question came
    back pending, carrying a requirement element naming Dev's slot ``absent``,
    "cured by the arrival of the missing evidence" — the arrival of evidence that
    had already arrived. ``:1698-1712`` forbids that edge (this.i @nuxitore).
    """
    hire = founded.act("hire", "hire")
    from_marta = founded.endorse(MARTA, hire)
    from_dev = founded.endorse(DEV, hire)
    founded.retract(DEV, from_dev)

    finding = evaluate(founded.corpus, Committed(hire), at=founded.now)

    assert isinstance(finding, Affirmed)
    assert finding.endorsements == (from_marta, from_dev)


def test_a_retraction_while_the_act_is_in_flight_returns_the_slot_to_pending(founded):
    """The live case, which the same rule has to keep working.

    Marta endorses and withdraws it before Dev acts. Nothing has settled, so the
    withdrawal reaches the act and her slot owes an endorsement again — which is
    what a pending requirement element correctly says can cure it.
    """
    hire = founded.act("hire", "hire")
    given = founded.endorse(MARTA, hire)
    founded.retract(MARTA, given)

    finding = evaluate(founded.corpus, Committed(hire), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV, MARTA]


def test_the_defeat_is_selected_canonically_where_two_slots_declined(founded):
    """Two verifiers holding the same bundle emit the same finding (``:1766-1770``)."""
    log = Log()
    log.law("inception", "inception", BOARD_LAW)
    amend = log.act("amend", "amend")
    log.decline(DEV, amend)
    log.decline(NINA, amend)

    finding = evaluate(log.corpus, Proposal("amend"), at=log.now)
    again = evaluate(Corpus.load(list(reversed(log.events))), Proposal("amend"), at=log.now)

    assert isinstance(finding, Defeated)
    assert finding == again


# --- the flip: one constant, one function --------------------------------------


def test_the_unreachable_reading_is_one_line_to_flip(founded, monkeypatch):
    """``UNREACHABLE_YIELDS`` is the whole switch, and the other branch works.

    ``custos-4.2.md:1966`` reads an unsatisfied operator group as discharging to
    a pending finding rather than a defeat, and carries no BCP-14 keyword doing
    it. The demo ships the pin — ``Defeated`` — because the acceptance oracle and
    ``docs/demo-script.md`` both require it, and because a two-slot decision
    whose only cure is re-tabling the act is dead in the sense the beat needs.
    The other reading is implemented, tested and one assignment away.
    """
    evaluator = importlib.import_module("utina.fold.evaluate")

    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.decline(DEV, hire)
    monkeypatch.setattr(evaluator, "UNREACHABLE_YIELDS", Pending)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV]
    assert finding.requirement[0].species is PendingSpecies.EXPIRED_ABANDONED


def test_the_flipped_reading_never_returns_an_empty_requirement_set(founded, monkeypatch):
    """The hole in ``:1966``, and why the spent slots are what the set names.

    "Exactly the unfilled slots" is the empty set when a declination is what made
    unity unreachable, and the codomain refuses a pending finding with an empty
    requirement — the Ground Axiom makes the cure path part of what a pending is.
    So the requirement names the spent slots, marked undischargeable.
    """
    evaluator = importlib.import_module("utina.fold.evaluate")

    hire = founded.act("hire", "hire")
    founded.decline(MARTA, hire)
    founded.decline(DEV, hire)
    monkeypatch.setattr(evaluator, "UNREACHABLE_YIELDS", Pending)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV, MARTA]
    assert all(
        element.species is PendingSpecies.EXPIRED_ABANDONED for element in finding.requirement
    )


# --- succession: which law judges which question -------------------------------


def test_a_committed_act_is_judged_under_the_law_in_force_at_its_own_coordinate(founded):
    """The utility claim: the past is recomputable, not retconned.

    The amendment is endorsed to unity here, so the law really does change after
    the act under appraisal. An unendorsed one confers nothing (@xhtvuxnc), which
    would make this case pass without succession having to work.
    """
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.endorse(DEV, hire)
    seat = founded.amend("seat-the-board", BOARD_LAW)
    founded.endorse(MARTA, seat)
    founded.endorse(DEV, seat)
    founded.act("later", "hire")

    finding = evaluate(founded.corpus, Committed(hire), at=founded.now)

    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A1",)


def test_an_amendment_is_judged_under_the_law_it_replaces(founded):
    """2270-2272: law never applies to itself at a coordinate, only to its successor."""
    seat = founded.amend("seat-the-board", BOARD_LAW)
    founded.endorse(MARTA, seat)
    founded.endorse(DEV, seat)

    finding = evaluate(founded.corpus, Committed(seat), at=founded.now)

    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A2",)


def test_a_proposal_is_judged_under_the_law_in_force_at_the_position(founded):
    """A proposal asks whether an act may be performed now, so now's law rules it.

    Nina's endorsement is what makes this B1's answer rather than A1's, and it
    only counts because the amendment that seated her carried: an edition takes
    force where its enactment reaches unity (@xhtvuxnc).
    """
    seat = founded.amend("seat-the-board", BOARD_LAW)
    founded.endorse(MARTA, seat)
    founded.endorse(DEV, seat)
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.endorse(NINA, hire)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("B1",)


# --- the cure path, and what closes it (issue #82 rules 1 and 2) ---------------


def amended_over(founded, clauses, act="hire"):
    """Table an act, endorse it half way, then amend the law to ``clauses``.

    The shape every case below needs: a pending act with a requirement space it
    declared at birth, and an amendment that either moves the rule under it or
    leaves it alone.
    """
    tabled = founded.act(act, act)
    founded.endorse(MARTA, tabled)
    seat = founded.amend("amendment", clauses)
    founded.endorse(MARTA, seat)
    founded.endorse(DEV, seat)
    return tabled, founded.said("amendment")


def test_an_amendment_to_the_governing_clause_closes_the_cure_path(founded):
    """Beat 9, and issue #82's first rule.

    The endorser who signed under a clause requiring two of two signed a bargain
    in which their signature was decisive; under any two of three it is
    dispensable. Carrying it across converts what they agreed to with no new act
    of will from them, so the requirement space the finding declared at birth is
    unreachable and the cure is re-presentation.
    """
    tabled, amendment = amended_over(founded, BOARD_LAW)

    finding = evaluate(founded.corpus, Committed(tabled), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.species for element in finding.requirement] == [
        PendingSpecies.EXPIRED_ABANDONED
    ]
    assert [element.ground for element in finding.requirement] == [amendment]
    assert [element.clause for element in finding.requirement] == ["A1"]


def test_an_amendment_elsewhere_leaves_the_cure_path_open(founded):
    """Beat 10, and issue #82's second rule — the half nobody guesses.

    A1 is re-committed byte-identical while A2 moves. A clause is its bytes, so
    the same identifier is the same clause and the bargain the endorser struck
    is the one still in force. Without this, any party able to enact anything
    could kill any inconvenient pending act by amending something irrelevant.
    """
    carried = [FOUNDERS_LAW[0], clause("A9", ["amend"], (MARTA, "1/3"), (DEV, "2/3"))]
    tabled, _ = amended_over(founded, carried)

    finding = evaluate(founded.corpus, Committed(tabled), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.species for element in finding.requirement] == [PendingSpecies.ABSENT]
    assert [element.ground for element in finding.requirement] == [""]


def test_an_amendment_that_leaves_the_class_ungoverned_closes_the_path_too(founded):
    """Nothing governs the act any more, so nothing could discharge it either."""
    tabled, amendment = amended_over(founded, [clause("A9", ["amend"], (MARTA, "1/1"))])

    finding = evaluate(founded.corpus, Committed(tabled), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.ground for element in finding.requirement] == [amendment]


def test_an_affirmed_act_is_not_reopened_by_an_amendment(founded):
    """Beat 24, and the reason this test sits beside the two above.

    Rule 1 reaches acts still in flight. A finding that reached a terminal value
    stands at its coordinate forever, and re-asking it later returns the same
    answer under the law in force then.
    """
    tabled = founded.act("hire", "hire")
    founded.endorse(MARTA, tabled)
    founded.endorse(DEV, tabled)
    seat = founded.amend("amendment", BOARD_LAW)
    founded.endorse(MARTA, seat)
    founded.endorse(DEV, seat)

    finding = evaluate(founded.corpus, Committed(tabled), at=founded.now)

    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A1",)


def test_a_defeated_act_is_not_reopened_by_an_amendment(founded):
    """The same, from the other terminal value."""
    tabled = founded.act("hire", "hire")
    founded.endorse(MARTA, tabled)
    founded.decline(DEV, tabled)
    seat = founded.amend("amendment", BOARD_LAW)
    founded.endorse(MARTA, seat)
    founded.endorse(DEV, seat)

    assert isinstance(evaluate(founded.corpus, Committed(tabled), at=founded.now), Defeated)


def test_a_proposal_has_no_cure_path_to_close(founded):
    """A proposal is judged under the law at the position it is asked from.

    So the clause that judges it and the clause in force are the same clause by
    construction, and the stability test can never fire. Asserted rather than
    assumed, because a test that fired here would be closing cure paths on
    questions about *now*.
    """
    amended_over(founded, BOARD_LAW)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert all(element.species is PendingSpecies.ABSENT for element in finding.requirement)
    assert all(element.ground == "" for element in finding.requirement)


# --- the amendment that lies about itself (issue #82, determination 5) --------


def under_declaring(founded, disturbs):
    """A record with a pending act, then an amendment declaring ``disturbs``.

    The hire is left half-endorsed and the amendment replaces the clause under
    it, so the amendment disturbs exactly one question. What it *says* is the
    caller's, which is the whole point: the declaration is a claim, and a claim
    is what can be false.
    """
    tabled = founded.act("hire", "hire")
    founded.endorse(MARTA, tabled)
    amendment = founded.amend("amendment", BOARD_LAW, disturbs=disturbs)
    founded.endorse(MARTA, amendment)
    founded.endorse(DEV, amendment)
    return tabled, amendment


def test_an_amendment_declaring_truthfully_is_affirmed(founded):
    """The claim and the computation agree, so there is nothing to convict."""
    # Re-run with the true set declared, over a fresh log of the same shape.
    log = Log()
    log.law("inception", "inception", FOUNDERS_LAW)
    tabled = log.act("hire", "hire")
    log.endorse(MARTA, tabled)
    amendment = log.amend("amendment", BOARD_LAW, disturbs=[tabled])
    log.endorse(MARTA, amendment)
    log.endorse(DEV, amendment)

    finding = evaluate(log.corpus, Committed(amendment), at=log.now)

    assert isinstance(finding, Affirmed)
    assert finding.clauses == ("A2",)


def test_an_amendment_that_under_declares_is_convicted_on_its_own_bytes(founded):
    """Beat 23, and determination 5.

    The amendment says it disturbs nothing and it disturbs the hire. No judge,
    no vote, no appeal to anything outside the log: the same committed bytes
    carry the claim and the change, and a stranger computes the gap.
    """
    tabled, amendment = under_declaring(founded, disturbs=[])

    finding = evaluate(founded.corpus, Committed(amendment), at=founded.now)

    assert isinstance(finding, SelfConvicted)
    assert finding.proof.package == disturbance.package((), (tabled,))
    assert finding.verdict is Verdict.SELF_CONVICTED


def test_an_amendment_that_over_declares_is_convicted_too(founded):
    """A false claim is false in either direction.

    Naming a question it did not disturb is testimony about its own effect that
    the record contradicts, exactly as omitting one is. Determination 5 convicts
    the *mismatch*, not the omission.
    """
    _, amendment = under_declaring(founded, disturbs=["E-not-an-act-at-all"])

    finding = evaluate(founded.corpus, Committed(amendment), at=founded.now)

    assert isinstance(finding, SelfConvicted)


def test_the_conviction_arrives_exactly_when_the_amendment_carries(founded):
    """Beat 22 against beat 23, which is one enactment read at three positions.

    An amendment that has not carried has disturbed nothing, so there is no
    mismatch to find and the enactment's own question is simply pending, short of
    its threshold. At the coordinate it reaches unity its edition takes force,
    the hire's cure path shuts, and the declaration is false in the same breath.
    Beat 22's "declared affirmed" is the amender's claim; this is the fold's
    answer, and it never was affirmed.
    """
    _, amendment = under_declaring(founded, disturbs=[])
    committed = founded.corpus.event(amendment).position

    reading = [
        type(evaluate(founded.corpus, Committed(amendment), at=Position(seq))).__name__
        for seq in range(committed.seq, founded.now.seq + 1)
    ]

    assert reading == ["Pending", "Pending", "SelfConvicted"]


def test_an_amendment_nobody_carried_disturbs_nothing_and_declares_nothing(founded):
    """An enactment that never took force cannot have disturbed a thing."""
    tabled = founded.act("hire", "hire")
    founded.endorse(MARTA, tabled)
    amendment = founded.amend("amendment", BOARD_LAW, disturbs=[])

    assert isinstance(evaluate(founded.corpus, Committed(amendment), at=founded.now), Pending)


def test_a_settled_act_is_not_disturbed_by_a_later_amendment(founded):
    """Disturbance reaches acts in flight, so a truthful declaration omits it."""
    settled = founded.act("hire", "hire")
    founded.endorse(MARTA, settled)
    founded.endorse(DEV, settled)
    amendment = founded.amend("amendment", BOARD_LAW, disturbs=[])
    founded.endorse(MARTA, amendment)
    founded.endorse(DEV, amendment)

    assert isinstance(evaluate(founded.corpus, Committed(amendment), at=founded.now), Affirmed)


# --- Q26: what a prospective question binds to ----------------------------------


def test_a_proposal_binds_to_the_latest_committed_act_of_that_kind(founded):
    """Q26, pinned: latest wins.

    The alternative reading — that a proposal aggregates every endorsement of the
    act *kind* — is the one that quietly destroys the demo. Under it the second
    tabling of an act inherits the first tabling's endorsements, so a decision
    that has been re-tabled precisely because it was contested comes back
    affirmed. Nothing about the output looks wrong; it is simply the wrong
    answer, which is why this is a test and not a comment.
    """
    first = founded.act("hire-first", "hire")
    founded.endorse(MARTA, first)
    founded.endorse(DEV, first)
    retabled = founded.act("hire-again", "hire")
    founded.endorse(MARTA, retabled)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV]


def test_a_proposal_does_not_aggregate_endorsements_across_acts(founded):
    """The same rule, stated as the arithmetic it forbids."""
    first = founded.act("hire-first", "hire")
    founded.endorse(DEV, first)
    retabled = founded.act("hire-again", "hire")
    founded.endorse(MARTA, retabled)

    finding = evaluate(founded.corpus, Proposal("hire"), at=founded.now)

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [DEV]


def test_the_earlier_tabling_is_still_answerable_on_its_own_bytes(founded):
    """Latest-wins is about the prospective question, and settles nothing about the past."""
    first = founded.act("hire-first", "hire")
    founded.endorse(MARTA, first)
    founded.endorse(DEV, first)
    founded.act("hire-again", "hire")

    assert isinstance(evaluate(founded.corpus, Committed(first), at=founded.now), Affirmed)


def test_a_declination_on_a_later_tabling_does_not_reach_back(founded):
    first = founded.act("hire-first", "hire")
    founded.endorse(MARTA, first)
    founded.endorse(DEV, first)
    retabled = founded.act("hire-again", "hire")
    founded.decline(DEV, retabled)

    assert isinstance(evaluate(founded.corpus, Committed(first), at=founded.now), Affirmed)
    assert isinstance(evaluate(founded.corpus, Proposal("hire"), at=founded.now), Defeated)


# --- the closed triple ---------------------------------------------------------


def test_the_evaluator_reads_exactly_the_three_committed_inputs(founded):
    """Axiom 2: evidence, law head, position. A fourth input is a conformance failure."""
    hire = founded.act("hire", "hire")
    founded.endorse(MARTA, hire)
    founded.endorse(DEV, hire)

    triple = appraisal_triple(founded.corpus, Proposal("hire"), at=founded.now)

    assert triple.inputs() == (triple.evidence, triple.law_head, triple.position)
    assert len(triple.evidence) == len(founded.events)
    assert triple.position == founded.now


def test_two_weights_that_only_sum_to_unity_as_rationals_do_reach_it():
    """Three thirds. In binary floating point they do not, and B2 is on that path."""
    log = Log()
    log.law("inception", "inception", BOARD_LAW)
    amend = log.act("amend", "amend")
    for who in (MARTA, DEV, NINA):
        log.endorse(who, amend)

    finding = evaluate(log.corpus, Proposal("amend"), at=log.now)

    assert isinstance(finding, Affirmed)
    assert sum(Fraction(1, 3) for _ in range(3)) == 1
