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

from utina.substrate import SAID_LENGTH
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


# --- determinism across processes ---------------------------------------------

FINGERPRINT = """
import json, sys
from utina.substrate.select import substrate_named

with substrate_named(sys.argv[1]) as substrate:
    gaid = substrate.incept("acme:gaid")
    marta = substrate.incept("acme:marta")
    said = substrate.said({"t": "end", "act": "issue", "disp": "endorse", "s": 4})
    print(json.dumps({
        "gaid": gaid,
        "marta": marta,
        "said": said,
        "sig": substrate.sign(marta, {"t": "act", "d": said}),
        "rot": substrate.rotate(gaid, said),
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
