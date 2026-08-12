"""The record every command reads, and the fold types it is built over.

``utina.acme`` is parameterized over a ``FoldValues`` protocol so the writing plane never
imports the fold (this.i @tvaq2s). The CLI is the composition root that hands it the real
constructors, which is the same job ``tests/conftest.py`` does for the acceptance oracle.

The record is rebuilt on every invocation rather than persisted. It is deterministic in
its own committed bytes, so two invocations produce the same log down to the identifier;
what does not survive is an act committed by ``utina enact``, which is a property this.i
@clphmr chose deliberately and which the enact screen states in words.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from utina.acme import GAID, Acme, build
from utina.enact import Constructor
from utina.fold.corpus import Corpus, Event
from utina.fold.triple import Position

__all__ = ["RealValues", "constructor_over", "world"]


class RealValues:
    """A ``utina.substrate.FoldValues`` over ``utina.fold``'s own value types."""

    def position(self, seq: int) -> Position:
        return Position(seq=seq)

    def event(
        self, *, said: str, kind: str, position: Position, body: Mapping[str, object]
    ) -> Event:
        return Event(said=said, kind=kind, position=position, body=body)

    def corpus(self, events: Sequence[Event]) -> Corpus:
        return Corpus.load(events)


def world() -> Acme:
    """Acme's law and committed log, folded over the real types."""
    return build(values=RealValues())


def constructor_over(record: Acme) -> Constructor:
    """A constructor that continues Acme's committed record instead of starting one.

    ``utina.enact`` offers no way to resume a log it did not itself write: ``_emit``
    takes its coordinate from ``len(self._emitted)``, ``_dispose`` checks
    ``self._saids`` before it will dispose against a subject, and every verb checks
    ``self._founded``. All three are set here from the committed record.

    This reaches into another package's internals, and it is the smaller of the two
    wrongs available (this.i @cladpt; ~7h6j is the tick against ``utina.enact`` for a
    public ``Constructor.resume``). The alternative is to re-implement ``_emit`` in the CLI,
    which would copy the committed byte layout — the field order, the
    coordinate-before-identifier rule, the signature-verified-before-recorded rule —
    across a seam that fails silently when the copies drift. ``tests/test_cli.py`` pins
    the invariants so this cannot rot unnoticed.
    """
    constructor = Constructor(record.substrate, GAID, values=record.values)
    constructor._emitted = list(record.events)
    constructor._saids = {event.said for event in record.events}
    constructor._founded = True
    return constructor
