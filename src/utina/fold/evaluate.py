"""The evaluator: a committed question, answered from the closed triple.

This is the fold's entry point and the place its axioms meet. Everything else in
``utina.fold`` is a value type or a predicate; this module is the order those are
consulted in, and the order is the semantics.

**The order of operations** (``docs/interfaces.md``), each step of which is a
Custos obligation rather than a convenience:

1. Find the governing clause. **No governing clause is a refusal**, never a
   finding: "where no committed rule makes the invocation evaluable at all, it
   refuses — and the refusal is not a finding but an operational fact"
   (``custos-4.2.md:1896-1902``). A fold that answered ``pending`` here would be
   claiming the law exists and the evidence is short, which is a different and
   false statement.
2. Build the question's complete requirement space from that clause **before
   returning anything**. No finding is terminal while an enumerated check sits
   unexamined, so the whole space is computed and the verdict chosen from it.
   The three returns below are one dispatch over precomputed values, and there is
   deliberately no early return between the classification and the decision.
3. Classify every slot from committed evidence at or before the position, and
   **fail closed**: anything the fold cannot verify is PENDING, never ENDORSED.
4. Endorsed weights reach unity — affirmed, carrying the clause and the
   endorsements that reached it.
5. Unity unreachable — see ``UNREACHABLE_YIELDS`` below.
6. Otherwise pending, naming the outstanding slots in canonical order.

**Which law judges which question** is the other rule here, and it differs by
constructor. A ``Committed`` question asks whether an act *was* lawful, so it is
judged under the law in force at that act's own coordinate — which is what makes
the past recomputable rather than retconned, and what makes an amendment
answerable under the law it replaces (``:2270-2272``). A ``Proposal`` asks
whether an act *may* be performed, which is a question about now, so it is judged
under the law in force at the appraisal position. The second half is utina's
reading; the register records it.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

from utina.fold.clause import Clause
from utina.fold.constitution import Constitution
from utina.fold.corpus import Corpus, Event
from utina.fold.finding import (
    Affirmed,
    Citation,
    Declination,
    Defeated,
    DefeaterClass,
    Finding,
    Pending,
    PendingSpecies,
    RequirementElement,
    canonical_requirement_set,
    select_defeat,
)
from utina.fold.group import Disposition
from utina.fold.question import Proposal, Question
from utina.fold.refusal import Refusal
from utina.fold.slots import SlotDisposition, classify, declinations, endorsements
from utina.fold.triple import SAID, AppraisalTriple, EvidenceBundle, Position

__all__ = [
    "UNREACHABLE_YIELDS",
    "appraisal_triple",
    "evaluate",
]


# --- the one reading the maintainer may still flip -----------------------------

UNREACHABLE_YIELDS: type[Finding] = Defeated
"""What the fold returns when unity can no longer be reached.

Custos does not settle this, and the two readings of it are the demo's
centerpiece, so the switch is one name and the branch behind it is one function
(:func:`_unreachable`). Flipping this assignment is the whole change.

``Defeated`` is what ships. ``docs/demo-script.md`` and the acceptance oracle both
require it, and it is the reading in which beat D3 says what the beat is for: a
two-slot decision with a signed no against it is dead, and nothing anyone does to
*that* decision will revive it.

``Pending`` is the other reading, and it is not a fringe one. ``:1966`` says an
unsatisfied operator group "is not a defect and not a defeat: it discharges as a
pending finding whose typed requirement set enumerates exactly the unfilled
slots". That sentence carries no BCP-14 keyword, so it binds nothing, but it is
the drafting authority's plain intent. It also has a hole: a declined slot is a
*filled* slot, so in the two-slot case "exactly the unfilled slots" is the empty
set — and a pending finding may not carry an empty requirement set, because the
Ground Axiom makes the cure path part of what a pending *is*. Under this reading
the requirement therefore names the **spent** slots, marked undischargeable
(``PendingSpecies.EXPIRED_ABANDONED``, whose cure is re-presentation), which
honours "not a defeat", satisfies the Ground Axiom, and still tells the reader
that nothing they do to this decision will move it.
"""


# --- what the fold reads out of committed bytes --------------------------------

#: The event kinds that commit an act of some class. An endorsement is excluded
#: deliberately: its ``act`` field carries the registry operation (``"issue"``),
#: not an act class, and reading one as the other would let an endorsement be
#: mistaken for the thing it endorses.
ACT_KINDS = ("act", "enactment")

#: Where a committed act names its class.
ACT_CLASS_FIELD = "act"

#: What the slot predicate is given as the subject when nothing has been tabled.
#: No committed event bears it, so every slot classifies PENDING — which is the
#: true answer: the law governs the class and no act of it stands to be endorsed.
_NOTHING_TABLED = ""


@dataclass(frozen=True)
class _Subject:
    """What a question resolves to, before any law is consulted.

    ``coordinate`` is the position whose law judges the question, which is the
    subject's own coordinate for a committed act and the appraisal position for a
    proposal.
    """

    act: str
    said: SAID
    coordinate: Position


def evaluate(corpus: Corpus, question: Question, *, at: Position) -> Finding | Refusal:
    """Appraise ``question`` over ``corpus`` at ``at``.

    Returns one of the four findings, each carrying its ground, or a refusal
    where committed law does not make the question evaluable at all. Never
    raises for want of evidence: missing evidence under a rule is a pending
    finding, and a missing rule is a refusal.
    """
    subject = _resolve(corpus, question, at)
    if isinstance(subject, Refusal):
        return subject

    law = Constitution.at(corpus, subject.coordinate)
    clause = law.governing(subject.act)
    if clause is None:
        return _ungoverned(subject.act)

    evidence = EvidenceBundle(corpus.upto(at))
    classified = classify(clause.group, evidence.events, subject.said)

    # The complete requirement space, built before any verdict is chosen. Both
    # halves are computed unconditionally: step 2 forbids returning while an
    # enumerated check is still unexamined, and the cost of a clause's worth of
    # arithmetic is not a reason to make a finding on partial information.
    outstanding = _requirements(clause, classified, Disposition.PENDING, PendingSpecies.ABSENT)
    spent = _requirements(
        clause, classified, Disposition.DECLINED, PendingSpecies.EXPIRED_ABANDONED
    )
    held = {one.endorser: one.disposition for one in classified}

    if clause.group.satisfied(held):
        return Affirmed(
            clauses=(clause.id,),
            endorsements=endorsements(classified),
            bundle=_bundle_identifier(evidence),
        )
    if not clause.group.reachable(held):
        return _unreachable(clause, classified, spent)
    # Reachable and unsatisfied means some slot with positive weight is still
    # pending, so ``outstanding`` is never empty here and the Ground Axiom's
    # requirement that a pending name its cure is satisfied by construction.
    return Pending(requirement=outstanding)


def appraisal_triple(corpus: Corpus, question: Question, *, at: Position) -> AppraisalTriple:
    """The closed three-input type this appraisal is a function of.

    Exposed because "exactly three, closed" (``:259-262``) is a claim worth being
    able to check from outside rather than a comment. The law head is the head of
    the law that judges *this* question, which is the subject's own coordinate for
    a committed act.
    """
    subject = _resolve(corpus, question, at)
    coordinate = at if isinstance(subject, Refusal) else subject.coordinate
    return AppraisalTriple(
        evidence=EvidenceBundle(corpus.upto(at)),
        law_head=Constitution.at(corpus, coordinate).law_head,
        position=at,
    )


# --- step 1: resolving the question --------------------------------------------


def _resolve(corpus: Corpus, question: Question, at: Position) -> _Subject | Refusal:
    """What the question is about, or a refusal that it is not about anything.

    A question naming bytes nobody committed, or bytes committed after the
    position it is asked at, is ill-posed rather than unproven: there is nothing
    at this coordinate for a finding to be a judgment *over*.
    """
    if isinstance(question, Proposal):
        tabled = _latest_act(corpus, question.act, at)
        return _Subject(
            act=question.act,
            said=tabled.said if tabled is not None else _NOTHING_TABLED,
            coordinate=at,
        )
    event = corpus.event(question.said)
    if event is None or at < event.position:
        return Refusal(
            missing=f"any committed event bearing the identifier {question.said}",
            detail=(
                "A finding is a judgment over committed bytes, and nothing committed "
                "at or before this position bears that identifier. Present the event, "
                "or ask at a position that can see it."
            ),
        )
    act = event.body.get(ACT_CLASS_FIELD)
    if event.kind not in ACT_KINDS or not isinstance(act, str) or act == "":
        return Refusal(
            missing=f"an act class on the committed event {question.said}",
            detail=(
                "The committed bytes name no class of act, so no clause can govern "
                "them: a clause rules act kinds, and this event claims none. The "
                "kind is read before the field, because an endorsement's own act "
                "field carries the registry operation rather than a class of act, "
                "and reading one as the other would judge the endorsement instead "
                "of the decision it endorses."
            ),
        )
    return _Subject(act=act, said=event.said, coordinate=event.position)


def _latest_act(corpus: Corpus, act: str, at: Position) -> Event | None:
    """The most recent committed act of class ``act`` at or before ``at``.

    **Latest wins** (S4 in the register). The alternative reading treats every
    endorsement of an act *class* as evidence for one prospective question, and
    that reading is quietly catastrophic: a decision re-tabled because it was
    contested would inherit the endorsements of the tabling it replaced and come
    back affirmed. Nothing in the output would look wrong.

    A committed act is a distinct subject with its own identifier, and an
    endorsement names the subject it endorses, so binding the class question to
    one subject is also the only reading under which the endorsement's ``said``
    field means anything.
    """
    found: Event | None = None
    for event in corpus.upto(at):
        if event.kind in ACT_KINDS and event.body.get(ACT_CLASS_FIELD) == act:
            found = event
    return found


def _ungoverned(act: str) -> Refusal:
    """Axiom 3, ``:277-278``: the fold refuses rather than legislates, and names it."""
    return Refusal(
        missing=f"a committed clause governing acts of the class {act}",
        detail=(
            "The law in force at this position rules no clause over this class of "
            "act. Where committed law runs out the fold refuses rather than "
            "legislating the missing rule, so this is not a pending finding: "
            "nothing anyone endorses would discharge it, because there is no rule "
            "for an endorsement to satisfy. Commit a clause that governs the class."
        ),
    )


# --- step 2: the requirement space ---------------------------------------------


def _requirements(
    clause: Clause,
    classified: Sequence[SlotDisposition],
    holding: Disposition,
    species: PendingSpecies,
) -> tuple[RequirementElement, ...]:
    """The slots in ``holding``, as typed requirement elements in canonical order.

    ``kind`` and ``species`` are populated here rather than left to the type's
    defaults: the element is the cure path, and an engine that let the cure path
    default has not decided what would discharge its own finding. Acme's law
    commits one cure — the arrival of a missing endorsement — so the kind is
    ``endorsement`` throughout, and the species distinguishes a slot that has not
    acted (absent, cured by the evidence arriving) from one that has spent itself
    (expired/abandoned, cured only by re-presentation).
    """
    return canonical_requirement_set(
        RequirementElement(
            endorser=one.endorser,
            clause=clause.id,
            kind="endorsement",
            species=species,
        )
        for one in classified
        if one.disposition is holding
    )


def _bundle_identifier(evidence: EvidenceBundle) -> SAID:
    """The identity of the evidence an affirmation was appraised over.

    SHA-256 over the bundle's canonical bytes, for the reason ``clause.py`` gives
    for the same choice: the fold imports no KERI library, so the KERI-native
    digest is not available to it. The bytes are the events' identifiers in
    committed order, so a permuted arrival order yields the same identifier.
    """
    return hashlib.sha256(evidence.canonical_bytes()).hexdigest()


# --- step 5: unity unreachable -------------------------------------------------


def _unreachable(
    clause: Clause,
    classified: Sequence[SlotDisposition],
    spent: tuple[RequirementElement, ...],
) -> Finding:
    """The finding for a threshold that can no longer reach unity.

    One function and one constant, so that the reading Custos leaves open is a
    one-line change and not an archaeology exercise. See ``UNREACHABLE_YIELDS``
    for what each reading claims and why the pin is what it is.
    """
    if UNREACHABLE_YIELDS is Pending and spent:
        return Pending(requirement=spent)
    return Defeated(citation=_citation(clause, classified))


def _citation(clause: Clause, classified: Sequence[SlotDisposition]) -> Citation:
    """The ground of a defeat: which clause, which signed no, under which class.

    Where several slots declined, the citation is the canonical selection of
    ``:1766-1770`` — "two verifiers holding the same bundle SHALL emit the same
    defeated finding down to the byte" — so the choice is made by
    :func:`~utina.fold.finding.select_defeat` and never by committed order.
    """
    spent = declinations(classified)
    if not spent:
        return Citation(
            clause=clause.id,
            reason=(
                f"Unity is unreachable under clause {clause.id}: the weights its slots "
                "can contribute do not sum to unity, so no arrangement of "
                "endorsements would satisfy it."
            ),
            defeater_class=_defeater_class(),
            subcode="",
        )
    return select_defeat(
        [
            Citation(
                clause=clause.id,
                declination=Declination(endorser=endorser, said=said),
                reason=(
                    f"Unity is unreachable under clause {clause.id}: {endorser} committed "
                    "a signed declination, which spends that slot's weight, and the "
                    "weight that can still arrive no longer reaches unity."
                ),
                defeater_class=_defeater_class(),
                subcode=endorser,
            )
            for endorser, said in spent
        ]
    )


def _defeater_class() -> DefeaterClass:
    """The class every defeat utina can currently reach is defeated under.

    ``authority`` (``:1771-1776``, and QC2 in the register): a threshold is a
    statement about who may act, so a decision that can no longer reach unity is
    one whose actor lacks the invoked power. It is computed by a named function
    rather than taken from the type's default, because the day this engine can
    also defeat on merit or supersession, the default would be silently wrong at
    every call site instead of loudly wrong at one.
    """
    return DefeaterClass.AUTHORITY
