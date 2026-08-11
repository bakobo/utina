"""The closed three-input type, and the encoding that makes replay checkable.

Custos closes the fold's inputs at exactly three committed values — "the inputs
are exactly three, closed: the committed evidence bundle, the committed law
head, and the appraisal position. No other input may influence the result"
(``custos-4.2.md:259-262``). A fourth field on ``AppraisalTriple`` would not be a
feature but a conformance failure, so the field list is asserted here rather than
trusted to review.

The encoding tests are about replay. ``:3098-3101`` requires streams presented in
permuted arrival order to fold to byte-identical Constitutions, which is only
testable once some encoding is pinned; the property that earns the "byte" in that
sentence is that no concatenation of fields can be read as a different split.
"""

import dataclasses
from collections.abc import Mapping

import pytest
from bakobo.errors import BakoboError

from utina.fold.triple import (
    AppraisalTriple,
    CommittedEvent,
    EvidenceBundle,
    LawHead,
    Position,
    encode_fields,
)


@dataclasses.dataclass(frozen=True)
class FakeEvent:
    """What ``utina.fold.corpus.Event`` will be, structurally, at integration."""

    said: str
    kind: str
    position: Position
    body: Mapping[str, object] = dataclasses.field(default_factory=dict)


def event(said: str, seq: int = 0) -> FakeEvent:
    return FakeEvent(said=said, kind="endorsement", position=Position(seq))


# --- Position ----------------------------------------------------------------


def test_a_position_is_a_committed_coordinate_and_orders_by_it() -> None:
    assert Position(1) < Position(2)
    assert not Position(2) < Position(1)
    assert sorted([Position(3), Position(1), Position(2)]) == [
        Position(1),
        Position(2),
        Position(3),
    ]


def test_a_position_is_frozen_and_hashable() -> None:
    assert {Position(1), Position(1)} == {Position(1)}
    with pytest.raises(dataclasses.FrozenInstanceError):
        Position(1).seq = 2  # type: ignore[misc]


def test_a_position_is_not_ordered_against_something_that_is_not_one() -> None:
    """``__lt__`` answers NotImplemented, so Python raises rather than guessing."""
    assert Position(1).__lt__(1) is NotImplemented
    with pytest.raises(TypeError):
        assert Position(1) < 1  # type: ignore[operator]


@pytest.mark.parametrize(
    "seq", [-1, 1.0, "1", True, None], ids=["negative", "float", "text", "bool", "none"]
)
def test_a_position_refuses_anything_that_is_not_a_sequence_number(seq: object) -> None:
    """A float is the shape a timestamp arrives in; Custos never measures in clocks."""
    with pytest.raises(BakoboError) as raised:
        Position(seq)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "sequence number" in str(raised.value)


# --- LawHead -----------------------------------------------------------------


def test_a_law_head_is_the_identifier_of_the_law_in_force() -> None:
    assert LawHead("ELaw1").said == "ELaw1"


@pytest.mark.parametrize("said", ["", None, 7], ids=["empty", "none", "number"])
def test_a_law_head_refuses_a_value_that_names_no_law(said: object) -> None:
    with pytest.raises(BakoboError) as raised:
        LawHead(said)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "law head" in str(raised.value)


# --- EvidenceBundle ----------------------------------------------------------


def test_a_bundle_holds_committed_events_in_the_order_the_corpus_gave_them() -> None:
    first, second = event("EA", 1), event("EB", 2)
    bundle = EvidenceBundle((first, second))
    assert len(bundle) == 2
    assert list(bundle) == [first, second]
    assert bundle.events == (first, second)


def test_a_bundle_freezes_whatever_sequence_it_was_handed() -> None:
    """A list would let a caller mutate a committed input after the fact."""
    events = [event("EA", 1)]
    bundle = EvidenceBundle(events)  # type: ignore[arg-type]
    events.append(event("EB", 2))
    assert len(bundle) == 1


def test_an_empty_bundle_is_lawful_because_genesis_has_no_evidence_yet() -> None:
    assert len(EvidenceBundle(())) == 0
    assert EvidenceBundle(()).canonical_bytes() == b""


def test_a_bundle_refuses_a_member_that_is_not_a_committed_event() -> None:
    with pytest.raises(BakoboError) as raised:
        EvidenceBundle(("EA",))  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "committed event" in str(raised.value)


def test_a_fake_event_satisfies_the_protocol_structurally() -> None:
    """The protocol is how the bundle avoids importing the corpus; this.i @e3qd53."""
    assert isinstance(event("EA"), CommittedEvent)
    assert not isinstance("EA", CommittedEvent)


# --- The canonical encoding --------------------------------------------------


def test_fields_cannot_be_reread_as_a_different_split() -> None:
    """``2:ab1:c`` is not ``3:abc``, which is what makes byte equality sound."""
    assert encode_fields("ab", "c") != encode_fields("abc")
    assert encode_fields("ab", "c") == b"2:ab1:c"


def test_the_encoder_takes_the_three_shapes_committed_evidence_arrives_in() -> None:
    assert encode_fields(b"ab", "cd", 7) == b"2:ab2:cd1:7"


def test_the_encoder_refuses_a_shape_it_cannot_canonicalize() -> None:
    with pytest.raises(BakoboError) as raised:
        encode_fields(1.5)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "canonically encoded" in str(raised.value)


def test_a_bundle_encodes_its_events_by_their_committed_identifiers() -> None:
    bundle = EvidenceBundle((event("EA", 1), event("EB", 2)))
    assert bundle.canonical_bytes() == encode_fields(encode_fields("EA"), encode_fields("EB"))


# --- AppraisalTriple ---------------------------------------------------------


def triple(seq: int = 1) -> AppraisalTriple:
    return AppraisalTriple(
        evidence=EvidenceBundle((event("EA", 1),)),
        law_head=LawHead("ELaw1"),
        position=Position(seq),
    )


def test_the_triple_has_exactly_three_inputs_and_they_are_the_named_three() -> None:
    """Custos :259-262 closes the inputs; a fourth field is a conformance failure."""
    names = tuple(f.name for f in dataclasses.fields(AppraisalTriple))
    assert names == ("evidence", "law_head", "position")
    assert AppraisalTriple.INPUT_COUNT == 3
    assert len(triple().inputs()) == 3


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("evidence", "EA"),
        ("law_head", "ELaw1"),
        ("position", 1),
    ],
)
def test_the_triple_refuses_an_input_it_cannot_check(field: str, value: object) -> None:
    parts: dict[str, object] = {
        "evidence": EvidenceBundle(()),
        "law_head": LawHead("ELaw1"),
        "position": Position(1),
    }
    parts[field] = value
    with pytest.raises(BakoboError) as raised:
        AppraisalTriple(**parts)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
    assert field.replace("_", " ") in str(raised.value)


def test_the_same_committed_inputs_encode_to_the_same_bytes() -> None:
    assert triple().canonical_bytes() == triple().canonical_bytes()
    assert triple() == triple()


def test_a_different_position_is_a_different_triple_down_to_the_bytes() -> None:
    assert triple(1).canonical_bytes() != triple(2).canonical_bytes()
