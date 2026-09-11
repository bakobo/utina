"""Every promise the ``Substrate`` protocol makes, asked of every implementation.

The demo's claim is not that the keripy backend looks plausible. It is that the
engine above the seam cannot tell which substrate it is standing on. A claim of
that shape is only worth what its statement is worth, so the protocol's promises
are written here once, as executable text, and each one is asked of both
backends by parametrization rather than by two files that drift apart.

Read this as the protocol's contract, not as the facade's tests: nothing below
may name a backend, reach for an implementation detail, or assert a shape only
one of them has. ``tests/test_substrate.py`` is where the facade's own internals
— its ``0B`` signature code, its key index — are pinned, and that division is
the reason this file can be trusted as a contract.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from bakobo.errors import BakoboError

from utina.substrate import (
    ACDC_DT,
    DI2I,
    ENDORSEMENT_SCHEMA,
    ISSUED,
    REVOKED,
    SAID_LENGTH,
)
from utina.substrate.select import NAMES, substrate_named

#: A body with no identifier and no signature: what a caller hands ``said``.
BODY: dict[str, object] = {"t": "end", "act": "issue", "disp": "endorse", "s": 4}

#: Things that are not a signature. Each must verify nothing, and raise nothing.
MALFORMED = ["", " ", "nonsense", "0B0", "E" + "x" * 43, "A" * 88, "\x00", "-" * 200]


@pytest.fixture(params=NAMES)
def substrate_name(request: pytest.FixtureRequest) -> str:
    """Every backend this build carries, so a new one is covered by existing."""
    name: str = request.param
    return name


@pytest.fixture
def conformant(substrate_name: str) -> Iterator[object]:
    """One backend, opened and closed, with no party incepted yet."""
    with substrate_named(substrate_name) as substrate:
        yield substrate


@pytest.fixture
def marta(conformant):
    """One incepted party, addressed by the identifier inception returned.

    Never by the alias: under keripy those differ, and a test that used the
    alias would be asserting a facade artifact (this.i @crrtzf).
    """
    return conformant.incept("acme:marta")


# --- said ---------------------------------------------------------------------


def test_a_said_is_the_length_the_placeholder_stands_in_for(conformant):
    """The identifier field is held at a placeholder of its own length."""
    assert len(conformant.said(BODY)) == SAID_LENGTH


def test_a_said_is_the_same_on_every_call(conformant):
    assert conformant.said(BODY) == conformant.said(BODY)


def test_a_said_does_not_depend_on_mapping_insertion_order(conformant):
    """The substrate owns canonicalization, so a caller's dict order is inert.

    keripy's Saider digests in insertion order and the facade sorts, so this is
    exactly the promise a backend has to work for rather than inherit (@fy5lwj).
    """
    forwards = dict(BODY)
    backwards = dict(reversed(list(BODY.items())))
    assert conformant.said(forwards) == conformant.said(backwards)


def test_different_bodies_get_different_saids(conformant):
    assert conformant.said({"act": "a"}) != conformant.said({"act": "b"})


def test_a_said_ignores_whatever_the_identifier_field_held(conformant):
    """The identifier is computed over a placeholder, so its prior value is inert."""
    assert conformant.said(BODY) == conformant.said({**BODY, "d": "E" + "x" * 43})


def test_a_said_is_idempotent_over_signing(conformant, marta):
    """Q27: a signature is an attachment, so signing may not move the identifier.

    This is the promise the constructor's whole emit order rests on — the
    identifier goes into the bytes, then the signature commits to it, and the
    identifier must still be the identifier afterwards.
    """
    sealed = {**BODY, "d": conformant.said(BODY)}
    signature = conformant.sign(marta, sealed)
    assert conformant.said({**sealed, "sig": signature}) == conformant.said(sealed)


def test_a_said_survives_the_values_a_committed_law_is_made_of(conformant):
    """Nested mappings, sequences, integers, booleans and null, all committed."""
    law = {
        "clauses": [{"id": "A1", "governs": ["hire"], "slots": [{"weight": "1/2"}]}],
        "seats": [],
        "sealed": True,
        "successor": None,
        "s": 0,
    }
    assert len(conformant.said(law)) == SAID_LENGTH
    assert conformant.said(law) == conformant.said(dict(reversed(list(law.items()))))


# --- incept -------------------------------------------------------------------


def test_inception_returns_the_identifier_the_caller_must_then_use(conformant):
    aid = conformant.incept("acme:marta")
    assert isinstance(aid, str)
    assert aid


def test_distinct_aliases_get_distinct_identifiers(conformant):
    """Two parties sharing one voice is the failure this forecloses."""
    assert conformant.incept("acme:marta") != conformant.incept("acme:dev")


def test_incepting_the_same_alias_twice_is_refused(conformant):
    """Silently returning the existing identifier would hide a duplicated party."""
    conformant.incept("acme:marta")
    with pytest.raises(BakoboError) as caught:
        conformant.incept("acme:marta")
    assert caught.value.code == "e.id.alias-taken.f"


def test_signing_as_an_identifier_with_no_key_state_is_refused(conformant):
    with pytest.raises(BakoboError) as caught:
        conformant.sign("EGhostGhostGhostGhostGhostGhostGhostGhostGho", BODY)
    assert caught.value.code == "e.id.aid-unknown.f"


def test_rotating_an_identifier_with_no_key_state_is_refused(conformant):
    with pytest.raises(BakoboError) as caught:
        conformant.rotate("EGhostGhostGhostGhostGhostGhostGhostGhostGho", "E" + "x" * 43)
    assert caught.value.code == "e.id.aid-unknown.f"


# --- sign and verify ----------------------------------------------------------


def test_a_signature_verifies_against_the_body_it_was_made_over(conformant, marta):
    assert conformant.verify(marta, BODY, conformant.sign(marta, BODY))


def test_a_signature_verifies_with_itself_present_in_the_body(conformant, marta):
    """enact stores the signature in the body; verification must survive that."""
    signature = conformant.sign(marta, BODY)
    assert conformant.verify(marta, {**BODY, "sig": signature}, signature)


def test_a_signature_does_not_verify_over_a_tampered_body(conformant, marta):
    """The declination that defeats D3 must not be re-readable as an endorsement."""
    signature = conformant.sign(marta, {**BODY, "disp": "decline"})
    assert not conformant.verify(marta, {**BODY, "disp": "endorse"}, signature)


def test_a_signature_does_not_verify_as_another_party(conformant, marta):
    """Attribution: a no nobody signed is not that party's no."""
    dev = conformant.incept("acme:dev")
    assert not conformant.verify(dev, BODY, conformant.sign(marta, BODY))


def test_an_unknown_identifier_verifies_nothing(conformant, marta):
    """Fail closed and total: no authority, and no exception either."""
    signature = conformant.sign(marta, BODY)
    ghost = "EGhostGhostGhostGhostGhostGhostGhostGhostGho"
    assert not conformant.verify(ghost, BODY, signature)
    assert not conformant.verify("", BODY, signature)


@pytest.mark.parametrize("signature", MALFORMED, ids=range(len(MALFORMED)))
def test_a_malformed_signature_verifies_nothing_and_raises_nothing(
    conformant, marta, signature
):
    """A real KERI library raises on malformed CESR; the protocol says False."""
    assert not conformant.verify(marta, BODY, signature)


def test_a_signature_is_the_same_on_every_call(conformant, marta):
    """Replay is theatre if a signature over the same bytes varies."""
    assert conformant.sign(marta, BODY) == conformant.sign(marta, BODY)


# --- rotate and the anchor binding --------------------------------------------


def test_a_rotation_seals_an_anchor_that_reads_back(conformant):
    """custos-4.2.md:2085-2087, and beat D4: the binding has to be answerable."""
    gaid = conformant.incept("acme:gaid")
    anchor = conformant.said({"t": "enact", "law": {"clauses": []}})
    establishment = conformant.rotate(gaid, anchor)
    assert isinstance(establishment, str)
    assert conformant.anchoring_event(anchor) == establishment


def test_an_unanchored_identifier_has_no_anchoring_event(conformant):
    conformant.incept("acme:gaid")
    assert conformant.anchoring_event("E" + "z" * 43) is None


def test_two_rotations_are_two_establishment_events(conformant):
    gaid = conformant.incept("acme:gaid")
    first = conformant.rotate(gaid, conformant.said({"t": "enact", "n": 1}))
    second = conformant.rotate(gaid, conformant.said({"t": "enact", "n": 2}))
    assert first != second
    assert conformant.anchoring_event(conformant.said({"t": "enact", "n": 1})) == first


def test_a_signature_made_before_a_rotation_still_verifies_after_it(conformant):
    """@zk27gz — Acme's gAID rotates mid-record, so replay dies here if this fails.

    Resolving a verifier's keys from current key state would turn every act the
    gAID signed before beat D4 from ENDORSED to PENDING, with no error anywhere.
    """
    gaid = conformant.incept("acme:gaid")
    signature = conformant.sign(gaid, BODY)
    conformant.rotate(gaid, conformant.said({"t": "enact"}))
    assert conformant.verify(gaid, BODY, signature)


def test_a_rotation_does_not_disturb_another_party_s_signatures(conformant, marta):
    gaid = conformant.incept("acme:gaid")
    signature = conformant.sign(marta, BODY)
    conformant.rotate(gaid, conformant.said({"t": "enact"}))
    assert conformant.verify(marta, BODY, signature)


# --- issue_acdc: a registry-less credential ------------------------------------

#: A SAID-shaped subject for a credential to be about.
SUBJECT = "E" + "s" * 43


def endorsement_acdc(substrate, issuer, disp: str = "endorse"):
    """One registry-less endorsement credential, as ``utina.enact`` would ask for it."""
    return substrate.issue_acdc(
        issuer, ENDORSEMENT_SCHEMA, {"said": SUBJECT, "act": "issue", "disp": disp}
    )


def test_a_credential_carries_the_dossier_required_fields(conformant, marta):
    """The shape is the dossier schema's required set, top level and attributes both."""
    sad, signature = endorsement_acdc(conformant, marta)
    assert set(sad) >= {"v", "d", "i", "s", "a"}
    attributes = sad["a"]
    assert set(attributes) >= {"d", "dt", "said", "act", "disp"}
    assert sad["i"] == marta
    assert sad["s"] == ENDORSEMENT_SCHEMA
    assert attributes["said"] == SUBJECT
    assert attributes["act"] == "issue"
    assert attributes["disp"] == "endorse"
    assert attributes["dt"] == ACDC_DT
    assert isinstance(signature, str) and signature


def test_a_declination_is_the_same_credential_with_one_field_changed(conformant, marta):
    endorsed, _ = endorsement_acdc(conformant, marta, disp="endorse")
    declined, _ = endorsement_acdc(conformant, marta, disp="decline")
    assert declined["a"]["disp"] == "decline"
    assert endorsed["d"] != declined["d"]


def test_a_credential_is_deterministic(conformant, marta):
    """Same issuer, same attributes, same bytes — the fixture dt is what makes it so."""
    first, _ = endorsement_acdc(conformant, marta)
    second, _ = endorsement_acdc(conformant, marta)
    assert first == second


def test_a_credential_is_anchored_in_the_issuers_key_log(conformant, marta):
    """The dossier's Endorsed predicate requires the anchor (dossier-spec-body.md:223)."""
    sad, _ = endorsement_acdc(conformant, marta)
    assert conformant.anchoring_event(sad["d"]) is not None


def test_issuing_as_an_identifier_with_no_key_state_is_refused(conformant):
    with pytest.raises(BakoboError) as caught:
        endorsement_acdc(conformant, "acme:never-incepted")
    assert caught.value.code == "e.id.aid-unknown.f"


# --- a governance registry, and the two credential kinds ----------------------

#: A schema-shaped token for a credential kind that is not an endorsement. The
#: seat credential's own schema is U1.3's; this stands in for it here, because a
#: registry's promises do not depend on which schema it holds.
SEAT_SCHEMA = "E" + "t" * 43


def seat_acdc(substrate, issuer, registry, issuee):
    """A registry-bound credential, as ``utina.enact`` will ask for one."""
    return substrate.issue_acdc(
        issuer, SEAT_SCHEMA, {"i": issuee, "seat": "board-seat-3"}, registry=registry
    )


def test_a_registry_is_opened_under_a_controller(conformant):
    """``custos-4.2.md:1420-1422``: a standing-conferring credential is revocable
    through its registry, so the registry has to exist as an identified thing."""
    gaid = conformant.incept("acme:gaid")
    registry = conformant.open_registry(gaid, "acme-governance")

    assert isinstance(registry, str) and registry != gaid


def test_a_registry_is_anchored_in_its_controllers_key_log(conformant):
    """The registry's own inception is sealed by the party that opened it."""
    gaid = conformant.incept("acme:gaid")
    registry = conformant.open_registry(gaid, "acme-governance")

    assert conformant.anchoring_event(registry) is not None


def test_opening_a_registry_under_an_unknown_identifier_is_refused(conformant):
    with pytest.raises(BakoboError) as caught:
        conformant.open_registry("acme:never-incepted", "acme-governance")
    assert caught.value.code == "e.id.aid-unknown.f"


def test_a_registry_bound_credential_stands_issued(conformant, marta):
    """Registry state is evidence, and the first thing it says is that it stands."""
    registry = conformant.open_registry(marta, "acme-governance")
    sad, _ = seat_acdc(conformant, marta, registry, "acme:seat3")

    assert conformant.registry_state(registry, sad["d"]) == ISSUED


def test_a_revoked_credential_stands_revoked(conformant, marta):
    """Beat 16: a rev event against the credential, and the state moves."""
    registry = conformant.open_registry(marta, "acme-governance")
    sad, _ = seat_acdc(conformant, marta, registry, "acme:seat3")

    revocation = conformant.revoke_acdc(registry, sad["d"])

    assert isinstance(revocation, str)
    assert conformant.registry_state(registry, sad["d"]) == REVOKED


def test_a_revocation_is_anchored_in_the_issuers_key_log(conformant, marta):
    registry = conformant.open_registry(marta, "acme-governance")
    sad, _ = seat_acdc(conformant, marta, registry, "acme:seat3")

    revocation = conformant.revoke_acdc(registry, sad["d"])

    assert conformant.anchoring_event(revocation) is not None


def test_a_credential_nobody_issued_has_no_registry_state(conformant, marta):
    """Total: never issued is ``None``, which is neither issued nor revoked."""
    registry = conformant.open_registry(marta, "acme-governance")
    assert conformant.registry_state(registry, SUBJECT) is None


def test_revoking_a_credential_nobody_issued_is_refused(conformant, marta):
    """Fail closed: a revocation of nothing would report a state change that
    never happened, and registry state is evidence the fold consumes."""
    registry = conformant.open_registry(marta, "acme-governance")
    with pytest.raises(BakoboError) as caught:
        conformant.revoke_acdc(registry, SUBJECT)
    assert caught.value.code == "e.state.not-issued.f"


@pytest.mark.parametrize("act", ["issue", "revoke", "read"], ids=["issue", "revoke", "read"])
def test_naming_a_registry_nobody_opened_is_refused(conformant, marta, act):
    """A registry is an identified thing, so an unknown one is an obstacle and
    not an empty answer — including on the read, where ``None`` would say the
    credential does not stand there and mean something else entirely."""
    ghost = "E" + "r" * 43
    with pytest.raises(BakoboError) as caught:
        if act == "issue":
            seat_acdc(conformant, marta, ghost, "acme:seat3")
        elif act == "revoke":
            conformant.revoke_acdc(ghost, SUBJECT)
        else:
            conformant.registry_state(ghost, SUBJECT)
    assert caught.value.code == "e.state.registry-unknown.f"


def test_an_endorsement_is_registry_less_and_has_no_state_anywhere(conformant, marta):
    """The other credential kind, and the difference the demo shows (@7db5c4).

    An endorsement carries no registry because the dossier's Endorsed predicate
    does not reach for one; a registry-less credential therefore has no state to
    read, in any registry, which is what makes revocation the seat credential's
    property and not the evidence's.
    """
    registry = conformant.open_registry(marta, "acme-governance")
    sad, _ = endorsement_acdc(conformant, marta)

    assert "ri" not in sad
    assert conformant.registry_state(registry, sad["d"]) is None


def test_a_registry_bound_credential_names_its_registry(conformant, marta):
    """The credential says which registry answers for it, in committed bytes."""
    registry = conformant.open_registry(marta, "acme-governance")
    sad, _ = seat_acdc(conformant, marta, registry, "acme:seat3")

    assert sad["ri"] == registry


def test_a_registry_and_its_events_are_deterministic(conformant, substrate_name, marta):
    """Every identifier the demo prints has to be the same on the next run."""
    registry = conformant.open_registry(marta, "acme-governance")
    sad, _ = seat_acdc(conformant, marta, registry, "acme:seat3")
    revocation = conformant.revoke_acdc(registry, sad["d"])

    with substrate_named(substrate_name) as again:
        marta_again = again.incept("acme:marta")
        registry_again = again.open_registry(marta_again, "acme-governance")
        sad_again, _ = seat_acdc(again, marta_again, registry_again, "acme:seat3")
        revocation_again = again.revoke_acdc(registry_again, sad_again["d"])

    assert (registry, sad["d"], revocation) == (
        registry_again,
        sad_again["d"],
        revocation_again,
    )


# --- verify_edges: the other current, and it is not the fold's ----------------


def seated(substrate, gaid):
    """A domain with a seat, a registry, and a seat credential issued to the seat.

    Returns the seat's identifier and the edge block an endorsement of its would
    carry: one node naming the seat credential under DI2I, which is the shape
    ``custos-4.2.md:1425-1428`` requires by name.
    """
    seat = substrate.delegate(gaid, "acme:seat3")
    registry = substrate.open_registry(gaid, "acme-governance")
    credential, _ = seat_acdc(substrate, gaid, registry, seat)
    return seat, {"qp": {"n": credential["d"], "s": SEAT_SCHEMA, "o": DI2I}}


def endorsement_with(substrate, issuer, edges):
    sad, _ = substrate.issue_acdc(
        issuer,
        ENDORSEMENT_SCHEMA,
        {"said": SUBJECT, "act": "issue", "disp": "endorse"},
        edges=edges,
    )
    return sad


def test_a_credential_carrying_no_edge_validates_trivially(conformant, marta):
    """Nothing is being claimed, so there is nothing to refuse."""
    sad, _ = endorsement_acdc(conformant, marta)
    assert conformant.verify_edges(sad) is True


def test_the_seat_itself_satisfies_its_own_seat_credentials_edge(conformant):
    """DI2I is a superset of I2I: issuer equal to the far node's issuee passes.

    Beat 12's machinery. The organ signs, and the edge says which office it
    signs as; the check is that the two are the same identifier.
    """
    gaid = conformant.incept("acme:gaid")
    seat, edges = seated(conformant, gaid)

    assert conformant.verify_edges(endorsement_with(conformant, seat, edges)) is True


@pytest.mark.parametrize("depth", [1, 2], ids=["device", "device-of-device"])
def test_a_delegated_identifier_satisfies_the_edge_at_any_depth(conformant, depth):
    """Beat 15, and the reading WebOfTrust/keripy#1564 settled.

    A delegated AID is one at any depth, bounded by the DND trait at the AID
    layer rather than by the operator. Reading DI2I as direct-only would forbid
    a two-layer hierarchy outright and need a second operator for every depth.
    """
    gaid = conformant.incept("acme:gaid")
    seat, edges = seated(conformant, gaid)
    signer = seat
    for hop in range(depth):
        signer = conformant.delegate(signer, f"acme:device{hop}")

    assert conformant.verify_edges(endorsement_with(conformant, signer, edges)) is True


def test_an_endorser_who_holds_no_seat_does_not_satisfy_the_edge(conformant):
    """Beat 14, which is the point of the whole act.

    Quinn's endorsement names a seat credential whose issuee Quinn is not. The
    edge does not validate, and that answer is not a finding: no verdict of the
    four is being returned here, and the fold is not in this code path at all.
    """
    gaid = conformant.incept("acme:gaid")
    _, edges = seated(conformant, gaid)
    quinn = conformant.incept("acme:quinn")

    assert conformant.verify_edges(endorsement_with(conformant, quinn, edges)) is False


def test_an_edge_naming_a_far_node_nobody_issued_does_not_validate(conformant):
    """Fail closed: an edge to a credential this substrate cannot resolve."""
    gaid = conformant.incept("acme:gaid")
    absent = {"qp": {"n": "E" + "z" * 43, "s": SEAT_SCHEMA, "o": DI2I}}

    assert conformant.verify_edges(endorsement_with(conformant, gaid, absent)) is False


def test_an_edge_whose_operator_is_not_implemented_does_not_validate(conformant):
    """An operator nobody implements confers nothing, and raises nothing either.

    keripy recognizes NOT and refuses it diagnosably rather than defaulting; at
    this seam both backends answer the same way, because every way an edge can
    fail to validate means the same thing.
    """
    gaid = conformant.incept("acme:gaid")
    seat, edges = seated(conformant, gaid)
    unimplemented = {"qp": {**edges["qp"], "o": "NOT"}}

    assert conformant.verify_edges(endorsement_with(conformant, seat, unimplemented)) is False


# --- delegate: a seat is an identifier, and its authority is another's ---------


def test_a_delegated_identifier_names_its_delegator(conformant):
    """The first half of a cooperative delegation: KERI's ``di`` (@2a25xudi).

    ``custos-4.2.md:2139-2148`` asks for a seated organ to be a delegated
    identifier of the gAID. A seat that did not name its delegator would be an
    ordinary identifier wearing an office's name.
    """
    gaid = conformant.incept("acme:gaid")
    seat = conformant.delegate(gaid, "acme:seat3")

    assert isinstance(seat, str) and seat != gaid
    assert conformant.delegator_of(seat) == gaid


def test_a_delegation_is_sealed_into_the_delegators_key_log(conformant):
    """The second half, and the one the demo's seat screen cites.

    The delegator seals the delegate's inception event, so the binding is a fact
    about committed KERI bytes on both sides rather than a claim on one.
    """
    gaid = conformant.incept("acme:gaid")
    seat = conformant.delegate(gaid, "acme:seat3")

    assert conformant.anchoring_event(seat) is not None


def test_a_self_incepted_identifier_has_no_delegator(conformant, marta):
    """Total and fail-closed: no delegator is ``None``, never an exception."""
    assert conformant.delegator_of(marta) is None
    assert conformant.delegator_of("E" + "z" * 43) is None


def test_a_delegated_identifier_signs_and_verifies_as_itself(conformant):
    """The organ signs. Its authority is delegated; its key material is its own."""
    gaid = conformant.incept("acme:gaid")
    seat = conformant.delegate(gaid, "acme:seat3")

    signature = conformant.sign(seat, BODY)

    assert conformant.verify(seat, BODY, signature)
    assert not conformant.verify(gaid, BODY, signature)


def test_a_delegated_identifier_may_itself_delegate(conformant):
    """The third stratum: gAID to seat to device, each hop a real delegation."""
    gaid = conformant.incept("acme:gaid")
    seat = conformant.delegate(gaid, "acme:seat3")
    device = conformant.delegate(seat, "acme:nina-device")

    assert conformant.delegator_of(device) == seat
    assert conformant.delegator_of(seat) == gaid


def test_delegating_under_an_identifier_with_no_key_state_is_refused(conformant):
    with pytest.raises(BakoboError) as caught:
        conformant.delegate("acme:never-incepted", "acme:seat3")
    assert caught.value.code == "e.id.aid-unknown.f"


def test_delegating_to_an_alias_already_taken_is_refused(conformant, marta):
    with pytest.raises(BakoboError) as caught:
        conformant.delegate(marta, "acme:marta")
    assert caught.value.code == "e.id.alias-taken.f"


def test_a_delegation_is_deterministic(conformant, substrate_name):
    """Two runs, two substrates of the same kind, one identifier.

    The record's replay claim reaches the seat as well: a delegated identifier
    derived from anything unpinned would move every beat that names it.
    """
    first = conformant.delegate(conformant.incept("acme:gaid"), "acme:seat3")
    with substrate_named(substrate_name) as again:
        second = again.delegate(again.incept("acme:gaid"), "acme:seat3")
    assert first == second


def test_issuing_does_not_disturb_the_issuers_signing_key_state(conformant, marta):
    """The anchor rides an interaction event: the log advances, the keys do not."""
    before = conformant.sign(marta, BODY)
    endorsement_acdc(conformant, marta)
    assert conformant.sign(marta, BODY) == before
    assert conformant.verify(marta, BODY, before)


# --- determinism across processes ---------------------------------------------

FINGERPRINT = """
import json, sys
from utina.substrate.select import substrate_named

with substrate_named(sys.argv[1]) as substrate:
    gaid = substrate.incept("acme:gaid")
    marta = substrate.incept("acme:marta")
    said = substrate.said({"t": "end", "act": "issue", "disp": "endorse", "s": 4})
    from utina.substrate import ENDORSEMENT_SCHEMA
    acdc, acdc_sig = substrate.issue_acdc(
        marta, ENDORSEMENT_SCHEMA, {"said": "E" + "s" * 43, "act": "issue", "disp": "endorse"}
    )
    print(json.dumps({
        "gaid": gaid,
        "marta": marta,
        "said": said,
        "sig": substrate.sign(marta, {"t": "act", "d": said}),
        "rot": substrate.rotate(gaid, said),
        "acdc": acdc["d"],
        "acdc_sig": acdc_sig,
    }))
"""


def fingerprint_in_a_separate_process(name: str, tmp_path: Path) -> dict[str, str]:
    """What a fresh interpreter, sharing nothing with this one, computes."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    script = tmp_path / f"fingerprint_{name}.py"
    script.write_text(FINGERPRINT, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(script), name],
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
        env={**os.environ, "PYTHONHASHSEED": "random"},
    )
    parsed: dict[str, str] = json.loads(completed.stdout)
    return parsed


def test_two_processes_compute_the_same_identifiers_and_the_same_signature(
    substrate_name, tmp_path
):
    """The claim replay rests on, checked where it can actually fail.

    Two interpreters, no shared state, randomized hash seeds. Identical output
    or the demo's replay beat is a performance. For keripy this holds because a
    KERI key event carries no timestamp and the salt, the inception order and
    the stretch tier are all pinned (this.i @7jrbt3).
    """
    first = fingerprint_in_a_separate_process(substrate_name, tmp_path / "a")
    second = fingerprint_in_a_separate_process(substrate_name, tmp_path / "b")
    assert first == second
    assert first["gaid"] != first["marta"]


# --- the selector itself ------------------------------------------------------


def test_asking_for_a_substrate_nobody_ships_is_refused():
    with pytest.raises(BakoboError) as caught:
        substrate_named("quantum")
    assert caught.value.code == "e.feature.substrate-unknown.f"
    assert "facade" in str(caught.value)
