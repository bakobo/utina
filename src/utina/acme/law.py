"""Acme, Inc.'s committed law, in both of its states.

Expressed as Acme's own committed clause predicate in a structure isomorphic to
the dossier specification's threshold operators — same operator, slot and
weight shape, same unity threshold, same three dispositions — rather than as
real ACDC edge groups, for the reasons this.i @ta7vle sets out. The evidence
half moved to real credentials (this.i @7db5c4); this, the law half, is the
wide commission tick ~5psg tracks — real edge groups oblige the semantics pin
and the refusal machinery axiom 4 demands.

The encoding is a field-for-field image of the parsed types in
``docs/interfaces.md``: a clause carries ``id``, ``governs`` and ``group``; a
group carries ``operator`` and ``slots``; a slot carries ``endorser`` and
``weight`` (this.i @5ujoa2). Weights are :class:`fractions.Fraction` and commit
as exact rational strings, because unity has to be decidable and a float would
make it not.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from fractions import Fraction

#: The governed domain. An *alias*, not an identifier: under keripy a prefix is
#: a digest of its own inception event and cannot be named beforehand, so the law
#: below is a function of what inception returned rather than of these strings
#: (this.i @crrtzf). Under the facade the two coincide, which is exactly the
#: coincidence that made the seam look thinner than it was.
GAID = "acme:gaid"

#: Marta Reyes and Dev Patel, founders. Nina Adeyemi, outside director, seated
#: by the amendment at beat D4.
MARTA = "acme:marta"
DEV = "acme:dev"
NINA = "acme:nina"

FOUNDERS = (MARTA, DEV)
BOARD = (MARTA, DEV, NINA)

#: What the ordinary-acts clause rules. ``declare-dividend`` is deliberately
#: absent from every clause: beat D8 needs the law to be genuinely silent
#: somewhere, and a fold that refuses has to have something to refuse about.
ORDINARY_ACTS = ("open-bank-account", "hire-vp-sales", "approve-budget")

#: What the amendment clause rules.
AMENDMENT_ACTS = ("amend-operating-agreement",)

#: The act nothing governs.
UNGOVERNED_ACT = "declare-dividend"


def slot(endorser: str, weight: Fraction) -> Mapping[str, object]:
    """One committed slot: who may act, and the share of authority they hold.

    The weight commits as an exact rational **string** — ``"1/2"`` — which is
    ``docs/interfaces.md``'s shape for the law body and what
    ``utina.fold.clause`` parses. It is written here rather than left to the
    encoder because the fold reads the committed value, not the committed bytes,
    and the two have to be the same thing. The bytes are unchanged either way:
    the canonical encoder writes a ``Fraction`` as ``"1/2"`` too, so no
    identifier moves.
    """
    return {"endorser": endorser, "weight": f"{weight.numerator}/{weight.denominator}"}


def clause(
    identifier: str, governs: Sequence[str], slots: Sequence[Mapping[str, object]]
) -> Mapping[str, object]:
    return {
        "id": identifier,
        "governs": tuple(governs),
        "group": {"operator": "MxN", "slots": tuple(slots)},
    }


def _even(endorsers: Sequence[str], weight: Fraction) -> tuple[Mapping[str, object], ...]:
    return tuple(slot(endorser, weight) for endorser in endorsers)


def founding_law(aids: Mapping[str, str]) -> Mapping[str, object]:
    """State 1, from inception, over the identifiers ``aids`` names.

    Two slots at a half apiece in both clauses, so every decision needs both
    founders. ``aids`` maps each alias above to the identifier inception
    returned for it; a slot names an identifier, because an endorsement names
    one and the fold matches the two.
    """
    founders = [aids[alias] for alias in FOUNDERS]
    return {
        "clauses": (
            clause("A1", ORDINARY_ACTS, _even(founders, Fraction(1, 2))),
            clause("A2", AMENDMENT_ACTS, _even(founders, Fraction(1, 2))),
        ),
    }


def board_law(aids: Mapping[str, str]) -> Mapping[str, object]:
    """State 2, after the amendment seats the board, over the same identifiers.

    Ordinary authority is distributed — three slots at a half, so any two reach
    unity — and the authority to change the rules is not: three slots at a
    third, so all three are needed. That retained bar is the point of the demo.
    """
    board = [aids[alias] for alias in BOARD]
    return {
        "clauses": (
            clause("B1", ORDINARY_ACTS, _even(board, Fraction(1, 2))),
            clause("B2", AMENDMENT_ACTS, _even(board, Fraction(1, 3))),
        ),
        "seats": (aids[NINA],),
    }


#: Every party under the substrate whose identifier *is* its alias. The facade's
#: reading of the law above, and what the law constants below are built over.
ALIASES: Mapping[str, str] = {name: name for name in (GAID, MARTA, DEV, NINA)}

#: State 1 as the facade sees it, kept as a constant because the demo script and
#: the unit tests address Acme's founding clauses without building a domain.
FOUNDING_LAW: Mapping[str, object] = founding_law(ALIASES)

#: State 2 as the facade sees it.
BOARD_LAW: Mapping[str, object] = board_law(ALIASES)
