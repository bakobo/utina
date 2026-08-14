"""The constructor's verb: every act performed onto the record, nothing judged.

The asymmetry this file exists to defend is the demo's centerpiece. An
endorsement and a declination are both signed committed events; an unsigned or
absent slot is not a decision by anybody. So there is no way through this API
to express "Dev said no" except by producing Dev's signed declination, and the
tests below are what make that a property rather than a hope.

Nothing here returns a finding, because nothing here judges.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from bakobo.errors import BakoboError

from utina.enact import Constructor
from utina.substrate import FacadeSubstrate

LAW: Mapping[str, object] = {"clauses": ()}
GAID = "acme:gaid"


@pytest.fixture
def constructor(substrate, values):
    """The gAID exists before the constructor does (this.i @crrtzf)."""
    return Constructor(substrate, substrate.incept(GAID), values=values)


@pytest.fixture
def founded(constructor):
    constructor.incept_domain(LAW)
    constructor.substrate.incept("acme:marta")
    constructor.substrate.incept("acme:dev")
    return constructor


# --- Inception ---------------------------------------------------------------


def test_incepting_the_domain_commits_its_founding_law(constructor):
    event = constructor.incept_domain(LAW)
    assert event.kind == "inception"
    assert event.body["law"] == LAW
    assert event.body["i"] == GAID
    assert event.position.seq == 0


def test_founding_a_domain_whose_identifier_was_never_incepted_is_refused(substrate, values):
    """@crrtzf: the composition root incepts, so an unincepted gAID fails closed."""
    constructor = Constructor(substrate, "acme:never-incepted", values=values)
    with pytest.raises(BakoboError) as caught:
        constructor.incept_domain(LAW)
    assert caught.value.code == "e.id.aid-unknown.f"
    assert constructor.emitted == ()


def test_a_domain_is_founded_once(constructor):
    constructor.incept_domain(LAW)
    with pytest.raises(BakoboError) as caught:
        constructor.incept_domain(LAW)
    assert caught.value.code == "e.state.domain-incepted.f"


@pytest.mark.parametrize(
    ("verb", "argument"),
    [("propose", "open-bank-account"), ("enact_amendment", LAW)],
    ids=["propose", "enact_amendment"],
)
def test_nothing_may_be_committed_before_the_domain_exists(constructor, verb, argument):
    with pytest.raises(BakoboError) as caught:
        getattr(constructor, verb)(argument)
    assert caught.value.code == "e.state.domain-unincepted.f"


# --- Every event, whatever its kind ------------------------------------------


def test_every_event_carries_its_own_coordinate_in_its_committed_bytes(founded):
    """Q24: the fold's order has to come from the bytes, so the bytes carry it."""
    act = founded.propose("open-bank-account")
    endorsement = founded.endorse("acme:marta", act.said)
    assert [event.body["s"] for event in founded.emitted] == [0, 1, 2]
    assert [event.position.seq for event in founded.emitted] == [0, 1, 2]
    assert endorsement.body["s"] == endorsement.position.seq


def test_every_event_is_identified_by_a_digest_of_its_own_bytes(founded):
    act = founded.propose("open-bank-account")
    assert act.said == founded.substrate.said(act.body)
    assert act.body["d"] == act.said


def test_every_event_carries_a_signature_that_verifies(founded):
    act = founded.propose("open-bank-account")
    endorsement = founded.endorse("acme:marta", act.said)
    for event, signer in ((act, GAID), (endorsement, "acme:marta")):
        assert founded.substrate.verify(signer, event.body, event.body["sig"])


def test_emitted_is_the_record_in_the_order_it_was_made(founded):
    act = founded.propose("open-bank-account")
    endorsement = founded.endorse("acme:marta", act.said)
    assert founded.emitted == (founded.emitted[0], act, endorsement)


# --- Endorsement and declination ---------------------------------------------


def test_an_endorsement_names_its_subject_and_its_disposition(founded):
    act = founded.propose("open-bank-account")
    endorsement = founded.endorse("acme:marta", act.said)
    assert endorsement.kind == "endorsement"
    assert endorsement.body["disp"] == "endorse"
    assert endorsement.body["said"] == act.said
    assert endorsement.body["i"] == "acme:marta"


def test_a_declination_is_the_same_signed_act_with_the_other_disposition(founded):
    """@7szbfw — one emitter, one committed field between yes and no."""
    act = founded.propose("open-bank-account")
    yes = founded.endorse("acme:marta", act.said)
    no = founded.decline("acme:dev", act.said)
    differing = {
        key for key in yes.body if yes.body[key] != no.body.get(key)
    }
    assert differing == {"disp", "i", "s", "d", "sig"}
    assert no.body["disp"] == "decline"
    assert no.kind == yes.kind == "endorsement"


def test_a_declination_is_signed_by_the_party_who_declined(founded):
    """A no nobody signed is not a no. This is the whole asymmetry."""
    act = founded.propose("open-bank-account")
    no = founded.decline("acme:dev", act.said)
    assert founded.substrate.verify("acme:dev", no.body, no.body["sig"])
    assert not founded.substrate.verify("acme:marta", no.body, no.body["sig"])


def test_the_constructor_offers_no_way_to_record_a_decision_without_signing_it(founded):
    """The absent slot has no constructor, and that absence is deliberate."""
    verbs = {name for name in dir(founded) if not name.startswith("_")}
    assert verbs == {
        "anchoring_event",
        "decline",
        "emitted",
        "enact_amendment",
        "endorse",
        "gaid",
        "incept_domain",
        "propose",
        "resume",
        "substrate",
    }


@pytest.mark.parametrize("verb", ["endorse", "decline"], ids=["endorse", "decline"])
def test_a_disposition_on_an_uncommitted_subject_is_refused(founded, verb):
    """Fail closed: a slot cannot be spent against something nobody committed."""
    with pytest.raises(BakoboError) as caught:
        getattr(founded, verb)("acme:marta", "E" + "x" * 43)
    assert caught.value.code == "e.state.subject-unknown.f"


@pytest.mark.parametrize("verb", ["endorse", "decline"], ids=["endorse", "decline"])
def test_a_disposition_from_an_identifier_with_no_key_state_is_refused(founded, verb):
    act = founded.propose("open-bank-account")
    with pytest.raises(BakoboError) as caught:
        getattr(founded, verb)("acme:ghost", act.said)
    assert caught.value.code == "e.id.aid-unknown.f"


# --- Amendment ---------------------------------------------------------------


def test_an_amendment_commits_the_successor_law(founded):
    successor: Mapping[str, object] = {"clauses": ({"id": "B1"},)}
    event = founded.enact_amendment(successor)
    assert event.kind == "enactment"
    assert event.body["law"] == successor


def test_an_amendment_names_the_class_of_act_it_performs(founded):
    """Amending the law is itself an act, and a clause governs it by class.

    Without the class in committed bytes the fold cannot find the clause that
    rules an amendment, so the one question the demo turns on — was the
    board-seating amendment lawful under the law it replaced? — has no governing
    clause and refuses. The domain names its own class, because "amending the
    operating agreement" is Acme's phrase and not the constructor's.
    """
    event = founded.enact_amendment(LAW, act="amend-operating-agreement")
    assert event.body["act"] == "amend-operating-agreement"


def test_an_amendment_that_names_no_class_commits_none(founded):
    """A domain that has not designated an amendment class does not get one invented."""
    assert "act" not in founded.enact_amendment(LAW).body


def test_an_amendment_anchors_in_an_establishment_event(founded):
    """custos-4.2.md:2085-2087 — an enactment amending law SHALL anchor in one."""
    event = founded.enact_amendment(LAW)
    assert founded.substrate.anchoring_event(event.said) is not None


def test_the_anchor_the_constructor_reports_is_the_substrate_s_own(founded):
    """@ygjwyw: the binding is asked of the key log, never cached beside it."""
    event = founded.enact_amendment(LAW)
    assert founded.anchoring_event(event.said) == founded.substrate.anchoring_event(
        event.said
    )


def test_an_unanchored_said_has_no_anchoring_event(founded):
    act = founded.propose("open-bank-account")
    assert founded.anchoring_event(act.said) is None


# --- Fail closed on the substrate itself -------------------------------------


class LyingSubstrate:
    """A substrate whose signatures do not verify — the case that must not pass."""

    def __init__(self, honest: FacadeSubstrate) -> None:
        self._honest = honest

    def said(self, body):
        return self._honest.said(body)

    def sign(self, aid, body):
        return self._honest.sign(aid, body)

    def incept(self, alias):
        return self._honest.incept(alias)

    def rotate(self, aid, anchor):
        return self._honest.rotate(aid, anchor)

    def anchoring_event(self, said):
        return self._honest.anchoring_event(said)

    def verify(self, aid, body, signature):
        return False


def test_an_event_whose_own_signature_does_not_verify_is_never_produced(values):
    """Fail closed: unverifiable bytes must not become a committed act."""
    lying = LyingSubstrate(FacadeSubstrate())
    constructor = Constructor(lying, lying.incept(GAID), values=values)
    with pytest.raises(BakoboError) as caught:
        constructor.incept_domain(LAW)
    assert caught.value.code == "e.proof.signature-unverifiable.f"
    assert constructor.emitted == ()


# --- Resuming a committed record (this.i @jzozfn) -----------------------------


def committed_record(founded):
    """A three-event record: the inception, an act, and an endorsement of it."""
    act = founded.propose("open-bank-account")
    founded.endorse("acme:marta", act.said)
    return founded.emitted


def test_resume_continues_the_committed_record(founded, values):
    """this.i @jzozfn: the coordinate, the subjects and the signature all continue."""
    events = committed_record(founded)
    substrate = founded.substrate
    resumed = Constructor.resume(substrate, GAID, values=values, events=events)
    assert resumed.emitted == events

    event = resumed.endorse("acme:dev", events[1].said)
    assert event.position.seq == len(events)
    sealed = {key: value for key, value in event.body.items() if key != "sig"}
    assert substrate.verify("acme:dev", sealed, event.body["sig"])


def test_resume_derives_founding_from_the_record(founded, values):
    """An inception among the events founds the domain; founding again is refused."""
    events = committed_record(founded)
    resumed = Constructor.resume(founded.substrate, GAID, values=values, events=events)
    with pytest.raises(BakoboError) as caught:
        resumed.incept_domain(LAW)
    assert caught.value.code == "e.state.domain-incepted.f"


def test_resume_of_an_empty_record_founds_nothing(substrate, values):
    """Resuming nothing is a fresh start: verbs are refused, inception is open."""
    resumed = Constructor.resume(substrate, substrate.incept(GAID), values=values, events=())
    with pytest.raises(BakoboError) as caught:
        resumed.propose("open-bank-account")
    assert caught.value.code == "e.state.domain-unincepted.f"
    assert resumed.incept_domain(LAW).position.seq == 0


def test_resume_without_an_inception_founds_nothing(substrate, values):
    """Founding is derived from event kinds, never from the record being non-empty."""
    gaid = substrate.incept(GAID)
    events = tuple(
        values.event(said=f"E{seq}", kind="act", position=values.position(seq), body={})
        for seq in range(2)
    )
    resumed = Constructor.resume(substrate, gaid, values=values, events=events)
    with pytest.raises(BakoboError) as caught:
        resumed.propose("open-bank-account")
    assert caught.value.code == "e.state.domain-unincepted.f"


@pytest.mark.parametrize(
    "mangle",
    [lambda events: events[:1] + events[2:], lambda events: events[::-1]],
    ids=["gapped", "permuted"],
)
def test_resume_refuses_a_record_whose_positions_do_not_run_from_zero(founded, values, mangle):
    """this.i @jzozfn: the next coordinate is the record's length, so a gap corrupts."""
    events = mangle(committed_record(founded))
    with pytest.raises(BakoboError) as caught:
        Constructor.resume(founded.substrate, GAID, values=values, events=events)
    assert caught.value.code == "e.input.format.resume-record.f"
