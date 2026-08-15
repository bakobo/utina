"""What the keripy backend is, as opposed to what every backend promises.

``tests/test_substrate_conformance.py`` states the protocol's contract and asks
it of both implementations. This file is the other half: the things that are
true here because this is real KERI and would be meaningless said of the facade
— that an identifier is a prefix, that the key log holds an inception and a
rotation in that order, that the anchor is a seal in the rotation's ``a`` field
where a stranger's tool looks for one.

It is also where the backend's own edges are pinned: the durable store it
refuses to clear, and the ways a signature can be malformed that a pure-Python
substrate would never have had to survive.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from bakobo.errors import BakoboError
from keri.core.eventing import verifySigs
from keri.core.indexing import Siger
from keri.core.serdering import SerderACDC
from keri.core.structing import SealDigest

from utina.substrate import ENDORSEMENT_SCHEMA
from utina.substrate.keripy import COORDINATE, MARKER, KeripySubstrate

BODY: dict[str, object] = {"t": "act", "act": "open-bank-account", "s": 1}


@pytest.fixture
def keripy():
    """An ephemeral store: the fast stretch tier, cleared on the way out."""
    with KeripySubstrate() as substrate:
        yield substrate


# --- what makes it real -------------------------------------------------------


def test_an_identifier_is_a_keri_prefix(keripy):
    """Not an alias. A 44-character qb64 Blake3 digest of the inception event."""
    aid = keripy.incept("acme:marta")
    assert len(aid) == 44
    assert aid.startswith("E")
    assert aid != "acme:marta"


def test_inception_writes_an_inception_event_to_a_real_key_log(keripy):
    aid = keripy.incept("acme:gaid")
    kel = [(s.sn, s.ked["t"], s.said) for s in keripy._hby.db.getEvtPreIter(pre=aid)]
    assert kel == [(0, "icp", aid)]


def test_a_rotation_is_an_establishment_event_carrying_a_digest_seal(keripy):
    """Beat D4's anchor, in the field any KERI tool reads it out of."""
    aid = keripy.incept("acme:gaid")
    anchor = keripy.said({"t": "enact", "law": {"clauses": []}})
    establishment = keripy.rotate(aid, anchor)

    kel = [(s.sn, s.ked["t"], s.said) for s in keripy._hby.db.getEvtPreIter(pre=aid)]
    assert kel == [(0, "icp", aid), (1, "rot", establishment)]
    rotation = keripy._hby.kevers[aid].serder
    assert rotation.sad["a"] == [{"d": anchor}]


def test_a_signature_is_an_establishment_coordinate_and_an_indexed_signature(keripy):
    """@zk27gz: the opaque string carries the key state it was made under."""
    aid = keripy.incept("acme:marta")
    established, _, qb64 = keripy.sign(aid, BODY).partition(COORDINATE)
    assert established == keripy._hby.habs[aid].kever.lastEst.d
    assert len(qb64) == 88


def test_the_digested_bytes_are_keri_json_with_the_identifier_first(keripy):
    """The one field order, visible: d first, then sorted, and no signature."""
    sealed = {"sig": "ignored", "t": "act", "act": "open-bank-account", "s": 1}
    sealed["d"] = keripy.said(sealed)
    said = sealed["d"]
    assert keripy._raw(sealed).decode() == (
        f'{{"d":"{said}","act":"open-bank-account","s":1,"t":"act"}}'
    )


def test_a_said_is_recomputable_by_keripy_alone(keripy):
    """A stranger with keripy and none of our code gets the same identifier."""
    from keri.core.coring import Saider

    said = keripy.said(BODY)
    sad = {"d": said, "act": "open-bank-account", "s": 1, "t": "act"}
    assert Saider(qb64=said).verify(sad, prefixed=True)


# --- the edges a real library brings -----------------------------------------


def test_a_signature_with_a_known_coordinate_and_a_malformed_body_verifies_nothing(
    keripy,
):
    """keripy raises on malformed CESR where the protocol requires False."""
    aid = keripy.incept("acme:marta")
    established, _, _ = keripy.sign(aid, BODY).partition(COORDINATE)
    assert not keripy.verify(aid, BODY, f"{established}{COORDINATE}not-a-signature")
    assert not keripy.verify(aid, BODY, f"{established}{COORDINATE}AAAA")


def test_a_signature_naming_an_establishment_event_that_never_happened(keripy):
    aid = keripy.incept("acme:marta")
    _, _, qb64 = keripy.sign(aid, BODY).partition(COORDINATE)
    assert not keripy.verify(aid, BODY, f"E{'z' * 43}{COORDINATE}{qb64}")


def test_a_rotation_carrying_several_seals_answers_for_each_of_them(keripy):
    """Nothing in utina writes two, and the walk may not stop at the first."""
    aid = keripy.incept("acme:gaid")
    first, second = keripy.said({"n": 1}), keripy.said({"n": 2})
    keripy._hby.habs[aid].rotate(
        data=[SealDigest(d=first)._asdict(), SealDigest(d=second)._asdict()]
    )
    rotation = keripy._hby.kevers[aid].serder.said
    assert keripy.anchoring_event(first) == rotation
    assert keripy.anchoring_event(second) == rotation


# --- the durable store --------------------------------------------------------


def test_a_durable_store_leaves_a_key_log_on_disk_for_somebody_else_to_read(
    tmp_path: Path,
):
    """The whole point of a store: the demo's evidence outlives the process."""
    store = tmp_path / "keri-store"
    with KeripySubstrate(store=store) as substrate:
        aid = substrate.incept("acme:gaid")

    assert (store / MARKER).exists()
    assert (store / "keri" / "db" / "utina").is_dir()
    assert aid.startswith("E")


def test_a_durable_store_is_rebuilt_from_nothing_on_every_run(tmp_path: Path):
    """Two runs, same identifiers: the record does not depend on the run count."""
    store = tmp_path / "keri-store"
    with KeripySubstrate(store=store) as first:
        before = first.incept("acme:gaid")
    with KeripySubstrate(store=store) as second:
        after = second.incept("acme:gaid")
    assert before == after


def test_a_directory_this_substrate_did_not_make_is_never_emptied(tmp_path: Path):
    """Fail closed: a store path is a path somebody typed."""
    store = tmp_path / "someones-documents"
    store.mkdir()
    (store / "thesis.txt").write_text("years of work", encoding="utf-8")

    with pytest.raises(BakoboError) as caught, KeripySubstrate(store=store):
        pass  # pragma: no cover - __enter__ raises, so the body is never reached
    assert caught.value.code == "e.state.store-not-ours.f"
    assert (store / "thesis.txt").exists()


def test_the_ephemeral_and_the_durable_store_are_different_key_material(tmp_path: Path):
    """@7jrbt3: the stretch tier differs, so the same salt is not the same AID.

    Stated as a test rather than as a warning, because the surprising half is
    that a pinned salt is *not* sufficient on its own.
    """
    with KeripySubstrate() as ephemeral:
        fast = ephemeral.incept("acme:gaid")
    with KeripySubstrate(store=tmp_path / "store") as durable:
        slow = durable.incept("acme:gaid")
    assert fast != slow


# --- a registry-less credential (this.i @7db5c4) -------------------------------


def endorsement_acdc(substrate, issuer):
    return substrate.issue_acdc(
        issuer, ENDORSEMENT_SCHEMA, {"said": "E" + "s" * 43, "act": "issue", "disp": "endorse"}
    )


def test_the_pinned_schema_said_is_the_dossier_specifications():
    """The one schema all four operators use (dossier-spec-body.md:367)."""
    assert ENDORSEMENT_SCHEMA == "EAfn0gRMUnp6d1hyE5qJCN86kBFBp80JwMdm0BqiC1B0"


def test_a_credential_is_a_real_acdc_a_stranger_verifies_with_keripy_alone(keripy):
    """SAID recomputed by keripy, signature checked against the named key state."""
    marta = keripy.incept("acme:marta")
    sad, signature = endorsement_acdc(keripy, marta)

    creder = SerderACDC(sad=dict(sad))  # re-verifies the SAID on construction
    assert creder.said == sad["d"]
    assert creder.regid is None  # no registry: structurally unrevokable

    established, _, qb64 = signature.partition(COORDINATE)
    serder = keripy._hby.db.evts.get(keys=(marta, established))
    verified, _ = verifySigs(raw=creder.raw, sigers=[Siger(qb64=qb64)], verfers=serder.verfers)
    assert verified


def test_the_credential_anchor_is_an_interaction_event_not_a_rotation(keripy):
    """The keys do not move to anchor a credential; the log grows by one ixn."""
    marta = keripy.incept("acme:marta")
    sad, _ = endorsement_acdc(keripy, marta)
    sealing = [
        serder
        for serder in keripy._hby.db.getEvtPreIter(pre=marta)
        for seal in (serder.sad.get("a") or ())
        if seal.get("d") == sad["d"]
    ]
    assert sealing
    assert all(serder.ilk == "ixn" for serder in sealing)


def test_a_credential_whose_signature_will_not_verify_is_never_returned(keripy, monkeypatch):
    """Fail closed at issuance, same discipline as the constructor's _emit."""
    marta = keripy.incept("acme:marta")
    monkeypatch.setattr(
        "utina.substrate.keripy.eventing.verifySigs", lambda **kwargs: ((), ())
    )
    with pytest.raises(BakoboError) as caught:
        endorsement_acdc(keripy, marta)
    assert caught.value.code == "e.proof.acdc-sig.f"
