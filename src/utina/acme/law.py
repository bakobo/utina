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

from utina.substrate import ENDORSEMENT_SCHEMA

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

#: Board seat 3: the *office*, a delegated identifier of the domain rather than
#: a person. Nina holds its keys; the seat is what the law slots and what the
#: seat credential is issued to, so a director leaving is a rotation on the seat
#: and not a reissued credential (custos-4.2.md:2139-2148, this.i @2a25xudi).
SEAT = "acme:seat3"

#: The device Nina signs from, delegated from the *seat* rather than from Nina or
#: from the domain. It fills seat 3's slot because the seat granted it authority
#: to, in a GCD the seat issued and can revoke — never because the delegation
#: exists, which proves a relationship and confers nothing (this.i @cglayqvw).
DEVICE = "acme:nina-device"

#: What the seat's grant to its device calls the relationship. Descriptive: the
#: published rules make ``constraints`` the whole of the authorization decision,
#: so this tells a reader what the grant is for and gates nothing.
DEVICE_ROLE = "board-seat-3-device"

#: The office the seat credential names, in Acme's own vocabulary. A label for a
#: reader; nothing computes over it, because what the law slots is the seat's
#: identifier.
SEAT_OFFICE = "board-seat-3"

#: Acme's own credential registry, through which a standing-conferring
#: credential is revocable (custos-4.2.md:1420-1422).
GOVERNANCE_REGISTRY = "acme-governance"

#: Board seat 3's own registry, through which the seat revokes what the seat
#: granted. Separate from the domain's because a transaction log takes its
#: authorization from the identifier that controls it, and because revocation
#: authority ought to follow the party whose authority was conferred.
SEAT_REGISTRY = "acme-seat3"

#: What board seat 3's grant lets its holder do, over the GCD act grid: create a
#: commitment. An endorsement and a declination are both exactly that — a party
#: committing itself for or against a tabled act — and the seat's authority under
#: Acme's law reaches nothing else, so the grant says nothing else. Every other
#: constraint dimension is deliberately absent: GCD's rule 1 makes an
#: unrecognized key inside ``constraints`` fail-closed, so a dimension utina's
#: fold cannot evaluate must not be written for it to skip (this.i @cglayqvw).
SEAT_ACTS = ("create commitment",)

FOUNDERS = (MARTA, DEV)

#: Who the board law slots: the two founders and the *seat*, never the director
#: who holds its keys (this.i @z373ew7j).
BOARD = (MARTA, DEV, SEAT)

#: What the ordinary-acts clause rules, in the order the record tables them.
#: ``declare-dividend`` is deliberately absent from every clause: one beat needs
#: the law to be genuinely silent somewhere, and a fold that refuses has to have
#: something to refuse about. The office lease is here to carry a declination
#: that used to stand against the hire, which has to stay pending across the
#: amendment (this.i @4tcsbw72).
ORDINARY_ACTS = (
    "open-bank-account",
    "hire-vp-sales",
    "sign-office-lease",
    "approve-budget",
)

#: What the amendment clause rules.
AMENDMENT_ACTS = ("amend-operating-agreement",)

#: What the founders' own clause rules, and the one act class no other clause
#: reaches. Escrowed founder equity is a founders' matter by construction:
#: seating a board distributes ordinary authority and the authority to amend, and
#: deliberately does not reach the equity the founders escrowed between
#: themselves. That is why A3 can be carried across the amendment unchanged for a
#: reason rather than as a fixture's control (this.i @rwo55zyw).
EQUITY_ACTS = ("release-escrowed-equity",)

#: The name the record files the Q2 forecast under. A second act of the budget
#: class rather than a class of its own: beats 13 to 15 turn on two tablings of
#: one kind of decision, not on two kinds, and giving it its own class would put
#: a clause in the law for a fixture's convenience.
Q2_FORECAST = "approve-q2-forecast"

#: The act nothing governs.
UNGOVERNED_ACT = "declare-dividend"


def slot(endorser: str, weight: Fraction) -> Mapping[str, object]:
    """One committed slot: who may act, with how much weight, and with what evidence.

    The weight commits as an exact rational **string** — ``"1/2"`` — which is
    ``docs/interfaces.md``'s shape for the law body and what
    ``utina.fold.clause`` parses. It is written here rather than left to the
    encoder because the fold reads the committed value, not the committed bytes,
    and the two have to be the same thing. The bytes are unchanged either way:
    the canonical encoder writes a ``Fraction`` as ``"1/2"`` too, so no
    identifier moves.

    Every slot of Acme's law names the dossier's endorsement schema, because
    every clause here is discharged by endorsements. The field is committed
    rather than assumed (``custos-4.2.md:1946-1951``): the seat credential is a
    second ACDC kind, and a requirement that could not say which of the two it
    wanted would be satisfiable by the wrong one.
    """
    return {
        "endorser": endorser,
        "weight": f"{weight.numerator}/{weight.denominator}",
        "schema": ENDORSEMENT_SCHEMA,
    }


def clause(
    identifier: str, governs: Sequence[str], slots: Sequence[Mapping[str, object]]
) -> Mapping[str, object]:
    return {
        "id": identifier,
        "governs": tuple(governs),
        "group": {"operator": "MxN", "slots": tuple(slots)},  # ~5psg
    }


def _even(endorsers: Sequence[str], weight: Fraction) -> tuple[Mapping[str, object], ...]:
    return tuple(slot(endorser, weight) for endorser in endorsers)


def equity_clause(aids: Mapping[str, str]) -> Mapping[str, object]:
    """A3, the founders' own clause, built once and committed in both editions.

    The point of the clause is that an amendment does not move it, and a clause
    is its bytes — each is independently SAID-addressed (custos-4.2.md:1483), so
    re-committing these bytes re-commits the same clause with the same
    identifier. Both editions build it through this one function so that the two
    sites cannot drift: an edit here changes A3 in edition 1 and edition 2
    together, or it changes neither, which is the only way the identity claim
    stays true under maintenance (this.i @rwo55zyw).
    """
    return clause(
        "A3", EQUITY_ACTS, _even([aids[alias] for alias in FOUNDERS], Fraction(1, 2))
    )


def founding_law(aids: Mapping[str, str]) -> Mapping[str, object]:
    """State 1, from inception, over the identifiers ``aids`` names.

    Two slots at a half apiece in all three clauses, so every decision needs
    both founders. ``aids`` maps each alias above to the identifier inception
    returned for it; a slot names an identifier, because an endorsement names
    one and the fold matches the two.
    """
    founders = [aids[alias] for alias in FOUNDERS]
    return {
        "clauses": (
            clause("A1", ORDINARY_ACTS, _even(founders, Fraction(1, 2))),
            clause("A2", AMENDMENT_ACTS, _even(founders, Fraction(1, 2))),
            equity_clause(aids),
        ),
    }


def board_law(aids: Mapping[str, str]) -> Mapping[str, object]:
    """State 2, after the amendment seats the board, over the same identifiers.

    Ordinary authority is distributed — three slots at a half, so any two reach
    unity — and the authority to change the rules is not: three slots at a
    third, so all three are needed. That retained bar is the point of the demo.

    The third slot is board seat 3, an office, and not Nina, who holds its keys.
    A law that slotted the officer would say a governance power attaches to a
    person; under the office, a director leaving is a rotation on the seat and
    the law does not move at all (this.i @z373ew7j).

    A3 is re-committed last and unchanged. An amendment replaces the edition
    rather than adding to it (this.i @wg3jr6), so a clause that does not change
    is re-committed rather than left implicitly in force; carrying its bytes is
    what makes it the same clause afterwards rather than a new one that resembles
    it.
    """
    board = [aids[alias] for alias in BOARD]
    return {
        "clauses": (
            clause("B1", ORDINARY_ACTS, _even(board, Fraction(1, 2))),
            clause("B2", AMENDMENT_ACTS, _even(board, Fraction(1, 3))),
            equity_clause(aids),
        ),
        "seats": (aids[SEAT],),
    }


#: Every party under the substrate whose identifier *is* its alias. The facade's
#: reading of the law above, and what the law constants below are built over.
ALIASES: Mapping[str, str] = {name: name for name in (GAID, MARTA, DEV, NINA, SEAT)}

#: State 1 as the facade sees it, kept as a constant because the demo script and
#: the unit tests address Acme's founding clauses without building a domain.
FOUNDING_LAW: Mapping[str, object] = founding_law(ALIASES)

#: State 2 as the facade sees it.
BOARD_LAW: Mapping[str, object] = board_law(ALIASES)
