"""Refusal, and the separation that is the whole point of it.

Custos, ``custos-4.2.md:1898-1900``: "Refusal is not a fifth finding value — it
is the evaluator declining to answer an ill-posed question, recorded as an
operational fact." Said again where the fold's verb is defined (``:229-231``):
where no committed rule makes the invocation evaluable at all, "the refusal is
not a finding but an operational fact: the evaluator declining an ill-posed
question rather than legislating the missing rule."

So the type relationship is itself a test. An engine that made ``Refusal`` a
``Finding`` subclass would satisfy every other test in this suite and would have
lost the distinction Custos's §8 separation rule exists to draw.
"""

import dataclasses

import pytest
from bakobo.errors import BakoboError

from utina.fold.finding import Affirmed, Defeated, Finding, Pending, SelfConvicted
from utina.fold.refusal import Refusal

VALUES = [Affirmed, Defeated, Pending, SelfConvicted]


def refusal() -> Refusal:
    return Refusal(
        missing="a committed clause governing declare-dividend",
        detail=(
            "Acme's law in force at this position assigns no composition rule to acts of "
            "this class, so the question is not evaluable under it."
        ),
    )


def test_a_refusal_is_not_a_finding_in_either_direction() -> None:
    """The separation rule, asserted rather than commented."""
    assert not issubclass(Refusal, Finding)
    assert not issubclass(Finding, Refusal)
    assert not isinstance(refusal(), Finding)


@pytest.mark.parametrize("value", VALUES, ids=lambda v: v.__name__)
def test_a_refusal_is_none_of_the_four_values(value: type[Finding]) -> None:
    assert not isinstance(refusal(), value)
    assert not issubclass(Refusal, value)


def test_a_refusal_never_appears_inside_a_finding() -> None:
    """No product object ever contains a refused coordinate (:1889-1891)."""
    outcome = refusal()
    with pytest.raises(BakoboError):
        Defeated(citation=outcome)  # type: ignore[arg-type]
    with pytest.raises(BakoboError):
        Pending(requirement=(outcome,))  # type: ignore[arg-type]
    with pytest.raises(BakoboError):
        SelfConvicted(proof=outcome)  # type: ignore[arg-type]


def test_a_refusal_carries_no_verdict_because_it_is_not_in_the_codomain() -> None:
    assert not hasattr(refusal(), "verdict")
    assert tuple(f.name for f in dataclasses.fields(Refusal)) == ("missing", "detail")


def test_a_refusal_names_what_the_law_does_not_supply() -> None:
    """Axiom 3 (:277-278): "The refusal names what is missing"."""
    outcome = refusal()
    assert "declare-dividend" in outcome.missing
    assert "not evaluable" in outcome.detail


def test_a_refusal_that_names_nothing_missing_is_not_constructible() -> None:
    with pytest.raises(BakoboError) as raised:
        Refusal(missing="", detail="the law is silent")
    assert raised.value.is_exactly("e.state.ground-missing.f")
    assert "what is missing" in str(raised.value)


@pytest.mark.parametrize(
    "kwargs",
    [{"missing": 7, "detail": "a"}, {"missing": "a", "detail": 7}],
    ids=["missing-not-text", "detail-not-text"],
)
def test_a_refusal_refuses_a_field_that_is_not_prose(kwargs: dict[str, object]) -> None:
    with pytest.raises(BakoboError) as raised:
        Refusal(**kwargs)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")


def test_a_refusal_with_no_further_detail_is_still_a_refusal() -> None:
    """``missing`` is the ground; ``detail`` amplifies it and may be empty."""
    assert Refusal(missing="a composition rule for this seam", detail="").detail == ""


def test_a_refusal_is_a_value_that_is_returned_not_an_error_that_is_thrown() -> None:
    """You cannot record as an operational fact what you threw away (this.i @zztcbs)."""
    assert not isinstance(refusal(), BaseException)
    assert refusal() == refusal()
    assert len({refusal(), refusal()}) == 1
    with pytest.raises(dataclasses.FrozenInstanceError):
        refusal().missing = "something else"  # type: ignore[misc]
