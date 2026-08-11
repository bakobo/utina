"""Fixtures for the writing plane, and the Acme corpus the oracle reads.

Two kinds of fold value live here, and the difference is deliberate.

``utina.enact`` and ``utina.acme`` are parameterized over a small ``FoldValues``
protocol rather than importing ``utina.fold`` (``this.i`` @tvaq2s), so the
writing plane can be built and fully exercised while the fold is still under
construction by its own commissions.
The unit tests in this directory therefore drive Acme with **doubles** — thin
stand-ins for ``Position``, ``Event`` and ``Corpus`` that exist only to be
constructed and ordered.

The ``acme`` fixture the acceptance oracle consumes is the other kind: it wires
the **real** fold types, and skips while they do not exist yet. Nothing in this
file may ever install a double into ``utina.fold``. A double that shadowed the
real package would make the oracle test this file instead of the engine, which
is the one failure that would let the suite lie.
"""

from __future__ import annotations

import bisect
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pytest

from utina.substrate import FacadeSubstrate

# --- Doubles for the fold's three value types --------------------------------
#
# Structural stand-ins, matching docs/interfaces.md field for field. They are
# constructed by the code under test and read by assertions; they carry no
# governance behavior, because every judgment belongs to the real fold.


@dataclass(frozen=True, order=False)
class DoublePosition:
    seq: int

    def __lt__(self, other: DoublePosition) -> bool:
        return self.seq < other.seq


@dataclass(frozen=True)
class DoubleEvent:
    said: str
    kind: str
    position: DoublePosition
    body: Mapping[str, object]


class DoubleCorpus:
    """Canonical order from committed bytes, and nothing else.

    The order is by committed coordinate — the ``s`` field inside the digested
    body, which ``Event.position`` mirrors — so a permuted arrival order folds
    to the same sequence. That is the whole property demo beat D10 asserts, and
    the double implements it so the permutation can be checked before the real
    ``Corpus`` exists.
    """

    def __init__(self, events: Sequence[DoubleEvent]) -> None:
        self._events = tuple(sorted(events, key=lambda event: event.position.seq))
        self._seqs = [event.position.seq for event in self._events]
        self._by_said = {event.said: event for event in self._events}

    @classmethod
    def load(cls, events: Iterable[DoubleEvent]) -> DoubleCorpus:
        return cls(tuple(events))

    def upto(self, position: DoublePosition) -> tuple[DoubleEvent, ...]:
        return self._events[: bisect.bisect_right(self._seqs, position.seq)]

    def event(self, said: str) -> DoubleEvent | None:
        return self._by_said.get(said)


class DoubleValues:
    """A ``FoldValues`` implementation over the doubles above."""

    def position(self, seq: int) -> DoublePosition:
        return DoublePosition(seq=seq)

    def event(
        self,
        *,
        said: str,
        kind: str,
        position: DoublePosition,
        body: Mapping[str, object],
    ) -> DoubleEvent:
        return DoubleEvent(said=said, kind=kind, position=position, body=body)

    def corpus(self, events: Sequence[DoubleEvent]) -> DoubleCorpus:
        return DoubleCorpus.load(events)


# --- Fixtures ----------------------------------------------------------------


@pytest.fixture
def values() -> DoubleValues:
    return DoubleValues()


@pytest.fixture
def substrate(values: DoubleValues) -> FacadeSubstrate:
    return FacadeSubstrate(values=values)


@pytest.fixture(scope="session")
def acme_double() -> Any:
    """Acme built on the doubles: available now, and unit-tested in test_acme.py."""
    from utina.acme import build

    return build(values=DoubleValues())


class RealValues:
    """A ``FoldValues`` implementation over the fold's own types.

    Imported inside the methods rather than at module scope so that collecting
    this file never depends on the fold existing.
    """

    def position(self, seq: int) -> Any:
        from utina.fold.triple import Position

        return Position(seq=seq)

    def event(self, *, said: str, kind: str, position: Any, body: Mapping[str, object]) -> Any:
        from utina.fold.corpus import Event

        return Event(said=said, kind=kind, position=position, body=body)

    def corpus(self, events: Sequence[Any]) -> Any:
        from utina.fold.corpus import Corpus

        return Corpus.load(events)


@pytest.fixture(scope="session")
def acme() -> Any:
    """Acme's committed law and corpus, built once, over the real fold types.

    Exposes ``.corpus``, ``.at(label)``, ``.said(name)`` and
    ``.permuted_corpus(seed=…)`` — the surface ``tests/test_acceptance_oracle.py``
    binds to. It skips rather than fails while the fold is unbuilt, because the
    oracle's own ``importorskip`` means this fixture is only ever requested once
    the fold exists.
    """
    pytest.importorskip(
        "utina.fold.corpus",
        reason="the fold has no Corpus yet — the acme fixture wires the real types",
    )
    from utina.acme import build

    return build(values=RealValues())
