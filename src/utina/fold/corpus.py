"""Committed evidence, and the single order the fold consumes it in.

Custos makes the consumption order a site rule at ``custos-4.2.md:3091-3101``:
"A fold consumes its log in exactly one order, and that order derives from
committed bytes: KEL anchoring order first, intra-anchor order as the anchoring
event's seal list states, and no tiebreak that consults anything uncommitted."
It then names the failure it is guarding against, so plainly that it is worth
quoting rather than paraphrasing: "An implementation whose fold result depends on
arrival order, storage order, or any ambient sequence does not conform."

That is the whole design of this module. A ``Corpus`` is not a container that
remembers how it was filled — it puts what it is given into the committed order
at construction and has no other order to offer. There is deliberately no
accessor that returns events in the order they arrived, because the cheapest way
to keep an ambient order out of a fold is to have nowhere to read one from.

The order is ``(anchoring coordinate, self-addressing identifier)``. The first
component is 3094-3095's anchoring order. The second is wall 6's default —
"lexicographic over the encoded self-addressing identifiers at the site unless
the site's clause commits a different derivable order" (2905-2915) — standing in
for 3095's intra-anchor seal-list order, which has been flattened away by the
time an event reaches the fold. That substitution is a guess, and it is logged
as QL1 in ``docs/questions-law.md`` because two conforming engines can order two
events sealed into one rotation differently.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

from utina.fold.triple import Position

#: Two committed spans bearing one self-addressing identifier and different
#: bytes. Their canonical keys collide, so the only thing that could separate
#: them is the order they turned up in, and consuming that is what 3097-3099
#: forbids by name. Refusing here rather than picking is the fail-closed reading;
#: QL3 in ``docs/questions-law.md`` records that wall 7 permits reading the same
#: stimulus as a duplicity conviction instead.
ORDER_AMBIENT = ErrorCode(
    code="e.state.order-ambient.f",
    title="This evidence cannot be put into a committed order.",
    detail=(
        "Two different events were presented under the identifier {said}. A "
        "self-addressing identifier ranges over an event's complete committed "
        "bytes, so one identifier over two sets of bytes leaves nothing "
        "committed to order them by, and the order they arrived in is not "
        "something a fold may consult."
    ),
    args=("said",),
    hint=(
        "Present the events under the identifiers their own bytes derive, and "
        "re-derive any identifier that does not match its event."
    ),
)


@dataclass(frozen=True)
class Event:
    """One committed event, at the coordinate that gives it its place in the order.

    ``body`` is opaque to this module and stays that way: the walk decides an
    order and never reads a payload to do it, which is what keeps the order a
    function of the coordinate and the identifier alone. Reading a body is the
    law fold's job, in ``constitution.py``.
    """

    said: str
    kind: str
    position: Position
    body: Mapping[str, object]


class Corpus:
    """Committed events, held in canonical order and offered in no other."""

    def __init__(self, events: tuple[Event, ...]) -> None:
        self._events = events
        self._by_said = {event.said: event for event in events}

    @classmethod
    def load(cls, events: Iterable[Event]) -> Corpus:
        """Put committed events into canonical order, or refuse to order them.

        An event presented more than once folds once: 3087-3089 makes the
        self-addressing identifier the identity and the coordinate merely a
        location, so a repeat presentation is one event arriving again rather
        than a competitor (QL2). Two *different* events under one identifier are
        the collision this cannot resolve, and it refuses.
        """
        seen: dict[str, Event] = {}
        for event in events:
            settled = seen.setdefault(event.said, event)
            if settled != event:
                raise ORDER_AMBIENT(said=event.said)
        ordered = sorted(seen.values(), key=lambda event: (event.position.seq, event.said))
        return cls(tuple(ordered))

    def upto(self, position: Position) -> tuple[Event, ...]:
        """The committed events at or before ``position``, in canonical order."""
        return tuple(event for event in self._events if not position < event.position)

    def event(self, said: str) -> Event | None:
        """The committed event bearing ``said``, or ``None`` where none does."""
        return self._by_said.get(said)
