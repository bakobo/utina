"""The law in force at a position, folded from the events committed before it.

A Constitution is a computed state, never a document: "a ratified text is an
event in the GEL; the Constitution is what the fold returns over all of them"
(``custos-4.2.md:1144-1149``). Nothing here is stored as law; ``at`` recomputes
it from committed bytes every time, which is the whole basis of the replay claim.

**Succession**, which is the mechanism this module exists for. The amendment that
changes the law is itself an event in the log this fold reads, and it is
appraised under the law in force immediately *before* its own coordinate. Custos
states it four times — 214-215, 2266-2268, 2270-2272, 3139-3143 — and the
operative form is "law never applies to itself at a coordinate, only to its
successor at the next, and succession is never retroactive" (2270-2272). At
keyword force, once: "this document's clauses are the GARD's law for every
position at and after the effectuation coordinate, and SHALL bind no position
before it" (3001-3003).

Genesis is the exception, and Custos names it in the next breath: "The
recursion's base case is genesis, constructed rather than judged" (2272-2274). A
founding law judged under its predecessor would have no predecessor, so the
inception event's clauses take force at their own coordinate while every later
enactment takes force strictly after its own. That asymmetry is the fold's whole
succession rule, and it is logged as QL5 because the text states it by
implication rather than outright.

**Editions, not deltas.** An enactment commits the complete clause set in force
after it, replacing its predecessor wholesale rather than adding to it. Custos
supplies no committed form for a repeal, so under the additive reading Acme's A1
and B1 both govern ordinary acts after the board is seated and ``governing`` has
two answers where it may have one — an uncommitted precedence seam, which
1874-1876 says an evaluator refuses rather than legislates. Logged as QL4, and
DIVERGENT: thesmo's ``m2-gamma`` reads the same spans additively.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

from utina.fold.clause import MALFORMED_LAW, Clause
from utina.fold.corpus import Corpus, Event
from utina.fold.triple import LawHead, Position

#: Where an inception or an enactment carries the law it commits. The event body
#: is the constructor's envelope — ``t``, ``i``, the committed coordinate, the
#: identifier — and the law body of ``docs/interfaces.md`` sits inside it under
#: this one key. Reading the envelope as though it were the law is the failure
#: the contract warned about in as many words: "disagree on a key and the
#: Constitution folds to nothing, with no error."
LAW_FIELD = "law"

#: The clause set inside the law body. The one field ``docs/interfaces.md``
#: makes authoritative there.
CLAUSES_FIELD = "clauses"

#: A clause id the law in force does not define. The obstacle is the law's
#: condition at this position, not the caller's bytes: "B2" is a well-formed
#: clause id that is simply not in force yet, and will be at a later coordinate.
#: (``docs/interfaces.md`` reserves ``e.law.clause-unknown.f`` for this, which is
#: not a legal Bakobo code — ``law`` is not one of the ten first descriptors and
#: the validator rejects it at import time. See ``docs/intent-law.md`` @f6mb8y.)
CLAUSE_UNKNOWN = ErrorCode(
    code="e.state.clause-unknown.f",
    title="The law in force at this position does not define that clause.",
    detail=(
        "No clause {clause} is in force at this position. A clause is in force "
        "only from the coordinate its enactment takes effect, so a clause that "
        "is unknown here may well be in force at a later position."
    ),
    args=("clause",),
    hint="Ask at a position at or after the enactment that commits the clause.",
)

#: A committed edition that cannot be read as law without inventing a rule. Two
#: clauses ruling one act kind is an uncommitted precedence seam, and 1874-1876
#: is explicit that an evaluator "SHALL refuse the invocation and SHALL NOT
#: legislate the missing seam."
CLAUSE_AMBIGUOUS = ErrorCode(
    code="e.state.clause-ambiguous.f",
    title="The law in force at this position contradicts itself.",
    detail=(
        "The committed law in force names {subject} twice, and nothing committed "
        "says which of the two rules. Choosing one would be legislating a seam "
        "the law left open, so the law is refused instead."
    ),
    args=("subject",),
    hint=(
        "Amend the domain's law so that one clause id and one act kind each have "
        "a single governing clause in any one edition."
    ),
)

#: Separates clause sub-blocks inside the aggregate. See ``canonical_bytes``.
_BLOCK = b"\x1e"


def _canonical_bytes(clauses: tuple[Clause, ...]) -> bytes:
    """Concatenate the clause sub-blocks in the one order we are free to choose.

    1475-1487 requires the clause-set head to be "an aggregate commitment over
    per-clause sub-blocks", and confesses in the same sentence that "the
    aggregate's digest function and concatenation order are semantics this
    document owes". So the order is ours, and we take wall 6's default for every
    site the spec does not rule: "lexicographic over the encoded self-addressing
    identifiers at the site" (2905-2915). Clause sub-blocks are therefore ordered
    by clause SAID.

    Ordering by SAID rather than by committed position is what makes 3101
    reachable — a stream in permuted arrival order folds to *byte-identical*
    Constitutions, which is stricter than semantic equality and is the binding
    obligation of that paragraph.
    """
    return _BLOCK.join(clause.sub_block() for clause in sorted(clauses, key=lambda c: c.said()))


def _takes_force(event: Event, position: Position) -> bool:
    """Whether this event's law is in force at ``position``.

    The asymmetry is the succession rule. Genesis is "constructed rather than
    judged" (2272-2274), so the founding law binds at its own coordinate: there
    is no predecessor to judge it under, and a domain ungoverned at its own
    inception could never enact anything. Every later enactment is judged, so it
    binds strictly after its own coordinate — "law never applies to itself at a
    coordinate, only to its successor at the next" (2270-2272). That is what
    makes an amendment answerable under the law it replaces.
    """
    if event.kind == "inception":
        return True
    if event.kind == "enactment":
        return bool(event.position < position)
    return False


def _edition_committed_by(event: Event) -> tuple[Clause, ...]:
    """The clause set a law event commits, read out of the constructor's envelope."""
    law = event.body.get(LAW_FIELD)
    if not isinstance(law, Mapping):
        raise MALFORMED_LAW(
            field=LAW_FIELD, expected="a mapping carrying the clauses this event commits"
        )
    return Clause.edition_from_committed(law.get(CLAUSES_FIELD))


def _refuse_a_contradictory_edition(clauses: tuple[Clause, ...]) -> None:
    """Fail closed where the committed edition names one thing twice."""
    ids: set[str] = set()
    ruled: set[str] = set()
    for clause in clauses:
        if clause.id in ids:
            raise CLAUSE_AMBIGUOUS(subject=f"the clause id {clause.id}")
        ids.add(clause.id)
        for act in clause.governs:
            if act in ruled:
                raise CLAUSE_AMBIGUOUS(subject=f"the act kind {act}")
            ruled.add(act)


@dataclass(frozen=True)
class Constitution:
    """The law in force at one position, and the head that identifies it."""

    law_head: LawHead
    clauses: tuple[Clause, ...]

    @classmethod
    def at(cls, corpus: Corpus, position: Position) -> Constitution:
        """Fold the committed law events up to ``position`` into the law in force.

        The inception event's law binds at its own coordinate, because genesis is
        constructed rather than judged. An enactment's law binds strictly after
        its own coordinate, because it is judged — under the law this fold is
        still holding when it reaches it, which is the law the enactment replaces.
        """
        edition: tuple[Clause, ...] = ()
        for event in corpus.upto(position):
            if _takes_force(event, position):
                edition = _edition_committed_by(event)
        _refuse_a_contradictory_edition(edition)
        head = hashlib.sha256(_canonical_bytes(edition)).hexdigest()
        return cls(law_head=LawHead(said=head), clauses=edition)

    def clause(self, id: str) -> Clause:
        """The clause bearing ``id``, or a refusal that it is not in force here."""
        for clause in self.clauses:
            if clause.id == id:
                return clause
        raise CLAUSE_UNKNOWN(clause=id)

    def governing(self, act: str) -> Clause | None:
        """The clause ruling ``act``, or ``None`` where the law is silent.

        ``None`` is load-bearing and must stay exact: it is what makes an
        ungoverned question a *refusal* rather than a finding. "Where no
        committed rule makes the invocation evaluable at all, it refuses — and
        the refusal is not a finding but an operational fact: the evaluator
        declining an ill-posed question rather than legislating the missing rule"
        (1896-1902). Returning a clause here on a guess would convert a refusal
        into a judgment, which is the one substitution Custos never permits.
        """
        for clause in self.clauses:
            if act in clause.governs:
                return clause
        return None

    def canonical_bytes(self) -> bytes:
        """The law in force, rendered to the bytes its head digests."""
        return _canonical_bytes(self.clauses)
