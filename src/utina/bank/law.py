"""Meridian Bank's committed law, in the one state it has.

One clause, two officers, one act class, and a domain that certifies. That is the whole
of it, and the smallness is the design rather than an unfinished draft: this domain
exists so that ``--domain`` resolves something other than Acme, so that the fold can be
shown folding a record it was not written around, and so that a domain with **no label
table** is a case the suite actually covers (``this.i`` @qprzacju, @er57yvs7).

The encoding is ``utina.domain.law``'s, the same one Acme's law commits through. What is
Meridian's own is what any domain's own law is: which acts its clause governs, who is
slotted, at what weight, and that it certifies at all.

**This is not the bank beat.** The demo has wanted a two-constitution beat since the
certification plan — cross-domain ground, an evaluation-seal credential, Meridian folding
Acme's GEL and reading a certified result without reading Acme's clauses. That beat has
its own design, is agreed and is not built, and the session that builds it should treat
everything here as scaffolding it is free to replace rather than as a decision it has to
honour.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction

from utina.domain.law import CERTIFICATION_FIELD, clause, even, semantics_block
from utina.fold.semantics import SEMANTICS_FIELD
from utina.substrate import CERTIFICATION_SCHEMA

__all__ = [
    "CREDIT_ACTS",
    "DISPLAY",
    "DOMAIN",
    "GAID",
    "GOVERNANCE_REGISTRY",
    "OFFICERS",
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
#: Slotted as themselves, because this law entitles them directly and nothing here needs
#: an office slot — Acme's record already carries the one case that does, and a second
#: copy of it would test the fixture rather than the fold.
PRIYA = "bank:priya"
TOMAS = "bank:tomas"

OFFICERS = (PRIYA, TOMAS)

#: What Meridian's one clause rules. A second class is deliberately absent: an act class
#: the law is silent about is Acme's beat D8, and re-telling it here would be a second
#: fixture making the same point rather than a second domain making the flag true.
CREDIT_ACTS = ("approve-credit-line",)

#: Meridian's own credential registry. Opened and never issued into, which is honest
#: rather than incomplete: ``utina registry --domain bank`` shows a registry that has
#: conferred nothing, and a record with no registry at all would have put the string
#: ``None`` on that screen where an identifier belongs.
GOVERNANCE_REGISTRY = "meridian-governance"


def charter(aids: Mapping[str, str]) -> Mapping[str, object]:
    """Meridian's founding law, over the identifiers ``aids`` names.

    Two slots at a half apiece, so a credit line needs both officers. The same shape as
    Acme's founding clause and for the same reason — unity is the threshold, and two
    equal slots is the smallest arrangement where a single endorsement is genuinely not
    enough, which is what leaves an act pending for a reader to see.

    **Meridian certifies**, like Acme and by the same governance choice (this.i
    @2e2dncfe): an act is consequential when the domain records that its threshold was
    met, not when the last endorsement happens to exist. Stated in its committed law
    rather than inherited from anywhere, because a domain that did not say so would
    authorize every act under it on arithmetic alone.
    """
    return {
        "clauses": (
            clause(
                "M1",
                CREDIT_ACTS,
                even([aids[alias] for alias in OFFICERS], Fraction(1, 2)),
            ),
        ),
        CERTIFICATION_FIELD: CERTIFICATION_SCHEMA,
        SEMANTICS_FIELD: semantics_block(),
    }
