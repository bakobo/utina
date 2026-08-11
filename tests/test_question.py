"""The two constructors of a question, and why there are exactly two.

A ``Proposal`` asks "may we do this?" and is evaluated before the fact; a
``Committed`` asks "was this act lawful?" and is evaluated after. The difference
is not cosmetic. Custos's evidence is committed bytes (``custos-4.2.md:259-262``)
and a proposal is not committed, so a proposal's un-committed approvals simply
are not evidence — which is what makes the same question answer ``pending``
before the last endorsement commits and ``affirmed`` after, with nothing else
changing. That is U12 in the requirements audit, and it is the closed triple
doing visible work.
"""

import dataclasses

import pytest
from bakobo.errors import BakoboError

from utina.fold.question import Committed, Proposal, Question


def test_a_proposal_names_the_act_class_it_asks_about() -> None:
    assert Proposal("open-bank-account").act == "open-bank-account"


def test_a_committed_question_names_the_act_by_its_committed_identifier() -> None:
    assert Committed("EAct1").said == "EAct1"


@pytest.mark.parametrize("question", [Proposal("open-bank-account"), Committed("EAct1")])
def test_both_constructors_are_questions(question: Question) -> None:
    assert isinstance(question, Question)


def test_the_two_constructors_are_not_each_other() -> None:
    """Same string, different question: one is an act class, one is an act."""
    assert not isinstance(Proposal("EAct1"), Committed)
    assert Proposal("EAct1") != Committed("EAct1")


def test_a_question_is_frozen_and_compares_by_value() -> None:
    assert Proposal("open-bank-account") == Proposal("open-bank-account")
    assert len({Committed("EAct1"), Committed("EAct1")}) == 1
    with pytest.raises(dataclasses.FrozenInstanceError):
        Proposal("open-bank-account").act = "hire-vp-sales"  # type: ignore[misc]


@pytest.mark.parametrize("act", ["", None, 7], ids=["empty", "none", "number"])
def test_a_proposal_about_nothing_is_refused(act: object) -> None:
    with pytest.raises(BakoboError) as raised:
        Proposal(act)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "act class" in str(raised.value)


@pytest.mark.parametrize("said", ["", None, 7], ids=["empty", "none", "number"])
def test_a_committed_question_about_nothing_is_refused(said: object) -> None:
    with pytest.raises(BakoboError) as raised:
        Committed(said)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "committed act" in str(raised.value)
