"""Whether this domain checked that its counterparty could lawfully act.

A domain may oblige itself to look before it transacts. Meridian Bank's law says that
opening an account for a customer requires confirming that the customer's own governance
approved it — and confirming means folding the customer's log, not being told.

**Neither domain reads the other's law.** Meridian's clause says "the counterparty's
domain approved this act"; it names no clause of Acme's, and Acme names nothing of
Meridian's. What crosses the boundary is a certified result over committed inputs.
``custos-4.2.md:2044`` defers a portable clause language — "sealing a subject to another
domain's law ... is chartered to the encoding round and not designed here" — and this is
deliberately not one (``this.i`` @rc5fibel).

**The seal commits the inputs and never the answer.** ``custos-4.2.md:2057`` names the
evaluation seal, defers it, and ships its admissibility rule as committed doctrine so
the deferral "cannot drift into silent adoption": admissible only over verifiable
algorithms, and "commit predicates, never verdicts. A sealed verdict a stranger cannot
recompute is smuggled authority." So a seal here carries the counterparty's gAID, the
coordinate, the law head in force there, the clause identifier and the subject's SAID —
and no verdict field exists for a later maintainer to start trusting (@gsli4bea).

**The answer is therefore recomputed every time anybody asks** (@fsbgamvi), from
evidence committed into *this* domain's own record rather than fetched from the
counterparty at question time (@odfkffca). The fold's inputs stay closed at Custos
§1.4 axiom 2's three committed values: a second, foreign corpus is never an argument to
anything. What Meridian relied on is in Meridian's log, the way a bank keeps the
customer's board resolution in the customer's file, and a stranger recomputes the whole
claim from that one log with no access to Acme at all.

**utina is a fixture for a construct the standard defers**, and says so. Custos notes
that no discriminating fixture exists for the evaluation seal; this is one. That is a
reason to build it exactly to the admissibility rule, and never a licence to describe
the seal as ratified.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from bakobo.errors import BakoboError  # type: ignore[import-untyped]

from utina.fold.corpus import Corpus, Event
from utina.fold.gel import anchored
from utina.fold.triple import SAID, Position

__all__ = [
    "CLAUSE_FIELD",
    "COORDINATE_FIELD",
    "DILIGENCE_KIND",
    "DOMAIN_FIELD",
    "EVALUATION_KIND",
    "EVENTS_FIELD",
    "EVIDENCE_FIELD",
    "HEAD_FIELD",
    "KEL_FIELD",
    "REQUIRES_FIELD",
    "SCHEMA_FIELD",
    "SEAL_FIELD",
    "SUBJECT_FIELD",
    "SUPPORTS_FIELD",
    "evidence_of",
    "recomputable",
    "required_by",
    "sealing",
    "unreadable_in",
]

#: The event kind a domain commits when it records diligence it performed. One event
#: carries both halves — the seal's inputs and the counterparty evidence it relied on —
#: because filing the resolution and recording what was checked against it are one act.
EVALUATION_KIND = "evaluation"

#: Where a law names the schema its evaluation seals must satisfy. A law naming none
#: requires no diligence, exactly as a law naming no certification schema authorizes its
#: acts by their arithmetic alone: whether a domain looks before it transacts is a
#: governance question and its law is where the answer belongs.
REQUIRES_FIELD = "diligence"

#: Which of this domain's own acts the diligence was performed for.
SUPPORTS_FIELD = "for"

#: The seal, and the four terms that make it recomputable rather than assertive.
SEAL_FIELD = "seal"

#: The schema the seal itself satisfies. Inside the seal block rather than at the top
#: of the event body, because ``_emit`` already owns ``s`` there for the GEL sequence
#: number — one letter, two meanings, and the coordinate got there first.
SCHEMA_FIELD = "schema"

DOMAIN_FIELD = "domain"
COORDINATE_FIELD = "at"
HEAD_FIELD = "head"
CLAUSE_FIELD = "clause"
SUBJECT_FIELD = "subject"

#: The counterparty's own committed record, admitted here (@odfkffca).
EVIDENCE_FIELD = "evidence"
EVENTS_FIELD = "events"
KEL_FIELD = "kel"

#: What a finding calls a requirement this module leaves outstanding.
DILIGENCE_KIND = "diligence"


def required_by(law: Mapping[str, object]) -> SAID | None:
    """The schema this law's evaluation seals must satisfy, or ``None`` for none."""
    named = law.get(REQUIRES_FIELD)
    return named if isinstance(named, str) and named else None


def unreadable_in(law: Mapping[str, object]) -> bool:
    """Whether this law's diligence field is present and not a usable identifier.

    Present-and-unreadable refuses the edition rather than exempting it, which is the
    posture ``certification.unreadable_in`` already takes and for the identical reason:
    reading an unreadable requirement as absent would let a domain switch off its own
    obligation with a typo. That is the cheapest available attack on a mechanism whose
    whole value is that the domain cannot quietly skip the check.

    Absent is not unreadable. A law naming no schema owes no diligence.
    """
    if REQUIRES_FIELD not in law:
        return False
    named = law[REQUIRES_FIELD]
    return not (isinstance(named, str) and named)


# Deliberately no per-clause override, where certification has one. A clause-level
# schema would be a new term in ``Clause.canonical_bytes``, and although it would be
# absent from a law that did not use it, the safest change to the type every pinned
# artifact hashes through is no change at all. Add one when a second clause wants a
# different answer, and not before.


def sealing(corpus: Corpus, said: SAID, upto: Position, schema: SAID) -> Event | None:
    """The evaluation seal admitted for ``said`` at or before ``upto``, if any.

    Existence only. Whether the seal's own inputs actually support it is
    :func:`recomputable`, and the two are separate for the reason certification keeps
    them separate: a requirement that is outstanding is a different fact from a
    requirement that is contradicted.
    """
    for event in corpus.upto(upto):
        if event.kind != EVALUATION_KIND:
            continue
        if event.body.get(SUPPORTS_FIELD) != said:
            continue
        seal = _seal_of(event)
        # Checked rather than assumed, for the reason a certification's schema is
        # (``custos-4.2.md:1946-1951``): a requirement that could not say which evidence
        # it wanted would be satisfiable by the wrong one. Read fail-closed — a seal
        # whose schema is absent or unusable satisfies nothing.
        if seal is None or seal.get(SCHEMA_FIELD) != schema:
            continue
        return event
    return None


def _seal_of(event: Event) -> Mapping[str, object] | None:
    seal = event.body.get(SEAL_FIELD)
    return seal if isinstance(seal, Mapping) else None


def evidence_of(event: Event) -> Corpus | None:
    """The counterparty's corpus, rebuilt from the evidence this event admitted.

    ``None`` where the block is missing or will not fold — a seal whose evidence does
    not reconstruct supports nothing, and the fold says so by leaving the requirement
    outstanding rather than by raising. Fail-closed: the effect does not land.
    """
    seal = _seal_of(event)
    block = event.body.get(EVIDENCE_FIELD)
    if seal is None or not isinstance(block, Mapping):
        return None
    events = block.get(EVENTS_FIELD)
    kel = block.get(KEL_FIELD)
    domain = seal.get(DOMAIN_FIELD)
    if not isinstance(events, Sequence) or not isinstance(kel, Sequence):
        return None
    if not isinstance(domain, str):
        return None
    rebuilt = []
    for one in events:
        if not isinstance(one, Mapping):
            return None
        said, kind, seq, body = (
            one.get("said"),
            one.get("kind"),
            one.get("seq"),
            one.get("body"),
        )
        if not isinstance(said, str) or not isinstance(kind, str):
            return None
        if not isinstance(seq, int) or not isinstance(body, Mapping):
            return None
        rebuilt.append(Event(said=said, kind=kind, position=Position(seq=seq), body=body))
    try:
        return anchored(rebuilt, list(kel), gaid=domain)
    except BakoboError:
        # Every wall ``anchored`` puts up is a coded refusal, and each one means the
        # same thing here: this evidence does not reconstruct, so it supports nothing.
        # Caught rather than propagated because a malformed seal is an act that fails
        # to authorize, not an error in the question somebody asked. Only the fold's
        # own refusals are caught; anything else is a defect and should surface.
        return None


def recomputable(event: Event) -> tuple[Corpus, SAID, Position, str, str] | None:
    """The corpus, subject, coordinate, clause and law head this seal names.

    Everything a caller needs to re-derive the counterparty's answer and to check that
    the inputs named are the inputs that produce it. ``None`` where the seal is
    malformed or its evidence does not fold, which leaves the requirement outstanding.

    The verdict is deliberately not here and is not anywhere: this returns the question,
    and the caller asks it (@gsli4bea, @fsbgamvi).
    """
    seal = _seal_of(event)
    corpus = evidence_of(event)
    if seal is None or corpus is None:
        return None
    subject, at = seal.get(SUBJECT_FIELD), seal.get(COORDINATE_FIELD)
    clause, head = seal.get(CLAUSE_FIELD), seal.get(HEAD_FIELD)
    if not isinstance(subject, str) or not isinstance(at, int):
        return None
    if not isinstance(clause, str) or not isinstance(head, str):
        return None
    return corpus, subject, Position(seq=at), clause, head
