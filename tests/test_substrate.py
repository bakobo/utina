"""The substrate facade: determinism, fail-closed verification, and rotation.

The promise the whole system rests on is that the same committed inputs give
the same answer to anyone. That promise is discharged here or nowhere: if a
SAID or a signature varies between runs, replay is theatre. So most of this
file is about sameness — same bytes from differently-ordered mappings, same
digest across calls, same signature from the same body — and the rest is about
refusing to produce authority from anything unverifiable.
"""

from __future__ import annotations

from fractions import Fraction

import pytest
from bakobo.errors import BakoboError

from utina.substrate import (
    SAID_PLACEHOLDER,
    FacadeSubstrate,
    canonical_bytes,
    digest,
)

# --- Canonical bytes ---------------------------------------------------------


def test_mapping_key_order_does_not_change_the_bytes():
    """Committed bytes are a function of content, never of dict insertion order."""
    assert canonical_bytes({"a": 1, "b": 2}) == canonical_bytes({"b": 2, "a": 1})


def test_nesting_is_encoded_structurally_not_by_repr():
    encoded = canonical_bytes({"outer": {"inner": [1, 2]}})
    assert encoded == b'{"outer":{"inner":[1,2]}}'


def test_a_list_and_a_tuple_of_the_same_items_encode_alike():
    """Acme commits tuples; a caller may hand in lists. Neither may change a SAID."""
    assert canonical_bytes({"k": [1, 2]}) == canonical_bytes({"k": (1, 2)})


def test_strings_are_escaped_the_same_way_on_every_platform():
    assert canonical_bytes({"k": "Adeyemi—Reyes"}) == b'{"k":"Adeyemi\\u2014Reyes"}'


def test_booleans_encode_as_booleans_and_not_as_integers():
    """bool is a subclass of int, so the naive encoder writes ``1`` and lies."""
    assert canonical_bytes({"k": True}) == b'{"k":true}'
    assert canonical_bytes({"k": False}) == b'{"k":false}'
    assert canonical_bytes({"k": 1}) == b'{"k":1}'


def test_none_encodes_as_null():
    assert canonical_bytes({"k": None}) == b'{"k":null}'


def test_a_weight_is_committed_as_an_exact_rational_string():
    """@ta7vle: unity must be decidable, so no weight ever becomes a float."""
    assert canonical_bytes({"weight": Fraction(1, 2)}) == b'{"weight":"1/2"}'
    assert canonical_bytes({"weight": Fraction(2, 4)}) == b'{"weight":"1/2"}'


def test_a_float_is_refused_rather_than_rounded():
    with pytest.raises(BakoboError) as caught:
        canonical_bytes({"weight": 0.5})
    assert caught.value.code == "e.input.not-canonical.f"
    assert "float" in str(caught.value)


def test_a_non_string_key_is_refused():
    with pytest.raises(BakoboError) as caught:
        canonical_bytes({1: "one"})
    assert caught.value.code == "e.input.not-canonical.f"


def test_an_unencodable_value_is_refused_by_type_name():
    with pytest.raises(BakoboError) as caught:
        canonical_bytes({"k": object()})
    assert caught.value.code == "e.input.not-canonical.f"
    assert "object" in str(caught.value)


# --- Digests and event identity ----------------------------------------------


def test_the_placeholder_is_as_long_as_the_identifier_it_stands_in_for():
    """custos-4.2.md:3083 — a placeholder of the encoded digest's length."""
    assert len(SAID_PLACEHOLDER) == len(digest(b"anything"))


def test_a_digest_is_stable_across_calls():
    assert digest(b"acme") == digest(b"acme")


def test_a_digest_is_a_keri_shaped_44_character_identifier():
    said = digest(b"acme")
    assert len(said) == 44
    assert said.startswith("E")


def test_the_said_of_a_body_ignores_whatever_the_identifier_field_held(substrate):
    """The identifier is computed over a placeholder, so its prior value is inert."""
    bare = substrate.said({"t": "act", "act": "open-bank-account"})
    stale = substrate.said(
        {"t": "act", "act": "open-bank-account", "d": "E" + "x" * 43}
    )
    assert bare == stale


def test_the_said_of_a_body_ignores_its_signature(substrate):
    """S5: a signature is an attachment, so signing may not move the identifier."""
    body = {"t": "act", "act": "open-bank-account"}
    assert substrate.said(body) == substrate.said({**body, "sig": "0B0.whatever"})


def test_different_bodies_get_different_saids(substrate):
    assert substrate.said({"act": "a"}) != substrate.said({"act": "b"})


# --- Identifiers -------------------------------------------------------------


def test_inception_returns_the_identifier_the_caller_must_then_use(substrate):
    """@d2nlhb: the facade's AID is its alias, and callers use what they are given."""
    assert substrate.incept("acme:marta") == "acme:marta"


def test_incepting_the_same_alias_twice_is_refused(substrate):
    """Silently returning the existing identifier would hide a duplicated party."""
    substrate.incept("acme:marta")
    with pytest.raises(BakoboError) as caught:
        substrate.incept("acme:marta")
    assert caught.value.code == "e.id.alias-taken.f"
    assert "acme:marta" in str(caught.value)


def test_signing_as_an_unincepted_identifier_is_refused(substrate):
    with pytest.raises(BakoboError) as caught:
        substrate.sign("acme:ghost", {"t": "act"})
    assert caught.value.code == "e.id.aid-unknown.f"
    assert "acme:ghost" in str(caught.value)


def test_rotating_an_unincepted_identifier_is_refused(substrate):
    with pytest.raises(BakoboError) as caught:
        substrate.rotate("acme:ghost", "E" + "x" * 43)
    assert caught.value.code == "e.id.aid-unknown.f"


# --- Signing and verifying ---------------------------------------------------


def test_a_signature_is_reproducible(substrate, values):
    """Two substrates, same seed material, same bytes — this is what replay needs."""
    other = FacadeSubstrate(values=values)
    substrate.incept("acme:marta")
    other.incept("acme:marta")
    body = {"t": "end", "disp": "endorse"}
    assert substrate.sign("acme:marta", body) == other.sign("acme:marta", body)


def test_a_signature_verifies_against_the_body_it_was_made_over(substrate):
    substrate.incept("acme:marta")
    body = {"t": "end", "disp": "endorse"}
    assert substrate.verify("acme:marta", body, substrate.sign("acme:marta", body))


def test_a_signature_does_not_verify_over_altered_bytes(substrate):
    """The declination that defeats D3 must not be re-readable as an endorsement."""
    substrate.incept("acme:dev")
    signature = substrate.sign("acme:dev", {"t": "end", "disp": "decline"})
    assert not substrate.verify("acme:dev", {"t": "end", "disp": "endorse"}, signature)


def test_a_signature_verifies_with_itself_present_in_the_body(substrate):
    """enact stores the signature in the body; verification must survive that."""
    substrate.incept("acme:marta")
    body = {"t": "end", "disp": "endorse"}
    signature = substrate.sign("acme:marta", body)
    assert substrate.verify("acme:marta", {**body, "sig": signature}, signature)


def test_an_unknown_identifier_verifies_nothing(substrate):
    """Fail closed: an unverifiable claim produces no authority, and no exception."""
    assert not substrate.verify("acme:ghost", {"t": "end"}, "0B0.whatever")


@pytest.mark.parametrize(
    "signature",
    ["", "nonsense", "0B0", "1B0.abc", "0Bx.abc", "0B9.abc"],
    ids=["empty", "unstructured", "no-mac", "wrong-code", "index-not-a-number",
         "index-out-of-range"],
)
def test_a_malformed_signature_verifies_nothing(substrate, signature):
    substrate.incept("acme:marta")
    assert not substrate.verify("acme:marta", {"t": "end"}, signature)


# --- Rotation ----------------------------------------------------------------


def test_a_rotation_is_an_establishment_event_carrying_the_anchor(substrate):
    """custos-4.2.md:2085-2087 — an enactment amending law anchors in one of these."""
    substrate.incept("acme:gaid")
    anchor = substrate.said({"t": "enact"})
    event = substrate.rotate("acme:gaid", anchor)
    assert event.kind == "rotation"
    assert event.body["t"] == "rot"
    assert event.body["a"] == ({"d": anchor},)
    assert event.said == substrate.said(event.body)


def test_a_rotation_advances_the_key_state(substrate):
    substrate.incept("acme:gaid")
    before = substrate.sign("acme:gaid", {"t": "act"})
    substrate.rotate("acme:gaid", substrate.said({"t": "enact"}))
    after = substrate.sign("acme:gaid", {"t": "act"})
    assert before != after
    assert before.startswith("0B0.")
    assert after.startswith("0B1.")


def test_a_signature_made_before_a_rotation_still_verifies_after_it(substrate):
    """@h7l67i — replay dies at the first amendment if this is not true."""
    substrate.incept("acme:gaid")
    body = {"t": "act", "act": "open-bank-account"}
    signature = substrate.sign("acme:gaid", body)
    substrate.rotate("acme:gaid", substrate.said({"t": "enact"}))
    assert substrate.verify("acme:gaid", body, signature)


def test_rotation_coordinates_climb_the_identifier_s_own_key_log(substrate):
    substrate.incept("acme:gaid")
    first = substrate.rotate("acme:gaid", substrate.said({"t": "enact", "n": 1}))
    second = substrate.rotate("acme:gaid", substrate.said({"t": "enact", "n": 2}))
    assert (first.position.seq, second.position.seq) == (1, 2)
    assert first.body["s"] == 1


def test_the_anchor_binding_is_recorded_and_answerable(substrate):
    """@jdie6v: the rotation stays out of the corpus, so the binding lives here."""
    substrate.incept("acme:gaid")
    anchor = substrate.said({"t": "enact"})
    rotation = substrate.rotate("acme:gaid", anchor)
    assert substrate.anchor_of(anchor) == rotation.said
    assert substrate.anchor_of("E" + "z" * 43) is None
