"""How a governed domain commits a clause, a group and a slot.

This is the encoding rather than anybody's law: a field-for-field image of the parsed
types in ``docs/interfaces.md``, which ``utina.fold.clause`` reads back. It lived in
``utina.acme.law`` while Acme was the only domain that had one, and moving it is the
same move as @s34hkwkv — a second domain writing its own encoder would be free to drift
from the interface in the one place a drift is invisible, since a law the fold cannot
parse fails loudly and a law it parses differently does not.

What each domain keeps for itself is its clauses: which acts they govern, who is
slotted, at what weight, and whether the domain certifies at all. Those are governance
choices. The bytes they commit as are not.

Weights are :class:`fractions.Fraction` and commit as exact rational strings, because
unity has to be decidable and a float would make it not (``this.i`` @qpqo3z).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from fractions import Fraction

from utina.fold.certification import REQUIRES_FIELD
from utina.fold.semantics import DOSSIER, DOSSIER_KEY
from utina.substrate import ENDORSEMENT_SCHEMA, GCD_SCHEMA

__all__ = [
    "CERTIFICATION_FIELD",
    "clause",
    "even",
    "seat_slot",
    "seated_by",
    "semantics_block",
    "slot",
]

#: Where a law names the schema its certifications must satisfy. The fold's own
#: field name, imported rather than spelled again here: a law that named the field
#: differently would require no certification at all, and would look on the page
#: exactly like one that did.
CERTIFICATION_FIELD = REQUIRES_FIELD


def slot(endorser: str, weight: Fraction) -> Mapping[str, object]:
    """One committed slot: who may act, and with how much weight.

    The weight commits as an exact rational **string** — ``"1/2"`` — which is
    ``docs/interfaces.md``'s shape for the law body and what ``utina.fold.clause``
    parses. It is written here rather than left to the encoder because the fold reads
    the committed value, not the committed bytes, and the two have to be the same
    thing. The bytes are unchanged either way: the canonical encoder writes a
    ``Fraction`` as ``"1/2"`` too, so no identifier moves.

    Every slot this builds names the dossier's endorsement schema, because every clause
    reached through here is discharged by endorsements. The field is committed rather
    than assumed (``custos-4.2.md:1946-1951``): a seat credential is a second ACDC kind,
    and a requirement that could not say which of the two it wanted would be satisfiable
    by the wrong one.

    A slot built here names a party the law entitles DIRECTLY, and so carries no
    qualification. A slot whose holder has to be standing on a credential is an office
    slot — :func:`seat_slot`, where the qualification is mandatory rather than optional
    (this.i @ftjpdph5).
    """
    return {
        "endorser": endorser,
        "weight": f"{weight.numerator}/{weight.denominator}",
        "schema": ENDORSEMENT_SCHEMA,
    }


def seat_slot(
    office: str, weight: Fraction, qualification: Mapping[str, object]
) -> Mapping[str, object]:
    """One committed slot that seats an OFFICE rather than naming a party.

    The difference from :func:`slot` is the whole of ``this.i`` @ftjpdph5, and it is
    one field: there is no ``endorser``, so the law commits no AID for this seat at
    all. Who fills it is read off the record — whoever holds a standing credential of
    the ``qualification`` seating them in ``office`` — which is what makes appointing
    a director an issuance rather than a constitutional amendment.

    A qualification is mandatory here and optional on a party slot, and that
    asymmetry is not an accident: a slot that named an office and required nothing to
    be standing on would be seated by anybody willing to claim the title. The fold
    refuses such a slot when it reads the law; committing one would be writing a
    defect for the fold to catch rather than not writing it.
    """
    return {
        "office": office,
        "weight": f"{weight.numerator}/{weight.denominator}",
        "schema": ENDORSEMENT_SCHEMA,
        "qualification": qualification,
    }


def clause(
    identifier: str, governs: Sequence[str], slots: Sequence[Mapping[str, object]]
) -> Mapping[str, object]:
    return {
        "id": identifier,
        "governs": tuple(governs),
        "group": {"operator": "MxN", "slots": tuple(slots)},  # ~5psg
    }


def even(endorsers: Sequence[str], weight: Fraction) -> tuple[Mapping[str, object], ...]:
    """Slots of equal weight, one per endorser the law entitles directly."""
    return tuple(slot(endorser, weight) for endorser in endorsers)


def seated_by(domain: str) -> Mapping[str, object]:
    """What an office slot's holder must be standing on: the domain's own GCD.

    Both terms are committed because §9 asks for both — "which schemas, issued by
    which registries, confer which powers" (custos-4.2.md:1924). The issuer is
    named rather than the registry because a registry's identifier is not known
    when the law that requires it is written: Acme opens its governance registry
    after the amendment that seats the board. Naming the issuer is the same
    restriction reached from the other side, and the fold resolves the registry
    out of the issuance itself.
    """
    return {"schema": GCD_SCHEMA, "issuer": domain}


def semantics_block() -> Mapping[str, object]:
    """What every edition of a law here pins, and why it pins anything.

    A composition rule expressed in the dossier specification's terms — its operator
    vocabulary, its slot shape, its three dispositions — makes that specification an
    external semantics, and axiom 4 (custos-4.2.md:290) requires an external semantics
    to be pinned by committed digest. An unrecognized or absent pin is refused by the
    fold rather than assumed at whatever revision happens to be installed
    (``utina.fold.semantics``, tick 2uhi).

    Committed in every edition rather than inherited from the first, for the reason a
    carried clause is re-committed in every edition: an amendment replaces the edition
    rather than adding to it (this.i @wg3jr6), so a term left out of a successor is a
    term that edition does not carry.
    """
    return {DOSSIER_KEY: DOSSIER}
