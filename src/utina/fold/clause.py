"""The clause: the committed unit of law, and the sub-block the head ranges over.

Custos defines it at ``custos-4.2.md:1199-1203`` — "A clause is the committed
unit of law: SAID-addressed bytes in the GEL, carrying one or more predicates and
their codomain mapping — the citable atom that grounds cite and disclosure binds
to, and the sub-block the aggregate-Constitution commitment of section 7 ranges
over."

Three of those words are load-bearing here. *Committed*: a clause is parsed from
bytes someone signed, never assembled by the engine, so a body that will not read
as law is refused rather than repaired. *SAID-addressed*: a clause has an
identity derived from its own bytes, which is what lets the Constitution order
clauses without consulting the order they were committed in. *Sub-block*: the
aggregate head of 1475-1487 ranges over these, so their byte rendering is part of
the law head and must be canonical.

On the digest. 1478-1481 says in as many words that "the aggregate's digest
function and concatenation order are semantics this document owes and the
encoding round pins — an openness of commitment form, confessed here". We take
the confession at its word and choose SHA-256, because ``utina.fold`` imports no
KERI library and Blake3 — the KERI-native answer — is on the forbidden list the
purity test enforces. A KERI-native engine will compute a different law head from
the same clauses. That is the openness, not a defect, but it is worth knowing.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

from utina.fold.group import Group, Slot

#: Bytes presented as law that will not read as law. Prefix-matches under the
#: contract's ``e.input.malformed.f`` branch without squatting on it, so a caller
#: can catch every malformed-input condition or just this one. Refusing here is
#: the fail-closed reading: a clause we cannot read is a clause we cannot apply,
#: and applying a guess at it would be legislating the missing seam that
#: 1874-1876 forbids.
MALFORMED_LAW = ErrorCode(
    code="e.input.malformed.law.f",
    title="Committed bytes will not read as the law they claim to be.",
    detail=(
        "A committed clause carries {field}, whose value is not {expected}. These "
        "bytes were presented as law and cannot be read as law, so they are "
        "refused rather than guessed at."
    ),
    args=("field", "expected"),
    hint=(
        "Check the enactment that committed this clause: a clause carries an id, "
        "the act kinds it governs, and a group of weighted slots."
    ),
)

#: The byte that separates a clause's fields inside its sub-block, and the one
#: that separates repeated values inside a field. Both are ASCII separators with
#: no meaning in the values they divide, so no value can forge a boundary.
_FIELD = b"\x1f"
_ITEM = b"\x1d"


def _as_str(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise MALFORMED_LAW(field=field, expected="a string")
    return value


def _as_sequence(value: object, field: str) -> Sequence[object]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise MALFORMED_LAW(field=field, expected="a list")
    return value


def _as_mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise MALFORMED_LAW(field=field, expected="a mapping")
    return value


def _as_weight(value: object, field: str) -> Fraction:
    """Weights are exact rationals, never floats, because unity must be decidable."""
    try:
        return Fraction(_as_str(value, field))
    except ValueError:
        raise MALFORMED_LAW(field=field, expected="an exact rational such as 1/2") from None


@dataclass(frozen=True)
class Clause:
    """One committed unit of law: what it governs, and what satisfies it."""

    id: str
    governs: tuple[str, ...]
    group: Group

    @classmethod
    def from_committed(cls, body: object) -> Clause:
        """Read one clause from its committed sub-block, or refuse the bytes."""
        block = _as_mapping(body, "clause")
        composition = _as_mapping(block.get("group"), "group")
        slots = tuple(
            Slot(
                endorser=_as_str(slot.get("endorser"), "endorser"),
                weight=_as_weight(slot.get("weight"), "weight"),
            )
            for slot in (
                _as_mapping(raw, "slot")
                for raw in _as_sequence(composition.get("slots"), "slots")
            )
        )
        return cls(
            id=_as_str(block.get("id"), "id"),
            governs=tuple(
                _as_str(act, "governs") for act in _as_sequence(block.get("governs"), "governs")
            ),
            group=Group(
                operator=_as_str(composition.get("operator"), "operator"),
                slots=slots,
            ),
        )

    @classmethod
    def edition_from_committed(cls, value: object) -> tuple[Clause, ...]:
        """Read the whole clause set an enactment or an inception commits."""
        return tuple(cls.from_committed(block) for block in _as_sequence(value, "clauses"))

    def sub_block(self) -> bytes:
        """This clause's canonical bytes, the unit the aggregate head ranges over.

        Repeated values are sorted rather than kept in committed order, so a
        serializer that writes the same slots in a different order commits the
        same clause. A clause's governed act kinds and its slots are sets in
        everything but their encoding, and letting an encoding accident change a
        law head would make the head a fact about a writer rather than about the
        law.
        """
        return _FIELD.join(
            [
                b"clause",
                self.id.encode("utf-8"),
                b"governs",
                _ITEM.join(sorted(act.encode("utf-8") for act in self.governs)),
                b"operator",
                self.group.operator.encode("utf-8"),
                b"slots",
                _ITEM.join(
                    sorted(
                        f"{slot.endorser}={slot.weight.numerator}/{slot.weight.denominator}".encode()
                        for slot in self.group.slots
                    )
                ),
            ]
        )

    def said(self) -> str:
        """This clause's self-addressing identifier: a digest of its own bytes."""
        return hashlib.sha256(self.sub_block()).hexdigest()
