"""Who certified an act, which is when it becomes consequential.

Votes being cast is not a result. An election is consequential when it is officially
tabulated and certified, and governance is the same: a decision is authorized when the
domain records that its threshold was met, not at the moment the last endorsement
happens to exist somewhere. Daniel ruled this on 2026-09-23 and ``this.i`` @2e2dncfe
carries the argument; what follows is only the part the fold needs.

**What a certification is.** A sponsor gathers the dispositions, issues a dossier ACDC
whose edges cite each one, and the domain verifies that dossier and admits it to the
GEL with an event of its own. The dossier is the proof and the admission is the act —
which is why the certifier is not merely asserting. A verifier walks the edges,
recomputes the threshold, and a certification that claims more than its edges support
contradicts itself on bytes its own signer committed.

This is the dossier specification's own machinery rather than a new invention. Joint
issuance already defines a **finalization event**, the ``fi`` field naming the AID whose
KEL carries it, and a **finalizer** who "observes the threshold to be met" and anchors
the threshold-satisfying proofs where a verifier can find them
(``schemas/dossier-spec-body.md:377-379``). There it is advisory, an aid to verifiers
who would rather not walk the graph. Here it is constitutive.

**A domain says whether it requires one**, by naming the schema its certifications must
satisfy, exactly as a slot names the endorsement schema its evidence must satisfy
(``custos-4.2.md:1946-1951``). A law that names none requires none, and its acts are
authorized by their arithmetic alone. That is not a migration convenience: whether
decisions in a domain need certifying is a governance question, and Custos delegates
this kind of committed form to the domain elsewhere for the same reason — ``:1924``
does it for expiry semantics.

**What this module does not decide.** Whether a certification's edges actually support
its claim, and what the domain must check before admitting one, are the next milestone's
(M3 and M4 of the build plan). Here the fold answers one question: does a certification
for this subject exist at or before this coordinate.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from fractions import Fraction

from utina.fold.clause import Clause
from utina.fold.corpus import Corpus, Event
from utina.fold.group import Disposition, Group
from utina.fold.slots import (
    SCHEMA_FIELD,
    SlotDisposition,
    classify,
    credential,
    declinations,
)
from utina.fold.triple import SAID, Position

__all__ = [
    "CERTIFICATION_KIND",
    "CERTIFIES_FIELD",
    "REQUIRES_FIELD",
    "certifications",
    "certifying",
    "contradicting",
    "counted_by",
    "reached_by",
    "required_by",
    "schema_for",
    "unreadable_in",
    "unresolved",
]

CERTIFICATION_KIND = "certification"
"""The committed event kind by which a domain admits a sponsor's tally to its GEL."""

CERTIFIES_FIELD = "certifies"
"""Where a certification names the subject whose threshold it reports as met."""

REQUIRES_FIELD = "certification"
"""Where a law names the schema its certifications must satisfy, or names none."""


def required_by(law: Mapping[str, object]) -> SAID | None:
    """The certification schema this law requires, or ``None`` where it requires none.

    ``None`` means the field is ABSENT. A field that is present and unreadable is a
    different thing and :func:`unreadable_in` is what asks about it — because reading
    one as the other is a fail-open, and it was one here until PR #9's substitute
    review set the field to a mapping and watched an uncertified act come back affirmed.

    The first draft of this called reading-as-absent "fail-closed in the same shape as
    the semantics block", and that had the shape exactly backwards: an unreadable
    semantics pin REFUSES the question rather than being ignored, and an unreadable
    certification requirement was being ignored. The clause level had it right all along
    — a malformed clause field inherits the law's rather than exempting the clause
    (``tests/test_evaluate.py``) — so the law level was the inconsistent one.
    """
    named = law.get(REQUIRES_FIELD)
    return named if isinstance(named, str) and named else None


def unreadable_in(law: Mapping[str, object]) -> bool:
    """Whether this law's certification field is present and not a usable identifier.

    A law that says something about certifying which this engine cannot read is law
    this engine may not apply, and the answer is a refusal rather than an exemption.
    That is axiom 4's own posture one field along: an unpinned or unrecognized external
    semantics is refused, never assumed at whatever revision happens to be installed
    (``fold/semantics.py``, ``custos-4.2.md:290``). Treating it as an exemption would
    let a domain disable its own certification requirement with a typo, which is the
    single cheapest attack on this whole mechanism.

    Absent is not unreadable. A law naming no schema requires none, and that is a
    governance choice Custos delegates (``:1924``), not a defect.
    """
    if REQUIRES_FIELD not in law:
        return False
    named = law[REQUIRES_FIELD]
    # ``False`` is the committed way a CLAUSE says "my acts stand on their arithmetic".
    # A law carrying it means the same thing and is read rather than refused.
    if named is False:
        return False
    return not (isinstance(named, str) and named)


def schema_for(clause: Clause, default: SAID | None) -> SAID | None:
    """What acts under ``clause`` must be certified against, or ``None`` for nothing.

    The clause decides and the law is the default, because how much ceremony a decision
    needs is a fact about the KIND of decision: minuting a board resolution and
    approving a routine purchase are not the same act wearing different clothes. A
    clause may be silent and inherit, may pin its own schema, or may say its acts stand
    on their arithmetic (``this.i`` @2e2dncfe).

    Here rather than in the evaluator because the law fold asks it too — an edition
    takes force where its enactment was certified (``this.i`` @pv7a6dhc) — and two
    readings of "does this domain certify at all" would drift. It takes the law's
    default rather than a ``Constitution`` because ``constitution`` imports this module
    and the reverse would be a cycle.
    """
    if clause.exempt_from_certification:
        return None
    return clause.certification if clause.certification is not None else default


def certifying(corpus: Corpus, said: SAID, upto: Position, schema: SAID) -> Event | None:
    """The committed certification of ``said`` at or before ``upto``, if there is one.

    The first rather than the last. A second certification of one subject is not a
    correction — the first one already made the act consequential, and a coordinate
    that moved when a later event arrived would make the moment of authorization a
    function of when the question was asked. "First" is well defined because
    ``Corpus`` holds its events in committed order and offers them in no other; this
    walk does not re-sort and must not, since an order of its own would be a second
    answer to a question ``corpus.py`` already answers.

    **``schema`` is required and is checked**, because a law that names the schema its
    tallies must satisfy has said something the fold has to hold it to. Without the
    check a certification issued against ANY schema discharged the requirement, which
    is the fail-open ``custos-4.2.md:1946-1951`` exists to prevent — the same sentence a
    slot's own schema field is committed for, and for the same reason: "a requirement
    that could not say which evidence it wanted would be satisfiable by the wrong one."
    Read fail-closed, in the shape the rest of this module uses: a credential whose
    schema is absent or is not a usable identifier satisfies nothing.

    **First-match is right for AUTHORIZATION and wrong for falsity**, which is why
    :func:`certifications` exists beside this. A later tally cannot move the coordinate
    an act became consequential at; it can perfectly well be a lie the domain signed.
    """
    return next(certifications(corpus, said, upto, schema), None)


def certifications(
    corpus: Corpus, said: SAID, upto: Position, schema: SAID
) -> Iterator[Event]:
    """Every certification of ``said`` this law would accept, in committed order.

    :func:`certifying` takes the first of these because that is the coordinate the act
    became consequential at. **Falsity has to look at all of them**, and the two are
    genuinely different questions: a second tally changes nothing about when the act was
    authorized, and is still a claim the domain signed — so a false one contradicts the
    record whether or not it was load-bearing (``this.i`` @epztz4wd, @7shpbven, whose
    "over every committed certification of the subject" this makes true).

    Found on PR #9, where the check read the first certification only: a sound tally
    followed by a short one left the second self-contradiction unexamined.
    """
    for event in corpus.upto(upto):
        if event.kind != CERTIFICATION_KIND:
            continue
        if event.body.get(CERTIFIES_FIELD) != said:
            continue
        if credential(event).get(SCHEMA_FIELD) == schema:
            yield event


TALLY_GROUP = "endorsements"
"""The edge group a certification's dossier carries its counted dispositions in."""


def counted_by(event: Event) -> tuple[tuple[SAID, Fraction], ...]:
    """Every disposition this certification cites, with the weight it claims for it.

    Read off the committed dossier rather than taken on anybody's word, which is what
    makes a certification proof rather than assertion: a verifier walks these edges,
    resolves each one against the record, and recomputes the sum for themselves.

    Malformed members are skipped rather than guessed at. A member that does not name
    a node, or whose weight will not parse, contributes nothing — which is the
    fail-closed direction, since the alternative is a certification reaching unity on
    bytes the fold could not read.

    **This reads what the dossier CLAIMS and resolves nothing**; :func:`unresolved` is
    the half that walks the record. The two are separate because a reader wants both
    numbers — what was claimed and what stands up — and a single function returning
    only the second would make a certification's own arithmetic unreadable.
    """
    group = credential(event).get("e", {})
    members = group.get(TALLY_GROUP) if isinstance(group, dict) else None
    if not isinstance(members, dict):
        return ()
    cited = []
    for key, member in members.items():
        if key == "o" or not isinstance(member, dict):
            continue
        node = member.get("n")
        weight = member.get("w")
        if not isinstance(node, str) or not node or not isinstance(weight, str):
            continue
        try:
            cited.append((node, Fraction(weight)))
        except (ValueError, ZeroDivisionError):
            continue
    return tuple(cited)


def reached_by(event: Event) -> Fraction:
    """What this certification's own edges add up to.

    Unity is the threshold every operator here is satisfied at, so this is the
    number a verifier compares against 1 — and a certification whose edges fall
    short has contradicted itself on bytes its sponsor signed.
    """
    return sum((weight for _, weight in counted_by(event)), Fraction(0))


def contradicting(
    corpus: Corpus, group: Group, subject: SAID, at: Position, schema: SAID
) -> tuple[Event, SAID | None] | None:
    """The committed certification of ``subject`` the record does not support, if any.

    A certification is proof rather than assertion, so one the record contradicts is
    self-contradiction on bytes its sponsor signed and its domain admitted (``this.i``
    @7shpbven). What comes back is the contradicting certification and, where the
    record names one, the disposition it cited around — never a finding, because
    whether a contradiction convicts is the evaluator's dispatch and not this module's.

    **Two contradictions, in a fixed order**, because a certification can carry both
    and two verifiers must name the same one.

    Against *itself*: the cited edges sum to less than unity while the certification
    claims a met threshold. ``utina.enact`` refuses to emit one of these
    (``this.i`` @qk3kcds6), and the check is kept anyway because the fold may not
    assume its own constructor wrote the log it is reading.

    Against *the record*: the clause's arithmetic over every disposition the domain
    admitted at or before the certification's own coordinate does not reach unity.
    This is the one @epztz4wd ruled, and it is the reason the check is not confined to
    the cited edges — edges prove presence and never absence, so a sponsor who cites
    around a declination leaves no trace in the certification itself. The coordinate
    is the certification's rather than the question's, because what a certification
    claims is that the threshold was met when it was admitted.

    **Over EVERY certification of the subject, and the earliest contradictory one wins.**
    Authorization takes the first tally and stops, because a later one cannot move the
    coordinate an act became consequential at — but falsity is a different question, and
    a lie the domain signed is a lie whether or not it was load-bearing. Reading only the
    first meant a sound tally followed by a short one left the second self-contradiction
    unexamined, which is a hole the round-two review on PR #9 found and which @7shpbven's
    own wording — "over every committed certification of the subject" — already forbade.
    Earliest rather than any, so two verifiers name the same one.
    """
    for event in certifications(corpus, subject, at, schema):
        found = _contradiction(event, corpus, group, subject)
        if found is not None:
            return found
    return None


def unresolved(event: Event, corpus: Corpus, group: Group, subject: SAID) -> SAID | None:
    """The first edge this certification cites that the record does not bear out.

    ``counted_by`` reads what the dossier CLAIMS. This walks it: every cited edge has to
    name a committed act that actually endorses ``subject``, in a slot this clause
    counts, at the weight the slot commits. An edge naming nothing, naming a declination,
    naming a party the clause does not slot, or claiming more weight than its slot
    carries, is a citation that does not stand up.

    **Without this a tally's edges were fiction and the fold did not notice.** The check
    was "do the claimed weights sum to unity" and "does the record independently reach
    unity", which are both true of a certification citing one edge that does not exist at
    weight 1 over a record that happens to carry the votes anyway — reproduced on PR #9
    by a substitute reviewer, which emitted exactly that and got ``Affirmed``. The
    docstring of ``counted_by`` had said a verifier "resolves each one against the
    record" since the day it was written, and nothing did (``this.i`` @epztz4wd's "a
    verifier walks the edges, resolves each one, and recomputes the sum for themselves").

    Returns the offending edge's identifier, which is what a proof pair wants: a reader
    sees the certification and the citation that does not hold.
    """
    endorsing = {
        one.said: one
        for one in classify(group, corpus.upto(event.position), subject)
        if one.said is not None and one.disposition is Disposition.ENDORSED
    }
    weights = {slot.key: slot.weight for slot in group.slots}
    for node, claimed in counted_by(event):
        stands = endorsing.get(node)
        if stands is None or claimed > weights.get(stands.key, Fraction(0)):
            return node
    return None


def _contradiction(
    event: Event, corpus: Corpus, group: Group, subject: SAID
) -> tuple[Event, SAID | None] | None:
    """Whether this one certification contradicts itself or the record, and on what.

    **Three checks, in this order, and the order decides which contradiction a proof
    names.** Cheapest and most internal first — the cited weights against unity. Then
    the record's own arithmetic, because that is the contradiction @epztz4wd ruled and
    the one the demo's beat 26 is about: a sponsor citing around a declination the domain
    already admitted. Then the citations themselves.

    The edge-resolution check goes LAST deliberately. An inflated weight is both a
    citation that does not stand up and a tally written around a signed no, so putting
    resolution first renamed every existing proof pair from the omitted declination to
    the offending edge — which is a worse answer for a reader, since absence is the
    surprising half. Last, it catches exactly what the other two cannot: a tally citing
    fiction over a record that independently reaches unity, which was a fail-open until
    PR #9's substitute review emitted one and got ``Affirmed``.
    """
    if reached_by(event) < 1:
        return event, None
    classified = classify(group, corpus.upto(event.position), subject)
    held: dict[str, Disposition] = {one.key: one.disposition for one in classified}
    if not group.satisfied(held):
        return event, _cited_around(event, classified)
    fiction = unresolved(event, corpus, group, subject)
    return None if fiction is None else (event, fiction)


def _cited_around(event: Event, classified: Sequence[SlotDisposition]) -> SAID | None:
    """The declination this certification omitted, where the record carries one.

    The lexicographic minimum, in the discipline ``:1766-1770`` applies to a defeated
    finding's citation: two verifiers holding the same bundle emit the same finding
    down to the byte, so which of several omissions is named may not be a property of
    the order they were walked in. ``None`` where the certification omitted nothing and
    the threshold simply was not met, in which case the contradiction is internal and
    the proof package alone names it.
    """
    cited = {said for said, _ in counted_by(event)}
    omitted = sorted(said for _, said in declinations(classified) if said not in cited)
    return omitted[0] if omitted else None
