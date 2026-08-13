"""Canonical bytes, and the digests taken over them.

Every identifier in utina is a digest of these bytes, so this module decides
what "the same committed inputs" means. Two properties are load-bearing and
both are tested rather than asserted: the encoding is a function of content
alone, so mapping insertion order cannot reach a SAID; and every value it
admits has exactly one encoding, so nothing rounds, widens or reorders on the
way to a digest.

What it refuses matters as much as what it encodes. A float has no exact
decimal image and a governance weight expressed as one makes unity
undecidable, so floats are refused at the encoder rather than tolerated and
regretted at the threshold (this.i @ta7vle).
"""

from __future__ import annotations

import base64
import hashlib
import json
from collections.abc import Mapping, Sequence
from fractions import Fraction

from .errors import NOT_CANONICAL

#: The length of an encoded identifier, and so of the placeholder that stands in
#: for one while it is being computed (custos-4.2.md:3081-3085).
SAID_LENGTH = 44

#: What an identifier field holds during its own computation.
SAID_PLACEHOLDER = "#" * SAID_LENGTH


def canonical_bytes(value: object) -> bytes:
    """The one byte-image of ``value``, or a refusal to produce any."""
    return json.dumps(canonical_json(value), separators=(",", ":")).encode("utf-8")


def canonical_json(value: object, path: str = "the body") -> object:
    """``value`` as JSON-ready data: mappings sorted, and nothing inexact.

    The same admissions and the same refusals as :func:`canonical_bytes`, one
    step earlier — a structure of ``dict``, ``list``, ``str``, ``int``, ``bool``
    and ``None`` rather than the bytes they serialize to. A substrate that hands
    a body to somebody else's serializer needs exactly this: the encoder's
    refusal of a float, and its ordering, without the encoder's bytes, since the
    other serializer will produce its own (this.i @fy5lwj).
    """
    return _canonical(value, path)


def digest(data: bytes) -> str:
    """A 44-character self-addressing identifier over ``data``.

    Blake2b-256 in a KERI-shaped envelope: a one-character code and 43
    characters of unpadded base64url. It is deliberately not KERI's Blake3
    primitive, because the facade claims no cryptographic dependency; Q23 in
    ``docs/custos-questions.md`` records the departure and its consequence,
    which is that utina's identifiers and a keripy engine's will differ over
    identical committed bytes.
    """
    raw = hashlib.blake2b(data, digest_size=32).digest()
    return "E" + base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _canonical(value: object, path: str) -> object:
    # bool before int: bool is an int subclass, and the naive order writes True
    # as 1, which silently changes a committed disposition into a number.
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, str):
        return value
    if value is None:
        return None
    if isinstance(value, Mapping):
        return _canonical_mapping(value, path)
    # str is a Sequence, so this test only runs once strings are already handled.
    if isinstance(value, Sequence):
        return [_canonical(item, f"{path}[{i}]") for i, item in enumerate(value)]
    raise NOT_CANONICAL(kind=type(value).__name__, path=path)


def _canonical_mapping(value: Mapping[object, object], path: str) -> dict[str, object]:
    """Sorted, so that mapping insertion order cannot reach a digest."""
    return {
        key: _canonical(value[key], f"{path}.{key}")
        for key in sorted(_keys(value, path))
    }


def _keys(value: Mapping[object, object], path: str) -> list[str]:
    keys = []
    for key in value:
        if not isinstance(key, str):
            raise NOT_CANONICAL(
                kind=f"{type(key).__name__} used as a mapping key", path=path
            )
        keys.append(key)
    return keys
