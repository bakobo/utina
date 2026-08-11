"""The clause: the committed unit of law, and its canonical sub-block.

Custos defines a clause at ``custos-4.2.md:1199-1203`` as "the committed unit of
law: SAID-addressed bytes in the GEL, carrying one or more predicates and their
codomain mapping — the citable atom that grounds cite and disclosure binds to,
and the sub-block the aggregate-Constitution commitment of section 7 ranges
over."

Two obligations follow, and both are tested here: a clause parses from committed
bytes, and it renders to a canonical sub-block that the Constitution's aggregate
head ranges over (1475-1487).
"""

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

from utina.fold.clause import Clause  # noqa: E402

A1 = {
    "id": "A1",
    "governs": ["open-bank-account", "hire-vp-sales"],
    "group": {
        "operator": "MxN",
        "slots": [
            {"endorser": "acme:marta", "weight": "1/2"},
            {"endorser": "acme:dev", "weight": "1/2"},
        ],
    },
}


def malformed(**overrides):
    body = {key: value for key, value in A1.items()}
    body.update(overrides)
    return body


# --- Parsing committed bytes --------------------------------------------------


def test_a_clause_parses_from_its_committed_sub_block():
    clause = Clause.from_committed(A1)
    assert clause.id == "A1"
    assert clause.governs == ("open-bank-account", "hire-vp-sales")
    assert clause.group.operator == "MxN"
    assert {slot.endorser for slot in clause.group.slots} == {"acme:marta", "acme:dev"}


def test_weights_are_exact_rationals_never_floats():
    """Unity must be decidable, so 1/3 may not become 0.333... (interfaces.md)."""
    thirds = malformed(
        group={
            "operator": "MxN",
            "slots": [{"endorser": "acme:marta", "weight": "1/3"}],
        }
    )
    weight = Clause.from_committed(thirds).group.slots[0].weight
    assert weight == Fraction(1, 3)
    assert isinstance(weight, Fraction)
    assert weight * 3 == 1


# --- The canonical sub-block --------------------------------------------------


def test_the_sub_block_does_not_depend_on_committed_slot_order():
    """A clause is its slots, not the order a serializer wrote them in."""
    reversed_slots = malformed(
        group={
            "operator": "MxN",
            "slots": [
                {"endorser": "acme:dev", "weight": "1/2"},
                {"endorser": "acme:marta", "weight": "1/2"},
            ],
        }
    )
    canonical = Clause.from_committed(A1).sub_block()
    assert Clause.from_committed(reversed_slots).sub_block() == canonical


def test_the_sub_block_does_not_depend_on_committed_act_kind_order():
    swapped = malformed(governs=["hire-vp-sales", "open-bank-account"])
    assert Clause.from_committed(A1).sub_block() == Clause.from_committed(swapped).sub_block()


def test_a_different_weight_is_a_different_sub_block():
    heavier = malformed(
        group={
            "operator": "MxN",
            "slots": [
                {"endorser": "acme:marta", "weight": "2/3"},
                {"endorser": "acme:dev", "weight": "1/2"},
            ],
        }
    )
    assert Clause.from_committed(A1).sub_block() != Clause.from_committed(heavier).sub_block()


def test_the_clause_said_is_a_digest_of_its_own_sub_block():
    clause = Clause.from_committed(A1)
    assert clause.said() == Clause.from_committed(A1).said()
    assert clause.said() != Clause.from_committed(malformed(id="A2")).said()


# --- Committed bytes that will not parse as the clause they claim to be -------


@pytest.mark.parametrize(
    ("overrides", "named"),
    [
        ({"id": 7}, "id"),
        ({"governs": "open-bank-account"}, "governs"),
        ({"group": ["not", "a", "mapping"]}, "group"),
        ({"group": {"operator": "MxN", "slots": [{"endorser": "acme:marta"}]}}, "weight"),
        (
            {"group": {"operator": "MxN", "slots": [{"endorser": "a", "weight": "half"}]}},
            "weight",
        ),
    ],
    ids=[
        "id-not-a-string",
        "governs-not-a-list",
        "group-not-a-mapping",
        "no-weight",
        "weight-nan",
    ],
)
def test_a_malformed_clause_refuses_rather_than_guesses(overrides, named):
    with pytest.raises(BakoboError) as raised:
        Clause.from_committed(malformed(**overrides))
    assert raised.value.code == "e.input.malformed.law.f"
    assert named in str(raised.value)
