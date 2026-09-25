"""Meridian Bank's committed law, in the one state it has.

One clause, two officers, one act class, and two things the clause's arithmetic cannot
supply on its own: Meridian certifies its own decisions, and Meridian **obliges itself
to look** before it transacts.

The second is why this domain exists. A governed domain that never touched another one
would show that the engine is domain-agnostic and nothing more, and Daniel ruled on
2026-09-25 that a second domain is pointless unless it intersects the first, because
composability is the whole point of having one (``this.i`` @rc5fibel). So Meridian's law
names a diligence requirement, and an act of opening an account is not authorized until
Meridian has folded the customer's own record and found the customer's own governance
approved it.

**Nothing here names anything of Acme's.** Not a clause, not an identifier, not an act
class. The requirement is stated in Meridian's own terms — an evaluation seal satisfying
this schema — and which counterparty it turns out to be about is a property of the seal
rather than of the law. That is what keeps this clear of the portable clause language
``custos-4.2.md:2044`` defers, and it is the whole reason the beat is buildable.

The encoding is ``utina.domain.law``'s, the same one Acme's law commits through. What is
Meridian's own is what any domain's own law is: which acts its clause governs, who is
slotted, at what weight, and what it requires of itself beyond a count.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction

from utina.domain.law import CERTIFICATION_FIELD, clause, even, semantics_block
from utina.fold.diligence import REQUIRES_FIELD as DILIGENCE_FIELD
from utina.fold.semantics import SEMANTICS_FIELD
from utina.substrate import CERTIFICATION_SCHEMA, EVALUATION_SCHEMA

__all__ = [
    "ACCOUNT_ACTS",
    "CUSTOMER",
    "DILIGENCE_FIELD",
    "DISPLAY",
    "DOMAIN",
    "GAID",
    "GOVERNANCE_REGISTRY",
    "OFFICERS",
    "OPEN_ACCOUNT",
    "PRIYA",
    "TOMAS",
    "charter",
]

#: What ``--domain`` takes to select this record, and what its display cast is keyed by.
DOMAIN = "bank"

#: What a screen calls this domain.
DISPLAY = "Meridian Bank"

#: The governed domain. An *alias*, not an identifier, for the reason Acme's is
#: (this.i @crrtzf): under keripy a prefix is a digest of its own inception event and
#: cannot be named before it exists.
GAID = "bank:gaid"

#: Priya Raman and Tomas Alvarez, the two officers Meridian's credit committee seats.
#: Slotted as themselves, because this law entitles them directly. No office slot here:
#: Acme's record already carries the one case that needs one, and a second copy would
#: test the fixture rather than the fold.
PRIYA = "bank:priya"
TOMAS = "bank:tomas"

OFFICERS = (PRIYA, TOMAS)

#: What Meridian calls the customer whose record it holds. Not a party Meridian
#: incepted — the identifier is the customer's own gAID, and Meridian learns it by
#: doing business — but a party Meridian's screens name, which is the only thing an
#: alias ever is (this.i @cldspl). Without it the counterparty renders as a raw
#: identifier on the one screen built to show the two domains meeting.
CUSTOMER = "bank:customer"

#: The one act Meridian's law rules: opening an account for a customer. Named from
#: Meridian's side of the table, because that is whose act it is — Acme's own act, at
#: the other end, is ``open-bank-account`` and Meridian's law never mentions it.
OPEN_ACCOUNT = "open-customer-account"
ACCOUNT_ACTS = (OPEN_ACCOUNT,)

#: Meridian's own credential registry.
GOVERNANCE_REGISTRY = "meridian-governance"


def charter(aids: Mapping[str, str]) -> Mapping[str, object]:
    """Meridian's founding law, over the identifiers ``aids`` names.

    Two slots at a half apiece, so an account needs both officers — the smallest
    arrangement in which one signature is genuinely not enough, which is what leaves an
    act visibly pending for a reader.

    **Meridian certifies**, like Acme and by the same governance choice (this.i
    @2e2dncfe): an act is consequential when the domain records that its threshold was
    met, not when the last endorsement happens to exist.

    **And Meridian owes diligence**, which is this domain's reason to exist. The field
    names the schema an evaluation seal must satisfy, exactly as the field beside it
    names the schema a certification must satisfy, and for the same stated reason
    (``custos-4.2.md:1946-1951``): a requirement that could not say which evidence it
    wanted would be satisfiable by the wrong one. A law naming neither field authorizes
    its acts on arithmetic alone — Acme's does not name this one, and owes no diligence.

    Committed in this edition rather than assumed, for the reason every other term is:
    an amendment replaces the edition rather than adding to it (this.i @wg3jr6), so a
    successor dropping this field would be a Meridian that quietly stopped looking.
    """
    return {
        "clauses": (
            clause(
                "M1",
                ACCOUNT_ACTS,
                even([aids[alias] for alias in OFFICERS], Fraction(1, 2)),
            ),
        ),
        CERTIFICATION_FIELD: CERTIFICATION_SCHEMA,
        DILIGENCE_FIELD: EVALUATION_SCHEMA,
        SEMANTICS_FIELD: semantics_block(),
    }
