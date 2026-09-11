"""The slot predicate: what each slot of a group holds, given committed evidence.

This module is the reason ``threshold.py`` is separate and short. Custos withdrew
the claim that KERI's threshold algebra transfers to the evidence tier — the two
constructions are "the same satisfaction shape over differently typed slot
judgments, never one algebra" (``custos-4.2.md:1956-1958``) — and the difference is
here: "a KERI signing slot asks whether a key signed; an edge slot here asks
whether a credential stands, and that is this document's own fold question —
schema, issuer qualification, registry state, disclosure state — never the
substrate's" (``:1958-1962``). An implementer who wires a substrate threshold
evaluator to an edge group "has discharged the arithmetic and none of the slot
dispositions."

**Fail closed.** A slot is ENDORSED only when every one of these holds:

1. the act is committed as an event of kind ``endorsement``;
2. the event embeds a credential (``this.i`` @vi4t4i), and the credential's issuer
   and the event's vouched signer are both exactly the endorser the slot names;
3. the credential names the pinned endorsement schema (``this.i`` @7db5c4);
4. its attributes carry ``act`` of ``"issue"`` — this domain commits no revocation
   operator;
5. its attributes carry ``disp`` of ``"endorse"``;
6. its attributes' ``said`` is the subject under appraisal;
7. its issuer has not retracted it while the act it endorses was still in flight
   (``this.i`` @nuxitore — a withdrawal after the act settles is inert, because
   withdrawal is not falsification);
8. every credential it cites as the endorser's qualification *stood* at the
   coordinate it was cited from. Custos names registry state as one of the four
   things this judgment asks (``:1958-1962``), and the coordinate it asks about
   is the citing act's own: "the credential did stand at p, and revocation
   changes its state going forward" (issue #82, rule 4).

Anything else — an unrecognized disposition, a body whose fields are not strings,
an event of another kind that happens to read like an endorsement — is PENDING.
Never ENDORSED, and never an exception either: a slot the fold cannot verify has
simply not been filled, which is exactly what PENDING means. That is why this
module declares no error codes.

What the fold does *not* do is check a signature. Axiom 2 closes its inputs at
committed values, and a committed event is one the substrate already verified; a
fold that re-ran the cryptography would need the KERI library the purity test
forbids (``this.i`` @yrkrqj). "Signed by the expected endorser" is therefore
enforced here as attribution over evidence the substrate has already vouched for.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from utina.fold.group import AID, SAID, Disposition, Group, Slot
from utina.fold.standing import stood_at
from utina.substrate import ENDORSEMENT_SCHEMA

__all__ = [
    "ACDC_FIELD",
    "ACT_FIELD",
    "ATTRIBUTES_FIELD",
    "DECLINE",
    "DISPOSITION_FIELD",
    "EDGES_FIELD",
    "EDGE_NODE_FIELD",
    "ENDORSE",
    "ENDORSEMENT_KIND",
    "ENDORSEMENT_SCHEMA",
    "ISSUANCE",
    "ISSUER_FIELD",
    "REVOKES_FIELD",
    "SCHEMA_FIELD",
    "SUBJECT_FIELD",
    "CommittedEvent",
    "SlotDisposition",
    "attributes",
    "classify",
    "credential",
    "declinations",
    "dispositions",
    "endorsements",
]

# The committed field names are the dossier specification's, so that swapping this
# encoding for real ACDC edge groups is a substrate change and not a rewrite
# (``this.i`` @ta7vle and @pj3xhi). They are literals here so
# the seam with ``utina.enact`` is one line to reconcile.

ENDORSEMENT_KIND = "endorsement"
"""The event kind an endorsement act is committed as."""

ACDC_FIELD = "acdc"
"""Where the event embeds its credential (``this.i`` @vi4t4i). The predicate reads
the credential; the event around it is the corpus's sealing discipline."""

ATTRIBUTES_FIELD = "a"
"""The credential's attributes block, where ``disp``, ``act`` and ``said`` live."""

SCHEMA_FIELD = "s"
"""The credential's schema. The dossier's slot names the schema its endorsement
MUST satisfy (``dossier-spec-body.md:356``); with the composition rule still
domain-native there is one schema, so the predicate pins ``ENDORSEMENT_SCHEMA``."""

ISSUER_FIELD = "i"
"""Who acted. The dossier identifies the expected endorser by the issuer (``i``) of
the ACDC a slot references (``dossier-spec-body.md:356``); utina requires the event's
vouched signer and the credential's claimed issuer to agree, because evidence in
which they diverge attributes an act to nobody."""

DISPOSITION_FIELD = "disp"
SUBJECT_FIELD = "said"
"""The SAID of the subject being endorsed — the decision, not this act."""

ACT_FIELD = "act"
REVOKES_FIELD = "revokes"
"""Names an earlier act of the same issuer's that no longer stands. utina's facade
substrate has no TEL to revoke an endorsement through, so the retraction is committed
as an ordinary event; see ``docs/custos-questions.md`` Q18, which is a guess."""

EDGES_FIELD = "e"
"""Where a credential carries the edges it cites. A seated endorser's endorsement
cites its seat credential here, under DI2I; the substrate checks the *relation*
(this.i @x7crwavm) and the fold asks the different question of whether what was
cited stood when it was cited."""

EDGE_NODE_FIELD = "n"
"""Where an edge names the credential it points at."""

ENDORSE = "endorse"
DECLINE = "decline"
ISSUANCE = "issue"
"""Every endorsement an MxN group counts "MUST carry ``act`` ``"issue"``"
(``dossier-spec-body.md:371``). Revocation is a different operator, which Acme's law
does not commit."""


_PRECEDENCE = ((DECLINE, Disposition.DECLINED), (ENDORSE, Disposition.ENDORSED))
"""Which committed act decides a slot when an endorser has committed both. A
declination is examined first and so wins whatever the order, which is the reading
that never grants authority (``docs/custos-questions.md`` Q20)."""


class CommittedEvent(Protocol):
    """The read-only view of a committed event that the predicate needs.

    A structural protocol rather than an import of ``utina.fold.corpus.Event``, which
    the real Event satisfies unchanged (``this.i`` @yenp2x). The
    position is absent on purpose: the caller hands in the events at or before the
    appraisal coordinate, so this module never sees an ordering question and cannot
    get one wrong.
    """

    @property
    def said(self) -> SAID: ...

    @property
    def kind(self) -> str: ...

    @property
    def body(self) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class SlotDisposition:
    """One slot's disposition, and the act that decided it.

    ``said`` is the committed act the disposition rests on, and it is ``None``
    exactly when the disposition is PENDING — because a pending slot is the absence
    of an act, and a ground it does not have is one the finding must not claim.
    """

    endorser: AID
    disposition: Disposition
    said: SAID | None = None


def classify(
    group: Group, events: Iterable[CommittedEvent], subject: SAID
) -> tuple[SlotDisposition, ...]:
    """Each slot of ``group``, in the order the law committed it, with what it holds.

    A declination is decisive: where an endorser has committed both an endorsement
    and a declination naming ``subject``, the slot is DECLINED whatever the committed
    order, because the reading that never grants authority is the one to take when
    the specification does not say (``docs/custos-questions.md`` Q20).

    A retraction is not decisive at all once the act has settled. Which
    withdrawals reach their act is :func:`_retracted`, and it is a question about
    the whole bundle rather than about one slot, so it is answered once here
    rather than per slot.
    """
    committed = tuple(events)
    retracted = _retracted(group, committed, subject)
    return tuple(_classify_slot(slot, committed, retracted, subject) for slot in group.slots)


def dispositions(
    group: Group, events: Iterable[CommittedEvent], subject: SAID
) -> dict[AID, Disposition]:
    """The mapping ``Group.reachable`` and ``Group.satisfied`` consume."""
    return {one.endorser: one.disposition for one in classify(group, events, subject)}


def endorsements(classified: Iterable[SlotDisposition]) -> tuple[SAID, ...]:
    """The acts that added weight — an affirmed finding's ground, in slot order."""
    return tuple(
        one.said
        for one in classified
        if one.disposition is Disposition.ENDORSED and one.said is not None
    )


def declinations(classified: Iterable[SlotDisposition]) -> tuple[tuple[AID, SAID], ...]:
    """The acts that spent a slot, each with its endorser — a defeat's citation."""
    return tuple(
        (one.endorser, one.said)
        for one in classified
        if one.disposition is Disposition.DECLINED and one.said is not None
    )


def _retracts(event: CommittedEvent) -> tuple[SAID, AID] | None:
    """The act this event withdraws and who withdrew it, or ``None`` for neither.

    Deliberately liberal about the retracting event's kind and strict about its
    issuer: a retraction removes authority rather than granting it, so a broad
    reading of what retracts is the fail-closed one, while letting a stranger
    cancel someone else's endorsement would not be.
    """
    target = event.body.get(REVOKES_FIELD)
    issuer = event.body.get(ISSUER_FIELD)
    if isinstance(target, str) and isinstance(issuer, str):
        return target, issuer
    return None


def _retracted(  # ~3h6k
    group: Group, committed: tuple[CommittedEvent, ...], subject: SAID
) -> dict[SAID, set[AID]]:
    """Which retractions reached their act, and by whom.

    **Withdrawal is not falsification.** A retraction says "I no longer give
    this", which is a fact about the giver's present will. An undercut says "this
    ground was never good", which is a fact about the artifact a finding
    appraised. Only the second is evidence about the state of affairs the prior
    finding judged, and only the second reopens it: ``:1730-1745`` permits a
    successor finding to reverse a terminal value "only where its grown bundle
    contains committed evidence falsifying a ground the prior finding cites …
    and never on added contrary weight alone". The distinction is the
    ``ground-evaporation`` the ratified text names at ``:1701`` and never
    defines (``docs/custos-questions.md`` Q18 as amended, ``this.i`` @nuxitore).

    So a retraction reaches its act only while the act is still **in flight** —
    unity neither reached nor unreachable — and one committed after that is
    inert. Honoring it later would run the edges ``:1698-1712`` forbids at
    keyword force (affirmed → pending and defeated → pending, "evidence does not
    un-arrive"), and would mean any party could unmake any settled question at
    any distance, unilaterally.

    The walk is forward, and each retraction is judged against the record before
    it. That is the only order available here: this module sees no coordinates
    (see :class:`CommittedEvent`), so it steps event by event through the
    committed order it was handed, and two events at one coordinate resolve by
    the canonical tiebreak rather than as one bundle.

    Entries naming an act that is not an endorsement of ``subject`` are never
    read — :func:`_classify_slot` looks a retraction up by the identifier of an
    act already filling one of this group's slots — so the gate's answer for
    them cannot change a disposition. The early return is the ordinary case,
    where nothing was withdrawn and there is nothing to gate; it keeps the
    quadratic walk off every classification with no withdrawal in it.
    """
    reaching: dict[SAID, set[AID]] = {}
    if not any(_retracts(event) is not None for event in committed):
        return reaching
    for index, event in enumerate(committed):
        withdrawal = _retracts(event)
        if withdrawal is not None:
            target, issuer = withdrawal
            reaching.setdefault(target, set()).add(issuer)
        if not _in_flight(group, committed[: index + 1], reaching, subject):
            break
    return reaching


def _in_flight(
    group: Group,
    committed: tuple[CommittedEvent, ...],
    retracted: Mapping[SAID, set[AID]],
    subject: SAID,
) -> bool:
    """Whether the act could still go either way over this much evidence.

    Unity neither reached nor unreachable. Both halves are what they are under
    either reading of an unreachable group: where unity cannot be reached, the
    shipped pin makes the finding terminal, and §9's competing pending reading
    types its requirement ``expired/abandoned``, whose ratified cure is
    re-presentation rather than the arrival of evidence. Under both, nothing
    further can be added to *this* act — which is why this predicate does not
    consult ``UNREACHABLE_YIELDS`` and must not (``this.i`` @dozrtx).
    """
    held = {
        one.endorser: one.disposition
        for one in (_classify_slot(slot, committed, retracted, subject) for slot in group.slots)
    }
    return group.reachable(held) and not group.satisfied(held)


def _classify_slot(
    slot: Slot,
    committed: tuple[CommittedEvent, ...],
    retracted: Mapping[SAID, set[AID]],
    subject: SAID,
) -> SlotDisposition:
    standing = [
        event
        for index, event in enumerate(committed)
        if _fills(event, slot, subject)
        and slot.endorser not in retracted.get(event.said, ())
        and _qualified(event, committed[: index + 1])
    ]
    for wanted, disposition in _PRECEDENCE:
        for event in standing:
            if attributes(event).get(DISPOSITION_FIELD) == wanted:
                return SlotDisposition(slot.endorser, disposition, event.said)
    return SlotDisposition(slot.endorser, Disposition.PENDING)


def _qualified(event: CommittedEvent, asof: tuple[CommittedEvent, ...]) -> bool:
    """Whether every credential this act cites stood when this act cited it.

    ``asof`` is the record up to and including this act, so the question is
    asked at the citing coordinate and not at the position the caller is asking
    from. That is the whole of Act III: a revocation reaches no earlier act,
    because no earlier act's citation is judged over a bundle containing it, and
    it reaches every later one, because theirs are (``:1958-1962``, issue #82
    rule 4, this.i @x7crwavm).

    An act that cites nothing is qualified trivially: the founders are slotted as
    themselves and cite no credential, because nothing qualifies them beyond
    being who the law names. A citation the record cannot resolve to an issuance
    is not qualified at all — fail closed, and never an exception, because a
    citation nobody can follow is exactly as good as none.
    """
    block = credential(event).get(EDGES_FIELD)
    if not isinstance(block, Mapping):
        return True
    for name, node in block.items():
        if name == "d" or not isinstance(node, Mapping):
            continue
        cited = node.get(EDGE_NODE_FIELD)
        if not isinstance(cited, str) or not stood_at(asof, cited):
            return False
    return True


def credential(event: CommittedEvent) -> Mapping[str, object]:
    """The credential the event embeds, or an empty mapping — never an error.

    Public because the display plane reads the same committed values the
    predicate reads, and two readings of one nesting would drift.
    """
    acdc = event.body.get(ACDC_FIELD)
    return acdc if isinstance(acdc, Mapping) else {}


def attributes(event: CommittedEvent) -> Mapping[str, object]:
    """The embedded credential's attributes block, or an empty mapping."""
    block = credential(event).get(ATTRIBUTES_FIELD)
    return block if isinstance(block, Mapping) else {}


def _fills(event: CommittedEvent, slot: Slot, subject: SAID) -> bool:
    """Whether ``event`` is an issuance act by this slot's endorser on this subject.

    The disposition itself is not read here: an act that reaches this far has been
    attributed and bound to the subject, and what it *says* is the caller's next
    question.
    """
    acdc = credential(event)
    block = attributes(event)
    return (
        event.kind == ENDORSEMENT_KIND
        and acdc.get(ISSUER_FIELD) == slot.endorser
        and event.body.get(ISSUER_FIELD) == slot.endorser
        and acdc.get(SCHEMA_FIELD) == ENDORSEMENT_SCHEMA
        and block.get(ACT_FIELD) == ISSUANCE
        and block.get(SUBJECT_FIELD) == subject
    )
