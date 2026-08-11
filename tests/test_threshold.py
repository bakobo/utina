"""The threshold arithmetic — the trivial half, tested as the trivial half.

Custos withdrew the claim that KERI's threshold algebra transfers to the evidence
tier: the two constructions are "analogous ... never one algebra"
(``custos-4.2.md:1956-1958``), because the predicate that decides what enters the
sum is a fold question. This module is everything that *is* shared — adding up
weights and comparing against unity — and the tests below are short because
there is nothing else in it. Everything that makes a governance answer correct
lives in ``test_slots.py``.
"""

from fractions import Fraction

from utina.fold import threshold


def test_nothing_sums_to_nothing():
    assert threshold.total(()) == 0


def test_unity_is_exactly_one():
    assert threshold.UNITY == 1


def test_three_thirds_are_exactly_unity():
    """Clause B2's shape: three slots at 1/3, and all three are needed."""
    thirds = (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))
    assert threshold.total(thirds) == 1
    assert threshold.reaches_unity(threshold.total(thirds))
    assert not threshold.reaches_unity(threshold.total(thirds[:2]))


def test_a_tenth_ten_times_is_exactly_unity():
    """The reason weights are rationals, and the reason it is not obvious.

    Accumulated in binary floating point, ten tenths fall short of one while three
    thirds happen to land on it — so a domain that wrote its law as ten equal
    seats would be governed differently from one that wrote three, for a reason no
    reader of the law could see. Rationals remove the question rather than
    answering it. (``sum`` itself is compensated since CPython 3.12 and would hide
    this; ordinary accumulation is what an implementation actually does.)
    """
    tenths = tuple(Fraction(1, 10) for _ in range(10))
    assert threshold.total(tenths) == 1

    accumulated = 0.0
    for _ in range(10):
        accumulated += 0.1
    assert accumulated != 1.0


def test_short_of_unity_does_not_reach_it():
    assert not threshold.reaches_unity(Fraction(999_999, 1_000_000))


def test_exactly_unity_reaches_it():
    """At least unity, so the boundary is inclusive."""
    assert threshold.reaches_unity(Fraction(1))


def test_over_unity_reaches_it():
    assert threshold.reaches_unity(Fraction(3, 2))


def test_totals_are_order_independent():
    weights = (Fraction(1, 6), Fraction(1, 2), Fraction(1, 3))
    assert threshold.total(weights) == threshold.total(tuple(reversed(weights)))
