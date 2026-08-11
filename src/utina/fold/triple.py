"""The fold's closed three-input type.

Custos's replay axiom, quoted whole because the whole of it binds
(``custos-4.2.md:259-262``):

    **Replay.** The same committed inputs yield the same computed state — and
    the inputs are exactly three, closed: the committed evidence bundle, the
    committed law head, and the appraisal position. No other input may
    influence the result.

Two consequences shape this module.

**A fourth input is a conformance failure, not a feature.** ``INPUT_COUNT`` and
the field list are asserted in the suite, because "exactly three, closed" is the
kind of claim that erodes the first time someone needs one more thing.

**A position is a coordinate, never a clock.** ``:1625-1626``: "The position is a
log coordinate in committed order, never wall-clock." A float is the shape a
timestamp arrives in, so it is refused rather than coerced.

The canonical encoding here is **utina's choice, not the document's**. Custos
grades finding conformance at semantic full-payload equality today
(``:1631-1634``) but requires permuted arrival to fold to byte-identical
Constitutions (``:3098-3101``), so some encoding has to be pinned for that
obligation to be testable at all. It is length-prefixed, so no concatenation of
fields can be reread as a different split — ``2:ab1:c`` is not ``3:abc`` — which
is what makes byte equality a sound test of value equality (this.i @asuj6q).
Nothing in the fold's semantics depends on these bytes and nothing outside utina
reads them.

The encoder derives from bakobo/thesmo's ``m1-beta`` reading and the type shapes
from its ``m1-alpha`` reading (Apache-2.0, see NOTICE).
"""

import dataclasses
from collections.abc import Iterable, Iterator, Mapping
from typing import Protocol, runtime_checkable

from utina.fold.errors import MALFORMED_INPUT, require

__all__ = [
    "AID",
    "SAID",
    "AppraisalTriple",
    "CommittedEvent",
    "EvidenceBundle",
    "LawHead",
    "Position",
    "encode_fields",
]

type SAID = str
"""A self-addressing digest of committed bytes."""

type AID = str
"""An identifier. ``"acme:marta"`` under the facade substrate."""


def encode_fields(*parts: bytes | str | int) -> bytes:
    """Encode ``parts`` as length-prefixed fields, unambiguously.

    Bytes are taken as they are, text as UTF-8, and a whole number as its
    decimal digits — the three shapes committed evidence reaches the fold in.
    Anything else is refused rather than stringified, because ``str()`` of an
    arbitrary object is exactly the ambient influence the replay axiom excludes.
    """
    out = bytearray()
    for part in parts:
        if isinstance(part, bytes):
            raw = part
        elif isinstance(part, str):
            raw = part.encode("utf-8")
        elif isinstance(part, int) and not isinstance(part, bool):
            raw = str(part).encode("ascii")
        else:
            raise MALFORMED_INPUT(
                field="a value to be canonically encoded",
                expected="bytes, text or a whole number",
                found=f"a {type(part).__name__}",
            )
        out += str(len(raw)).encode("ascii") + b":" + raw
    return bytes(out)


def _identifier(value: object, field: str, expected: str) -> None:
    """An identifier is a non-empty string, and nothing else is one."""
    require(
        isinstance(value, str) and value != "",
        MALFORMED_INPUT,
        field=field,
        expected=expected,
        found=repr(value),
    )


@runtime_checkable
class CommittedEvent(Protocol):
    """What an evidence bundle needs of a committed event.

    ``utina.fold.corpus.Event`` satisfies this structurally. The protocol exists
    so the closed input type does not import the corpus that imports it back —
    the cycle is real, and a ``TYPE_CHECKING`` import would only move it
    (this.i @e3qd53).
    """

    said: SAID
    kind: str
    position: Position
    body: Mapping[str, object]


@dataclasses.dataclass(frozen=True)
class Position:
    """The appraisal coordinate: where in committed order the question is asked."""

    seq: int

    def __post_init__(self) -> None:
        require(
            isinstance(self.seq, int) and not isinstance(self.seq, bool) and self.seq >= 0,
            MALFORMED_INPUT,
            field="a position's sequence number",
            expected="a whole number of zero or more, counted in committed order",
            found=repr(self.seq),
        )

    def __lt__(self, other: object) -> bool:
        """Order by committed coordinate. Never by arrival, and never by a clock."""
        if not isinstance(other, Position):
            return NotImplemented
        return self.seq < other.seq

    def canonical_bytes(self) -> bytes:
        return encode_fields(self.seq)


@dataclasses.dataclass(frozen=True)
class LawHead:
    """The self-addressing identifier of the law an appraisal runs under."""

    said: SAID

    def __post_init__(self) -> None:
        _identifier(
            self.said,
            "a law head",
            "the self-addressing identifier of the law in force",
        )

    def canonical_bytes(self) -> bytes:
        return encode_fields(self.said)


@dataclasses.dataclass(frozen=True)
class EvidenceBundle:
    """The committed evidence a finding is a function of, in committed order.

    The order is the corpus's to derive from committed bytes; the bundle carries
    it and does not re-derive it. Whatever sequence a caller hands in is frozen
    to a tuple on the way, so a committed input cannot be mutated after the
    appraisal that read it.
    """

    events: tuple[CommittedEvent, ...] = ()

    def __post_init__(self) -> None:
        require(
            isinstance(self.events, Iterable) and not isinstance(self.events, str | bytes),
            MALFORMED_INPUT,
            field="an evidence bundle's events",
            expected="a sequence of committed events in committed order",
            found=repr(self.events),
        )
        events = tuple(self.events)
        for member in events:
            require(
                isinstance(member, CommittedEvent),
                MALFORMED_INPUT,
                field="a member of an evidence bundle",
                expected="a committed event carrying its identifier, kind and position",
                found=repr(member),
            )
        object.__setattr__(self, "events", events)

    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self) -> Iterator[CommittedEvent]:
        return iter(self.events)

    def canonical_bytes(self) -> bytes:
        """The bundle's committed identity: its events' identifiers, in order.

        The identifier is enough, and the body is deliberately not encoded here:
        a self-addressing identifier already commits the bytes it addresses, so
        encoding the body again would put one fact in two places and invite them
        to disagree.
        """
        return encode_fields(*(encode_fields(member.said) for member in self.events))


@dataclasses.dataclass(frozen=True)
class AppraisalTriple:
    """The fold's complete input. Exactly three, closed (``custos-4.2.md:259-262``)."""

    evidence: EvidenceBundle
    law_head: LawHead
    position: Position

    INPUT_COUNT = 3

    def __post_init__(self) -> None:
        for value, kind, field in (
            (self.evidence, EvidenceBundle, "evidence"),
            (self.law_head, LawHead, "law head"),
            (self.position, Position, "position"),
        ):
            require(
                isinstance(value, kind),
                MALFORMED_INPUT,
                field=f"the triple's {field}",
                expected=f"a {kind.__name__}",
                found=repr(value),
            )

    def inputs(self) -> tuple[EvidenceBundle, LawHead, Position]:
        """The three, in the order the axiom names them."""
        return (self.evidence, self.law_head, self.position)

    def canonical_bytes(self) -> bytes:
        return encode_fields(
            self.evidence.canonical_bytes(),
            self.law_head.canonical_bytes(),
            self.position.canonical_bytes(),
        )
