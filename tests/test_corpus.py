"""The canonical order, and the ambient orders it refuses.

Custos fixes the consumption order at ``custos-4.2.md:3091-3101``: "A fold
consumes its log in exactly one order, and that order derives from committed
bytes: KEL anchoring order first, intra-anchor order as the anchoring event's
seal list states, and no tiebreak that consults anything uncommitted." The
paragraph then names the failure directly — "An implementation whose fold result
depends on arrival order, storage order, or any ambient sequence does not
conform."

So the tests that matter here are the permutation tests: the same committed
events, handed in in a different order, must come back in the same order.
"""

import sys
import types
from dataclasses import dataclass

import pytest


def _ensure_triple() -> None:
    """Stub ``utina.fold.triple`` only while the sibling module is still unbuilt.

    The contract (``docs/interfaces.md``) owns ``Position``; this file must never
    become its second definition. The stub is installed only when the real module
    cannot be imported, so it retires itself the moment the triple lands.
    """
    try:
        import utina.fold.triple  # noqa: F401
    except ImportError:
        module = types.ModuleType("utina.fold.triple")

        @dataclass(frozen=True)
        class Position:
            seq: int

            def __lt__(self, other: Position) -> bool:
                return self.seq < other.seq

        @dataclass(frozen=True)
        class LawHead:
            said: str

        module.Position = Position  # type: ignore[attr-defined]
        module.LawHead = LawHead  # type: ignore[attr-defined]
        sys.modules["utina.fold.triple"] = module


_ensure_triple()

from bakobo.errors import BakoboError  # noqa: E402
from utina.fold.triple import Position  # noqa: E402

from utina.fold.corpus import Corpus, Event  # noqa: E402


def event(said: str, seq: int, kind: str = "act") -> Event:
    return Event(said=said, kind=kind, position=Position(seq=seq), body={})


# --- The order derives from committed bytes alone ----------------------------


def test_load_orders_by_anchoring_coordinate_not_arrival():
    """Anchoring order first (3094-3095). Arrival order is not an input."""
    late, early = event("EEE", 4), event("AAA", 1)
    assert [e.said for e in Corpus.load([late, early]).upto(Position(9))] == ["AAA", "EEE"]


def test_intra_anchor_order_is_lexicographic_over_saids():
    """Two events at one coordinate. Wall 6 (2908-2910) supplies the total order."""
    corpus = Corpus.load([event("ZZZ", 2), event("BBB", 2), event("MMM", 2)])
    assert [e.said for e in corpus.upto(Position(9))] == ["BBB", "MMM", "ZZZ"]


@pytest.mark.parametrize(
    "arrival",
    [
        ("AAA", "BBB", "CCC", "DDD"),
        ("DDD", "CCC", "BBB", "AAA"),
        ("CCC", "AAA", "DDD", "BBB"),
        ("BBB", "DDD", "AAA", "CCC"),
    ],
    ids=["straight", "reversed", "shuffled-1", "shuffled-2"],
)
def test_every_arrival_permutation_folds_to_one_order(arrival):
    """The conformance obligation of 3099-3101, at the corpus grain."""
    seqs = {"AAA": 1, "BBB": 1, "CCC": 2, "DDD": 2}
    corpus = Corpus.load([event(said, seqs[said]) for said in arrival])
    assert [e.said for e in corpus.upto(Position(9))] == ["AAA", "BBB", "CCC", "DDD"]


def test_a_re_presented_event_folds_once():
    """A said is an identity; a coordinate is only a location (3087-3089)."""
    corpus = Corpus.load([event("AAA", 1), event("AAA", 1), event("BBB", 2)])
    assert [e.said for e in corpus.upto(Position(9))] == ["AAA", "BBB"]


def test_two_different_events_sharing_a_said_refuse_the_stream():
    """Their canonical keys collide, so only arrival order could separate them."""
    with pytest.raises(BakoboError) as raised:
        Corpus.load([event("AAA", 1), event("AAA", 1, kind="enactment")])
    assert raised.value.code == "e.state.order-ambient.f"
    assert "AAA" in str(raised.value)


# --- upto is the positional cut ----------------------------------------------


def test_upto_is_inclusive_of_its_own_coordinate():
    corpus = Corpus.load([event("AAA", 1), event("BBB", 2), event("CCC", 3)])
    assert [e.said for e in corpus.upto(Position(2))] == ["AAA", "BBB"]


def test_upto_before_everything_is_empty():
    assert Corpus.load([event("AAA", 5)]).upto(Position(1)) == ()


# --- event() lookup -----------------------------------------------------------


def test_event_returns_the_committed_event():
    assert Corpus.load([event("AAA", 1)]).event("AAA").said == "AAA"


def test_event_of_an_unknown_said_is_none():
    assert Corpus.load([event("AAA", 1)]).event("ZZZ") is None
