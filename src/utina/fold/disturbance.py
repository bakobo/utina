"""What an amendment claims to disturb, what it actually disturbs, and the gap.

Issue #82's fifth determination, ruled 2026-08-27. An amending enactment carries
a **declared disturbance set**: the pending questions whose requirement space it
claims to disturb. The fold computes the true set from the same committed bytes,
and a mismatch convicts the declaration — "the amender has testified falsely
about its own amendment, in committed bytes".

**Why a declaration at all**, when the fold can compute the set unaided. Because
the computation is the check and the declaration is the claim, and a claim is
what can be false. An amender that declared nothing could be careless; an amender
that declares wrongly has said something untrue about bytes it signed, and a
stranger holding the same log can show it with no judge, no vote and no appeal to
anything outside the record. That is KERI's duplicity-evidence doctrine lifted
one tier, and it is the strongest answer available to "why is governance not just
a document?" — a document cannot lie about itself in a way a stranger can
compute.

**What counts as disturbed.** An act is disturbed by an enactment exactly when it
was still in flight before that enactment took force and its cure path is closed
after. Both halves matter. An act that had already settled is not disturbed by
anything — it stands at its coordinate forever — and an act whose governing
clause the amendment left alone is not disturbed either, which is the specificity
half of the requirement: without it, any party able to enact anything could kill
any inconvenient pending act by amending something irrelevant
(``docs/custos-proposals.md`` R3).
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

from utina.fold.corpus import Corpus, Event
from utina.fold.triple import SAID, Position

__all__ = [
    "DISTURBS_FIELD",
    "declared",
    "package",
]

DISTURBS_FIELD = "disturbs"
"""Where an amending enactment declares the questions it claims to disturb. A
field on the enactment rather than a separate event, because the declaration and
the law change have to be the same commitment: two events could be separated, and
an amender who could commit the change without the claim would be back to
declaring nothing."""

#: What the proof package digests, so that two verifiers holding one record
#: compute one identifier for one mismatch. The sets are rendered in canonical
#: order rather than as declared, because the declaration's *order* is not part
#: of what it claims — a set is a set — and a package that moved with it would
#: make the same falsehood two different proofs.
_SEPARATOR = b"\x1e"


def declared(enactment: Event) -> tuple[SAID, ...]:
    """The disturbance set an enactment declares, in canonical order.

    An enactment that declares nothing returns an empty set, which is a claim
    like any other: it says this amendment disturbs no pending question. A field
    whose members are not identifiers is read as declaring nothing rather than
    raising — the fold reads committed bytes fail-closed, and a declaration it
    cannot read is one it cannot hold the amender to.
    """
    field = enactment.body.get(DISTURBS_FIELD)
    if not isinstance(field, Iterable) or isinstance(field, str | bytes):
        return ()
    return tuple(sorted(member for member in field if isinstance(member, str)))


def package(declared_set: tuple[SAID, ...], computed_set: tuple[SAID, ...]) -> SAID:
    """The canonical proof package identifying the mismatch between two sets.

    ``:1659-1660`` requires a self-convicted finding to carry "the identifier of
    the canonical proof package for the contradictory pair", and here the pair is
    two commitments of one enactment: what it declared, and what the fold
    computes from the same bytes it committed. The package is a digest over both
    sets in canonical order, so a stranger recomputes the identifier from the
    record alone and can say which of the two they were shown.

    SHA-256, for the reason ``clause.py`` gives for the same choice: the fold
    imports no KERI library, so the KERI-native digest is not available to it.
    """
    rendered = _SEPARATOR.join(
        [
            b"declared",
            *(member.encode("utf-8") for member in declared_set),
            b"computed",
            *(member.encode("utf-8") for member in computed_set),
        ]
    )
    return hashlib.sha256(rendered).hexdigest()


def before(position: Position) -> Position | None:
    """The last position under the law an enactment at ``position`` replaced.

    ``None`` at genesis, where there is no earlier coordinate and nothing could
    have been in flight to disturb.
    """
    return None if position.seq == 0 else Position(seq=position.seq - 1)


def acts(corpus: Corpus, kinds: tuple[str, ...], upto: Position) -> tuple[Event, ...]:
    """Every committed act of ``kinds`` at or before ``upto``, in canonical order."""
    return tuple(event for event in corpus.upto(upto) if event.kind in kinds)
