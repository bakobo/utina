"""Whether an observed duplicity touches a finding, and which edge it fires.

``custos-4.2.md:1683-1694``. A conviction bears on a finding "exactly when it is
conviction-grade and pertinent": the pair convicts under the tier's committed
rules, and the convicted party's artifact is a member of one of the finding's two
birth-committed enumerations. Then the sentence this module exists for:

    The convict's role dispatches the edge: a convicted subject fires the edge
    into self-convicted; a convicted cited third party fires the taint
    succession of the duplicity section — the finding's voice is poisoned, not
    the question.

**This module shares no code path with revocation, deliberately.** Issue #82's
determination 4 asks an implementation to "make the two unmistakable in the
bearing machinery", and they are genuinely different things: a revocation moves
what a registry says about a credential and reaches no finding in either
direction, while a taint poisons a party's voice from the observation forward and
cannot be cured by evidence at all — "no missing bytes cure a taint, no log
growth cures it; only a committed act owned by the party whose conflict it is"
(``:1809-1812``). Sharing a path would make that separation a coincidence of
layout rather than a property of the engine, so ``fold/standing.py`` is neither
imported here nor importing this.

**The fold does not convict; it reads that a conviction happened.** ``:1680-1683``
makes a conviction conviction-grade at the registry and governance tiers "only
within frames that committed the violated predicate — no committed predicate, no
conviction, and the pair is ordinary evidence to consume". Acme's law commits no
predicate about signing duplicity, so the only tier left is the key tier, under
KERI's superseding-recovery calculus — which no plane above the substrate may run
(``this.i`` @yrkrqj). So the record carries a committed event saying duplicity was
OBSERVED, and this consumes it as evidence. That is the same posture the slot
predicate already takes toward signatures, and it is a weaker claim than "the fold
convicts" (``this.i`` @f3pmxu3x).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Protocol

from utina.fold.group import AID, SAID

__all__ = [
    "DUPLICITY_KIND",
    "PAIR_FIELD",
    "PARTY_FIELD",
    "CommittedEvent",
    "Role",
    "convicted",
    "pair_of",
    "role",
    "taint_ground",
]

DUPLICITY_KIND = "duplicity"
"""The event kind a committed duplicity observation carries."""

PARTY_FIELD = "party"
"""Whose signing position the observation names."""

PAIR_FIELD = "pair"
"""The two contradicting identifiers, carried so a reader holding the finding does
not have to fetch the proof package to see what contradicted what."""


class CommittedEvent(Protocol):
    """The read-only view of a committed event this module needs."""

    @property
    def said(self) -> SAID: ...

    @property
    def kind(self) -> str: ...

    @property
    def body(self) -> Mapping[str, object]: ...


class Role(Enum):
    """Which enumeration of the finding the convicted party's artifact sits in.

    The two members are the two arms of the dispatch and there is deliberately no
    third for "bears but neither" — a party that is neither the subject's
    committer nor a cited third party does not bear at all, and :func:`role`
    answers ``None`` rather than inventing a role for it.
    """

    SUBJECT = "subject"
    CITED = "cited"


def convicted(event: CommittedEvent) -> AID | None:
    """The party an observation convicts, or ``None`` where it convicts nobody.

    Fail closed and total, like every other read of a stranger's bytes in the
    fold: an event of another kind, and one whose party is not an identifier, are
    the same answer. A fold that guessed here would poison a voice nobody
    convicted, which is the most expensive mistake available in this module.
    """
    if event.kind != DUPLICITY_KIND:
        return None
    party = event.body.get(PARTY_FIELD)
    return party if isinstance(party, str) and party else None


def pair_of(event: CommittedEvent) -> tuple[SAID, ...]:
    """The contradicting identifiers an observation carries, in canonical order."""
    carried = event.body.get(PAIR_FIELD)
    if isinstance(carried, str) or not isinstance(carried, Sequence):
        return ()
    return tuple(sorted(one for one in carried if isinstance(one, str)))


def role(
    party: AID,
    *,
    committer: AID,
    ground: Sequence[SAID],
    acts: Mapping[SAID, AID],
) -> Role | None:
    """Which edge ``party``'s duplicity fires against this finding, if any.

    ``committer`` is who committed the subject the finding is about; ``ground``
    is the acts the finding cites; ``acts`` attributes each committed act to the
    party that made it. Attribution is looked up rather than taken on trust
    because "pertinence is derived, never declared" (``:1688``) — an act nobody
    can be shown to have committed is not anybody's cited artifact.

    The subject arm is tested first, and that ordering is the text's rather than
    a convenience: a convicted subject fires self-convicted, and a party that
    both committed the subject and endorsed it is convicted on the question
    rather than merely tainted.

    ``None`` is the third arm and the one that matters most. "Contradictory pairs
    convict only where they bear on the question — duplicity elsewhere in a
    subject's history taints that history's standing, but it does not convert
    this question's finding" (``:1751-1753``). A fold that let any convicted
    party anywhere poison every finding would make one bad actor fatal to a whole
    record, which is the opposite of what the duplicity doctrine is for.
    """
    if party == committer:
        return Role.SUBJECT
    if any(acts.get(cited) == party for cited in ground):
        return Role.CITED
    return None


def taint_ground(event: CommittedEvent) -> SAID:
    """What a tainted pending finding names as its ground: the observation itself.

    A pending that named no ground is the discretion replay exists to remove
    (axiom 3). The cure for a taint is not the arrival of evidence, so the ground
    cannot be the missing bytes — it is the committed act that poisoned the voice,
    and the cure the requirement names is an owned act of the party whose conflict
    it is.
    """
    return event.said
