"""The four-valued codomain, with the ground as a component of each value's type.

Custos, ``custos-4.2.md:1502-1507``:

    Governance appraisal in a GARD returns exactly one type: the finding. A
    finding is a judgment over a committed regime that carries its own ground —
    the citation, requirement, or proof that justifies it. A value that does not
    carry its ground is not a member of this type, whatever else it may be.

That is why the grounds are checked in ``__post_init__`` and not by a validator a
caller may forget: a groundless finding is unconstructible here, and
``e.state.ground-missing.f`` is a typing failure rather than a validation result
(this.i @ppnadi). An engine that can return a bare verdict is the engine this one
must not be.

The four values and their grounds are at ``:1514-1533``; the ruled payloads at
``:1641-1660``; canonical selection among simultaneous defeats at ``:1766-1779``.

Four readings are pinned here, each with an entry in
``docs/custos-questions.md``:

- **affirmed carries a payload** (Q4 in ``custos-questions.md``). The payload
  enumeration presents itself as complete and omits affirmed, while ``:1516-1518``
  gives affirmed a ground — the evidence bundle and the clause set. The Ground
  Axiom outranks an enumeration that dropped a row.
- **species collates by the document's own enumeration order** (Q5), not by the
  bytes of its name, which would order ``expired/abandoned`` before ``window-open``.
- **a signed declination defeats under the authority class** (Q6). A threshold
  is a statement about who may act.
- **an empty subcode orders last** (Q7), though it is the lexicographic minimum
  the selection sentence asks for.

Refusal is deliberately **not** here, and is not a ``Finding``: see
``utina.fold.refusal`` and this.i @zztcbs.

Derived from bakobo/thesmo's ``m1-alpha`` reading of the same surface
(Apache-2.0, see NOTICE); the payloads are utina's contract, not alpha's, and
alpha read an edition whose sections were numbered differently.
"""

import dataclasses
from collections.abc import Iterable, Sequence
from enum import Enum
from typing import ClassVar, cast

from utina.fold.errors import GROUND_MISSING, MALFORMED_INPUT, require
from utina.fold.triple import AID, SAID

__all__ = [
    "Affirmed",
    "Citation",
    "Declination",
    "Defeated",
    "DefeaterClass",
    "Finding",
    "Pending",
    "PendingSpecies",
    "Proof",
    "RequirementElement",
    "SelfConvicted",
    "Verdict",
    "canonical_requirement_set",
    "select_defeat",
]


class Verdict(Enum):
    """The four values, and no fifth (``custos-4.2.md:1514-1533``)."""

    AFFIRMED = "affirmed"
    DEFEATED = "defeated"
    PENDING = "pending"
    SELF_CONVICTED = "self-convicted"


class DefeaterClass(Enum):
    """The defeater classes, "enumerated and ranked, in this order" (``:1771-1776``).

    The rank is the document's, which is deliberately not alphabetical: comparing
    the class names as bytes would put authority ahead of crypto and select a
    different defeat.
    """

    CRYPTO = (0, "a cryptographic verification failed")
    AUTHORITY = (1, "the actor lacked the invoked power")
    MERIT = (2, "the content violates a committed clause")
    SUPERSEDED = (3, "a later lawful act displaced the subject")

    @property
    def rank(self) -> int:
        return self.value[0]

    @property
    def gloss(self) -> str:
        return self.value[1]


class PendingSpecies(Enum):
    """The four discharge species and their cures (``:1560-1561``, ``:1575-1586``).

    Each carries the document's own enumeration rank, because the four-field
    canonical order ends in species (``:1650-1651``) and the document never says
    how one species compares to another — Q5.
    """

    ABSENT = (0, "absent", "cured by the arrival of the missing evidence")
    WINDOW_OPEN = (1, "window-open", "cured when no superseding event remains admissible")
    UNRESOLVED_CONFLICT = (
        2,
        "unresolved-conflict",
        "cured by an owned act of the party whose conflict it is",
    )
    EXPIRED_ABANDONED = (3, "expired/abandoned", "cured by re-presentation")

    @property
    def rank(self) -> int:
        return self.value[0]

    @property
    def name_(self) -> str:
        return self.value[1]

    @property
    def cure(self) -> str:
        return self.value[2]


def _identifier(value: object, field: str, expected: str) -> None:
    """An identifier is a non-empty string, and nothing else is one."""
    require(
        isinstance(value, str),
        MALFORMED_INPUT,
        field=field,
        expected=expected,
        found=repr(value),
    )


def _identifiers(values: object, field: str, expected: str) -> tuple[str, ...]:
    """A canonical, deduplicated tuple of identifiers, or a refusal."""
    require(
        isinstance(values, Iterable) and not isinstance(values, str | bytes),
        MALFORMED_INPUT,
        field=field,
        expected=expected,
        found=repr(values),
    )
    members = tuple(cast(Iterable[object], values))
    for member in members:
        _identifier(member, f"a member of {field}", expected)
        require(
            member != "",
            MALFORMED_INPUT,
            field=f"a member of {field}",
            expected=expected,
            found="an empty identifier",
        )
    return tuple(sorted(set(cast(tuple[str, ...], members))))


# --- the grounds -------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Declination:
    """A committed, signed no: the act that spends a slot."""

    endorser: AID
    said: SAID

    def __post_init__(self) -> None:
        for value, field in ((self.endorser, "endorser"), (self.said, "identifier")):
            _identifier(
                value, f"a declination's {field}", "the identifier of a committed party or act"
            )
            require(
                value != "",
                MALFORMED_INPUT,
                field=f"a declination's {field}",
                expected="the identifier of a committed party or act",
                found="an empty identifier",
            )


@dataclasses.dataclass(frozen=True)
class Citation:
    """What defeats a proposition, and under which class it defeats.

    ``:1641-1646`` rules both components: "A defeated finding SHALL carry its
    defeater class and its citation … Neither is reconstructible from a bare
    verdict." The class defaults to ``authority`` because the demo's defeats are
    thresholds that cannot reach unity, and a threshold is a statement about who
    may act — Q6, and this.i @jaabkd. A caller whose defeat is cryptographic,
    meritorious or superseding must say so; the default will not guess it right.

    ``subcode`` is "the defeat's discriminator within its citation, assigned by
    the cited clause's own committed enumeration" (``:1776-1779``); where the
    clause defines none it is empty.
    """

    clause: str
    declination: Declination | None = None
    reason: str = ""
    defeater_class: DefeaterClass = DefeaterClass.AUTHORITY
    subcode: str = ""

    def __post_init__(self) -> None:
        _identifier(
            self.clause, "a citation's clause", "the identifier of the clause that defeats"
        )
        require(
            self.clause != "",
            GROUND_MISSING,
            value="a citation",
            ground="the identifier of the clause that defeats",
        )
        require(
            self.declination is None or isinstance(self.declination, Declination),
            MALFORMED_INPUT,
            field="a citation's declination",
            expected="a committed Declination, or nothing where no signed no defeated it",
            found=repr(self.declination),
        )
        _identifier(self.reason, "a citation's reason", "prose, empty where none is offered")
        require(
            isinstance(self.defeater_class, DefeaterClass),
            MALFORMED_INPUT,
            field="a citation's defeater class",
            expected="one of crypto, authority, merit or superseded",
            found=repr(self.defeater_class),
        )
        _identifier(
            self.subcode,
            "a citation's subcode",
            "the cited clause's own discriminator, empty where it defines none",
        )

    def selection_key(self) -> tuple[int, str, bool, str]:
        """The canonical-selection key of ``:1766-1779``.

        The third component is Q7's repair: the sentence says an empty subcode
        "orders last", and an empty string is the lexicographic minimum, so the
        presence of a subcode has to be compared before the subcode itself.
        """
        return (self.defeater_class.rank, self.clause, self.subcode == "", self.subcode)


@dataclasses.dataclass(frozen=True)
class RequirementElement:
    """One element of a pending finding's typed requirement set.

    ``:1522-1526`` names the ground — "each element naming its requirement kind,
    its subject, and the clauses that make it required" — and ``:1647-1656`` rules
    the carriage, the four-field order and the deduplication key. ``kind`` and
    ``species`` default because Acme's only cure path is the arrival of a missing
    endorsement; an engine with a second one must say which (this.i @7wysgy).
    """

    endorser: AID
    clause: str
    kind: str = "endorsement"
    species: PendingSpecies = PendingSpecies.ABSENT

    def __post_init__(self) -> None:
        _identifier(
            self.endorser, "a requirement element's subject", "the identifier of the party"
        )
        require(
            self.endorser != "",
            MALFORMED_INPUT,
            field="a requirement element's subject",
            expected="the identifier of the party whose act would discharge it",
            found="an empty identifier",
        )
        _identifier(
            self.clause, "a requirement element's clause", "the identifier of the citing clause"
        )
        require(
            self.clause != "",
            GROUND_MISSING,
            value="a requirement element",
            ground="the citing clause that makes it required",
        )
        _identifier(self.kind, "a requirement element's kind", "the name of the requirement")
        require(
            self.kind != "",
            MALFORMED_INPUT,
            field="a requirement element's kind",
            expected="the name of the requirement, such as an endorsement",
            found="an empty name",
        )
        require(
            isinstance(self.species, PendingSpecies),
            MALFORMED_INPUT,
            field="a requirement element's discharge species",
            expected="one of absent, window-open, unresolved-conflict or expired/abandoned",
            found=repr(self.species),
        )

    def sort_key(self) -> tuple[str, str, bytes, int]:
        """"subject, then kind, then citing-clause bytes, then species" (``:1650-1651``)."""
        return (self.endorser, self.kind, self.clause.encode("utf-8"), self.species.rank)

    def dedup_key(self) -> tuple[str, str, bytes, int]:
        """The key "sees every field the element carries" (``:1652-1656``).

        Which is the sort key, exactly: elements differing only in species do not
        merge, and species is the fourth field of the order.
        """
        return self.sort_key()


@dataclasses.dataclass(frozen=True)
class Proof:
    """The canonical proof package identifying a contradictory pair (``:1659-1660``).

    The ruled payload is the package's identifier alone. ``pair`` is optional and
    carries the two contradicting identifiers where the caller has them, because
    a reader holding the finding should not have to fetch the package to see what
    contradicted what.
    """

    package: SAID
    pair: tuple[SAID, ...] = ()

    def __post_init__(self) -> None:
        _identifier(
            self.package, "a proof's package", "the identifier of the canonical proof package"
        )
        require(
            self.package != "",
            GROUND_MISSING,
            value="a proof of self-conviction",
            ground="the identifier of the canonical proof package for the contradictory pair",
        )
        pair = _identifiers(
            self.pair, "a proof's pair", "the identifiers of the two contradicting events"
        )
        require(
            len(pair) in (0, 2),
            MALFORMED_INPUT,
            field="a proof's pair",
            expected=(
                "two contradicting identifiers, or none where the package alone names them"
            ),
            found=f"{len(pair)} of them",
        )


# --- the codomain ------------------------------------------------------------


class Finding:
    """A judgment over a committed regime, carrying its ground.

    The base class has no verdict of its own, precisely so that a bare verdict
    cannot be built: the four values below are the whole codomain.
    """

    VERDICT: ClassVar[Verdict]

    def __init__(self) -> None:
        raise GROUND_MISSING(
            value="a bare finding",
            ground="one of the four grounds: affirmed, defeated, pending or self-convicted",
        )

    @property
    def verdict(self) -> Verdict:
        """Which of the four this value is. Only a value has one; the type has none."""
        return self.VERDICT


@dataclasses.dataclass(frozen=True)
class Affirmed(Finding):
    """The proposition holds over the committed evidence (``:1516-1518``).

    Ground: the clause set it was appraised under, the endorsements that reached
    unity, and the identity of the evidence bundle. The payload enumeration at
    ``:1641-1660`` omits affirmed; the Ground Axiom does not, and Q4 in
    ``docs/custos-questions.md`` records the gap.
    """

    clauses: tuple[str, ...]
    endorsements: tuple[SAID, ...]
    bundle: SAID

    VERDICT = Verdict.AFFIRMED

    def __post_init__(self) -> None:
        clauses = _identifiers(
            self.clauses, "an affirmation's clause set", "the identifier of a clause"
        )
        require(
            clauses != (),
            GROUND_MISSING,
            value="an affirmed finding",
            ground="the clause set it was appraised under",
        )
        endorsements = _identifiers(
            self.endorsements,
            "an affirmation's endorsements",
            "the identifier of a committed endorsement",
        )
        require(
            endorsements != (),
            GROUND_MISSING,
            value="an affirmed finding",
            ground="the endorsements that reached unity",
        )
        _identifier(
            self.bundle,
            "an affirmation's evidence bundle",
            "the identifier of the bundle it was appraised over",
        )
        require(
            self.bundle != "",
            GROUND_MISSING,
            value="an affirmed finding",
            ground="the identity of the evidence bundle it was appraised over",
        )
        object.__setattr__(self, "clauses", clauses)
        object.__setattr__(self, "endorsements", endorsements)


@dataclasses.dataclass(frozen=True)
class Defeated(Finding):
    """The proposition is defeated by committed evidence (``:1519-1521``).

    Ground: the citation of the defeating clause or superseding act, together
    with the defeater's class — both carried by ``Citation``.
    """

    citation: Citation

    VERDICT = Verdict.DEFEATED

    def __post_init__(self) -> None:
        require(
            self.citation is not None,
            GROUND_MISSING,
            value="a defeated finding",
            ground="the citation of the clause or act that defeats it",
        )
        require(
            isinstance(self.citation, Citation),
            MALFORMED_INPUT,
            field="a defeated finding's citation",
            expected="a Citation naming the clause and the defeater class",
            found=repr(self.citation),
        )


@dataclasses.dataclass(frozen=True)
class Pending(Finding):
    """The evidence neither affirms nor defeats; the finding names what is missing.

    Ground: the typed requirement set, deduplicated and in the canonical
    four-field order (``:1647-1656``). The invariant is checked here rather than
    assumed, so a set built by hand cannot be smuggled into a finding whose
    payload equality is supposed to be decidable;
    ``canonical_requirement_set`` is how one is built.
    """

    requirement: tuple[RequirementElement, ...]

    VERDICT = Verdict.PENDING

    def __post_init__(self) -> None:
        require(
            isinstance(self.requirement, Iterable)
            and not isinstance(self.requirement, str | bytes),
            MALFORMED_INPUT,
            field="a pending finding's requirement",
            expected="a sequence of typed requirement elements",
            found=repr(self.requirement),
        )
        elements = tuple(self.requirement)
        for member in elements:
            require(
                isinstance(member, RequirementElement),
                MALFORMED_INPUT,
                field="a member of a pending finding's requirement",
                expected="a RequirementElement carrying its subject, kind, clause and species",
                found=repr(member),
            )
        require(
            elements != (),
            GROUND_MISSING,
            value="a pending finding",
            ground="the typed requirement set that names what would discharge it",
        )
        keys = [member.sort_key() for member in elements]
        require(
            keys == sorted(keys),
            MALFORMED_INPUT,
            field="a pending finding's requirement",
            expected="the canonical order: subject, kind, citing-clause bytes, then species",
            found="a set in some other order — build it with canonical_requirement_set",
        )
        require(
            len(set(keys)) == len(keys),
            MALFORMED_INPUT,
            field="a pending finding's requirement",
            expected="deduplicated elements, one per committed requirement",
            found="two elements sharing a key — build it with canonical_requirement_set",
        )
        object.__setattr__(self, "requirement", elements)


@dataclasses.dataclass(frozen=True)
class SelfConvicted(Finding):
    """The subject's own committed bytes contain a contradiction (``:1527-1533``).

    Ground: the canonical proof package identifying the contradictory pair.
    """

    proof: Proof

    VERDICT = Verdict.SELF_CONVICTED

    def __post_init__(self) -> None:
        require(
            self.proof is not None,
            GROUND_MISSING,
            value="a self-convicted finding",
            ground="the canonical proof package for the contradictory pair",
        )
        require(
            isinstance(self.proof, Proof),
            MALFORMED_INPUT,
            field="a self-convicted finding's proof",
            expected="a Proof naming the canonical proof package",
            found=repr(self.proof),
        )


# --- building the grounds canonically ----------------------------------------


def canonical_requirement_set(
    elements: Iterable[RequirementElement],
) -> tuple[RequirementElement, ...]:
    """Deduplicate and order requirement elements as ``:1647-1656`` requires.

    The deduplication key sees every field the element carries, so two elements
    differing only in species do not merge: a party told that missing evidence
    would cure and a party told that a recovery window stands open have received
    materially different instructions from the same record.
    """
    merged = {member.dedup_key(): member for member in elements}
    return tuple(sorted(merged.values(), key=RequirementElement.sort_key))


def select_defeat(citations: Sequence[Citation]) -> Citation:
    """The one citation a defeated finding carries, where several are available.

    ``:1766-1770``: "the finding SHALL cite the lexicographic minimum of
    (defeater-class rank, citation identifier, subcode). Two verifiers holding
    the same bundle SHALL emit the same defeated finding down to the byte."

    Selecting from nothing is refused rather than answered with a sentinel: the
    set is computed before one is chosen, and an empty set means the caller
    reached this line without a defeat, which is a different finding entirely
    (``:1757-1765``).
    """
    require(
        len(citations) > 0,
        MALFORMED_INPUT,
        field="the set a defeat is selected from",
        expected="at least one citation, since selection presupposes a defeat",
        found="an empty set",
    )
    return min(citations, key=Citation.selection_key)
