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
from utina.acme import DEV, MARTA, build
from utina.fold import evaluate
from utina.fold.constitution import Constitution
from utina.fold.finding import Affirmed, Pending
from utina.fold.group import Disposition
from utina.fold.question import Committed, Proposal
from utina.fold.slots import dispositions
from utina.substrate import canonical_bytes


def test_the_committed_law_reads_as_law(acme):
    """The Constitution folds Acme's own inception event, not a fixture's."""
    law = Constitution.at(acme.corpus, acme.at("inception"))

    assert [clause.id for clause in law.clauses] == ["A1", "A2"]
    assert law.governing("open-bank-account").id == "A1"
    assert {slot.weight for slot in law.clause("A1").group.slots} == {Fraction(1, 2)}


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

    assert held == {MARTA: Disposition.ENDORSED, DEV: Disposition.ENDORSED}


def test_the_declination_at_d3_is_read_as_a_spent_slot(acme):
    """The centerpiece's raw material: Dev's signed no, seen as DECLINED."""
    law = Constitution.at(acme.corpus, acme.at("d3"))
    subject = acme.said("hire-vp-sales")
    committed = acme.corpus.upto(acme.at("d3"))

    held = dispositions(law.clause("A1").group, committed, subject)

    assert held == {MARTA: Disposition.ENDORSED, DEV: Disposition.DECLINED}
    assert not law.clause("A1").group.reachable(held)


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
    assert [element.endorser for element in finding.requirement] == ["acme:nina"]

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
