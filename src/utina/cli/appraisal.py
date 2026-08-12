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
from utina.fold.clause import Clause
from utina.fold.constitution import Constitution
from utina.fold.corpus import Corpus, Event
from utina.fold.evaluate import ACT_CLASS_FIELD, ACT_KINDS, evaluate
from utina.fold.finding import Finding
from utina.fold.question import Committed, Proposal, Question
from utina.fold.refusal import Refusal
from utina.fold.slots import SlotDisposition, classify
from utina.fold.triple import SAID, Position

__all__ = ["Appraisal", "appraise", "question_from", "resolve_subject"]

#: The domain's display name. ``utina.acme.GAID`` is the identifier; this is what a
#: person calls it, and the CLI's whole world is this one domain.
DOMAIN = "Acme"

#: What the fold hands its slot predicate when nothing of the class has been tabled. No
#: committed event bears it, so every slot classifies pending, which is the true answer.
NOTHING_TABLED = ""

_EVAL_USAGE = (
    "utina eval <act-class> --at <position>, or utina eval --said <token> --at <position>"
)


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


def appraise(corpus: Corpus, question: Question, *, at: Position, label: str) -> Appraisal:
    """Answer ``question`` at ``at``, and recover the working behind the answer."""
    outcome = evaluate(corpus, question, at=at)
    act, subject, coordinate = _subject(corpus, question, at)
    law = Constitution.at(corpus, coordinate)
    clause = None if act is None else law.governing(act)
    slots: tuple[SlotDisposition, ...] = ()
    if clause is not None:
        slots = classify(clause.group, corpus.upto(at), subject or NOTHING_TABLED)
    return Appraisal(
        question=question,
        headline=_headline(question, subject),
        label=label,
        position=at,
        law=law,
        outcome=outcome,
        clause=clause,
        act=act,
        subject=subject,
        slots=slots,
    )


def _headline(question: Question, subject: SAID | None) -> str:
    if isinstance(question, Proposal):
        return f"may {DOMAIN} perform an act of the class {question.act}?"
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
