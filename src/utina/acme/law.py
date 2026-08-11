"""Acme, Inc.'s committed law, in both of its states.

Expressed as Acme's own committed clause predicate in a structure isomorphic to
the dossier specification's threshold operators — same operator, slot and
weight shape, same unity threshold, same three dispositions — rather than as
real ACDC edge groups, for the reasons this.i @ta7vle sets out. When the keripy
commission swaps the encoding, the substrate changes and the fold does not.

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

#: The governed domain.
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
    return {"endorser": endorser, "weight": weight}


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


#: State 1, from inception. Two slots at a half apiece in both clauses, so every
#: decision needs both founders.
FOUNDING_LAW: Mapping[str, object] = {
    "clauses": (
        clause("A1", ORDINARY_ACTS, _even(FOUNDERS, Fraction(1, 2))),
        clause("A2", AMENDMENT_ACTS, _even(FOUNDERS, Fraction(1, 2))),
    ),
}

#: State 2, after the amendment seats the board. Ordinary authority is
#: distributed — three slots at a half, so any two reach unity — and the
#: authority to change the rules is not: three slots at a third, so all three
#: are needed. That retained bar is the point of the demo.
BOARD_LAW: Mapping[str, object] = {
    "clauses": (
        clause("B1", ORDINARY_ACTS, _even(BOARD, Fraction(1, 2))),
        clause("B2", AMENDMENT_ACTS, _even(BOARD, Fraction(1, 3))),
    ),
    "seats": (NINA,),
}
