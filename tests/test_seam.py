"""The seam: the writing plane's committed bytes, read by the real fold.

Four commissions built against ``docs/interfaces.md`` in parallel and never ran
each other's code. The contract warned twice about exactly this — "disagree on a
key and the Constitution folds to nothing, with no error", and "if the writer and
the predicate disagree on a name, every slot silently reads PENDING and every
decision is pending forever". Both hazards were real at the merge, and neither
raised anything: a law that will not read as law and a slot that reads pending
are the *quiet* failures.

So this file is the integration test the per-stream suites structurally could
not be. Every assertion below is over ``utina.acme``'s committed log read by
``utina.fold``'s own types, with no double anywhere in the path.
"""

from __future__ import annotations

from fractions import Fraction

from conftest import RealValues
from utina.acme import DEV, MARTA, NINA, SEAT, build
from utina.fold import evaluate, standing
from utina.fold.constitution import Constitution
from utina.fold.finding import Affirmed, Pending
from utina.fold.group import Disposition
from utina.fold.question import Committed, Proposal
from utina.fold.slots import dispositions
from utina.substrate import ISSUED, canonical_bytes


def test_the_committed_law_reads_as_law(acme):
    """The Constitution folds Acme's own inception event, not a fixture's."""
    law = Constitution.at(acme.corpus, acme.at("inception"))

    assert [clause.id for clause in law.clauses] == ["A1", "A2", "A3"]
    assert law.governing("open-bank-account").id == "A1"
    assert {slot.weight for slot in law.clause("A1").group.slots} == {Fraction(1, 2)}


def test_the_board_law_takes_force_where_the_amendment_carries_and_not_before(acme):
    """@xhtvuxnc over Acme's own record, which is where the bug was measurable.

    The amendment seating the board is committed, then endorsed twice, and only
    the second endorsement reaches unity — the coordinate the record labels
    ``board-seated``. One coordinate earlier the amendment is committed and
    short, and the founding law is still the law; the shipped engine had the
    board law in force there, a full event before the amendment enacting it
    carried, so every question asked at that coordinate was answered under a law
    nobody had yet enacted (tick ``4pmw``).
    """
    seated = acme.at("board-seated")
    short = acme.values.position(seated.seq - 1)
    committed = acme.corpus.event(acme.said("seat-the-board")).position

    def clauses(position):
        return [clause.id for clause in Constitution.at(acme.corpus, position).clauses]

    assert committed.seq < short.seq, "the amendment is committed before this coordinate"
    assert clauses(short) == ["A1", "A2", "A3"]
    assert clauses(seated) == ["B1", "B2", "A3"]


def test_a_committed_weight_is_an_exact_rational_string(acme):
    """``docs/interfaces.md``: weight is a string in the committed body.

    The bytes are the same either way — the canonical encoder writes a Fraction
    as ``"1/2"`` too — so the identifiers this changes are none. What it changes
    is whether ``Clause.from_committed`` can read the value it is handed, and a
    seam that agrees on the bytes and disagrees on the parsed value is the
    expensive kind.
    """
    inception = acme.corpus.upto(acme.at("inception"))[0]
    clauses = inception.body["law"]["clauses"]
    weights = [slot["weight"] for slot in clauses[0]["group"]["slots"]]

    assert weights == ["1/2", "1/2"]
    assert all(Fraction(weight) == Fraction(1, 2) for weight in weights)
    assert b'"weight":"1/2"' in canonical_bytes(inception.body)


def test_the_slot_predicate_reads_the_endorsements_the_constructor_wrote(acme):
    """The contract's endorsement body, both ends of it.

    A slot is ENDORSED only on an act carrying ``act`` of ``"issue"``. The
    constructor committed no such field, so every slot read PENDING and every
    beat of the demo would have been pending forever — silently, because a
    pending slot is what the fold says when it cannot verify anything.
    """
    law = Constitution.at(acme.corpus, acme.at("d1"))
    subject = acme.said("open-bank-account")
    committed = acme.corpus.upto(acme.at("d1"))

    held = dispositions(law.clause("A1").group, committed, subject)

    assert held == {acme.aid(MARTA): Disposition.ENDORSED, acme.aid(DEV): Disposition.ENDORSED}


def test_the_declination_at_d3_is_read_as_a_spent_slot(acme):
    """The centerpiece's raw material: Dev's signed no, seen as DECLINED."""
    law = Constitution.at(acme.corpus, acme.at("d3"))
    subject = acme.said("sign-office-lease")
    committed = acme.corpus.upto(acme.at("d3"))

    held = dispositions(law.clause("A1").group, committed, subject)

    assert held == {acme.aid(MARTA): Disposition.ENDORSED, acme.aid(DEV): Disposition.DECLINED}
    assert not law.clause("A1").group.reachable(held)


def test_the_fold_reads_the_seats_standing_out_of_committed_events(acme):
    """@exy3u4t7, and the seam it is really about.

    The substrate holds a transaction log and can answer what the registry says.
    The fold cannot ask it — the purity fitness function forbids the import —
    and must not, because that would be the ambient read issue #82 rule 3 rules
    out. So the constructor commits the issuance as a governance event, and the
    fold folds that. Both answers are asserted here, and the point is that they
    agree *without* the fold having consulted the one that holds the TEL.
    """
    seating = acme.corpus.event(acme.said("seat-credential"))
    credential = seating.body["acdc"]["d"]

    assert seating.kind == standing.ISSUANCE_KIND
    assert seating.body["ri"] == acme.registry
    assert seating.body["acdc"]["a"]["i"] == acme.aid(SEAT), "the issuee is the seat"

    folded = standing.state_over(acme.corpus.upto(acme.at("b8")), acme.registry, credential)
    before = standing.state_over(acme.corpus.upto(acme.at("d4")), acme.registry, credential)

    assert folded == ISSUED
    assert before is None, "nothing stands before the event that issued it"
    assert acme.substrate.registry_state(acme.registry, credential) == ISSUED


def test_the_carried_clause_is_one_clause_on_both_sides_of_the_amendment(acme):
    """Demo 2 beat 10's ground: same clause SAID, read out of the fold twice.

    ``tests/test_acme.py`` asserts the committed bytes are equal; this asserts
    the fold agrees, which is the form the finding cites. Two clauses with equal
    weights and different digests would satisfy that test and fail this one, and
    the requirement space a pending act declared at birth would then be
    unreachable on the far side of an amendment that never touched its rule.
    """
    before = Constitution.at(acme.corpus, acme.at("b5"))
    after = Constitution.at(acme.corpus, acme.at("board-seated"))

    assert [clause.id for clause in before.clauses] == ["A1", "A2", "A3"]
    assert [clause.id for clause in after.clauses] == ["B1", "B2", "A3"]
    assert before.clause("A3").said() == after.clause("A3").said()
    assert before.clause("A3").sub_block() == after.clause("A3").sub_block()
    assert before.law_head != after.law_head, "the edition moved even though A3 did not"


def test_the_founders_equity_question_is_pending_across_the_amendment_and_then_cured(acme):
    """Demo 2 beats 5, 10 and 11, which the demo-2 oracle will own row by row.

    One committed act, three coordinates. Pending under A3 before the board is
    seated, pending under the same A3 after it — the same clause and the same
    outstanding slot, which is what makes the cure path *open* — and affirmed
    once Dev acts. Beat 9's contrast, the cure path that closes, is U3's work.
    """
    equity = "release-escrowed-equity"
    tabled = evaluate(acme.corpus, Proposal(equity), at=acme.at("b5"))
    across = evaluate(acme.corpus, Proposal(equity), at=acme.at("board-seated"))
    cured = evaluate(acme.corpus, Proposal(equity), at=acme.at("b11"))

    assert isinstance(tabled, Pending)
    assert isinstance(across, Pending)
    assert tabled.requirement == across.requirement
    assert [element.clause for element in across.requirement] == ["A3"]
    assert [element.endorser for element in across.requirement] == [acme.aid(DEV)]

    assert isinstance(cured, Affirmed)
    assert cured.clauses == ("A3",)
    assert len(cured.endorsements) == 2


def test_a_proposal_binds_to_the_latest_act_and_never_aggregates(acme):
    """Q26 on the demo's own log, where the aggregating reading would be fatal.

    Acme tables ``approve-budget`` twice: once at D5, where Marta and Nina carry
    it, and again at D6, where Marta endorses and Dev declines. Both tablings are
    committed and both are of the same act class, so a prospective question about
    that class has to choose. Latest wins.

    The aggregating reading — treat every endorsement of the act class as
    evidence for one question — reaches unity at D6 on Nina's endorsement of the
    *first* budget and affirms it. That collapses the centerpiece: D6 is supposed
    to be the beat where the same signed no that killed a two-slot decision only
    delays a three-slot one, and under aggregation it silently becomes a beat
    about a decision that passed. Nothing in the output would look wrong, which
    is why the counterfactual is spelled out here rather than trusted to a
    comment.
    """
    committed = acme.corpus.upto(acme.at("d6"))
    budgets = [
        event.said
        for event in committed
        if event.kind == "act" and event.body.get("act") == "approve-budget"
    ]
    assert len(budgets) == 2, "the beat needs both tablings committed"

    finding = evaluate(acme.corpus, Proposal("approve-budget"), at=acme.at("d6"))

    assert isinstance(finding, Pending)
    assert [element.endorser for element in finding.requirement] == [acme.aid(NINA)]

    # The counterfactual, computed rather than asserted: pooled across both
    # tablings, Nina's slot reads endorsed and the group reaches unity.
    group = Constitution.at(acme.corpus, acme.at("d6")).clause("B1").group
    pooled = {
        endorser: disposition
        for subject in budgets
        for endorser, disposition in dispositions(group, committed, subject).items()
        if disposition is not Disposition.PENDING
    }
    assert group.satisfied(pooled), "the aggregating reading really does affirm D6"


def test_each_tabling_of_one_act_class_keeps_its_own_verdict(acme):
    """The other half of latest-wins: the earlier tabling is untouched by the later."""
    first = evaluate(acme.corpus, Committed(acme.said("approve-budget")), at=acme.at("d6"))
    retabled = evaluate(
        acme.corpus, Committed(acme.said("approve-budget-retabled")), at=acme.at("d6")
    )

    assert isinstance(first, Affirmed)
    assert isinstance(retabled, Pending)


def test_the_real_fold_types_satisfy_the_values_protocol():
    """Ratifying ``FoldValues`` now that the fold exists (this.i @tvaq2s).

    The writing plane was built against a structural protocol so that it could be
    finished and tested while the fold did not exist. The protocol stays — it is
    the Custos §1.3 separation between the constructor's plane and the judge's,
    and the demo asserts it on stage — so what integration owes is a proof that
    the real types satisfy it, not its removal.
    """
    from utina.fold.corpus import Corpus, Event
    from utina.fold.triple import Position

    values = RealValues()
    position = values.position(0)
    event = values.event(said="E0", kind="act", position=position, body={})

    assert isinstance(position, Position)
    assert isinstance(event, Event)
    assert isinstance(values.corpus([event]), Corpus)


def test_the_writing_plane_imports_nothing_from_the_fold():
    """The separation the protocol buys, stated as the test that would catch a lapse."""
    import ast
    import importlib
    from pathlib import Path

    for name in ("utina.enact.constructor", "utina.acme.build", "utina.substrate.protocol"):
        source = importlib.import_module(name).__file__
        assert source is not None
        tree = ast.parse(Path(source).read_text(encoding="utf-8"))
        imported = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        } | {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        assert not any(module.startswith("utina.fold") for module in imported)


def test_a_second_build_commits_byte_identical_evidence():
    """Determinism across builds, which is what makes the demo repeatable."""
    first, second = build(values=RealValues()), build(values=RealValues())

    assert [event.said for event in first.events] == [event.said for event in second.events]
