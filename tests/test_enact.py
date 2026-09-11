"""The constructor's verb: every act performed onto the record, nothing judged.

The asymmetry this file exists to defend is the demo's centerpiece. An
endorsement and a declination are both signed committed events; an unsigned or
absent slot is not a decision by anybody. So there is no way through this API
to express "Dev said no" except by producing Dev's signed declination, and the
tests below are what make that a property rather than a hope.

Nothing here returns a finding, because nothing here judges.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import jsonschema
import pytest
from bakobo.errors import BakoboError

from utina.enact import Constructor
from utina.fold import standing
from utina.substrate import (
    ENDORSEMENT_SCHEMA,
    GCD_RULES,
    GCD_SCHEMA,
    ISSUED,
    REVOKED,
    FacadeSubstrate,
)

LAW: Mapping[str, object] = {"clauses": ()}
GAID = "acme:gaid"

#: The published GCD, as vendored, so what the constructor writes is checked
#: against the document a stranger would validate against.
GCD_DOCUMENT = json.loads(
    (Path(__file__).resolve().parents[1] / "schemas" / "gcd-2.0.1.json").read_text(
        encoding="utf-8"
    )
)


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
    attributes = endorsement.body["acdc"]["a"]
    assert attributes["disp"] == "endorse"
    assert attributes["said"] == act.said
    assert endorsement.body["acdc"]["i"] == "acme:marta"
    assert endorsement.body["i"] == "acme:marta"


def test_an_endorsement_embeds_an_anchored_registry_less_credential(founded):
    """this.i @7db5c4/@vi4t4i: the evidence is a real credential, and it is anchored."""
    act = founded.propose("open-bank-account")
    endorsement = founded.endorse("acme:marta", act.said)
    acdc = endorsement.body["acdc"]
    assert acdc["s"] == ENDORSEMENT_SCHEMA
    assert "ri" not in acdc and "rd" not in acdc  # no registry: unrevokable
    assert founded.substrate.anchoring_event(acdc["d"]) is not None
    assert isinstance(endorsement.body["acdc_sig"], str) and endorsement.body["acdc_sig"]


def test_a_declination_is_the_same_signed_act_with_the_other_disposition(founded):
    """@7szbfw — one emitter, and between yes and no the credential's attributes
    differ in the disposition alone (plus the digest that seals it)."""
    act = founded.propose("open-bank-account")
    yes = founded.endorse("acme:marta", act.said)
    no = founded.decline("acme:dev", act.said)
    differing = {
        key for key in yes.body if yes.body[key] != no.body.get(key)
    }
    assert differing == {"acdc", "acdc_sig", "i", "s", "d", "sig"}
    yes_attributes = yes.body["acdc"]["a"]
    no_attributes = no.body["acdc"]["a"]
    assert {
        key for key in yes_attributes if yes_attributes[key] != no_attributes.get(key)
    } == {"d", "disp"}
    assert no_attributes["disp"] == "decline"
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
        "confer",
        "decline",
        "emitted",
        "enact_amendment",
        "endorse",
        "gaid",
        "incept_domain",
        "open_registry",
        "propose",
        "registry",
        "resume",
        "revoke",
        "substrate",
    }


def test_a_domain_has_no_registry_until_one_is_opened(founded):
    """And opening one writes no committed event: a registry confers nothing."""
    assert founded.registry is None
    before = len(founded.emitted)

    registry = founded.open_registry("acme-governance")

    assert isinstance(registry, str)
    assert founded.registry == registry
    assert len(founded.emitted) == before


def test_conferring_authority_before_the_registry_is_opened_is_refused(founded):
    """Fail closed: a grant nobody can revoke is the one shape this must not mint.

    Authority comes from a revocable credential and from nothing else
    (``this.i`` @cglayqvw), so a GCD outside a registry would confer authority
    that no act of the conferring party could ever take back — the KERI
    delegation underneath it being permanent.
    """
    with pytest.raises(BakoboError) as caught:
        founded.confer("acme:seat3", role="board-seat-3", acts=["create commitment"])
    assert caught.value.code == "e.state.registry-unopened.f"
    assert not caught.value.retryable


def test_a_grant_names_the_delegate_as_issuee_under_the_domains_registry(founded):
    """The second credential kind, and the things that make it one."""
    registry = founded.open_registry("acme-governance")

    event = founded.confer("acme:seat3", role="board-seat-3", acts=["create commitment"])

    assert event.kind == "issuance"
    assert event.body["ri"] == registry
    credential = event.body["acdc"]
    assert credential["i"] == founded.gaid, "the domain confers its own authority"
    assert credential["ri"] == registry, "revocable through the registry it names"
    assert credential["s"] == GCD_SCHEMA, "a GCD, not a schema of utina's own"
    assert credential["r"] == GCD_RULES, "issued under the published framework"
    assert credential["a"]["i"] == "acme:seat3", "the issuee is the delegate"
    assert credential["a"]["facet"]["role"] == "board-seat-3"
    assert credential["a"]["facet"]["relationType"] == "delegation"
    assert credential["a"]["facet"]["exerciseMode"] == "act"
    assert credential["a"]["constraints"]["acts"] == ["create commitment"]
    assert founded.substrate.verify(founded.gaid, event.body, event.body["sig"])


def test_a_grant_carries_no_presents_as_unless_one_is_asked_for(founded):
    """The seat presents as itself, so the field would be saying nothing.

    It is descriptive either way — the rules make ``constraints`` the whole of
    the authorization decision (bakobo/schema#3) — but a field asserting that an
    identifier presents as itself is noise in committed bytes.
    """
    founded.open_registry("acme-governance")

    event = founded.confer("acme:seat3", role="board-seat-3", acts=["create commitment"])

    assert "presentsAs" not in event.body["acdc"]["a"]["facet"]


def test_a_grant_may_say_which_office_its_delegate_presents_under(founded):
    """Beat 15's device: it signs with its own key and presents as the seat."""
    founded.open_registry("acme-governance")

    event = founded.confer(
        "acme:nina-device",
        role="board-seat-3-device",
        acts=["create commitment"],
        presents_as="acme:seat3",
    )

    assert event.body["acdc"]["a"]["facet"]["presentsAs"] == "acme:seat3"


def test_a_grant_is_conferred_by_the_party_that_holds_the_authority(founded):
    """The seat grants to its own device; the domain is not the issuer there.

    A grant issued by the domain would be the domain delegating, which is a
    different fact about who answers for the delegate and who may end it.
    """
    seat = founded.substrate.delegate(founded.gaid, "acme:seat3")
    device = founded.substrate.delegate(seat, "acme:nina-device")
    founded.open_registry("acme-governance")

    event = founded.confer(
        device,
        role="board-seat-3-device",
        acts=["create commitment"],
        issuer=seat,
        presents_as=seat,
    )

    assert event.body["acdc"]["i"] == seat
    assert event.body["i"] == seat
    assert founded.substrate.verify(seat, event.body, event.body["sig"])


def test_a_grant_validates_against_the_published_gcd_document(founded):
    """A stranger's validator passes what Acme's constructor writes."""
    founded.open_registry("acme-governance")

    event = founded.confer("acme:seat3", role="board-seat-3", acts=["create commitment"])

    jsonschema.validate(instance=dict(event.body["acdc"]), schema=GCD_DOCUMENT)


# --- the qualification an endorser cites, and the check on it (@x7crwavm) -----


@pytest.fixture
def seated(founded):
    """A founded domain with a registry, a delegated seat, and its credential.

    Returns the constructor, the seat's identifier, and the seat credential's
    own identifier — the three things an endorsement offered as the seat's needs.
    """
    seat = founded.substrate.delegate(founded.gaid, "acme:seat3")
    founded.open_registry("acme-governance")
    event = founded.confer(seat, role="board-seat-3", acts=["create commitment"])
    return founded, seat, str(event.body["acdc"]["d"])


def test_a_seats_endorsement_carries_a_di2i_edge_to_its_seat_credential(seated):
    """Beat 12's ground: the edge is in the committed credential, not implied.

    ``custos-4.2.md:1425-1428`` requires the edge by name and requires DI2I on
    it, so that "the endorser holds the seat it claims" is checkable by the
    existing toolchain rather than by this engine.
    """
    constructor, seat, credential = seated
    subject = constructor.propose("approve-budget").said

    event = constructor.endorse(seat, subject, qualification=credential)

    edge = event.body["acdc"]["e"]["qp"]
    assert edge["n"] == credential
    assert edge["o"] == "DI2I"
    assert edge["s"] == GCD_SCHEMA, "the far node's schema, read off the far node"
    assert constructor.substrate.verify_edges(event.body["acdc"]) is True


def test_an_unseated_endorser_citing_a_seat_credential_commits_nothing(seated):
    """Beat 14. The claim is made, the toolchain refuses it, the record does not move.

    Quinn's shape exactly: a real party citing a real seat credential whose
    issuee he is not. The endorsement is issued and anchored in his own key log,
    because he really did make the claim; what does not happen is the
    commitment. Under the refusal reading the fold never sees this at all, which
    is why the two currents cannot merge here (this.i @x7crwavm).
    """
    constructor, _, credential = seated
    quinn = constructor.substrate.incept("acme:quinn")
    subject = constructor.propose("approve-budget").said
    before = len(constructor.emitted)

    with pytest.raises(BakoboError) as caught:
        constructor.endorse(quinn, subject, qualification=credential)

    assert caught.value.code == "e.proof.edge-unvalidated.f"
    assert not caught.value.retryable
    assert len(constructor.emitted) == before, "nothing was committed"


def test_an_unseated_declination_is_refused_on_the_same_terms(seated):
    """A "no" from an unseated party is no more attributable than their "yes"."""
    constructor, _, credential = seated
    quinn = constructor.substrate.incept("acme:quinn")
    subject = constructor.propose("approve-budget").said

    with pytest.raises(BakoboError) as caught:
        constructor.decline(quinn, subject, qualification=credential)
    assert caught.value.code == "e.proof.edge-unvalidated.f"


def test_a_delegate_of_the_seat_satisfies_the_seats_own_edge(seated):
    """Beat 15: the third stratum. Same slot, different key, no law change."""
    constructor, seat, credential = seated
    device = constructor.substrate.delegate(seat, "acme:nina-device")
    subject = constructor.propose("approve-budget").said

    event = constructor.endorse(device, subject, qualification=credential)

    assert event.body["acdc"]["i"] == device
    assert constructor.substrate.verify_edges(event.body["acdc"]) is True


def test_a_citation_resolves_by_identifier_and_not_by_the_latest_issuance(seated):
    """Two seats, and the endorser cites the one whose issuee it is.

    A record with more than one seat credential in it is the ordinary case for
    any board, and a constructor that resolved a citation to the most recent
    issuance would attach an edge naming a credential the endorser does not
    hold — which the toolchain would then correctly refuse, for a reason nobody
    could find.
    """
    constructor, _, first_credential = seated
    second_seat = constructor.substrate.delegate(constructor.gaid, "acme:seat4")
    second = constructor.confer(second_seat, role="board-seat-4", acts=["create commitment"])
    second_credential = str(second.body["acdc"]["d"])
    subject = constructor.propose("approve-budget").said

    event = constructor.endorse(second_seat, subject, qualification=second_credential)

    assert first_credential != second_credential
    assert event.body["acdc"]["e"]["qp"]["n"] == second_credential
    assert constructor.substrate.verify_edges(event.body["acdc"]) is True


# --- revocation: the registry moves, and the record says so -------------------


def test_revoking_a_credential_commits_that_the_registry_moved(seated):
    """The fold reads registry state out of the record, so the record carries it."""
    constructor, _, credential = seated

    event = constructor.revoke(credential)

    assert event.kind == "revocation"
    assert event.body["said"] == credential
    assert event.body["ri"] == constructor.registry
    assert event.body["i"] == constructor.gaid, "the domain revokes what it conferred"
    assert isinstance(event.body["tel"], str) and event.body["tel"]
    assert "acdc" not in event.body, "the credential has not changed and is not re-embedded"
    assert constructor.substrate.verify(constructor.gaid, event.body, event.body["sig"])


def test_the_fold_and_the_registry_agree_after_a_revocation(seated):
    """Both currents, read at the same coordinate, and neither consulted the other."""
    constructor, _, credential = seated
    registry = constructor.registry

    assert standing.state_over(constructor.emitted, registry, credential) == ISSUED

    constructor.revoke(credential)

    assert standing.state_over(constructor.emitted, registry, credential) == REVOKED
    assert constructor.substrate.registry_state(registry, credential) == REVOKED


def test_revoking_the_same_credential_twice_is_refused(seated):
    """Registry state is a state machine, and there is no second departure from rev."""
    constructor, _, credential = seated
    constructor.revoke(credential)

    with pytest.raises(BakoboError) as caught:
        constructor.revoke(credential)
    assert caught.value.code == "e.state.not-issued.f"


def test_revoking_before_the_registry_is_opened_is_refused(founded):
    with pytest.raises(BakoboError) as caught:
        founded.revoke("E" + "z" * 43)
    assert caught.value.code == "e.state.registry-unopened.f"


def test_a_seats_endorsement_still_validates_after_its_credential_is_revoked(seated):
    """Beat 19's half of the machinery, at the layer that decides it.

    DI2I asks whether the issuer is the far node's issuee, which is a fact about
    delegation and not about registry state — so edge validation is untouched by
    the revocation, and what changes is what the *fold* reads out of the record.
    Keeping those two separate is the whole of Act III.
    """
    constructor, seat, credential = seated
    constructor.revoke(credential)
    subject = constructor.propose("approve-budget").said

    event = constructor.endorse(seat, subject, qualification=credential)

    assert constructor.substrate.verify_edges(event.body["acdc"]) is True


def test_citing_a_credential_this_record_does_not_carry_is_refused(founded):
    """A citation a stranger cannot resolve from the record is not a qualification."""
    marta = founded.substrate.incept("acme:marta-again")
    subject = founded.propose("approve-budget").said

    with pytest.raises(BakoboError) as caught:
        founded.endorse(marta, subject, qualification="E" + "z" * 43)
    assert caught.value.code == "e.state.citation-unknown.f"


def test_an_endorsement_citing_nothing_carries_no_edge_and_is_committed(founded):
    """Marta and Dev are slotted as themselves, so they cite nothing and need to."""
    subject = founded.propose("approve-budget").said

    event = founded.endorse("acme:marta", subject)

    assert "e" not in event.body["acdc"]


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
