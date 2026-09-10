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

from keri.core.scheming import Schemer  # type: ignore[import-untyped]

from utina.acme import SEAT_SCHEMA

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"


def said_of(document: str) -> str:
    """The schema identifier keripy computes for the document as it stands on disk."""
    said: str = Schemer(sed=json.loads((SCHEMAS / document).read_text(encoding="utf-8"))).said
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
