"""The four-valued codomain, and the ground that is part of each value's type.

The tests that matter here are the ones that try to build a finding without its
ground and are refused. Custos: "A finding is a judgment over a committed regime
that carries its own ground — the citation, requirement, or proof that justifies
it. A value that does not carry its ground is not a member of this type, whatever
else it may be" (``custos-4.2.md:1504-1507``). An engine that returns bare
verdicts is precisely the engine utina must not be, so groundlessness is a
construction failure and not a validation result a caller may ignore.

Two pins are exercised here and logged as guesses in
``docs/questions-codomain.md``: species collates by the document's own
enumeration order (QC1), and an empty subcode sorts after every non-empty one
(QC3) even though it is the lexicographic minimum.
"""

import dataclasses

import pytest
from bakobo.errors import BakoboError

from utina.fold.finding import (
    Affirmed,
    Citation,
    Declination,
    Defeated,
    DefeaterClass,
    Finding,
    Pending,
    PendingSpecies,
    Proof,
    RequirementElement,
    SelfConvicted,
    Verdict,
    canonical_requirement_set,
    select_defeat,
)


def affirmed() -> Affirmed:
    return Affirmed(clauses=("A1",), endorsements=("EEnd1", "EEnd2"), bundle="EBundle1")


def element(endorser: str = "acme:dev", clause: str = "A1") -> RequirementElement:
    return RequirementElement(endorser=endorser, clause=clause)


# --- The type itself ---------------------------------------------------------


def test_the_codomain_has_four_values_and_no_fifth() -> None:
    assert {v.value for v in Verdict} == {"affirmed", "defeated", "pending", "self-convicted"}
    assert len(Verdict) == 4


def test_the_bare_type_is_not_a_value_and_cannot_be_built() -> None:
    """``Finding`` is the type; a bare verdict is what the Ground Axiom excludes."""
    with pytest.raises(BakoboError) as raised:
        Finding()
    assert raised.value.is_exactly("e.state.ground-missing.f")
    assert "affirmed" in str(raised.value)


@pytest.mark.parametrize(
    ("finding", "verdict"),
    [
        (affirmed(), Verdict.AFFIRMED),
        (Defeated(citation=Citation(clause="A1")), Verdict.DEFEATED),
        (Pending(requirement=(element(),)), Verdict.PENDING),
        (SelfConvicted(proof=Proof(package="EProof1")), Verdict.SELF_CONVICTED),
    ],
    ids=lambda v: getattr(v, "value", type(v).__name__),
)
def test_every_value_is_a_finding_and_knows_its_verdict(
    finding: Finding, verdict: Verdict
) -> None:
    assert isinstance(finding, Finding)
    assert finding.verdict is verdict


def test_findings_are_frozen_and_compare_by_value() -> None:
    """Two evaluations of the same triple return equal findings (:1631-1634)."""
    assert affirmed() == affirmed()
    assert len({affirmed(), affirmed()}) == 1
    with pytest.raises(dataclasses.FrozenInstanceError):
        affirmed().bundle = "EOther"  # type: ignore[misc]


# --- affirmed ----------------------------------------------------------------


def test_affirmed_carries_the_clause_set_the_endorsements_and_the_bundle() -> None:
    """Custos Q4's pin: the enumeration forgets affirmed, the Ground Axiom does not."""
    finding = affirmed()
    assert finding.clauses == ("A1",)
    assert finding.endorsements == ("EEnd1", "EEnd2")
    assert finding.bundle == "EBundle1"


def test_affirmed_canonicalizes_its_clause_set_and_its_endorsements() -> None:
    """Committed order is the corpus's; the ground's own order is ours to fix."""
    finding = Affirmed(
        clauses=("B1", "A1", "A1"), endorsements=("EB", "EA", "EB"), bundle="EBundle1"
    )
    assert finding.clauses == ("A1", "B1")
    assert finding.endorsements == ("EA", "EB")


@pytest.mark.parametrize(
    ("clauses", "endorsements", "bundle", "ground"),
    [
        ((), ("EEnd1",), "EBundle1", "the clause set"),
        (("A1",), (), "EBundle1", "the endorsements"),
        (("A1",), ("EEnd1",), "", "the identity of the evidence bundle"),
    ],
    ids=["no-clauses", "no-endorsements", "no-bundle"],
)
def test_an_affirmation_without_its_ground_is_not_constructible(
    clauses: tuple[str, ...], endorsements: tuple[str, ...], bundle: str, ground: str
) -> None:
    with pytest.raises(BakoboError) as raised:
        Affirmed(clauses=clauses, endorsements=endorsements, bundle=bundle)
    assert raised.value.is_exactly("e.state.ground-missing.f")
    assert ground in str(raised.value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"clauses": ("",), "endorsements": ("EEnd1",), "bundle": "EBundle1"},
        {"clauses": (1,), "endorsements": ("EEnd1",), "bundle": "EBundle1"},
        {"clauses": ("A1",), "endorsements": ("",), "bundle": "EBundle1"},
        {"clauses": ("A1",), "endorsements": ("EEnd1",), "bundle": 7},
    ],
    ids=["empty-clause", "clause-not-text", "empty-endorsement", "bundle-not-text"],
)
def test_an_affirmation_refuses_a_ground_that_is_not_an_identifier(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(BakoboError) as raised:
        Affirmed(**kwargs)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")


# --- defeated ----------------------------------------------------------------


def test_defeated_carries_a_citation_naming_the_clause_that_defeats_it() -> None:
    citation = Citation(
        clause="A1",
        declination=Declination(endorser="acme:dev", said="EDecline1"),
        reason="the second slot is spent, so unity is unreachable",
    )
    finding = Defeated(citation=citation)
    assert finding.citation.clause == "A1"
    assert finding.citation.declination is not None
    assert finding.citation.declination.endorser == "acme:dev"


def test_a_defeat_defaults_to_the_authority_class_and_says_so_where_it_matters() -> None:
    """QC2's pin: a threshold that cannot reach unity is a power not conferred."""
    assert Citation(clause="A1").defeater_class is DefeaterClass.AUTHORITY
    assert DefeaterClass.CRYPTO.rank < DefeaterClass.AUTHORITY.rank
    assert DefeaterClass.AUTHORITY.rank < DefeaterClass.MERIT.rank
    assert DefeaterClass.MERIT.rank < DefeaterClass.SUPERSEDED.rank
    assert "power" in DefeaterClass.AUTHORITY.gloss


def test_a_defeat_without_a_citation_is_not_constructible() -> None:
    with pytest.raises(BakoboError) as raised:
        Defeated(citation=None)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.state.ground-missing.f")
    assert "citation" in str(raised.value)


def test_a_defeat_refuses_a_citation_that_is_not_one() -> None:
    with pytest.raises(BakoboError) as raised:
        Defeated(citation="A1")  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")


def test_a_citation_that_names_no_clause_is_not_a_ground() -> None:
    with pytest.raises(BakoboError) as raised:
        Citation(clause="")
    assert raised.value.is_exactly("e.state.ground-missing.f")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"clause": 1},
        {"clause": "A1", "declination": "acme:dev"},
        {"clause": "A1", "reason": 7},
        {"clause": "A1", "defeater_class": "authority"},
        {"clause": "A1", "subcode": 7},
    ],
    ids=["clause", "declination-not-one", "reason-not-text", "class-not-one", "subcode"],
)
def test_a_citation_refuses_a_component_that_is_not_what_it_claims(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(BakoboError) as raised:
        Citation(**kwargs)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")


@pytest.mark.parametrize(
    "kwargs",
    [{"endorser": "", "said": "EDecline1"}, {"endorser": "acme:dev", "said": ""}],
    ids=["no-endorser", "no-said"],
)
def test_a_declination_names_both_the_endorser_and_the_committed_act(
    kwargs: dict[str, str],
) -> None:
    with pytest.raises(BakoboError) as raised:
        Declination(**kwargs)
    assert raised.value.is_exactly("e.input.malformed.f")


# --- canonical selection (:1766-1779) ----------------------------------------


def test_the_lowest_ranked_defeater_class_is_cited_first() -> None:
    crypto = Citation(clause="B2", defeater_class=DefeaterClass.CRYPTO)
    merit = Citation(clause="A1", defeater_class=DefeaterClass.MERIT)
    assert select_defeat([merit, crypto]) is crypto


def test_within_a_class_the_citation_identifier_decides() -> None:
    first = Citation(clause="A1")
    second = Citation(clause="B2")
    assert select_defeat([second, first]) is first


def test_an_empty_subcode_orders_last_though_it_is_the_lexicographic_minimum() -> None:
    """QC3: :1778-1779 says "orders last", and :1767-1769 would put it first."""
    bare = Citation(clause="A1")
    coded = Citation(clause="A1", subcode="b")
    assert select_defeat([bare, coded]) is coded
    assert select_defeat([coded, Citation(clause="A1", subcode="a")]).subcode == "a"


def test_selecting_from_no_defeats_at_all_is_refused() -> None:
    """A fold that stops at its first defeat computes the set first (:1757-1765)."""
    with pytest.raises(BakoboError) as raised:
        select_defeat([])
    assert raised.value.is_exactly("e.input.malformed.f")


# --- pending -----------------------------------------------------------------


def test_pending_names_what_would_discharge_it() -> None:
    finding = Pending(requirement=(element(),))
    assert [e.endorser for e in finding.requirement] == ["acme:dev"]
    assert finding.requirement[0].clause == "A1"


def test_a_requirement_element_carries_its_kind_and_its_discharge_species() -> None:
    """:1585-1586 rules the species; the demo's only cure path is absent."""
    assert element().species is PendingSpecies.ABSENT
    assert element().kind == "endorsement"
    assert "arrival" in PendingSpecies.ABSENT.cure


def test_the_species_rank_is_the_documents_own_enumeration_order() -> None:
    """QC1's pin: :1560-1561 enumerates them, and byte order would disagree."""
    ranked = sorted(PendingSpecies, key=lambda s: s.rank)
    assert [s.name_ for s in ranked] == [
        "absent",
        "window-open",
        "unresolved-conflict",
        "expired/abandoned",
    ]


def test_a_pending_finding_that_names_nothing_missing_is_not_constructible() -> None:
    """QC4's pin: an undischargeable requirement set is not a ground."""
    with pytest.raises(BakoboError) as raised:
        Pending(requirement=())
    assert raised.value.is_exactly("e.state.ground-missing.f")
    assert "typed requirement" in str(raised.value)


def test_a_pending_finding_refuses_a_requirement_that_is_not_typed() -> None:
    with pytest.raises(BakoboError) as raised:
        Pending(requirement=("acme:dev",))  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")


def test_a_pending_finding_refuses_a_set_that_is_not_in_canonical_order() -> None:
    """:1650-1651 rules the order, so a hand-built set out of order is refused."""
    with pytest.raises(BakoboError) as raised:
        Pending(requirement=(element("acme:nina"), element("acme:dev")))
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "canonical" in str(raised.value)


def test_a_pending_finding_refuses_a_set_that_is_not_deduplicated() -> None:
    with pytest.raises(BakoboError) as raised:
        Pending(requirement=(element(), element()))
    assert raised.value.is_exactly("e.input.malformed.f")
    assert "deduplicated" in str(raised.value)


def test_a_requirement_element_citing_no_clause_is_not_a_ground() -> None:
    with pytest.raises(BakoboError) as raised:
        RequirementElement(endorser="acme:dev", clause="")
    assert raised.value.is_exactly("e.state.ground-missing.f")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"endorser": "", "clause": "A1"},
        {"endorser": 1, "clause": "A1"},
        {"endorser": "acme:dev", "clause": 1},
        {"endorser": "acme:dev", "clause": "A1", "kind": ""},
        {"endorser": "acme:dev", "clause": "A1", "species": "absent"},
    ],
    ids=["no-endorser", "endorser-not-text", "clause-not-text", "no-kind", "species-not-one"],
)
def test_a_requirement_element_refuses_a_field_that_is_not_what_it_claims(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(BakoboError) as raised:
        RequirementElement(**kwargs)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")


def test_the_canonical_set_sorts_on_four_fields_and_merges_only_exact_repeats() -> None:
    """:1650-1656: subject, kind, citing-clause bytes, species — and the key sees all four."""
    window = RequirementElement(
        endorser="acme:dev", clause="A1", species=PendingSpecies.WINDOW_OPEN
    )
    ordered = canonical_requirement_set(
        [element("acme:nina"), window, element("acme:dev"), element("acme:dev")]
    )
    assert [(e.endorser, e.species) for e in ordered] == [
        ("acme:dev", PendingSpecies.ABSENT),
        ("acme:dev", PendingSpecies.WINDOW_OPEN),
        ("acme:nina", PendingSpecies.ABSENT),
    ]
    assert Pending(requirement=ordered).requirement == ordered


def test_two_elements_differing_only_in_species_do_not_merge() -> None:
    """:1652-1656 states it outright, and it is why species is in the key at all."""
    absent = element()
    window = RequirementElement(
        endorser="acme:dev", clause="A1", species=PendingSpecies.WINDOW_OPEN
    )
    assert absent.dedup_key() != window.dedup_key()
    assert len(canonical_requirement_set([absent, window])) == 2


def test_the_canonical_set_of_nothing_is_nothing() -> None:
    """Emptiness is refused by Pending, not by the ordering helper."""
    assert canonical_requirement_set([]) == ()


# --- self-convicted ----------------------------------------------------------


def test_self_conviction_carries_the_canonical_proof_package() -> None:
    """:1659-1660 rules the payload: the identifier of the package for the pair."""
    finding = SelfConvicted(proof=Proof(package="EProof1", pair=("EA", "EB")))
    assert finding.proof.package == "EProof1"
    assert finding.proof.pair == ("EA", "EB")


def test_a_proof_may_identify_the_pair_by_its_package_alone() -> None:
    assert SelfConvicted(proof=Proof(package="EProof1")).proof.pair == ()


def test_a_self_conviction_without_its_proof_is_not_constructible() -> None:
    with pytest.raises(BakoboError) as raised:
        SelfConvicted(proof=None)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.state.ground-missing.f")
    assert "proof" in str(raised.value)


def test_a_self_conviction_refuses_a_proof_that_is_not_one() -> None:
    with pytest.raises(BakoboError) as raised:
        SelfConvicted(proof="EProof1")  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")


def test_a_proof_package_that_names_nothing_is_not_a_ground() -> None:
    with pytest.raises(BakoboError) as raised:
        Proof(package="")
    assert raised.value.is_exactly("e.state.ground-missing.f")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"package": 1},
        {"package": "EProof1", "pair": ("EA",)},
        {"package": "EProof1", "pair": 7},
    ],
    ids=["package-not-text", "pair-of-one", "pair-not-a-pair"],
)
def test_a_proof_refuses_anything_that_is_not_a_contradictory_pair(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(BakoboError) as raised:
        Proof(**kwargs)  # type: ignore[arg-type]
    assert raised.value.is_exactly("e.input.malformed.f")
