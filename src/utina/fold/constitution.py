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

**Effectuation**, which is the coordinate that sentence turns on and the one
Custos never defines. An enactment is an act: "a ratification is an enactment, an
enactment is judged under the Constitution it amends, and the judgment is a
finding like any other" (214-215). So an edition takes force where its enactment
*carried* — the first coordinate at which the enactment's own lawfulness reaches
unity under the clause governing it — and an enactment that is never endorsed, or
that is defeated, confers nothing however well signed. Keying force on the
enactment being merely committed is the reading this module shipped with, and
under it a single party amends the law alone (tick ``4pmw``, R4 in
``docs/custos-proposals.md``, Q33 in ``docs/custos-questions.md``, ``this.i``
@xhtvuxnc). The consequence for this module is that the law fold is no longer a
walk over law events: it consults the slot predicate, because whether an edition
is in force is a question about evidence.

Genesis is the exception, and Custos names it in the next breath: "The
recursion's base case is genesis, constructed rather than judged" (2272-2274). A
founding law judged under its predecessor would have no predecessor, so the
inception event's clauses take force at their own coordinate while every later
enactment takes force strictly after its own. That asymmetry is the fold's whole
succession rule, and it is logged as Q15 because the text states it by
implication rather than outright.

**Editions, not deltas.** An enactment commits the complete clause set in force
after it, replacing its predecessor wholesale rather than adding to it. Custos
supplies no committed form for a repeal, so under the additive reading Acme's A1
and B1 both govern ordinary acts after the board is seated and ``governing`` has
two answers where it may have one — an uncommitted precedence seam, which
1874-1876 says an evaluator refuses rather than legislates. Logged as Q14, and
DIVERGENT: thesmo's ``m2-gamma`` reads the same spans additively.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

from utina.fold import certification, semantics
from utina.fold.clause import MALFORMED_LAW, Clause
from utina.fold.corpus import Corpus, Event
from utina.fold.slots import dispositions
from utina.fold.triple import SAID, LawHead, Position

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

#: Where a committed act names its class. An enactment is an act — judged like any
#: other (214-215) — so the law fold is the first reader of this field, and
#: ``utina.fold.evaluate`` imports it from here rather than declaring a second name
#: for the same committed bytes.
ACT_CLASS_FIELD = "act"

#: The event kinds that commit an edition of law. Genesis and amendment differ in
#: how they take force and in nothing else: one is constructed, one is judged.
INCEPTION_KIND = "inception"
ENACTMENT_KIND = "enactment"

#: A clause id the law in force does not define. Not the caller's bytes: "B2" is
#: a well-formed clause id that is simply not in force yet, and will be at a
#: later coordinate. It is the contract's reserved code, and ``rule`` is the
#: descriptor because governance rules live there and a clause id is the
#: identity of a governance rule. (The law commission read an earlier
#: ``docs/interfaces.md`` that reserved ``e.law.clause-unknown.f``, which is not
#: a legal Bakobo code — ``law`` is outside the closed descriptor set and the
#: validator rejects it at import — and chose ``e.state`` as the repair. The
#: contract has since been corrected to a legal code, so the repair is spent.
#: See ``this.i`` @f6mb8y.)
CLAUSE_UNKNOWN = ErrorCode(
    code="e.rule.clause-unknown.f",
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


#: Where an enactment cites the law event whose edition it amends (this.i @fougolzt).
PRIOR_FIELD = "prior"


@dataclass(frozen=True)
class Succession:
    """One link of the succession record ``custos-4.2.md:3039-3042`` asks for:
    the predecessor, the ratifying enactment, and the effectuation coordinate."""

    predecessor: str
    enactment: str
    effectuation: Position


def _chain(corpus: Corpus, position: Position) -> tuple[Event, tuple[Succession, ...]] | None:
    """The law event in force at ``position``, and the succession that led to it.

    Genesis is "constructed rather than judged" (2272-2274), so the founding law
    binds at its own coordinate and is the chain's root. From each edition the
    succession is the earliest enactment in GEL order that claims it, is eligible
    under it, and has taken force by ``position`` — "the GEL's committed order
    rules: the earlier lawful enactment is the succession, and the later travels
    as evidence" (3047-3050, this.i @fougolzt). ``None`` before any founding law.
    """
    committed = corpus.upto(position)
    current = next((event for event in committed if event.kind == INCEPTION_KIND), None)
    if current is None:
        return None
    links: list[Succession] = []
    while True:
        found = _successor(corpus, committed, current, position)
        if found is None:
            return current, tuple(links)
        successor, effectuation = found
        links.append(Succession(current.said, successor.said, effectuation))
        current = successor


def _successor(
    corpus: Corpus, committed: tuple[Event, ...], current: Event, position: Position
) -> tuple[Event, Position] | None:
    for event in committed:
        # Strictly between: an enactment never binds at its own coordinate (2270-2272),
        # and asking for the law there is how its judging law is found, so an
        # enactment at ``position`` itself would recur without descending.
        if event.kind != ENACTMENT_KIND or not current.position < event.position < position:
            continue
        cited = event.body.get(PRIOR_FIELD)
        if cited is not None and cited != current.said:
            continue
        judging = Constitution.at(corpus, event.position)
        if not _claims(event, current.said, judging):
            continue
        effectuation = _effectuation(corpus, event, position, judging)
        if effectuation is not None:
            return event, effectuation
    return None


def _claims(enactment: Event, predecessor: str, judging: Constitution) -> bool:
    """Whether ``enactment`` is an eligible claimant of ``predecessor``'s edition.

    Eligibility is latest-unsuperseded (3043-3047): the edition in force at the
    enactment's own coordinate must be the one it claims. An enactment citing
    none claims the edition in force at its coordinate, since §18 never obliges
    the citation (Q33); one citing a different edition was already passed over
    by :func:`_successor`, before its judging law was computed.
    """
    return judging.source == predecessor


def _effectuation(
    corpus: Corpus,
    enactment: Event,
    position: Position,
    judging: Constitution,
) -> Position | None:
    """The coordinate at which ``enactment`` reached unity, or ``None`` by ``position``.

    The first crossing, and the first is the only one that counts: a finding
    stands at its coordinate and "evidence does not un-arrive" (1698-1712), so an
    enactment that carried has carried, and a later retraction of an endorsement
    that reached unity does not unmake the edition. The scan is over candidate
    coordinates strictly after the enactment's own, with every slot reclassified
    from the whole bundle at each one — the slot predicate is consulted rather
    than reimplemented, because the rules that decide a slot are subtle (a
    declination is decisive whatever the committed order) and two readings of
    them would drift.

    ``None`` where the enactment names no act class, where the law in force at
    its own coordinate governs no such class, or where unity is not reached at or
    before ``position``. All three are the same fail-closed answer: nothing
    committed says this enactment carried, so it confers no law.
    """
    act = enactment.body.get(ACT_CLASS_FIELD)
    if not isinstance(act, str) or not act:
        return None
    clause = _governing(judging.clauses, act)
    if clause is None:
        return None
    committed = corpus.upto(position)
    for candidate in committed:
        if not enactment.position < candidate.position:
            continue
        bundle = tuple(one for one in committed if not candidate.position < one.position)
        if clause.group.satisfied(dispositions(clause.group, bundle, enactment.said)):
            return candidate.position
    return None


def _governing(clauses: tuple[Clause, ...], act: str) -> Clause | None:
    """The clause ruling ``act`` in ``clauses``, or ``None`` where none does."""
    for clause in clauses:
        if act in clause.governs:
            return clause
    return None


def _edition_committed_by(
    event: Event,
) -> tuple[tuple[Clause, ...], str | None, str | None]:
    """The clause set a law event commits, the semantics it pins, and what it certifies by.

    All three come out of one envelope because they are one commitment: a clause
    set, the lens it is to be read through, and whether a decision under it needs
    certifying are not separable claims, and an edition that carried some without
    the others would be law nobody can apply (``fold/semantics.py``, axiom 4).
    """
    law = event.body.get(LAW_FIELD)
    if not isinstance(law, Mapping):
        raise MALFORMED_LAW(
            field=LAW_FIELD, expected="a mapping carrying the clauses this event commits"
        )
    return (
        Clause.edition_from_committed(law.get(CLAUSES_FIELD)),
        semantics.declared(law),
        certification.required_by(law),
    )


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
    semantics: SAID | None = None
    """The digest of the external semantics this edition's clauses are expressed
    in, or ``None`` where the edition pins none. Carried rather than checked here
    because folding the law and refusing a question are different jobs: a
    Constitution is the law in force, and whether this engine can apply it is the
    evaluator's question (``fold/semantics.py``, axiom 4, tick 2uhi)."""

    certification: SAID | None = None
    """The schema this domain's certifications must satisfy, or ``None`` where the
    edition requires none and an act is authorized by its arithmetic alone. Named by
    the law for the same reason a slot names its endorsement schema
    (``custos-4.2.md:1946-1951``): a requirement that could not say which evidence it
    wanted would be satisfiable by the wrong one. See ``fold/certification.py``."""

    source: SAID = ""
    """The identifier of the law event whose edition this is — the inception, or
    the enactment that took force. Carried because a finding that says a cure
    path closed has to name what closed it, and the answer is this event
    (issue #82, determination 1). Empty where no law is in force at all."""

    @classmethod
    def at(cls, corpus: Corpus, position: Position) -> Constitution:
        """Fold the committed law events up to ``position`` into the law in force.

        The inception event's law binds at its own coordinate, because genesis is
        constructed rather than judged. An enactment's law binds from the
        coordinate its own judgment reached unity, because it is judged — under
        the law in force at its own coordinate, which is the law it replaces.

        Which enactment succeeds an edition is §17's rule rather than the walk's:
        the earliest eligible claimant in GEL order that has taken force
        (3043-3050, :func:`_chain`, this.i @fougolzt).
        """
        key = (cls, position.seq)
        known = corpus.memo.get(key)
        if isinstance(known, Constitution):
            return known
        edition: tuple[Clause, ...] = ()
        source = ""
        pinned: str | None = None
        certifies_by: str | None = None
        chain = _chain(corpus, position)
        if chain is not None:
            edition, pinned, certifies_by = _edition_committed_by(chain[0])
            source = chain[0].said
        _refuse_a_contradictory_edition(edition)
        head = hashlib.sha256(_canonical_bytes(edition)).hexdigest()
        constitution = cls(
            law_head=LawHead(said=head),
            clauses=edition,
            source=source,
            semantics=pinned,
            certification=certifies_by,
        )
        corpus.memo[key] = constitution
        return constitution

    @classmethod
    def succession(cls, corpus: Corpus, position: Position) -> tuple[Succession, ...]:
        """The succession record at ``position``, derived from the GEL alone.

        ``custos-4.2.md:3039-3042``: "predecessor digest, ratifying enactment, and
        effectuation coordinate — SHALL be derivable from the GEL as a detached
        record". Empty before any founding law, and where the founding law is
        still in force.
        """
        chain = _chain(corpus, position)
        return () if chain is None else chain[1]

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
        return _governing(self.clauses, act)

    def canonical_bytes(self) -> bytes:
        """The law in force, rendered to the bytes its head digests."""
        return _canonical_bytes(self.clauses)
