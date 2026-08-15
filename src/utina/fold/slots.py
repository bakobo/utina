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
7. its issuer has not retracted it.

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
from utina.substrate import ENDORSEMENT_SCHEMA

__all__ = [
    "ACDC_FIELD",
    "ACT_FIELD",
    "ATTRIBUTES_FIELD",
    "DECLINE",
    "DISPOSITION_FIELD",
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
    """
    committed = tuple(events)
    retracted = _retracted(committed)
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


def _retracted(committed: tuple[CommittedEvent, ...]) -> dict[SAID, set[AID]]:
    """Which acts have been retracted, and by whom.

    Deliberately liberal about the retracting event's kind and strict about its
    issuer: a retraction removes authority rather than granting it, so a broad
    reading of what retracts is the fail-closed one, while letting a stranger
    cancel someone else's endorsement would not be.
    """
    retractions: dict[SAID, set[AID]] = {}
    for event in committed:
        target = event.body.get(REVOKES_FIELD)
        issuer = event.body.get(ISSUER_FIELD)
        if isinstance(target, str) and isinstance(issuer, str):
            retractions.setdefault(target, set()).add(issuer)
    return retractions


def _classify_slot(
    slot: Slot,
    committed: tuple[CommittedEvent, ...],
    retracted: Mapping[SAID, set[AID]],
    subject: SAID,
) -> SlotDisposition:
    standing = [
        event
        for event in committed
        if _fills(event, slot, subject)
        and slot.endorser not in retracted.get(event.said, ())
    ]
    for wanted, disposition in _PRECEDENCE:
        for event in standing:
            if attributes(event).get(DISPOSITION_FIELD) == wanted:
                return SlotDisposition(slot.endorser, disposition, event.said)
    return SlotDisposition(slot.endorser, Disposition.PENDING)


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
