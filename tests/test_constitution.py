"""The law in force at a position, and the succession that changes it.

The mechanism under test is the one the demo exists to show. Custos states it
four times and rules it once: "law never applies to itself at a coordinate, only
to its successor at the next, and succession is never retroactive"
(``custos-4.2.md:2270-2272``), and at keyword force "this document's clauses are
the GARD's law for every position at and after the effectuation coordinate, and
SHALL bind no position before it" (3001-3003).

So the amendment that changes the law is itself an event in the log this fold
reads, and it is appraised under the law in force immediately *before* its own
coordinate. ``test_the_amendment_is_judged_under_the_law_it_replaces`` is that
sentence as a test, and it is the one to read first.

The other binding obligation here is 3101: streams presented in permuted arrival
order "SHALL fold to byte-identical Constitutions" — byte-identical, which is
stricter than semantic equality and is why ``canonical_bytes`` exists.
"""

import itertools
import sys
import types
from dataclasses import dataclass
from fractions import Fraction

import pytest


def _ensure_siblings() -> None:
    """Stub the sibling modules only while they are still unbuilt.

    ``docs/interfaces.md`` owns ``Position``, ``LawHead``, ``Slot`` and
    ``Group``; this file must never become their second definition. Each stub is
    installed only when the real module cannot be imported, so it retires itself
    the moment the sibling lands.
    """
    try:
        import utina.fold.triple
    except ImportError:
        triple = types.ModuleType("utina.fold.triple")

        @dataclass(frozen=True)
        class Position:
            seq: int

            def __lt__(self, other: Position) -> bool:
                return self.seq < other.seq

        @dataclass(frozen=True)
        class LawHead:
            said: str

        triple.Position = Position  # type: ignore[attr-defined]
        triple.LawHead = LawHead  # type: ignore[attr-defined]
        sys.modules["utina.fold.triple"] = triple

    try:
        import utina.fold.group  # noqa: F401
    except ImportError:
        group = types.ModuleType("utina.fold.group")

        @dataclass(frozen=True)
        class Slot:
            endorser: str
            weight: Fraction

        @dataclass(frozen=True)
        class Group:
            operator: str
            slots: tuple[Slot, ...]

            def satisfied_by(self, endorsers) -> bool:
                reached = sum(
                    (slot.weight for slot in self.slots if slot.endorser in endorsers),
                    Fraction(0),
                )
                return reached >= 1

        group.Slot = Slot  # type: ignore[attr-defined]
        group.Group = Group  # type: ignore[attr-defined]
        sys.modules["utina.fold.group"] = group


_ensure_siblings()

from bakobo.errors import BakoboError  # noqa: E402
from utina.fold.triple import Position  # noqa: E402

from utina.fold.constitution import Constitution  # noqa: E402
from utina.fold.corpus import Corpus, Event  # noqa: E402


def slots(*pairs):
    return [{"endorser": endorser, "weight": weight} for endorser, weight in pairs]


def clause(ident, governs, *pairs):
    group = {"operator": "MxN", "slots": slots(*pairs)}
    return {"id": ident, "governs": governs, "group": group}


MARTA, DEV, NINA = "acme:marta", "acme:dev", "acme:nina"

#: Acme's founding law: two founders, both required, for ordinary acts and for
#: amending the operating agreement alike.
STATE_ONE = [
    clause("A1", ["open-bank-account", "hire-vp-sales"], (MARTA, "1/2"), (DEV, "1/2")),
    clause("A2", ["amend-operating-agreement"], (MARTA, "1/2"), (DEV, "1/2")),
]

#: After the board is seated: ordinary authority is distributed so any two reach
#: unity, and the bar for amending the agreement is retained at all three. That
#: retained bar is the point of the whole demo.
STATE_TWO = [
    clause(
        "B1",
        ["open-bank-account", "hire-vp-sales", "approve-budget"],
        (MARTA, "1/2"),
        (DEV, "1/2"),
        (NINA, "1/2"),
    ),
    clause(
        "B2",
        ["amend-operating-agreement"],
        (MARTA, "1/3"),
        (DEV, "1/3"),
        (NINA, "1/3"),
    ),
]

INCEPTION, AMENDMENT, LATER = Position(0), Position(4), Position(5)

EVENTS = [
    Event(
        said="E0-inception",
        kind="inception",
        position=INCEPTION,
        body={"clauses": STATE_ONE},
    ),
    Event(said="E1-act", kind="act", position=Position(1), body={}),
    Event(said="E2-endorse", kind="endorsement", position=Position(2), body={}),
    Event(
        said="E4-seat-board",
        kind="enactment",
        position=AMENDMENT,
        body={"clauses": STATE_TWO},
    ),
]


def corpus(events=None):
    return Corpus.load(events if events is not None else EVENTS)


# --- Succession: the centerpiece ---------------------------------------------


def test_the_founding_law_is_in_force_at_its_own_coordinate():
    """Genesis is constructed rather than judged (2272-2274), so it binds at once."""
    law = Constitution.at(corpus(), INCEPTION)
    assert [c.id for c in law.clauses] == ["A1", "A2"]


def test_the_amendment_is_judged_under_the_law_it_replaces():
    """2270-2272: law never applies to itself at a coordinate, only to its successor."""
    law = Constitution.at(corpus(), AMENDMENT)
    assert [c.id for c in law.clauses] == ["A1", "A2"]
    assert law.governing("amend-operating-agreement").id == "A2"


def test_the_amendment_binds_every_position_after_its_own():
    """3001-3003, at keyword force: law for every position at and after effectuation."""
    law = Constitution.at(corpus(), LATER)
    assert [c.id for c in law.clauses] == ["B1", "B2"]


def test_succession_is_never_retroactive():
    """The same corpus, read at an earlier position, still yields the earlier law."""
    assert Constitution.at(corpus(), Position(3)).clauses == Constitution.at(
        corpus(), INCEPTION
    ).clauses


def test_an_amendment_replaces_the_edition_rather_than_adding_to_it():
    """Otherwise A1 and B1 both govern ordinary acts and governing() has two answers."""
    law = Constitution.at(corpus(), LATER)
    assert law.governing("open-bank-account").id == "B1"
    assert [c.id for c in law.clauses] == ["B1", "B2"]


def test_the_retained_bar_survives_the_amendment():
    before = Constitution.at(corpus(), AMENDMENT)
    after = Constitution.at(corpus(), LATER)
    assert before.clause("A2").group.satisfied_by({MARTA, DEV})
    assert after.clause("B1").group.satisfied_by({MARTA, NINA})
    assert not after.clause("B2").group.satisfied_by({MARTA, NINA})
    assert after.clause("B2").group.satisfied_by({MARTA, DEV, NINA})


# --- governing(): the refusal hinge, so it must be exact ----------------------


def test_governing_names_the_clause_ruling_an_act_kind():
    assert Constitution.at(corpus(), INCEPTION).governing("hire-vp-sales").id == "A1"


def test_an_ungoverned_act_kind_is_none_not_a_clause():
    """None is what makes an ungoverned question a refusal rather than a finding."""
    assert Constitution.at(corpus(), LATER).governing("declare-dividend") is None


def test_a_corpus_with_no_committed_law_governs_nothing():
    empty = Corpus.load([Event(said="E1", kind="act", position=Position(1), body={})])
    law = Constitution.at(empty, LATER)
    assert law.clauses == ()
    assert law.governing("open-bank-account") is None


# --- clause() ------------------------------------------------------------------


def test_clause_returns_the_clause_in_force():
    assert Constitution.at(corpus(), INCEPTION).clause("A1").id == "A1"


def test_a_clause_the_law_in_force_does_not_define_refuses():
    """B2 exists, but not yet. The obstacle is the law's condition here."""
    with pytest.raises(BakoboError) as raised:
        Constitution.at(corpus(), INCEPTION).clause("B2")
    assert raised.value.code == "e.state.clause-unknown.f"
    assert "B2" in str(raised.value)


# --- Canonical bytes: binding at 3101 ------------------------------------------


def test_permuted_arrival_folds_to_byte_identical_constitutions():
    """The binding obligation of 3101. Byte-identical, not merely equivalent."""
    straight = Constitution.at(corpus(EVENTS), LATER).canonical_bytes()
    for permutation in itertools.permutations(EVENTS):
        assert Constitution.at(corpus(list(permutation)), LATER).canonical_bytes() == straight


def test_the_law_head_is_derived_from_the_canonical_bytes():
    """C14/G7: a law head is derivable as the fold of the designated GEL."""
    law = Constitution.at(corpus(), LATER)
    assert law.law_head.said
    assert law.law_head == Constitution.at(corpus(), LATER).law_head


def test_a_different_law_has_a_different_head():
    before = Constitution.at(corpus(), AMENDMENT)
    after = Constitution.at(corpus(), LATER)
    assert before.law_head != after.law_head
    assert before.canonical_bytes() != after.canonical_bytes()


def test_clause_sub_blocks_are_ordered_by_clause_said():
    """Our concatenation order, and 1478-1481 confesses that it is ours to choose."""
    law = Constitution.at(corpus(), LATER)
    by_said = sorted(law.clauses, key=lambda c: c.said())
    assert law.canonical_bytes() == b"\x1e".join(c.sub_block() for c in by_said)
    # The order is the SAIDs' order, which is not the order the clauses were
    # committed in unless the digests happen to agree with it.
    assert [c.said() for c in by_said] == sorted(c.said() for c in law.clauses)


# --- A committed edition that cannot be read as law ---------------------------


def test_two_clauses_governing_one_act_kind_refuse():
    """An uncommitted precedence seam. 1874-1876: refuse, never legislate."""
    both = [
        clause("C1", ["approve-budget"], (MARTA, "1/1")),
        clause("C2", ["approve-budget"], (DEV, "1/1")),
    ]
    conflicted = Corpus.load(
        [Event(said="E0", kind="inception", position=INCEPTION, body={"clauses": both})]
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(conflicted, INCEPTION)
    assert raised.value.code == "e.state.clause-ambiguous.f"
    assert "approve-budget" in str(raised.value)


def test_one_clause_id_committed_twice_refuses():
    twice = [
        clause("C1", ["approve-budget"], (MARTA, "1/1")),
        clause("C1", ["hire-vp-sales"], (DEV, "1/1")),
    ]
    conflicted = Corpus.load(
        [Event(said="E0", kind="inception", position=INCEPTION, body={"clauses": twice})]
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(conflicted, INCEPTION)
    assert raised.value.code == "e.state.clause-ambiguous.f"
    assert "C1" in str(raised.value)


def test_a_law_event_whose_clauses_are_not_a_list_refuses():
    broken = Corpus.load(
        [Event(said="E0", kind="inception", position=INCEPTION, body={"clauses": "A1"})]
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(broken, INCEPTION)
    assert raised.value.code == "e.input.malformed.law.f"


def test_a_law_event_with_no_clauses_field_refuses():
    broken = Corpus.load([Event(said="E0", kind="inception", position=INCEPTION, body={})])
    with pytest.raises(BakoboError) as raised:
        Constitution.at(broken, INCEPTION)
    assert raised.value.code == "e.input.malformed.law.f"
    assert "clauses" in str(raised.value)
