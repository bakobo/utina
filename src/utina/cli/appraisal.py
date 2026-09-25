"""One appraisal, with everything a screen needs to show its working.

``evaluate`` returns a finding, and a finding carries its ground but never the whole slot
table: an affirmation names the endorsements that reached unity, a defeat names the one
declination it cites, a pending names only the slots still outstanding. None of them
names every slot with its weight and what it holds, which is what this.i @clarth requires
on the screen — the audience is here to check arithmetic, and arithmetic with the
subtrahend missing is not checkable.

So this module recomputes the table, from the same committed values, with the fold's own
predicate. That is a second path to a governance-relevant fact, and a second path can
diverge in silence, so ``tests/test_cli.py`` walks every beat and asserts the table
implies the verdict (this.i @clxchk). Two rules keep the paths together by construction:
the constants that decide what a committed act *is* are imported from the evaluator
rather than restated, and the clause comes from ``Constitution.governing`` — the call the
evaluator itself makes — rather than being read back off the finding, which would make
the two agree trivially and prove nothing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from utina.cli.errors import COMMAND_MALFORMED, SAID_PREFIX_AMBIGUOUS
from utina.fold import diligence as diligence_predicate
from utina.fold import slots as slot_predicate
from utina.fold import standing
from utina.fold.clause import Clause
from utina.fold.constitution import ACT_CLASS_FIELD, Constitution
from utina.fold.corpus import Corpus, Event
from utina.fold.evaluate import ACT_KINDS, evaluate, supported
from utina.fold.finding import Finding
from utina.fold.question import Committed, Proposal, Question
from utina.fold.refusal import Refusal
from utina.fold.slots import SlotDisposition, classify
from utina.fold.triple import SAID, Position

__all__ = [
    "Appraisal",
    "Diligence",
    "appraise",
    "held_by",
    "question_from",
    "registry_holdings",
    "resolve_credential",
    "resolve_subject",
]

#: What the fold hands its slot predicate when nothing of the class has been tabled. No
#: committed event bears it, so every slot classifies pending, which is the true answer.
NOTHING_TABLED = ""

_EVAL_USAGE = (
    "utina eval <act-class> --at <position>, or utina eval --said <token> --at <position>"
)


@dataclass(frozen=True)
class Diligence:
    """One discharged diligence requirement, with the working behind it.

    Every field is read back off the committed seal and the re-fold, never off the
    finding: the point of the mechanism is that a reader recomputes rather than trusts,
    and a screen that printed what the seal *claimed* would be demonstrating the
    opposite of what the beat is about (``this.i`` @fsbgamvi).
    """

    counterparty: str
    """The customer's own governed-domain identifier."""
    at: Position
    """The coordinate in the customer's log that was relied on."""
    head: str
    """The law head in force there — what makes the coordinate mean one thing."""
    clause: str
    """The customer's own clause that answered."""
    subject: SAID
    """The customer's committed act."""
    events: int
    """How many of the customer's events this domain holds, which is what a stranger
    re-folds. A count rather than a list: the screen's claim is that the evidence is
    HERE, and thirty identifiers would not make it more here."""
    outcome: Finding | Refusal
    """What re-folding that evidence says, computed now."""


@dataclass(frozen=True)
class Appraisal:
    """One question, its answer, and the working behind the answer."""

    question: Question
    headline: str
    label: str
    position: Position
    law: Constitution
    outcome: Finding | Refusal
    clause: Clause | None
    act: str | None
    subject: SAID | None
    slots: tuple[SlotDisposition, ...]
    diligence: Diligence | None = None
    """What this domain checked about a counterparty before acting, where its law
    obliges it to check anything. ``None`` where the law obliges none — which is every
    domain but Meridian — and where the obligation stands undischarged, since a
    requirement the finding already names as outstanding needs no second telling."""


def resolve_subject(
    names: Mapping[str, SAID], events: tuple[Event, ...], token: str
) -> SAID:
    """The committed identifier ``token`` names: a record name, a prefix, or itself.

    A 44-character identifier is not something a narrator types, so the demo record's own
    names (``seat-the-board``) and the 12-character prefix the screens print are both
    accepted (this.i @clhndl). A token matching nothing is handed to the fold unchanged
    rather than refused here: a question about bytes nobody committed is ill-posed, and
    the fold's answer to an ill-posed question is a refusal, which is a result and not an
    error.
    """
    if token in names:
        return names[token]
    matches = tuple(event.said for event in events if event.said.startswith(token))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise SAID_PREFIX_AMBIGUOUS(
            prefix=token, matches=", ".join(match[:12] + "..." for match in matches)
        )
    return token


def resolve_credential(
    names: Mapping[str, SAID], events: tuple[Event, ...], token: str | None
) -> SAID | None:
    """The *credential* ``token`` names, out of the issuance that committed it.

    A citation names a credential and not the event that carried it, so this
    cannot reuse :func:`resolve_subject`: the record's own names point at events,
    and the credential lives one level inside. ``None`` in, ``None`` out, because
    an endorser who cites nothing is making no claim about their qualification
    rather than making an empty one.

    A token that resolves to no committed credential is handed back unchanged, so
    that a citation nobody can follow is refused by the constructor — which is
    where the claim is judged — rather than rewritten here into one that can be.
    """
    if token is None:
        return None
    said = names.get(token, token)
    for event in events:
        acdc = event.body.get("acdc")
        if event.said == said and isinstance(acdc, Mapping) and isinstance(acdc.get("d"), str):
            return str(acdc["d"])
    return said


def held_by(upto: tuple[Event, ...], seat: str) -> dict[str, object]:
    """The standing credential the record shows this office holding, folded.

    The LAST issuance naming the office as issuee, because an office re-seated
    after a revocation holds the newer credential and a screen showing the older
    one would report an office as empty while it is filled. Its state is read at
    the same coordinate, so the two halves of the row cannot disagree.
    """
    held: dict[str, object] = {
        "said": "",
        "schema": "",
        "issuer": "",
        "issuee": seat,
        "registry": "",
        "state": None,
        "acts": "",
    }
    for event in upto:
        acdc = slot_predicate.credential(event)
        block = slot_predicate.attributes(event)
        if event.kind != standing.ISSUANCE_KIND or block.get("i") != seat:
            continue
        constraints = block.get("constraints")
        registry = str(event.body.get("ri", ""))
        said = str(acdc.get("d", ""))
        may = constraints.get("acts", ()) if isinstance(constraints, Mapping) else ()
        held = {
            "said": said,
            "schema": acdc.get("s", ""),
            "issuer": acdc.get("i", ""),
            "issuee": seat,
            "registry": registry,
            "state": standing.state_over(upto, registry, said),
            "acts": ", ".join(str(one) for one in may),
        }
    return held


def registry_holdings(upto: tuple[Event, ...], registry: str) -> list[dict[str, object]]:
    """Every credential this registry issued, with its state and what moved it."""
    rows: list[dict[str, object]] = []
    for event in upto:
        if event.kind != standing.ISSUANCE_KIND or event.body.get("ri") != registry:
            continue
        said = str(slot_predicate.credential(event).get("d"))
        moved = next(
            (
                one.said
                for one in upto
                if one.kind == standing.REVOCATION_KIND
                and one.body.get("ri") == registry
                and one.body.get("said") == said
            ),
            "",
        )
        rows.append(
            {
                "said": said,
                "issued": event.position.seq,
                "state": standing.state_over(upto, registry, said) or "unknown",
                "moved": moved,
            }
        )
    return rows


def question_from(
    names: Mapping[str, SAID], events: tuple[Event, ...], act: str | None, said: str | None
) -> Question:
    """The question a person asked, from the two ways they can ask it.

    Exactly one of the two, because the alternatives mean different things: an act class
    asks what may be done now, and an identifier asks whether a committed act was lawful.
    A command supplying both has not said which, and guessing would pick the law of a
    different coordinate.
    """
    if (act is None) == (said is None):
        raise COMMAND_MALFORMED(
            detail=(
                "eval takes either an act class or --said, and exactly one of the two: an "
                "act class asks what may be done now, an identifier asks whether a "
                "committed act was lawful"
            ),
            usage=_EVAL_USAGE,
        )
    if act is not None:
        return Proposal(act)
    return Committed(resolve_subject(names, events, str(said)))


def diligence_behind(
    corpus: Corpus, law: Constitution, subject: SAID | None, at: Position
) -> Diligence | None:
    """The discharged diligence standing behind an act, re-derived rather than read.

    ``None`` where the law obliges none, where nothing is tabled, or where the seal
    does not hold up — in that last case the finding is already PENDING and names the
    requirement, so a screen repeating it would be saying the same thing twice.

    Whether it holds up is asked of :func:`~utina.fold.evaluate.supported`, which is the
    function the evaluator itself calls. Deciding it here instead would be a second path
    to a governance-relevant fact, and it diverged the first time it was written.
    """
    if law.diligence is None or subject is None:
        return None
    sealed = diligence_predicate.sealing(corpus, subject, at, law.diligence)
    # The evaluator's own predicate, not a second one. A seal that does not hold up
    # shows no block: the finding beside it is already PENDING and names the
    # requirement, so a block here would report a failed check as though it had worked.
    if sealed is None or not supported(sealed):
        return None
    recomputed = diligence_predicate.recomputable(sealed)
    assert recomputed is not None  # ``supported`` read it, so it reads
    theirs, their_subject, their_at, their_clause, their_head = recomputed
    seal = sealed.body[diligence_predicate.SEAL_FIELD]
    assert isinstance(seal, Mapping)  # ``recomputable`` read it as one already
    return Diligence(
        counterparty=str(seal[diligence_predicate.DOMAIN_FIELD]),
        at=their_at,
        head=their_head,
        clause=their_clause,
        subject=their_subject,
        events=len(theirs.upto(their_at)),
        outcome=evaluate(theirs, Committed(their_subject), at=their_at),
    )


def appraise(
    corpus: Corpus, question: Question, *, at: Position, label: str, domain: str
) -> Appraisal:
    """Answer ``question`` at ``at``, and recover the working behind the answer.

    ``domain`` is what a screen calls the governed domain — ``Record.display`` — and it
    reaches only the headline. It was a module constant reading ``"Acme"`` while there
    was one fixture, and a constant cannot vary by domain (this.i @s34hkwkv).
    """
    outcome = evaluate(corpus, question, at=at)
    act, subject, coordinate = _subject(corpus, question, at)
    law = Constitution.at(corpus, coordinate)
    clause = None if act is None else law.governing(act)
    slots: tuple[SlotDisposition, ...] = ()
    if clause is not None:
        slots = classify(clause.group, corpus.upto(at), subject or NOTHING_TABLED)
    return Appraisal(
        question=question,
        headline=_headline(question, subject, domain),
        label=label,
        position=at,
        law=law,
        outcome=outcome,
        clause=clause,
        act=act,
        subject=subject,
        slots=slots,
        diligence=diligence_behind(corpus, law, subject, at),
    )


def _headline(question: Question, subject: SAID | None, domain: str) -> str:
    if isinstance(question, Proposal):
        return f"may {domain} perform an act of the class {question.act}?"
    return f"was the committed act {subject or question.said} lawful?"


def _subject(
    corpus: Corpus, question: Question, at: Position
) -> tuple[str | None, SAID | None, Position]:
    """What the question is about, and whose law judges it.

    The coordinate is the subject's own for a committed act — the past is recomputed
    under the law in force then — and the appraisal position for a proposal, which is a
    question about now. Where the subject cannot be resolved at all, there is no act, no
    clause and no arithmetic, and the fold's own answer is a refusal.
    """
    if isinstance(question, Proposal):
        return question.act, _latest_act(corpus, question.act, at), at
    event = corpus.event(question.said)
    if event is None or at < event.position:
        return None, None, at
    act = event.body.get(ACT_CLASS_FIELD)
    if event.kind not in ACT_KINDS or not isinstance(act, str) or act == "":
        return None, event.said, event.position
    return act, event.said, event.position


def _latest_act(corpus: Corpus, act: str, at: Position) -> SAID | None:
    """The most recent committed act of this class at or before ``at``, if any.

    Latest wins, as the evaluator's own ``_latest_act`` does and for the same reason: a
    decision re-tabled because it was contested must not inherit the endorsements of the
    tabling it replaced.
    """
    found: SAID | None = None
    for event in corpus.upto(at):
        if event.kind in ACT_KINDS and event.body.get(ACT_CLASS_FIELD) == act:
            found = event.said
    return found
