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

from utina.fold import bearing, certification, disturbance, semantics
from utina.fold.clause import Clause
from utina.fold.constitution import ACT_CLASS_FIELD, Constitution
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
    Proof,
    RequirementElement,
    SelfConvicted,
    canonical_requirement_set,
    select_defeat,
)
from utina.fold.group import AID, Disposition
from utina.fold.question import Committed, Proposal, Question
from utina.fold.refusal import Refusal
from utina.fold.slots import (
    SlotDisposition,
    classify,
    declinations,
    endorsements,
    seating_is_ambiguous,
)
from utina.fold.triple import SAID, AppraisalTriple, EvidenceBundle, Position

__all__ = [
    "UNREACHABLE_YIELDS",
    "appraisal_triple",
    "disturbed_by",
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

#: Where a committed act names its class. Declared in ``constitution.py``, which
#: reads it first: an enactment is an act, and the law fold now has to know which
#: clause judged it before it can say whether its edition is in force.

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

    # Axiom 4, before any clause is read. A law expressed in a semantics this
    # engine cannot apply is not law this engine may guess at, and the check goes
    # here rather than inside the clause walk so that an unreadable lens refuses
    # the whole question instead of one clause of it (fold/semantics.py).
    unreadable = semantics.refusal_for(law.semantics)
    if unreadable is not None:
        return unreadable

    clause = law.governing(subject.act)
    if clause is None:
        return _ungoverned(subject.act)

    evidence = EvidenceBundle(corpus.upto(at))
    contested = seating_is_ambiguous(clause.group, evidence.events)
    if contested is not None:
        return _doubly_seated(contested)
    classified = classify(clause.group, evidence.events, subject.said)
    closed = _cure_path_closed(corpus, subject, clause, at)

    # The complete requirement space, built before any verdict is chosen. Both
    # halves are computed unconditionally: step 2 forbids returning while an
    # enumerated check is still unexamined, and the cost of a clause's worth of
    # arithmetic is not a reason to make a finding on partial information.
    outstanding = _requirements(
        clause,
        classified,
        Disposition.PENDING,
        PendingSpecies.EXPIRED_ABANDONED if closed else PendingSpecies.ABSENT,
        ground=closed,
    )
    spent = _requirements(
        clause, classified, Disposition.DECLINED, PendingSpecies.EXPIRED_ABANDONED
    )
    held = {one.endorser: one.disposition for one in classified}

    uncertified = _uncertified(corpus, law, subject, clause, at)

    tainted = _tainted(corpus, subject, clause, classified, at)
    if tainted is not None:
        return tainted

    if clause.group.satisfied(held):
        # The threshold is met and that is not the same as the act being
        # authorized. Where the law requires a certification, what is outstanding
        # here is the domain's own act of recording that the threshold WAS met —
        # votes cast are not a result until they are tabulated (this.i @2e2dncfe).
        if uncertified is not None:
            return Pending(requirement=(uncertified,))
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

    **Latest wins** (Q26 in the register). The alternative reading treats every
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


def _doubly_seated(office: str) -> Refusal:
    """One office, two holders: the fold refuses rather than choosing between them.

    A slot that seats an office is one candidate endorser, which is what ``MxN``
    commits — "exactly N slots, one per candidate endorser". Two standing seatings
    break that structurally, and nothing in the law says which supersedes, so a fold
    that picked one would be inventing the rule it exists to apply. Refusing names
    the defect where it can be fixed: in the registry, by revoking one.

    An office held by many BY DESIGN, whose count moves as people come and go, is a
    different operator rather than this defect — the dossier's ``MxQ``, an open-ended
    set of qualified endorsers, which utina does not implement yet (tick 5psg).
    """
    return Refusal(
        missing=f"exactly one standing seating of the office {office}",
        detail=(
            f"Two parties hold {office} at once, and this clause gives that office a "
            "single share of authority. Nothing committed says which seating "
            "supersedes the other, so choosing between them would be legislating "
            "rather than folding. This is not a pending finding: no endorsement "
            "discharges it, because the defect is in who holds the seat rather than "
            f"in who has acted. Revoke one of the two seatings of {office}."
        ),
    )


# --- step 2: the requirement space ---------------------------------------------


def disturbed_by(corpus: Corpus, enactment: Event, at: Position) -> tuple[SAID, ...]:
    """The questions this enactment actually ended, at or before ``at``.

    An act is disturbed when it was in flight before the enactment took force and
    its cure path is closed after — both halves, because an act that had settled
    is disturbed by nothing and an act whose own clause the amendment left alone
    is the specificity this requirement turns on.

    **Reporting, not judgment.** This computes what an amendment did; nothing is
    convicted of anything on the strength of it. The amender used to declare the
    same set and be convicted where the two differed, and that duty is gone
    (this.i @ow6dzro4) — an obligation that changed no outcome, whose only
    function was to create something that could be false. What remains is worth
    printing on its own: an amendment ends live matters, and a reader is owed
    which.

    **In flight means the cure path was still OPEN**, and not merely that the act
    was pending. An act a previous amendment already closed is not in flight, and
    a fold that counted it would have every later amendment inherit every earlier
    one's — the set would grow without bound down the chain. Acme's own record
    shows it: the hire
    has been expired/abandoned since the board-seating amendment, and the second
    amendment disturbs it not at all.

    Computed at the enactment's *effectuation*, which is where its edition
    started binding, and not at its commitment: an enactment that has not carried
    has disturbed nothing yet, and one that never carries disturbs nothing ever
    (this.i @xhtvuxnc).
    """
    effectuation = next(
        (
            link.effectuation
            for link in Constitution.succession(corpus, at)
            if link.enactment == enactment.said
        ),
        None,
    )
    if effectuation is None:
        return ()
    earlier = disturbance.before(effectuation)
    if earlier is None:  # pragma: no cover - an enactment is never at genesis
        return ()
    disturbed = []
    for act in disturbance.acts(corpus, ACT_KINDS, earlier):
        if act.said == enactment.said:
            continue
        was = evaluate(corpus, Committed(act.said), at=earlier)
        now = evaluate(corpus, Committed(act.said), at=effectuation)
        if (
            isinstance(was, Pending)
            and not _closed(was)
            and isinstance(now, Pending)
            and _closed(now)
        ):
            disturbed.append(act.said)
    return tuple(sorted(disturbed))


def _certification_schema(law: Constitution, clause: Clause) -> SAID | None:
    """What acts under ``clause`` must be certified against, or ``None`` for nothing.

    The clause decides and the law is the default, because how much ceremony a
    decision needs is a fact about the KIND of decision: minuting a board resolution
    and approving a routine purchase are not the same act wearing different clothes.
    A clause may be silent and inherit, may pin its own schema, or may say its acts
    stand on their arithmetic (this.i @2e2dncfe).
    """
    if clause.exempt_from_certification:
        return None
    return clause.certification if clause.certification is not None else law.certification


def _uncertified(
    corpus: Corpus,
    law: Constitution,
    subject: _Subject,
    clause: Clause,
    at: Position,
) -> RequirementElement | None:
    """What is outstanding when a law wants a certification and has not got one yet.

    ``None`` where the law requires none — a domain that names no certification
    schema authorizes its acts by their arithmetic alone — and ``None`` where one has
    already been admitted.

    The element names the party who committed the subject, because that is the domain
    whose log this is and admitting the sponsor's tally is its act rather than
    anybody else's. A sponsor may assemble a certification and cannot make it
    consequential; only the domain can do that, so only the domain's absence is a
    requirement the finding can name. Where no committed act underlies the question
    there is nothing to certify and nothing outstanding.
    """
    schema = _certification_schema(law, clause)
    if schema is None:
        return None
    if certification.certifying(corpus, subject.said, at) is not None:
        return None
    committer = _committer(corpus, subject)
    if not committer:  # pragma: no cover - a satisfied threshold implies a subject
        return None
    return RequirementElement(
        endorser=committer,
        clause=clause.id,
        schema=schema,
        kind=certification.CERTIFICATION_KIND,
    )


def _tainted(
    corpus: Corpus,
    subject: _Subject,
    clause: Clause,
    classified: Sequence[SlotDisposition],
    at: Position,
) -> Finding | None:
    """The finding an observed duplicity converts this question into, if any.

    Consulted after the requirement space is built and before a verdict is
    chosen, because "no finding is terminal while any enumerated check in the
    question's committed requirement space is unexamined" (``:1755-1757``) and a
    bearing conviction is one of those checks.

    The dispatch is ``fold/bearing.py``'s and the two arms are the text's. A
    convicted SUBJECT fires self-convicted, and the proof package names the
    contradicting pair. A convicted CITED third party fires the taint succession:
    pending, species unresolved-conflict, ground the observation. Neither arm
    reaches backwards — the walk only sees observations at or before ``at``, so a
    finding asked at a coordinate before the observation is untouched, which is
    the whole difference between this and a revocation.
    """
    committer = _committer(corpus, subject)
    ground = [one.said for one in classified if one.said is not None]
    acts = _attributions(corpus, at)
    # The whole walk, not the first hit: a subject conviction anywhere beats every
    # taint, and every taint is its own check (this.i @zmlvpkhl, Q38).
    # Each classified disposition sits at its slot's index, so a cited act leads
    # back to the slot it filled and to the schema that slot commits.
    filled: list[tuple[SAID, SAID]] = [
        (one.said, slot.schema)
        for slot, one in zip(clause.group.slots, classified, strict=True)
        if one.said is not None
    ]
    taints: list[RequirementElement] = []
    for event in corpus.upto(at):
        party = bearing.convicted(event)
        if party is None:
            continue
        which = bearing.role(party, committer=committer, ground=ground, acts=acts)
        if which is bearing.Role.SUBJECT:
            return SelfConvicted(proof=Proof(package=event.said, pair=bearing.pair_of(event)))
        if which is bearing.Role.CITED:
            # One element per slot the party's cited acts filled: a holder of two
            # offices is tainted in both, and each slot commits its own schema.
            taints.extend(
                RequirementElement(
                    endorser=party,
                    clause=clause.id,
                    schema=schema,
                    species=PendingSpecies.UNRESOLVED_CONFLICT,
                    ground=bearing.taint_ground(event),
                )
                for cited, schema in filled
                if acts.get(cited) == party
            )
    if taints:
        return Pending(requirement=canonical_requirement_set(taints))
    return None


def _committer(corpus: Corpus, subject: _Subject) -> AID:
    """Who committed the act this question is about, or ``""`` where nobody did."""
    event = corpus.event(subject.said)
    if event is None:
        return ""
    who = event.body.get("i")
    return who if isinstance(who, str) else ""


def _attributions(corpus: Corpus, at: Position) -> dict[SAID, AID]:
    """Every committed act at or before ``at``, by the party that committed it.

    Read off the events rather than taken from a caller, because pertinence is
    derived and never declared (``:1688``): an act's author is a fact about its
    committed bytes, and a fold that accepted an attribution would let a writer
    name somebody else's artifact as their own.
    """
    attributed: dict[SAID, AID] = {}
    for event in corpus.upto(at):
        who = event.body.get("i")
        if isinstance(who, str):
            attributed[event.said] = who
    return attributed


def _closed(finding: Pending) -> bool:
    """Whether a pending finding's cure path was shut *by an amendment*.

    Keyed on the species rather than on the presence of a ground, which is what
    this tested when an amendment was the only thing that could close one. A
    taint names a ground too, and it is a different closure with a different
    cure — an owned act rather than re-presentation — so a test that read any
    ground as an amendment's would report a tainted act as newly disturbed by
    whatever amendment happened to come next (``this.i`` @f3pmxu3x).
    """
    return any(
        element.species is PendingSpecies.EXPIRED_ABANDONED
        for element in finding.requirement
    )


def _cure_path_closed(
    corpus: Corpus, subject: _Subject, clause: Clause, at: Position
) -> SAID:
    """The enactment that closed this question's cure path, or ``""`` if it is open.

    Issue #82's first two rules, which are one test read twice. A pending
    finding declares its requirement space at birth, under the clause in force
    at the act's own coordinate; at a later position that space is reachable
    only if the same rule is still the rule. The test is three-part — same
    clause SAID, same requirement space, same pinned lens — and the first part
    carries the second here, because a clause *is* its bytes and an edition
    refuses to rule one act class twice, so a clause with the same identifier
    has the same slots, weights and schemas by construction.

    The third part is the pinned lens, and it is asked here: two editions can
    name one clause identifier over one set of bytes and still mean different
    things, if the semantics those bytes are read through moved between them. A
    test that compared only the clause would call that stable and it is not —
    the requirement space a pending act declared at birth was declared under the
    old lens, and nothing about the new one is bound to agree with it. So a
    change of semantics closes every cure path, exactly as a change of clause
    does, and names the enactment that made it (``fold/semantics.py``).

    Where the rule moved, the enactment that moved it is the ground: issue #82's
    first determination widened ``expired/abandoned`` to admit the amending
    enactment rather than minting a fifth species, because the amendment is
    committed by construction and an eviction receipt is not. Where it did not
    move — or where the question is a proposal, judged under the law at the
    position it is asked from, so that the two clauses are the same clause by
    construction — the answer is the empty string and nothing changes.
    """
    now = Constitution.at(corpus, at)
    governing = now.governing(subject.act)
    stable = (
        governing is not None
        and governing.said() == clause.said()
        and now.semantics == Constitution.at(corpus, subject.coordinate).semantics
    )
    return "" if stable else now.source


def _requirements(
    clause: Clause,
    classified: Sequence[SlotDisposition],
    holding: Disposition,
    species: PendingSpecies,
    ground: SAID = "",
) -> tuple[RequirementElement, ...]:
    """The slots in ``holding``, as typed requirement elements in canonical order.

    ``kind`` and ``species`` are populated here rather than left to the type's
    defaults: the element is the cure path, and an engine that let the cure path
    default has not decided what would discharge its own finding. Acme's law
    commits one cure — the arrival of a missing endorsement — so the kind is
    ``endorsement`` throughout, and the species distinguishes a slot that has not
    acted (absent, cured by the evidence arriving) from one that has spent itself
    (expired/abandoned, cured only by re-presentation).

    The walk is over the clause's own slots rather than over the classifications,
    because the schema an element must name lives in the slot and nowhere else
    (this.i @z373ew7j). The dispositions are read back by endorser, which is
    exact: a group slots each endorser at most once.

    ``ground`` names the committed event that made these elements what they are,
    and is empty for every cure that is simply the arrival of missing evidence.
    """
    held = {one.endorser: one.disposition for one in classified}
    return canonical_requirement_set(
        RequirementElement(
            endorser=slot.endorser,
            clause=clause.id,
            schema=slot.schema,
            kind="endorsement",
            species=species,
            ground=ground,
        )
        for slot in clause.group.slots
        if held.get(slot.endorser) is holding
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

    ``authority`` (``:1771-1776``, and Q6 in the register): a threshold is a
    statement about who may act, so a decision that can no longer reach unity is
    one whose actor lacks the invoked power. It is computed by a named function
    rather than taken from the type's default, because the day this engine can
    also defeat on merit or supersession, the default would be silently wrong at
    every call site instead of loudly wrong at one.
    """
    return DefeaterClass.AUTHORITY
