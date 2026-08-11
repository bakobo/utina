"""Slot groups: the shape of a composition rule, and the arithmetic over one.

Custos §9 requires only that a composition rule be committed, and permits — with
the section's single BCP-14 keyword, at ``custos-4.2.md:1945`` — expressing it in
the ACDC edge grammar as the dossier specification profiles it. Acme commits its
own clause predicate instead, in a structure isomorphic to the dossier's threshold
operators: the same operator/slot/weight shape, the same unity threshold, the same
three dispositions (``this.i`` @ta7vle). Swapping the encoding for real edge groups
is then a substrate change rather than a rewrite.

A group is satisfied when the weights of its **Endorsed** slots sum to at least
unity. Nothing else adds weight — not presence, not a declination, not an
endorsement from someone the group does not slot.

The three dispositions are the whole point of the module, and the difference
between them is not a nuance:

- **Pending** contributes nothing and is equivalent, in trust terms, to an absent
  slot: neither attributes any act to the candidate.
- **Endorsed** adds the slot's weight.
- **Declined** adds nothing *and spends the slot*, so the weight is no longer
  reachable. That last clause is what makes one signed refusal fatal to a
  two-slot decision and survivable by a three-slot one.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

from utina.fold import threshold

__all__ = [
    "AID",
    "GROUP_ENDORSER_REPEATED",
    "GROUP_SLOTS_MISSING",
    "SAID",
    "SLOT_WEIGHT_NOT_POSITIVE",
    "SLOT_WEIGHT_NOT_RATIONAL",
    "Disposition",
    "Group",
    "Slot",
]

type AID = str
"""An identifier. ``"acme:marta"`` under the facade substrate."""

type SAID = str
"""A self-addressing digest of committed bytes."""


SLOT_WEIGHT_NOT_RATIONAL = ErrorCode(
    code="e.input.format.slot-weight.f",
    title="A slot weight must be an exact rational.",
    detail=(
        "The slot for {endorser} carries a weight of type {kind}, and a weight is a "
        "fractions.Fraction. Unity has to be exactly decidable, and in binary floating point "
        "ten tenths do not sum to one, so a law expressed in floats would be satisfied or not "
        "according to rounding."
    ),
    args=("endorser", "kind"),
    hint=(
        "Construct the weight as Fraction(1, 3) rather than converting 1/3, which is "
        "already lossy by the time it arrives."
    ),
)

SLOT_WEIGHT_NOT_POSITIVE = ErrorCode(
    code="e.input.range.slot-weight.f",
    title="A slot weight must be greater than zero.",
    detail=(
        "The slot for {endorser} carries a weight of {weight}. A negative weight would make an "
        "endorsement subtract from the sum, so an endorser could defeat a decision by "
        "endorsing it; a zero weight puts an endorser in the requirement space who can "
        "never discharge anything."
    ),
    args=("endorser", "weight"),
)

GROUP_SLOTS_MISSING = ErrorCode(
    code="e.input.missing.group-slots.f",
    title="A composition rule must have at least one slot.",
    detail=(
        "The {operator} group names no endorser, so it can never reach unity and would "
        "discharge as a pending finding with an empty requirement set. A domain that permits "
        "nobody to act says so by committing no clause, and the fold then refuses."
    ),
    args=("operator",),
)

GROUP_ENDORSER_REPEATED = ErrorCode(
    code="e.input.multi.slot-endorser.f",
    title="A composition rule slots each endorser at most once.",
    detail=(
        "The {operator} group slots {endorser} more than once, which leaves one identifier "
        "holding two weights and no committed rule for which of them applies."
    ),
    args=("operator", "endorser"),
)


class Disposition(StrEnum):
    """The three dispositions a slot can be in, and it is in exactly one."""

    PENDING = "pending"
    ENDORSED = "endorsed"
    DECLINED = "declined"


#: The dispositions whose weight is in the sum now.
_COUNTED = frozenset({Disposition.ENDORSED})

#: The dispositions whose weight is in the sum now or could still be. A declined slot
#: is in neither: an authenticated refusal is the one act that spends a slot.
_REACHABLE = frozenset({Disposition.ENDORSED, Disposition.PENDING})

#: The dispositions that leave a slot still owing an act.
_OUTSTANDING = frozenset({Disposition.PENDING})


@dataclass(frozen=True)
class Slot:
    """One candidate endorser and the share of authority the law gives them."""

    endorser: AID
    weight: Fraction

    def __post_init__(self) -> None:
        if not isinstance(self.weight, Fraction):
            raise SLOT_WEIGHT_NOT_RATIONAL(
                endorser=self.endorser, kind=type(self.weight).__name__
            )
        if self.weight <= 0:
            raise SLOT_WEIGHT_NOT_POSITIVE(endorser=self.endorser, weight=str(self.weight))


@dataclass(frozen=True)
class Group:
    """A committed composition rule: an operator, and the slots it sums over."""

    operator: str
    slots: tuple[Slot, ...]

    def __post_init__(self) -> None:
        if not self.slots:
            raise GROUP_SLOTS_MISSING(operator=self.operator)
        seen: set[AID] = set()
        for slot in self.slots:
            if slot.endorser in seen:
                raise GROUP_ENDORSER_REPEATED(operator=self.operator, endorser=slot.endorser)
            seen.add(slot.endorser)

    def slot(self, endorser: AID) -> Slot | None:
        """The slot this group gives ``endorser``, or ``None`` if it slots them nowhere."""
        for slot in self.slots:
            if slot.endorser == endorser:
                return slot
        return None

    def endorsed_weight(self, dispositions: Mapping[AID, Disposition]) -> Fraction:
        """The weight that is in the sum: endorsed slots, and nothing else."""
        return self._weight_of(dispositions, _COUNTED)

    def reachable_weight(self, dispositions: Mapping[AID, Disposition]) -> Fraction:
        """The most the sum could still become: endorsed weight plus still-pending weight."""
        return self._weight_of(dispositions, _REACHABLE)

    def satisfied(self, dispositions: Mapping[AID, Disposition]) -> bool:
        """Whether the endorsed weights have reached unity."""
        return threshold.reaches_unity(self.endorsed_weight(dispositions))

    def satisfied_by(self, endorsers: AbstractSet[AID]) -> bool:
        """Whether the named endorsers, taken as endorsing, reach unity.

        The convenience form the tests and the CLI use. A name this group does not
        slot contributes nothing rather than raising: this is a read path that
        displays a verdict, and the property that matters — an endorsement from the
        wrong identifier can never help — holds either way.
        """
        return self.satisfied(dict.fromkeys(endorsers, Disposition.ENDORSED))

    def reachable(self, dispositions: Mapping[AID, Disposition]) -> bool:
        """Whether unity is *still attainable* given what has been spent.

        This is the method the demo turns on. A declination removes its slot's
        weight from what can still arrive, so two slots at 1/2 with one declination
        can never reach unity while three slots at 1/2 still can — the same signed
        refusal, opposite consequence, because the group changed.

        ``docs/custos-questions.md`` Q1 records that Custos does not settle which
        finding an unreachable group produces, and ``docs/custos-questions.md`` Q16
        records that §9:1966 leans the other way from the pin. This method answers
        only the arithmetic question; the codomain question is the evaluator's.
        """
        return threshold.reaches_unity(self.reachable_weight(dispositions))

    def outstanding(self, dispositions: Mapping[AID, Disposition]) -> tuple[Slot, ...]:
        """The slots that have not acted, in the order the law committed them."""
        return tuple(self._where(dispositions, _OUTSTANDING))

    def _weight_of(
        self, dispositions: Mapping[AID, Disposition], admitted: AbstractSet[Disposition]
    ) -> Fraction:
        return threshold.total(slot.weight for slot in self._where(dispositions, admitted))

    def _where(
        self, dispositions: Mapping[AID, Disposition], admitted: AbstractSet[Disposition]
    ) -> Iterable[Slot]:
        """The slots whose disposition is one of ``admitted``.

        A slot the mapping does not mention is pending, because a pending slot and an
        absent one are equivalent in trust terms; and an entry naming an endorser this
        group does not slot is never reached, so it can neither add weight nor keep any.
        """
        for slot in self.slots:
            if dispositions.get(slot.endorser, Disposition.PENDING) in admitted:
                yield slot
