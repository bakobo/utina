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

from utina.fold.group import Group, Qualification, Slot

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

#: The byte that separates a slot's own three parts. A third separator rather
#: than a printable character, for the reason the other two are separators: an
#: endorser, a weight and a schema identifier are all strings a domain chooses,
#: and any printable delimiter one of them could contain would let a slot forge
#: a boundary and commit a clause whose bytes read as a different clause.
_PART = b"\x1e"


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


def _as_qualification(value: object) -> Qualification | None:
    """The credential a slot's endorser must hold, or ``None`` where none is asked.

    Absence is a statement and not a gap: a slot with no qualification names a
    party the law entitles directly. A malformed one is refused rather than read
    as absent, because "this slot requires nothing" and "this slot requires
    something I could not parse" must never collapse into one answer.
    """
    if value is None:
        return None
    block = _as_mapping(value, "qualification")
    return Qualification(
        schema=_as_str(block.get("schema"), "qualification schema"),
        issuer=_as_str(block.get("issuer"), "qualification issuer"),
    )


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
    group: Group  # ~66mh

    certification: str | None = None
    """The schema acts under this clause must be certified against, overriding
    whatever the law names. ``None`` means the clause says nothing and inherits."""

    exempt_from_certification: bool = False
    """Whether acts under this clause need no certification at all, whatever the law
    requires. Distinct from ``certification`` being ``None``, which inherits: a clause
    may be silent, may pin its own schema, or may say that decisions of this kind are
    ordinary enough to stand on their arithmetic (this.i @2e2dncfe).

    Loosening is safe here in a way it would not be under a weaker succession rule. A
    clause that exempted the most consequential acts is the obvious abuse, and it
    cannot be smuggled in: an enactment is judged under the law it replaces, so
    committing that exemption is itself an act the predecessor law governs — and
    certifies, where the predecessor asked for certification."""

    @classmethod
    def from_committed(cls, body: object) -> Clause:
        """Read one clause from its committed sub-block, or refuse the bytes."""
        block = _as_mapping(body, "clause")
        composition = _as_mapping(block.get("group"), "group")
        slots = tuple(
            _slot_from_committed(slot)
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
            certification=_as_certification(block.get("certification")),
            exempt_from_certification=block.get("certification") is False,
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
                        _slot_bytes(slot)
                        for slot in self.group.slots
                    )
                ),
                *self._certification_bytes(),
            ]
        )

    def _certification_bytes(self) -> list[bytes]:
        """What this clause says about certifying, in the bytes, or nothing.

        In the bytes for the reason the slot schema is (see :func:`_slot_bytes`): a
        clause that needed a different kind of proof before its acts took effect is a
        different clause, and a head that could not tell them apart would let an
        amendment exempt the acts it cared about without moving the law head.

        Emitted only where the clause says something, so a clause that inherits
        commits the bytes it always did and no existing law head moves.
        """
        if self.exempt_from_certification:
            return [b"certification", b"none"]
        if self.certification is not None:
            return [b"certification", self.certification.encode("utf-8")]
        return []

    def said(self) -> str:
        """This clause's self-addressing identifier: a digest of its own bytes."""
        return hashlib.sha256(self.sub_block()).hexdigest()


def _slot_from_committed(slot: Mapping[str, object]) -> Slot:
    """One committed slot: a named party, or an office a credential fills.

    Exactly one of the two, and the refusal where neither is present is the point
    rather than defensiveness: a slot that named no party and seated no office would
    be a share of authority nobody could ever exercise, and guessing which was meant
    is precisely what the fold does not do.
    """
    office = slot.get("office")
    named = slot.get("endorser")
    if isinstance(office, str) and office:
        if isinstance(named, str) and named:
            raise MALFORMED_LAW(
                field="slot",
                expected="either an endorser or an office, never both — a slot that "
                "named a party AND seated an office would say who fills a seat that "
                "a credential is supposed to fill",
            )
        endorser = ""
    else:
        office = None
        endorser = _as_str(named, "endorser")
    return Slot(
        endorser=endorser,
        weight=_as_weight(slot.get("weight"), "weight"),
        schema=_as_str(slot.get("schema"), "schema"),
        qualification=_as_qualification(slot.get("qualification")),
        office=office,
    )


def _as_certification(value: object) -> str | None:
    """The schema a clause pins for its certifications, or ``None`` to inherit.

    ``False`` is the committed form of an exemption and is read as pinning no schema;
    the exemption itself is carried separately. Anything else unreadable inherits
    rather than exempts, which is the fail-closed direction: a malformed field must
    not be a way out of a requirement the law imposes.
    """
    return value if isinstance(value, str) and value else None


def _slot_bytes(slot: Slot) -> bytes:
    """One slot's three committed parts: who may act, how much, and with what.

    The schema is in the bytes because it is law: a clause whose slots wanted a
    different kind of credential would be a different clause, and a head that
    could not tell them apart would let an amendment change what discharges a
    requirement without changing the law head.

    So is the qualification, and for a sharper version of the same reason: it
    decides who may act in the slot at all, so an amendment that added or dropped
    one while leaving the head unmoved could unseat an office in silence. An
    absent qualification contributes two empty parts, which no present one can
    produce — :class:`~utina.fold.group.Qualification` refuses an empty term — so
    "requires nothing" and "requires something" never digest alike.
    """
    qualification = slot.qualification
    parts = [
        slot.endorser.encode("utf-8"),
        f"{slot.weight.numerator}/{slot.weight.denominator}".encode(),
        slot.schema.encode("utf-8"),
        b"" if qualification is None else qualification.schema.encode("utf-8"),
        b"" if qualification is None else qualification.issuer.encode("utf-8"),
    ]
    # The office, where the slot seats one, for the same reason as everything above:
    # a slot that seated a different office would be a different slot, and a head
    # that could not tell them apart would let an amendment move authority from one
    # seat to another in silence. Appended only where there is one, so a slot naming
    # a party commits the bytes it always did and no existing law head moves.
    if slot.office is not None:
        parts.extend((b"office", slot.office.encode("utf-8")))
    return _PART.join(parts)
