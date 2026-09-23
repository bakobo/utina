"""What an amendment ended: the acts that were in flight and can no longer finish.

An act is disturbed by an enactment exactly when it was still in flight before
that enactment took force and its cure path is closed after. Both halves matter.
An act that had already settled is not disturbed by anything — it stands at its
coordinate forever — and an act whose governing clause the amendment left alone
is not disturbed either, which is the specificity half: without it, any party
able to enact anything could kill any inconvenient pending act by amending
something irrelevant (``docs/custos-proposals.md`` R3).

**The amender declares nothing, and this is a report rather than a charge**
(this.i @ow6dzro4). An amending enactment used to carry a declared set of the
questions it claimed to disturb, and a mismatch against the computed set
convicted it on its own bytes. Daniel removed that on 2026-09-23: the declared
set gated nothing — the law changed identically whether it was accurate, wrong
or absent — so it existed only to create something that could be false, and an
obligation that changes no outcome is not one governance should impose. It could
not always be discharged honestly either, since the truth is computed at
effectuation while the declaration was made at commitment, and any party could
table an act in between.

What is left is the computation, which is worth having on its own: an amendment
ends live matters, and a reader is owed which ones. ``utina.fold.evaluate``'s
``disturbed_by`` does the work; this module holds the two coordinate helpers it
walks with.
"""

from __future__ import annotations

from utina.fold.corpus import Corpus, Event
from utina.fold.triple import Position

__all__ = [
    "acts",
    "before",
]


def before(position: Position) -> Position | None:
    """The last position under the law an enactment at ``position`` replaced.

    ``None`` at genesis, where there is no earlier coordinate and nothing could
    have been in flight to disturb.
    """
    return None if position.seq == 0 else Position(seq=position.seq - 1)


def acts(corpus: Corpus, kinds: tuple[str, ...], upto: Position) -> tuple[Event, ...]:
    """Every committed act of ``kinds`` at or before ``upto``, in canonical order."""
    return tuple(event for event in corpus.upto(upto) if event.kind in kinds)
