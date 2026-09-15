"""Bearing: whether an observed duplicity touches a finding, and how.

``custos-4.2.md:1683-1694``. A conviction bears on a finding when it is
conviction-grade and pertinent, and then **the convict's role dispatches the
edge**: a convicted subject fires self-convicted; a convicted cited third party
fires the taint succession, and "the finding's voice is poisoned, not the
question".

Most of these are about the third arm — the pair that does not bear at all —
because that is where an engine goes wrong quietly. ``:1751-1753``: "Contradictory
pairs convict only where they bear on the question — duplicity elsewhere in a
subject's history taints that history's standing, but it does not convert this
question's finding."
"""

from __future__ import annotations

import pytest

from utina.fold import bearing
from utina.fold.group import AID

GAID = "acme:gaid"
SEAT = "acme:seat3"
MARTA = "acme:marta"
STRANGER = "acme:mallory"

SUBJECT = "EBudgetAct"
GROUND = ("ESeatEndorsement", "EMartaEndorsement")


class Observation:
    """A stand-in for a committed duplicity observation, carrying what is read."""

    def __init__(self, said: str, party: AID, *, kind: str = bearing.DUPLICITY_KIND) -> None:
        self.said = said
        self.kind = kind
        self.body = {
            "t": "dup",
            "i": GAID,
            "party": party,
            "pair": ("EFirstVoice", "ESecondVoice"),
        }


def committed(said: str, party: AID) -> Observation:
    return Observation(said, party)


def test_an_observation_names_the_party_whose_voice_it_poisons():
    assert bearing.convicted(committed("EDup", SEAT)) == SEAT


def test_an_event_of_another_kind_convicts_nobody():
    """Read fail-closed. An event the fold cannot read as an observation is not
    one, and a fold that guessed would poison a voice nobody convicted."""
    assert bearing.convicted(Observation("EDup", SEAT, kind="endorsement")) is None


@pytest.mark.parametrize("party", [None, 42, "", ()], ids=["none", "int", "empty", "tuple"])
def test_an_observation_naming_no_party_convicts_nobody(party):
    event = committed("EDup", SEAT)
    event.body["party"] = party

    assert bearing.convicted(event) is None


def test_duplicity_at_the_subjects_committer_convicts_the_question():
    """The role the transition table's affirmed-to-self-convicted edge is about."""
    assert (
        bearing.role(GAID, committer=GAID, ground=GROUND, acts={})
        is bearing.Role.SUBJECT
    )


def test_duplicity_at_a_cited_third_party_taints_the_voice():
    """Seat 3's endorsement is the affirmation's ground, so seat 3 is cited."""
    acts = {"ESeatEndorsement": SEAT, "EMartaEndorsement": MARTA}

    assert (
        bearing.role(SEAT, committer=GAID, ground=GROUND, acts=acts)
        is bearing.Role.CITED
    )


def test_duplicity_at_a_party_the_finding_never_leaned_on_does_not_bear():
    """The arm that matters most. Duplicity elsewhere in a party's history taints
    that history and does not convert THIS question's finding — a fold that let
    any convicted party anywhere poison every finding would make one bad actor
    fatal to a whole record."""
    acts = {"ESeatEndorsement": SEAT, "EMartaEndorsement": MARTA}

    assert bearing.role(STRANGER, committer=GAID, ground=GROUND, acts=acts) is None


def test_a_cited_act_the_record_cannot_attribute_does_not_bear():
    """Pertinence is derived, never declared (``:1688``). An act nobody can be
    shown to have committed is not somebody's cited artifact."""
    assert bearing.role(SEAT, committer=GAID, ground=GROUND, acts={}) is None


def test_the_subject_arm_wins_when_one_party_is_both():
    """A domain that both committed the subject and endorsed it is convicted on
    the question rather than merely tainted. The stronger edge is the one the
    text fires: a convicted subject fires self-convicted, full stop."""
    acts = {"ESeatEndorsement": GAID}

    assert (
        bearing.role(GAID, committer=GAID, ground=("ESeatEndorsement",), acts=acts)
        is bearing.Role.SUBJECT
    )


def test_a_finding_that_cites_nothing_can_still_be_convicted_on_its_subject():
    """A pending finding has no endorsements to cite, and its subject's committer
    can be duplicitous all the same."""
    assert bearing.role(GAID, committer=GAID, ground=(), acts={}) is bearing.Role.SUBJECT


def test_the_taint_names_the_observation_as_its_ground():
    """A pending that named no ground would be the discretion replay exists to
    remove. The cure is not evidence, so the ground is the act that poisoned it."""
    assert bearing.taint_ground(committed("EDup", SEAT)) == "EDup"


def test_an_observation_carries_its_pair_in_canonical_order():
    """A reader holding the finding should not have to fetch the proof package to
    see what contradicted what, and a set is a set: a pair that moved with the
    order of observation would make one duplicity two facts."""
    assert bearing.pair_of(committed("EDup", SEAT)) == ("EFirstVoice", "ESecondVoice")


@pytest.mark.parametrize(
    "carried",
    [None, "EFirstVoice", 42, ("EOne", 7, "ETwo")],
    ids=["none", "str", "int", "mixed"],
)
def test_a_pair_the_fold_cannot_read_contributes_what_it_can_and_never_raises(carried):
    """Fail closed, like every other read of a stranger's bytes. A malformed pair
    is not a reason to stop folding — the conviction is still recorded, and the
    pair is a courtesy to the reader rather than the ruled payload (``:1659``)."""
    event = committed("EDup", SEAT)
    event.body["pair"] = carried

    read = bearing.pair_of(event)

    assert all(isinstance(one, str) for one in read)
    assert read == tuple(sorted(read))
