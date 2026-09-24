"""A record utina did not write, rebuilt in a stranger's substrate and folded.

``custos-4.2.md:31-34``: "any stranger holding the logs computes the same
Constitution and the same findings". Here the stranger is a substrate that wrote
nothing: Acme's record is exported, carried as JSON, and ingested into a fresh
substrate of the same kind, which replays every key log, re-derives every
identifier and verifies every signature before the fold sees anything
(this.i @k6agmgtn). Then everything must come out the same. Every other test
here is a way the record can be wrong, shown refused (this.i @gnviwwjc).
"""

from __future__ import annotations

import copy
import json

import pytest
from bakobo.errors import BakoboError

from utina.fold.constitution import Constitution
from utina.fold.evaluate import evaluate
from utina.fold.gel import Genesis
from utina.fold.question import Committed
from utina.replay import FORMAT, export, ingest
from utina.substrate.select import substrate_named


@pytest.fixture
def record(acme):
    """Acme's record as a stranger receives it: JSON text, parsed."""
    return json.loads(json.dumps(export(acme.events, acme.gaid, acme.substrate)))


def backend(acme) -> str:
    """The name of the backend Acme was built on, so the stranger runs the same one."""
    return "keripy" if type(acme.substrate).__name__ == "KeripySubstrate" else "facade"


def stranger(acme):
    return substrate_named(backend(acme))


def test_a_stranger_rebuilds_the_same_record(acme, record):
    with stranger(acme) as substrate:
        corpus = ingest(record, substrate)
        last = acme.values.position(len(acme.events) - 1)
        assert [e.said for e in corpus.upto(last)] == [e.said for e in acme.events]
        assert corpus.genesis is Genesis.BORN
        for label in ("inception", "board-seated", "b22"):
            at = acme.at(label)
            assert (
                Constitution.at(corpus, at).canonical_bytes()
                == Constitution.at(acme.corpus, at).canonical_bytes()
            )
        for name in ("open-bank-account", "sign-office-lease", "seat-the-board"):
            subject = Committed(acme.said(name))
            assert evaluate(corpus, subject, at=last) == evaluate(acme.corpus, subject, at=last)


def refused(acme, record, code: str) -> None:
    with stranger(acme) as substrate, pytest.raises(BakoboError) as raised:
        ingest(record, substrate)
    assert raised.value.is_exactly(code), raised.value.code


def event_named(acme, record, name):
    said = acme.said(name)
    return next(entry for entry in record["events"] if entry["said"] == said)


def test_an_edited_event_is_refused(acme, record):
    """One committed field changed: the identifier no longer derives from the bytes."""
    event_named(acme, record, "sign-office-lease")["body"]["act"] = "something-else"
    refused(acme, record, "e.proof.record-unverifiable.f")


def test_an_edited_event_given_a_fresh_identifier_is_refused(acme, record):
    """Re-deriving the identifier does not help: the signature no longer verifies."""
    with stranger(acme) as scratch:
        entry = event_named(acme, record, "sign-office-lease")
        entry["body"]["act"] = "something-else"
        entry["said"] = entry["body"]["d"] = scratch.said(entry["body"])
    refused(acme, record, "e.proof.record-unverifiable.f")


def test_an_event_whose_signer_brought_no_key_log_is_refused(acme, record):
    """Leaving the signer's key log out leaves their signature unverifiable."""
    marta = acme.aid("acme:marta")
    record["kels"] = [entry for entry in record["kels"] if entry["aid"] != marta]
    refused(acme, record, "e.proof.record-unverifiable.f")


def test_a_withheld_event_is_refused(acme, record):
    del record["events"][5]
    refused(acme, record, "e.state.gel-membership.f")


def test_a_key_log_nobody_needs_is_refused(acme, record):
    """Content the fold would not examine (this.i @gnviwwjc)."""
    with substrate_named(backend(acme)) as other:
        extra = other.incept("acme:stranger")
        record["kels"].append({"aid": extra, "log": other.export_kel(extra)})
    refused(acme, record, "e.input.record-malformed.f")


def test_an_event_of_a_kind_no_fold_reads_is_refused(acme, record):
    record["events"][3]["kind"] = "memo"
    refused(acme, record, "e.input.record-malformed.f")


@pytest.mark.parametrize(
    "edit",
    [
        lambda r: r.update(extra=1),
        lambda r: r.update(format="utina-record/0"),
        lambda r: r.update(gaid=7),
        lambda r: r.update(kels="none"),
        lambda r: r["kels"][0].update(note="x"),
        lambda r: r["kels"][0].update(log=7),
        lambda r: r["events"][0].update(note="x"),
        lambda r: r["events"][0].update(body="x"),
        lambda r: r["events"].__setitem__(0, "x"),
    ],
    ids=["extra-field", "format", "gaid", "kels", "kel-field", "kel-log", "event-field",
         "event-body", "event-not-map"],
)
def test_a_record_of_the_wrong_shape_is_refused(acme, record, edit):
    edit(record)
    refused(acme, record, "e.input.record-malformed.f")


@pytest.mark.parametrize(
    "edit",
    [
        lambda body: body.pop("sig"),
        lambda body: body.update(i=7),
        lambda body: body.update(s=-1),
        lambda body: body.update(s=True),
    ],
    ids=["no-signature", "signer-not-text", "negative-sn", "bool-sn"],
)
def test_an_event_that_cannot_be_checked_is_refused(acme, record, edit):
    with stranger(acme) as scratch:
        entry = record["events"][2]
        edit(entry["body"])
        entry["said"] = entry["body"]["d"] = scratch.said(entry["body"])
    refused(acme, record, "e.proof.record-unverifiable.f")


def test_the_record_is_self_describing(record):
    assert record["format"] == FORMAT
    assert copy.deepcopy(record) == record


def test_an_event_relabelled_as_another_kind_is_refused(acme, record):
    """The kind label sits outside every signature, so it is checked against the
    signed body's own ilk rather than believed: an endorsement relabelled as an
    act would otherwise stop counting toward unity."""
    endorsement = next(e for e in record["events"] if e["kind"] == "endorsement")
    endorsement["kind"] = "act"
    refused(acme, record, "e.proof.record-unverifiable.f")


def test_a_signer_whose_key_log_the_record_does_not_carry_is_refused(acme, record):
    """Key state the stranger already held is not evidence this record presented."""
    marta = acme.aid("acme:marta")
    record["kels"] = [entry for entry in record["kels"] if entry["aid"] != marta]
    with stranger(acme) as substrate:
        substrate.ingest_kel(marta, acme.substrate.export_kel(marta))
        with pytest.raises(BakoboError) as raised:
            ingest(record, substrate)
    assert raised.value.is_exactly("e.input.record-malformed.f")


def test_an_embedded_credential_its_issuer_did_not_sign_is_refused(acme, record):
    """The event's own signature says nothing about whether the credential's
    issuer signed the credential. Only the facade lets a stranger re-sign an
    event, which is what makes the credential check the one left standing."""
    if backend(acme) != "facade":
        pytest.skip("only the facade lets a test re-sign an event it did not write")
    from utina.substrate import FacadeSubstrate

    entry = next(e for e in record["events"] if e["kind"] == "endorsement")
    body = entry["body"]
    forger = FacadeSubstrate()
    forger.incept(body["i"])
    body["acdc_sig"] = "0B0.not-the-issuers"
    body.pop("sig")
    body["d"] = forger.said(body)
    body["sig"] = forger.sign(body["i"], body)
    entry["said"] = body["d"]
    refused(acme, record, "e.proof.record-unverifiable.f")


@pytest.mark.parametrize(
    ("bound", "value"),
    [("MAX_EVENTS", 3), ("MAX_KELS", 1), ("MAX_EVENT_TEXT", 50), ("MAX_DEPTH", 1)],
)
def test_a_record_past_its_bounds_is_refused_before_it_is_replayed(
    acme, record, monkeypatch, bound, value
):
    """Size, then shape, then meaning (bakobo dev/standards/input-handling.md)."""
    monkeypatch.setattr(f"utina.replay.{bound}", value)
    refused(acme, record, "e.input.record-malformed.f")
