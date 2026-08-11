"""Slot groups: the shape of a composition rule, and the arithmetic over it.

Acme's law from ``docs/demo-script.md`` supplies the cases, because these are the
groups the demo actually turns on: A1/A2 (two founders at 1/2), B1 (three seats at
1/2, so any two reach unity) and B2 (three seats at 1/3, so all three are needed).

The property this file exists to prove is ``test_one_declination_two_outcomes``:
the same signed refusal makes unity unreachable under two slots and leaves it
reachable under three. Nothing about the endorser changed; the group did.
"""

from fractions import Fraction

import pytest
from bakobo.errors import BakoboError

from utina.fold.group import Disposition, Group, Slot

HALF = Fraction(1, 2)
THIRD = Fraction(1, 3)

MARTA = "acme:marta"
DEV = "acme:dev"
NINA = "acme:nina"
MALLORY = "acme:mallory"


def founders() -> Group:
    """Clause A1: two slots at 1/2, so unity needs both."""
    return Group("MxN", (Slot(MARTA, HALF), Slot(DEV, HALF)))


def board() -> Group:
    """Clause B1: three slots at 1/2, so any two reach unity."""
    return Group("MxN", (Slot(MARTA, HALF), Slot(DEV, HALF), Slot(NINA, HALF)))


def amendment_bar() -> Group:
    """Clause B2: three slots at 1/3, so all three are needed."""
    return Group("MxN", (Slot(MARTA, THIRD), Slot(DEV, THIRD), Slot(NINA, THIRD)))


# --- What a slot will and will not accept -------------------------------------


def test_a_slot_carries_an_exact_rational_weight():
    slot = Slot(MARTA, HALF)
    assert slot.endorser == MARTA
    assert slot.weight == Fraction(1, 2)


def test_a_float_weight_is_refused_rather_than_converted():
    """Converting is where the lie enters: Fraction(0.1) is not one tenth."""
    with pytest.raises(BakoboError) as raised:
        Slot(MARTA, 0.5)  # type: ignore[arg-type]
    assert raised.value.code == "e.input.format.slot-weight.f"
    assert not raised.value.retryable
    assert "float" in raised.value.detail


def test_an_integer_weight_is_refused_too():
    """Exact, but not a Fraction. One rule, so a law parser has one thing to do."""
    with pytest.raises(BakoboError) as raised:
        Slot(MARTA, 1)  # type: ignore[arg-type]
    assert raised.value.code == "e.input.format.slot-weight.f"


def test_a_negative_weight_is_refused_because_it_would_invert_an_endorsement():
    with pytest.raises(BakoboError) as raised:
        Slot(MARTA, Fraction(-1, 2))
    assert raised.value.code == "e.input.range.slot-weight.f"


def test_a_zero_weight_is_refused_because_it_can_never_discharge():
    with pytest.raises(BakoboError) as raised:
        Slot(MARTA, Fraction(0))
    assert raised.value.code == "e.input.range.slot-weight.f"


# --- What a group will and will not accept ------------------------------------


def test_a_group_with_no_slots_is_refused():
    with pytest.raises(BakoboError) as raised:
        Group("MxN", ())
    assert raised.value.code == "e.input.missing.group-slots.f"


def test_a_group_may_not_slot_one_endorser_twice():
    with pytest.raises(BakoboError) as raised:
        Group("MxN", (Slot(MARTA, HALF), Slot(MARTA, HALF)))
    assert raised.value.code == "e.input.multi.slot-endorser.f"
    assert MARTA in raised.value.detail


def test_a_group_finds_its_slot_by_endorser_and_admits_when_it_has_none():
    group = founders()
    assert group.slot(DEV) == Slot(DEV, HALF)
    assert group.slot(MALLORY) is None


# --- Satisfaction by a set of endorsers ---------------------------------------


def test_nobody_satisfies_nothing():
    assert not founders().satisfied_by(set())


def test_one_of_two_founders_falls_short():
    assert not founders().satisfied_by({MARTA})


def test_both_founders_reach_unity():
    assert founders().satisfied_by({MARTA, DEV})


def test_any_two_of_the_board_reach_unity():
    assert board().satisfied_by({MARTA, NINA})
    assert board().satisfied_by({DEV, NINA})


def test_the_amendment_bar_needs_all_three():
    assert not amendment_bar().satisfied_by({MARTA, NINA})
    assert amendment_bar().satisfied_by({MARTA, DEV, NINA})


def test_an_endorser_the_group_does_not_slot_adds_no_weight():
    """The wrong AID must never help. It is ignored, not an error, because this
    is the read path the CLI uses to display a verdict."""
    assert not founders().satisfied_by({MARTA, MALLORY})
    assert not founders().satisfied_by({MALLORY})


# --- Satisfaction by dispositions ---------------------------------------------


def test_only_endorsed_weight_counts():
    group = founders()
    marta_only = {MARTA: Disposition.ENDORSED, DEV: Disposition.PENDING}
    marta_alone = {MARTA: Disposition.ENDORSED, DEV: Disposition.DECLINED}
    assert group.endorsed_weight(marta_only) == HALF
    assert group.endorsed_weight(marta_alone) == HALF
    assert group.endorsed_weight({MARTA: Disposition.ENDORSED, DEV: Disposition.ENDORSED}) == 1


def test_a_declination_adds_nothing_just_as_a_pending_slot_adds_nothing():
    group = founders()
    declined = {MARTA: Disposition.ENDORSED, DEV: Disposition.DECLINED}
    pending = {MARTA: Disposition.ENDORSED, DEV: Disposition.PENDING}
    assert group.endorsed_weight(declined) == group.endorsed_weight(pending)
    assert not group.satisfied(declined)
    assert not group.satisfied(pending)


def test_an_absent_disposition_is_a_pending_one():
    """A pending slot and an absent slot are equivalent in trust terms."""
    group = founders()
    assert group.endorsed_weight({MARTA: Disposition.ENDORSED}) == HALF
    assert group.reachable({MARTA: Disposition.ENDORSED})


def test_a_disposition_for_an_unslotted_endorser_is_ignored():
    group = founders()
    both = {MARTA: Disposition.ENDORSED, DEV: Disposition.ENDORSED}
    assert group.satisfied({**both, MALLORY: Disposition.ENDORSED})
    assert not group.satisfied({MARTA: Disposition.ENDORSED, MALLORY: Disposition.ENDORSED})
    assert group.reachable({MALLORY: Disposition.DECLINED})


# --- Reachability: the property the demo turns on -----------------------------


def test_unity_is_reachable_before_anyone_acts():
    assert founders().reachable({})


def test_unity_is_reachable_once_it_has_been_reached():
    assert founders().reachable({MARTA: Disposition.ENDORSED, DEV: Disposition.ENDORSED})


def test_a_declination_spends_the_slot():
    """Not merely 'adds nothing' — the weight is gone from what can still arrive."""
    group = founders()
    spent = {MARTA: Disposition.PENDING, DEV: Disposition.DECLINED}
    assert group.reachable_weight(spent) == HALF
    assert group.reachable_weight({MARTA: Disposition.PENDING, DEV: Disposition.PENDING}) == 1


def test_one_declination_two_outcomes():
    """The centerpiece, as one assertion pair.

    Dev's signed refusal is one act. Under two slots at 1/2 it puts unity out of
    reach; under three slots at 1/2 it does not. The engine did not treat Dev
    differently — the Constitution changed and the arithmetic did the rest.
    """
    declined = {MARTA: Disposition.ENDORSED, DEV: Disposition.DECLINED}
    assert not founders().reachable(declined)
    assert board().reachable(declined)


def test_the_retained_amendment_bar_is_unreachable_on_one_declination():
    """Beat D7, and the case that needs exact thirds: 2/3 is short of unity."""
    group = amendment_bar()
    dissent = {
        MARTA: Disposition.ENDORSED,
        DEV: Disposition.ENDORSED,
        NINA: Disposition.DECLINED,
    }
    assert group.endorsed_weight(dissent) == Fraction(2, 3)
    assert not group.reachable(dissent)


def test_three_thirds_are_reachable_and_exactly_unity():
    group = amendment_bar()
    assert group.reachable({})
    assert group.satisfied(dict.fromkeys((MARTA, DEV, NINA), Disposition.ENDORSED))


def test_two_declinations_under_the_board_put_unity_out_of_reach():
    dissent = {
        MARTA: Disposition.PENDING,
        DEV: Disposition.DECLINED,
        NINA: Disposition.DECLINED,
    }
    assert not board().reachable(dissent)


def test_reachability_is_endorsed_plus_pending():
    group = board()
    mixed = {MARTA: Disposition.ENDORSED, DEV: Disposition.DECLINED, NINA: Disposition.PENDING}
    assert group.reachable_weight(mixed) == 1
    assert group.reachable(mixed)
    assert not group.satisfied(mixed)


# --- What is still outstanding ------------------------------------------------


def test_outstanding_names_only_the_pending_slots_in_the_law_s_order():
    group = board()
    mixed = {MARTA: Disposition.ENDORSED, DEV: Disposition.DECLINED}
    assert group.outstanding(mixed) == (Slot(NINA, HALF),)


def test_outstanding_is_empty_once_every_slot_has_acted():
    group = founders()
    acted = {MARTA: Disposition.ENDORSED, DEV: Disposition.DECLINED}
    assert group.outstanding(acted) == ()


def test_outstanding_keeps_the_committed_order_rather_than_sorting():
    """Canonical order is the order the law committed, which is already a total one."""
    group = Group("MxN", (Slot(NINA, THIRD), Slot(MARTA, THIRD), Slot(DEV, THIRD)))
    assert [slot.endorser for slot in group.outstanding({})] == [NINA, MARTA, DEV]


# --- A law that cannot be satisfied at all ------------------------------------


def test_a_group_whose_weights_cannot_reach_unity_is_permitted_and_unreachable():
    """questions-slots.md S7: the fold does not rule on the wisdom of committed law."""
    group = Group("MxN", (Slot(MARTA, THIRD), Slot(DEV, THIRD)))
    assert not group.reachable({})
    assert not group.satisfied_by({MARTA, DEV})
