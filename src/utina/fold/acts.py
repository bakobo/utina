"""The act grid, and what a GCD's ``acts`` entries let a delegate do.

A GCD credential confers authority, and ``constraints.acts`` is where it says
*which* authority: "the set of (effect, state-kind) POINTS this delegate may act
on — the enabling 'may' over the act grid" (``schemas/gcd-2.0.1.json``). An act
is located by an effect over a kind of state, "the two axes of one coordinate,
neither meaningful alone", and the rule that follows is the one this module
exists to apply: "An act is authorized only if EVERY (effect, state-kind) point
it occupies is covered here."

**Why the fold may evaluate this dimension and not the others.** GCD's rule 1
says enforceable constraints live only inside the ``constraints`` container and
that an unrecognized key inside it is fail-closed — "a verifier that does not
recognize it MUST assume that constraint is unmet and MUST deny". utina's fold
therefore owes an evaluator for every dimension it admits and a denial for every
dimension it does not. ``acts`` is string parsing over committed bytes with no
clock and no KERI library in it, so it is one the fold can honestly answer;
``jurisdictions``, ``icals``, ``monetaryLimit`` and their siblings each need
context no committed byte carries, and ``validFrom``/``validUntil`` need a wall
clock, which is the ambient input axiom 2 forbids (``this.i`` @cglayqvw, ~5c5z).

**The grammar is the published pattern, not the prose beside it.** The schema
constrains each entry with a regular expression, and the vocabulary below is
read off that pattern: five effects, six state-kinds, exactly one space between
the halves, braces on one side only, and items separating on one or more commas
or spaces. Two-sided braces and wildcards are "intentionally not allowed", and
the pattern is case-sensitive, so ``Create commitment`` is not an entry.

Nothing here raises. An entry outside the grammar contributes no points, exactly
as an endorsement the slot predicate cannot read fills no slot
(``fold/slots.py:33-37``) — a grant nobody can parse is a grant of nothing, and
a fold that raised on a stranger's bytes would let anybody stop it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

__all__ = [
    "EFFECTS",
    "KINDS",
    "Point",
    "covered",
    "permits",
    "points",
]

Point = tuple[str, str]
"""One coordinate of the grid: an effect over a kind of state."""

EFFECTS = frozenset({"observe", "create", "modify", "preserve", "destroy"})
"""The effect axis, as ``schemas/gcd-2.0.1.json`` enumerates it."""

KINDS = frozenset({"info", "record", "commitment", "authority", "resource", "relationship"})
"""The state-kind axis. Note ``info`` rather than ``information``: the published
document's pattern is what a stranger validates against, so it is what this
agrees with."""

_ENTRY = re.compile(
    r"^(?:"
    r"(?P<effect>[a-z]+) (?:(?P<kind>[a-z]+)|\{(?P<kinds>[^{}]*)\})"
    r"|\{(?P<effects>[^{}]*)\} (?P<lone_kind>[a-z]+)"
    r")$"
)
"""The entry's *shape*, deliberately looser than the published pattern.

The shape is matched here and the vocabulary is checked in :func:`points`
against :data:`EFFECTS` and :data:`KINDS`. Reproducing the schema's full
alternation would put the token lists in two places, where they could drift;
splitting shape from vocabulary keeps one copy of each and makes an unknown
token fail closed on the same path as a malformed one.
"""

_SEPARATOR = re.compile(r"[ ,]+")
"""What separates items inside a brace: "one or more commas or spaces"."""


def _enumerated(contents: str, vocabulary: frozenset[str]) -> tuple[str, ...]:
    """The items a brace encloses, or ``()`` where it encloses anything else.

    The published pattern admits no separator before the first item or after the
    last, so ``{info,}`` and ``{,info}`` are malformed; splitting leaves an empty
    string at that end, which no vocabulary contains, and the whole entry is
    refused. An empty brace refuses by the same path.
    """
    items = tuple(_SEPARATOR.split(contents))
    if all(item in vocabulary for item in items):
        return items
    return ()


def points(entry: str) -> frozenset[Point]:
    """Every grid point ``entry`` covers, or nothing where it is not an entry.

    The three admitted shapes are a bare point (``create commitment``), one
    effect over braced kinds (``observe {info, record}``), and braced effects
    over one kind (``{create, modify} record``). A braced side is a cross product
    with the lone side, which is what makes one entry able to name several
    points.
    """
    matched = _ENTRY.match(entry)
    if matched is None:
        return frozenset()
    effect, kind, kinds, effects, lone_kind = matched.group(
        "effect", "kind", "kinds", "effects", "lone_kind"
    )
    if effect is not None:
        wanted = (kind,) if kind is not None else _enumerated(kinds or "", KINDS)
        if effect not in EFFECTS or any(one not in KINDS for one in wanted):
            return frozenset()
        return frozenset((effect, one) for one in wanted)
    if lone_kind not in KINDS:
        return frozenset()
    return frozenset((one, lone_kind) for one in _enumerated(effects or "", EFFECTS))


def covered(entries: Iterable[str]) -> frozenset[Point]:
    """Every point the grant reaches, over all of its entries.

    Entries are unioned because "within a single field, values are effectively
    ORed, meaning that any match is enough to satisfy that field". An entry this
    module cannot parse drops out of the union and takes nothing with it: it
    denies itself, never its siblings, because a grant is not falsified by one
    malformed line and widening on one would be the wrong direction anyway.
    """
    return frozenset[Point]().union(*(points(entry) for entry in entries))


def permits(entries: Iterable[str], required: Iterable[Point]) -> bool:
    """Whether the grant covers *every* point the act occupies.

    Coverage is total rather than partial because the schema says so: "An act is
    authorized only if EVERY (effect, state-kind) point it occupies is covered
    here", and its own example is filing a return, which is ``create record``
    *and* ``create commitment`` in one move. A grant covering one of them
    authorizes neither the move nor half of it.

    An act occupying no points at all is refused. That is not the vacuous answer
    set theory gives, and it is deliberate: an act that names no point has not
    said what it is, so authorizing it would authorize anything, and the
    fail-closed reading is the one this engine takes everywhere else.
    """
    wanted = frozenset(required)
    return bool(wanted) and wanted <= covered(entries)
