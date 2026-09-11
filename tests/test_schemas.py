"""Every schema identifier this domain pins is the digest of a document here.

A credential names its schema by identifier, and nothing in utina validates a
credential against the document — that is the existing KERI toolchain's job,
which is the whole point of typing an object by schema identifier. So the pin is
the only thing standing between the record and a schema nobody can produce, and
an unchecked pin is a forty-four character claim that some file somewhere says
what the demo says it says.

This recomputes it with the tooling a stranger would use: keripy's ``Schemer``,
which is what puts a schema's own identifier in its ``$id``. It imports keripy
directly, which is lawful here — the purity fitness function governs
``src/utina``, and the point of this file is to check a pin against the library
that computes it.
"""

from __future__ import annotations

import json
from pathlib import Path

from keri.core.coring import Saider  # type: ignore[import-untyped]
from keri.core.scheming import Schemer  # type: ignore[import-untyped]

from utina.acme import SEAT_SCHEMA
from utina.substrate import GCD_RULES, GCD_SCHEMA

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"


def document(name: str) -> dict:
    """One vendored document, as it stands on disk."""
    loaded: dict = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    return loaded


def said_of(name: str) -> str:
    """The schema identifier keripy computes for the document as it stands on disk."""
    said: str = Schemer(sed=document(name)).said
    return said


def test_the_seat_schema_pin_is_the_digest_of_the_committed_document():
    """Acme's law names this identifier, so the document has to derive it."""
    assert said_of("acme-seat.json") == SEAT_SCHEMA


def test_the_seat_schema_carries_its_own_identifier_in_its_id():
    """ACDC's convention, and what makes the document self-describing.

    The identifier is computed with ``$id`` held at a dummy of its own length,
    so a document whose ``$id`` is its own SAID is stable under recomputation —
    which is what lets a stranger check the pin without being told the answer.
    """
    document = json.loads((SCHEMAS / "acme-seat.json").read_text(encoding="utf-8"))
    assert document["$id"] == SEAT_SCHEMA


def test_the_seat_schema_requires_the_fields_custos_names():
    """``custos-4.2.md:1420-1425``: typed by schema, registry-bound, issuee named.

    A schema that left ``ri`` or the issuee optional would type a credential
    that satisfies the schema and not the requirement, which is worse than
    having no schema at all: the toolchain would pass it.
    """
    document = json.loads((SCHEMAS / "acme-seat.json").read_text(encoding="utf-8"))
    assert "ri" in document["required"]
    attributes = next(
        form for form in document["properties"]["a"]["oneOf"] if form.get("type") == "object"
    )
    assert {"i", "seat"} <= set(attributes["required"])


def test_the_gcd_schema_pin_is_the_digest_of_the_vendored_document():
    """The GCD is not utina's schema, so the pin has to be checkable against bytes.

    ``bakobo/schema`` publishes the document and its ``$id``; utina vendors a copy
    and pins the identifier (``this.i`` @cglayqvw). Recomputing it with the same
    tooling a stranger would use is what stops the pin from being a claim that
    some file somewhere says what utina says it says — and what makes a silent
    upstream edit a red test rather than a credential nobody can type.
    """
    assert said_of("gcd-2.0.1.json") == GCD_SCHEMA
    assert document("gcd-2.0.1.json")["$id"] == GCD_SCHEMA


def test_the_vendored_gcd_is_the_published_one_and_not_a_lookalike():
    """The fields the adoption rests on, asserted against the document itself."""
    gcd = document("gcd-2.0.1.json")
    assert gcd["title"] == "Generalized Cooperative Delegation Credential"
    assert set(gcd["required"]) == {"v", "d", "i", "ri", "s", "a", "r"}
    attributes = next(
        form for form in gcd["properties"]["a"]["oneOf"] if form.get("type") == "object"
    )
    assert "i" in attributes["required"]
    assert "acts" in attributes["properties"]["constraints"]["properties"]


def test_the_gcd_rules_pin_is_the_digest_of_the_vendored_ruleset():
    """A GCD's ``r`` names the governance framework it is issued under.

    "The act of issuing or receiving a GCD credential constitutes binding
    acceptance of the rules", so the compact form utina commits — the ruleset's
    SAID alone — is load-bearing rather than decorative, and a pin nobody can
    resolve would be an acceptance of nothing.
    """
    rules = document("gcd-rules.json")
    _, saidified = Saider.saidify(sad=dict(rules), label="d")
    assert saidified["d"] == GCD_RULES
    assert rules["d"] == GCD_RULES


def test_the_vendored_ruleset_carries_the_disclaimer_that_bounds_the_gate():
    """``noConstraintOutsideConstraints`` is why the fold may ignore the facet.

    It is the rule that makes ``constraints`` the whole of the authorization
    decision, and therefore the rule the slot predicate's shape rests on
    (``this.i`` @cglayqvw, and bakobo/schema#3 for the field description that
    contradicts it).
    """
    assert "noConstraintOutsideConstraints" in document("gcd-rules.json")
