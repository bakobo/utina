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

from utina.fold.certification import REQUIRES_FIELD
from utina.fold.semantics import DOSSIER, DOSSIER_KEY, SEMANTICS_FIELD
from utina.substrate import CERTIFICATION_SCHEMA, ENDORSEMENT_SCHEMA, GCD_SCHEMA

#: Where a law names the schema its certifications must satisfy. The fold's own
#: field name, imported rather than spelled again here: a law that named the field
#: differently would require no certification at all, and would look on the page
#: exactly like one that did.
CERTIFICATION_FIELD = REQUIRES_FIELD

#: The governed domain. An *alias*, not an identifier: under keripy a prefix is
#: a digest of its own inception event and cannot be named beforehand, so the law
#: below is a function of what inception returned rather than of these strings
#: (this.i @crrtzf). Under the facade the two coincide, which is exactly the
#: coincidence that made the seam look thinner than it was.
GAID = "acme:gaid"

#: Marta Reyes and Dev Patel, founders.
MARTA = "acme:marta"
DEV = "acme:dev"

#: Board seat 3, held by Nina Adeyemi, the outside director the amendment seats at
#: beat D4. **The AID is hers**, dedicated to that capacity and to nothing else —
#: custos-4.2.md:2145 requires the seat credential to name "the organ's AID as
#: issuee", and the organ's AID is one its holder owns in that role. Nina has other
#: AIDs for the other facets of her life and none of them is this record's business.
#: Under the previous reading the seat was Acme's own, which left no accountable human
#: anywhere in the log and attached duplicity to an abstraction.
SEAT = "acme:seat3"

#: Quinn Okafor, Acme's chief financial officer. Senior on purpose: beat 14 refuses
#: his endorsement of a budget act, and a refusal only teaches something when the
#: refused party had a plausible claim. A stranger being turned away surprises nobody;
#: a CFO who cannot approve the budget makes a room ask why, and the answer — he
#: prepares it, the board approves it — is the distinction the beat exists to draw.
#: He holds no seat, so the endorsement he offers citing the seat credential is
#: refused by edge validation before any fold runs.
QUINN = "acme:quinn"

#: The device Nina signs from, delegated from her seat AID. It fills seat 3's slot
#: because the seat granted it authority to, in a GCD the seat issued and can revoke
#: — never because the delegation exists, which proves a relationship and confers
#: nothing (this.i @cglayqvw).
DEVICE = "acme:nina-device"

#: What the seat's grant to its device calls the relationship. Descriptive: the
#: published rules make ``constraints`` the whole of the authorization decision,
#: so this tells a reader what the grant is for and gates nothing.
DEVICE_ROLE = "board-seat-3-device"

#: The office the seat credential names, in Acme's own vocabulary, and what the
#: board law's third slot SEATS. The law creates the seat and a credential fills it
#: (this.i @ftjpdph5), so this is no longer a label a reader interprets: it is in the
#: clause's committed bytes, and the fold resolves it to whoever holds a standing
#: seating credential for it. Appointing a director is therefore an issuance and
#: removing one a revocation, and neither is an amendment.
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

#: The name the record files the Q3 budget under. A third act of the budget
#: class, tabled after the seat credential is revoked, so that beat 17 asks a new
#: question over a bundle the revocation is already in.
Q3_BUDGET = "approve-q3-budget"

#: The name the record files the capital plan under. A fourth act of the budget
#: class, on the same reasoning as the two above: beats 21 to 23 turn on there
#: being TWO questions pending under B1 at once, which is a fact about how many
#: acts are in flight and not about how many classes the law rules.
CAPITAL_PLAN = "approve-capital-plan"

#: The nonce that makes the re-seating a NEW credential rather than the revoked
#: one presented again. A revoked credential cannot be reissued — two credentials
#: with the same issuer, schema, attributes and datetime are the same credential,
#: and a conforming transaction log refuses the duplicate, which keripy does by
#: name. A fresh appointment is a fresh credential, and ACDC's salty nonce is
#: what makes it one. Pinned rather than generated, like the salt and the
#: registry nonce, because a generated one would end the replay claim.
RESEATING_NONCE = "0AB1dGluYS1yZXNlYXQtMDAx"

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

    Every slot this builds names a party the law entitles DIRECTLY, and so carries no
    qualification: Acme's founders are slotted as themselves and nothing but the law
    qualifies them. The one slot whose holder had to be standing on a credential was
    board seat 3's, and it is an office slot now — :func:`seat_slot`, where the
    qualification is mandatory rather than optional (this.i @ftjpdph5).
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


def _even(endorsers: Sequence[str], weight: Fraction) -> tuple[Mapping[str, object], ...]:
    """Slots of equal weight, one per endorser the law entitles directly."""
    return tuple(slot(endorser, weight) for endorser in endorsers)


def _board_slots(aids: Mapping[str, str], weight: Fraction) -> tuple[Mapping[str, object], ...]:
    """The board's three slots at ``weight`` apiece: two founders and one office.

    The founders are slotted as themselves because the law entitles them directly;
    board seat 3 is slotted as an OFFICE, filled by whoever holds Acme's own seating
    credential for it. Built here rather than at each edition so that the two
    editions cannot drift in the one place where a drift would be invisible — B1 and
    B2 differ only in their weights, and a third slot that differed in anything else
    would be two different seats wearing one name.
    """
    founders = _even([aids[alias] for alias in FOUNDERS], weight)
    return (*founders, seat_slot(SEAT_OFFICE, weight, seated_by(aids[GAID])))


def seated_by(domain: str) -> Mapping[str, object]:
    """What board seat 3's holder must be standing on: the domain's own GCD.

    Both terms are committed because §9 asks for both — "which schemas, issued by
    which registries, confer which powers" (custos-4.2.md:1924). The issuer is
    named rather than the registry because a registry's identifier is not known
    when the law that requires it is written: Acme opens its governance registry
    after the amendment that seats the board. Naming the issuer is the same
    restriction reached from the other side, and the fold resolves the registry
    out of the issuance itself.
    """
    return {"schema": GCD_SCHEMA, "issuer": domain}


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


def semantics_block() -> Mapping[str, object]:
    """What every edition of Acme's law pins, and why it pins anything.

    Acme's composition rule is expressed in the dossier specification's terms —
    its operator vocabulary, its slot shape, its three dispositions — so that
    specification is an external semantics, and axiom 4 (custos-4.2.md:290)
    requires an external semantics to be pinned by committed digest. An
    unrecognized or absent pin is refused by the fold rather than assumed at
    whatever revision happens to be installed (utina.fold.semantics, tick 2uhi).

    Committed in every edition rather than inherited from the first, for the
    reason A3 is re-committed in every edition: an amendment replaces the edition
    rather than adding to it (this.i @wg3jr6), so a term left out of a successor
    is a term that edition does not carry.
    """
    return {DOSSIER_KEY: DOSSIER}


def founding_law(aids: Mapping[str, str]) -> Mapping[str, object]:
    """State 1, from inception, over the identifiers ``aids`` names.

    Two slots at a half apiece in all three clauses, so every decision needs
    both founders. ``aids`` maps each alias above to the identifier inception
    returned for it; a slot names an identifier, because an endorsement names
    one and the fold matches the two.

    **Acme certifies from inception**, in this edition and both successors. A
    decision is consequential when the domain records that its threshold was met,
    not when the last endorsement happens to exist (this.i @2e2dncfe), and whether a
    domain works that way is a governance choice its law has to state. Committed in
    every edition rather than inherited from the first, for the same reason A3 and
    the semantics pin are: an amendment replaces the edition rather than adding to
    it, so a term left out of a successor is a term that successor does not carry —
    and a successor that silently dropped this one would quietly authorize every act
    under it on arithmetic alone.
    """
    founders = [aids[alias] for alias in FOUNDERS]
    return {
        "clauses": (
            clause("A1", ORDINARY_ACTS, _even(founders, Fraction(1, 2))),
            clause("A2", AMENDMENT_ACTS, _even(founders, Fraction(1, 2))),
            equity_clause(aids),
        ),
        CERTIFICATION_FIELD: CERTIFICATION_SCHEMA,
        SEMANTICS_FIELD: semantics_block(),
    }


def board_law(aids: Mapping[str, str]) -> Mapping[str, object]:
    """State 2, after the amendment seats the board, over the same identifiers.

    Ordinary authority is distributed — three slots at a half, so any two reach
    unity — and the authority to change the rules is not: three slots at a
    third, so all three are needed. That retained bar is the point of the demo.

    The third slot names the OFFICE of board seat 3 and no identifier at all — not
    the seat's, and not Nina's, who holds its keys. The law creates the seat; a
    credential fills it (this.i @ftjpdph5). Under the previous reading the slot named
    the seat's AID, which still welded personnel to law one step removed: seating a
    different director would have moved a clause, and with it the law head. Now
    appointing one is an issuance and removing one is a revocation, and neither
    touches the law (this.i @z373ew7j, @ftjpdph5).

    A3 is re-committed last and unchanged. An amendment replaces the edition
    rather than adding to it (this.i @wg3jr6), so a clause that does not change
    is re-committed rather than left implicitly in force; carrying its bytes is
    what makes it the same clause afterwards rather than a new one that resembles
    it.
    """
    return {
        "clauses": (
            clause("B1", ORDINARY_ACTS, _board_slots(aids, Fraction(1, 2))),
            clause("B2", AMENDMENT_ACTS, _board_slots(aids, Fraction(1, 3))),
            equity_clause(aids),
        ),
        CERTIFICATION_FIELD: CERTIFICATION_SCHEMA,
        SEMANTICS_FIELD: semantics_block(),
    }


def lowered_law(aids: Mapping[str, str]) -> Mapping[str, object]:
    """State 3, after the second amendment lowers the ordinary-acts bar.

    B1's three slots keep their endorsers and take a full share each, so any one
    of them reaches unity where two were needed before. That is the whole change:
    B2's retained bar and A3's founders' clause are re-committed byte-identical,
    for the reason edition 2 re-commits A3 — an amendment replaces the edition
    rather than adding to it (this.i @wg3jr6).

    It is a real change to B1, so every question in flight under B1 has its cure
    path closed by it, which is what makes beat 23's computed disturbance set
    contain BOTH pending questions. The amendment declares only one of them.
    """
    return {
        "clauses": (
            clause("B1", ORDINARY_ACTS, _board_slots(aids, Fraction(1, 1))),
            clause("B2", AMENDMENT_ACTS, _board_slots(aids, Fraction(1, 3))),
            equity_clause(aids),
        ),
        CERTIFICATION_FIELD: CERTIFICATION_SCHEMA,
        SEMANTICS_FIELD: semantics_block(),
    }


#: Every party under the substrate whose identifier *is* its alias. The facade's
#: reading of the law above, and what the law constants below are built over.
ALIASES: Mapping[str, str] = {name: name for name in (GAID, MARTA, DEV, SEAT)}

#: State 1 as the facade sees it, kept as a constant because the demo script and
#: the unit tests address Acme's founding clauses without building a domain.
FOUNDING_LAW: Mapping[str, object] = founding_law(ALIASES)

#: State 2 as the facade sees it.
BOARD_LAW: Mapping[str, object] = board_law(ALIASES)
