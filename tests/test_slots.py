"""The slot predicate: deciding, from committed evidence, what each slot holds.

This is the half of the composition rule that keripy's ``Tholder`` cannot answer.
A signing threshold asks whether a key signed; a slot here asks whether *this*
endorser endorsed *this* subject and still stands behind it — issuer, disposition,
subject SAID and revocation status, which is a fold question and never the
substrate's (``custos-4.2.md:1956-1962``, ``this.i`` @mw6dxh).

So the tests below are mostly about refusal. Each of the checks that gate ENDORSED
is proven to fail on its own, because a predicate that is right on the happy path
and loose on one input is a predicate that counts the wrong endorsement.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

import pytest
from bakobo.errors import BakoboError

from utina.fold import slots
from utina.fold.group import Disposition, Group, Qualification, Slot

HALF = Fraction(1, 2)

#: The schema a slot names as what its evidence must satisfy. Committed law
#: (custos-4.2.md:1946-1951), so every slot carries one.
SCHEMA = slots.ENDORSEMENT_SCHEMA

MARTA = "acme:marta"
DEV = "acme:dev"
NINA = "acme:nina"
MALLORY = "acme:mallory"

SUBJECT = "EOpenBankAccount"
OTHER_SUBJECT = "EHireVpSales"


@dataclass(frozen=True)
class Ev:
    """A stand-in for ``utina.fold.corpus.Event``, carrying what the predicate reads.

    The real Event satisfies ``slots.CommittedEvent`` unchanged; this exists so the
    predicate could be driven red-to-green while the corpus was being written in
    another worktree (``this.i`` @yenp2x).
    """

    said: str
    kind: str = "endorsement"
    body: dict[str, Any] = field(default_factory=dict)


def signed(
    said: str,
    issuer: str,
    *,
    subject: str = SUBJECT,
    disp: str = "endorse",
    act: str = "issue",
    kind: str = "endorsement",
    schema: str = slots.ENDORSEMENT_SCHEMA,
) -> Ev:
    """One committed endorsement act, embedding its credential (this.i @vi4t4i).

    ``a["said"]`` is the SUBJECT's SAID — the decision being endorsed — while
    ``Ev.said`` is this act's own. That collision of names is the dossier's, kept
    deliberately so the shape stays isomorphic.
    """
    acdc: dict[str, Any] = {
        "v": "ACDCtest",
        "d": f"{said}-credential",
        "i": issuer,
        "s": schema,
        "a": {
            "d": f"{said}-attributes",
            "dt": "2026-01-01T00:00:00.000000+00:00",
            "said": subject,
            "act": act,
            "disp": disp,
        },
    }
    body: dict[str, Any] = {"t": "end", "i": issuer, "acdc": acdc, "acdc_sig": f"{said}-sig"}
    return Ev(said=said, kind=kind, body=body)


def founders() -> Group:
    return Group("MxN", (Slot(MARTA, HALF, SCHEMA), Slot(DEV, HALF, SCHEMA)))


def board() -> Group:
    return Group(
        "MxN", (Slot(MARTA, HALF, SCHEMA), Slot(DEV, HALF, SCHEMA), Slot(NINA, HALF, SCHEMA))
    )


def disposition_of(group: Group, events: list[Ev], endorser: str) -> Disposition:
    return slots.dispositions(group, events, SUBJECT)[endorser]


# --- The three dispositions ---------------------------------------------------


def test_no_evidence_leaves_every_slot_pending():
    classified = slots.classify(founders(), (), SUBJECT)
    assert [(one.endorser, one.disposition) for one in classified] == [
        (MARTA, Disposition.PENDING),
        (DEV, Disposition.PENDING),
    ]
    assert all(one.said is None for one in classified)


def test_a_signed_endorsement_endorses_the_slot_and_names_the_act():
    classified = slots.classify(founders(), [signed("EAct1", MARTA)], SUBJECT)
    assert classified[0].disposition is Disposition.ENDORSED
    assert classified[0].said == "EAct1"


def test_a_signed_declination_declines_the_slot_and_names_the_act():
    classified = slots.classify(founders(), [signed("EAct1", DEV, disp="decline")], SUBJECT)
    assert classified[1].disposition is Disposition.DECLINED
    assert classified[1].said == "EAct1"


def test_the_result_follows_the_law_s_slot_order():
    events = [signed("EAct1", DEV), signed("EAct2", MARTA)]
    assert [one.endorser for one in slots.classify(founders(), events, SUBJECT)] == [MARTA, DEV]


# --- Each gate on ENDORSED fails on its own -----------------------------------


def test_an_endorsement_from_the_wrong_identifier_never_counts():
    """The check that matters most. Mallory endorses; nobody's slot moves."""
    events = [signed("EAct1", MALLORY)]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING
    assert disposition_of(founders(), events, DEV) is Disposition.PENDING
    assert not founders().satisfied(slots.dispositions(founders(), events, SUBJECT))


def test_an_endorsement_fills_only_its_own_issuer_s_slot():
    events = [signed("EAct1", DEV)]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING
    assert disposition_of(founders(), events, DEV) is Disposition.ENDORSED


def test_a_disposition_the_law_does_not_recognize_leaves_the_slot_pending():
    events = [signed("EAct1", MARTA, disp="abstain")]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


def test_a_missing_disposition_leaves_the_slot_pending():
    unnamed = signed("EAct1", MARTA)
    del unnamed.body["acdc"]["a"]["disp"]
    assert disposition_of(founders(), [unnamed], MARTA) is Disposition.PENDING


def test_an_endorsement_of_a_different_subject_never_counts():
    events = [signed("EAct1", MARTA, subject=OTHER_SUBJECT)]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


def retraction(said: str, issuer: str, target: str) -> Ev:
    """``issuer`` withdrawing their own earlier act ``target``."""
    return Ev(said=said, kind="retraction", body={"i": issuer, "revokes": target})


def test_a_revoked_endorsement_leaves_the_slot_pending():
    """The in-flight case: Marta alone holds 1/2, the act is live, and she withdraws."""
    events = [signed("EAct1", MARTA), retraction("EAct2", MARTA, "EAct1")]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


def test_only_the_issuer_can_revoke_their_own_act():
    events = [signed("EAct1", MARTA), retraction("EAct2", MALLORY, "EAct1")]
    assert disposition_of(founders(), events, MARTA) is Disposition.ENDORSED


# --- The citation a slot judgment asks about: did it stand when it was cited? --

SEAT = "acme:seat3"
SEAT_CREDENTIAL = "ESeatCredential"
REGISTRY = "ERegistry"
SEAT_SCHEMA = "E" + "t" * 43


def issuance(said: str, credential: str = SEAT_CREDENTIAL, registry: str = REGISTRY) -> Ev:
    """The domain issuing a seat credential to the seat, in its registry."""
    return Ev(
        said=said,
        kind="issuance",
        body={
            "t": "iss",
            "i": "acme:gaid",
            "ri": registry,
            "acdc": {"d": credential, "i": "acme:gaid", "s": SEAT_SCHEMA, "a": {"i": SEAT}},
        },
    )


def revocation(said: str, credential: str = SEAT_CREDENTIAL, registry: str = REGISTRY) -> Ev:
    return Ev(
        said=said,
        kind="revocation",
        body={"t": "rev", "i": "acme:gaid", "ri": registry, "said": credential},
    )


def citing(said: str, issuer: str, cited: str = SEAT_CREDENTIAL) -> Ev:
    """An endorsement citing ``cited`` as the endorser's qualification."""
    event = signed(said, issuer)
    event.body["acdc"]["e"] = {
        "d": f"{said}-edges",
        "qp": {"n": cited, "s": SEAT_SCHEMA, "o": "DI2I"},
    }
    return event


def seat_group() -> Group:
    return Group("MxN", (Slot(SEAT, HALF, SCHEMA), Slot(DEV, HALF, SCHEMA)))


def test_a_citation_that_stands_when_cited_fills_the_slot():
    events = [issuance("E1"), citing("E2", SEAT)]
    assert disposition_of(seat_group(), events, SEAT) is Disposition.ENDORSED


def test_a_citation_revoked_before_it_was_cited_does_not_fill_the_slot():
    """Beat 17: a new question after the revocation finds the seat's slot unfilled.

    Not defeated and not an error — *pending*, naming the slot, because nothing
    attributable to that slot has arrived. The credential was revoked before the
    endorsement cited it, so the endorsement cites something that did not stand.
    """
    events = [issuance("E1"), revocation("E2"), citing("E3", SEAT)]
    assert disposition_of(seat_group(), events, SEAT) is Disposition.PENDING


def test_a_citation_revoked_after_it_was_cited_still_fills_the_slot():
    """Beats 18 and 19, and the sentence Nicholas banked: evidence does not un-arrive.

    The revocation is in the bundle and reaches nothing, because the citation is
    judged at the coordinate it was made from. A prospective revocation
    falsifies no cited ground — the credential did stand at p.
    """
    events = [issuance("E1"), citing("E2", SEAT), revocation("E3")]
    assert disposition_of(seat_group(), events, SEAT) is Disposition.ENDORSED


def test_the_same_endorsement_reads_the_same_way_however_far_past_the_revocation():
    """The re-ask at a later position, which is beat 19's surprise.

    Appending more record after the revocation cannot move it, because none of
    it is in the bundle the citation is judged over.
    """
    events = [issuance("E1"), citing("E2", SEAT), revocation("E3")]
    later = [*events, signed("E4", DEV), revocation("E5", credential="EOther")]
    assert disposition_of(seat_group(), later, SEAT) is Disposition.ENDORSED


def test_a_citation_the_record_never_issued_does_not_fill_the_slot():
    """Fail closed: a citation nobody can follow is exactly as good as none."""
    events = [citing("E1", SEAT)]
    assert disposition_of(seat_group(), events, SEAT) is Disposition.PENDING


def test_an_unseated_endorsers_citation_is_not_the_folds_question(): 
    """The two currents, from the fold's side.

    Whether the *relation* holds — that this endorser is the cited credential's
    issuee or a delegate of it — is edge validation's question, and the fold
    does not ask it: Dev citing the seat's credential fills *Dev's* slot here,
    because the credential stood. What stops that endorsement existing at all is
    the constructor refusing to commit it (this.i @x7crwavm), which is a
    different current and a different code path.
    """
    events = [issuance("E1"), citing("E2", DEV)]
    assert disposition_of(seat_group(), events, DEV) is Disposition.ENDORSED


def test_an_edges_block_the_fold_cannot_read_as_edges_leaves_the_slot_filled():
    """The block's own identifier is not an edge, and neither is a stray value."""
    event = signed("E2", SEAT)
    event.body["acdc"]["e"] = {"d": "E2-edges", "junk": "not a node"}
    assert disposition_of(seat_group(), [issuance("E1"), event], SEAT) is Disposition.ENDORSED


def test_an_edge_naming_no_credential_leaves_the_slot_unfilled():
    event = signed("E2", SEAT)
    event.body["acdc"]["e"] = {"d": "E2-edges", "qp": {"s": SEAT_SCHEMA, "o": "DI2I"}}
    assert disposition_of(seat_group(), [issuance("E1"), event], SEAT) is Disposition.PENDING


# --- Retraction, bounded by settlement: Q18 as amended, this.i @nuxitore -------


def test_a_retraction_after_the_act_settles_does_not_unmake_the_endorsement():
    """``:1698-1712``, at keyword force: affirmed → pending, "evidence does not un-arrive".

    Both founders endorse, so the act is settled at Dev's endorsement. Dev then
    withdraws it. Under the unconditional filter this slot fell back to PENDING
    at any distance, which returned a settled affirmation to pending and named
    its cure as the arrival of the evidence that had already arrived. A
    withdrawal is a fact about Dev's present will, not about the artifact the
    finding appraised, so it reverses nothing.
    """
    events = [
        signed("EAct1", MARTA),
        signed("EAct2", DEV),
        retraction("EAct3", DEV, "EAct2"),
    ]
    assert disposition_of(founders(), events, DEV) is Disposition.ENDORSED
    assert disposition_of(founders(), events, MARTA) is Disposition.ENDORSED


def test_a_retraction_is_judged_against_the_record_before_it_and_not_the_whole_bundle():
    """Marta withdraws while the act is live, then endorses again, and the act settles.

    The retraction reached the first act because at its own coordinate nothing
    had settled. What fills the slot afterwards is the second endorsement, on its
    own identifier — the withdrawal is keyed to the act it names and does not
    reach an act committed after it.
    """
    events = [
        signed("EAct1", MARTA),
        retraction("EAct2", MARTA, "EAct1"),
        signed("EAct3", MARTA),
        signed("EAct4", DEV),
    ]
    classified = slots.classify(founders(), events, SUBJECT)
    assert classified[0].disposition is Disposition.ENDORSED
    assert classified[0].said == "EAct3"


def test_an_event_of_another_kind_is_not_an_endorsement_however_it_reads():
    """A proposal whose body happens to carry the endorsement fields is still a proposal."""
    events = [signed("EAct1", MARTA, kind="act")]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


def test_an_endorsement_that_is_not_an_issuance_does_not_count_toward_issuance():
    """MxN counts endorsements carrying act "issue"; a revocation endorsement is
    the business of a revocation operator this domain has not committed."""
    events = [signed("EAct1", MARTA, act="revoke")]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


def test_a_body_whose_fields_are_not_strings_is_unverifiable_and_so_pending():
    malformed = signed("EAct1", MARTA)
    malformed.body["acdc"]["a"]["disp"] = 7
    assert disposition_of(founders(), [malformed], MARTA) is Disposition.PENDING


def test_an_event_with_no_body_at_all_is_pending_rather_than_an_error():
    assert disposition_of(founders(), [Ev(said="EAct1")], MARTA) is Disposition.PENDING


def test_the_retired_flat_encoding_no_longer_fills_a_slot():
    """The pre-@vi4t4i shape — fields on the body, no credential — is not evidence now.

    Pinned so the old bytes cannot quietly keep working beside the new: a predicate
    honoring both encodings would let an event carry two answers to what it says.
    """
    flat = Ev(
        said="EAct1", body={"i": MARTA, "disp": "endorse", "act": "issue", "said": SUBJECT}
    )
    assert disposition_of(founders(), [flat], MARTA) is Disposition.PENDING


def test_a_credential_claiming_another_schema_never_counts():
    """The dossier's slot names the schema its endorsement MUST satisfy (:356)."""
    events = [signed("EAct1", MARTA, schema="E" + "x" * 43)]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


def test_a_credential_that_is_not_a_mapping_is_pending_rather_than_an_error():
    impostor = signed("EAct1", MARTA)
    impostor.body["acdc"] = "not a credential"
    assert disposition_of(founders(), [impostor], MARTA) is Disposition.PENDING


def test_an_attributes_block_that_is_not_a_mapping_is_pending_rather_than_an_error():
    impostor = signed("EAct1", MARTA)
    impostor.body["acdc"]["a"] = "compacted-away"
    assert disposition_of(founders(), [impostor], MARTA) is Disposition.PENDING


def test_a_credential_wrapped_by_a_different_signer_never_counts():
    """The event's vouched signer and the credential's claimed issuer must agree.

    The dossier identifies the endorser by the credential's i (:356), and utina's
    wrapper discipline makes the event's i the party the substrate vouched for. A
    committed event where the two diverge is not attributed to either — fail closed.
    """
    wrapped = signed("EAct1", MARTA)
    wrapped.body["i"] = MALLORY
    assert disposition_of(founders(), [wrapped], MARTA) is Disposition.PENDING
    assert disposition_of(
        Group("MxN", (Slot(MALLORY, HALF, SCHEMA),)), [wrapped], MALLORY
    ) is Disposition.PENDING


# --- Contradiction ------------------------------------------------------------


@pytest.mark.parametrize("order", ["endorse-first", "decline-first"])
def test_a_declination_is_decisive_whatever_the_committed_order(order):
    """custos-questions.md Q20: pinned fail-closed, and the pin is not confident."""
    endorsement = signed("EAct1", MARTA)
    declination = signed("EAct2", MARTA, disp="decline")
    events = (
        [endorsement, declination] if order == "endorse-first" else [declination, endorsement]
    )
    assert disposition_of(founders(), events, MARTA) is Disposition.DECLINED


def test_a_revoked_declination_releases_the_slot_while_unity_is_still_reachable():
    """Q18's reading A, in the case it was always right for: the act is still live.

    Three slots at a half, so Marta's declination leaves Dev and Nina able to
    reach unity between them. The act is in flight, her withdrawal reaches it,
    and her weight is reachable again.
    """
    events = [
        signed("EAct1", MARTA, disp="decline"),
        retraction("EAct2", MARTA, "EAct1"),
    ]
    assert disposition_of(board(), events, MARTA) is Disposition.PENDING


def test_a_revoked_declination_does_not_release_a_slot_whose_declination_ended_the_flight():
    """The same two events under two slots instead of three, and the answer inverts.

    Marta's declination spends her slot, so the weight that can still arrive is
    Dev's half and unity is unreachable: the act is settled at that coordinate,
    and under the shipped pin the finding is defeated. Her withdrawal then
    arrives at a question that is over. Honoring it would run the forbidden
    defeated → pending edge, and would mean a party could settle a decision
    against itself and reopen it at will.
    """
    events = [
        signed("EAct1", MARTA, disp="decline"),
        retraction("EAct2", MARTA, "EAct1"),
    ]
    assert disposition_of(founders(), events, MARTA) is Disposition.DECLINED


def test_the_same_endorsement_committed_twice_endorses_once():
    events = [signed("EAct1", MARTA), signed("EAct2", MARTA)]
    classified = slots.classify(founders(), events, SUBJECT)
    assert classified[0].disposition is Disposition.ENDORSED
    assert classified[0].said == "EAct1"


# --- The seam with the arithmetic ---------------------------------------------


def test_dispositions_is_the_mapping_the_group_consumes():
    events = [signed("EAct1", MARTA), signed("EAct2", DEV)]
    mapping = slots.dispositions(founders(), events, SUBJECT)
    assert mapping == {MARTA: Disposition.ENDORSED, DEV: Disposition.ENDORSED}
    assert founders().satisfied(mapping)


def test_endorsements_names_the_acts_that_reached_unity():
    events = [signed("EAct1", MARTA), signed("EAct2", DEV)]
    classified = slots.classify(founders(), events, SUBJECT)
    assert slots.endorsements(classified) == ("EAct1", "EAct2")


def test_declinations_names_the_acts_that_spent_a_slot():
    events = [signed("EAct1", MARTA), signed("EAct2", DEV, disp="decline")]
    classified = slots.classify(founders(), events, SUBJECT)
    assert slots.declinations(classified) == ((DEV, "EAct2"),)


def test_one_declination_two_verdicts_end_to_end():
    """The centerpiece, through the predicate rather than through hand-made dispositions.

    Dev commits one signed refusal. Under the founders' two slots it puts unity out
    of reach; under the board's three it does not. Nothing about the act changed.
    """
    events = [signed("EAct1", MARTA), signed("EAct2", DEV, disp="decline")]

    under_founders = slots.dispositions(founders(), events, SUBJECT)
    under_board = slots.dispositions(board(), events, SUBJECT)

    assert under_founders[DEV] is Disposition.DECLINED
    assert under_board[DEV] is Disposition.DECLINED
    assert not founders().reachable(under_founders)
    assert board().reachable(under_board)


# --- acting for a slot through a granted authority (this.i @cglayqvw) ---------

REGISTRY = "ERegistryOfAcme"
DEVICE = "acme:nina-device"

#: The one act point an endorsement occupies, and the whole of what a grant has
#: to cover for its holder to endorse.
ENDORSING = ["create commitment"]


def grant(
    said: str,
    *,
    issuer: str,
    issuee: str,
    acts: Any = None,
    constraints: Any = None,
    schema: str = slots.GCD_SCHEMA,
    registry: str = REGISTRY,
) -> Ev:
    """One committed GCD issuance: the credential that confers authority.

    ``constraints`` overrides ``acts`` wholesale, so a case can commit a
    constraint dimension the fold does not implement and prove it denies.
    """
    if constraints is None:
        constraints = {"acts": ENDORSING if acts is None else acts}
    acdc: dict[str, Any] = {
        "v": "ACDCtest",
        "d": f"{said}-credential",
        "i": issuer,
        "ri": registry,
        "s": schema,
        "a": {
            "d": f"{said}-attributes",
            "dt": "2026-01-01T00:00:00.000000+00:00",
            "i": issuee,
            "facet": {"role": "board-seat-3-device", "presentsAs": issuer},
            "constraints": constraints,
        },
        "r": "ERulesOfGcd",
    }
    body: dict[str, Any] = {"t": "iss", "i": issuer, "ri": registry, "acdc": acdc}
    return Ev(said=said, kind=slots.ISSUANCE_KIND, body=body)


def revoked(said: str, credential: str, *, registry: str = REGISTRY) -> Ev:
    return Ev(
        said=said,
        kind=slots.REVOCATION_KIND,
        body={"t": "rev", "i": NINA, "ri": registry, "said": credential},
    )


def test_a_delegate_holding_a_standing_grant_fills_its_granters_slot():
    """Beat 15. Nina's device signs with its own key and fills seat 3's slot.

    Nothing the device says about itself decides this. The fold *searches* the
    record for a grant whose issuer is the slotted endorser and whose issuee is
    the acting identifier — the endorsement points at nothing, so there is no
    citation for a stranger to have written.
    """
    events = [grant("EGrant", issuer=NINA, issuee=DEVICE), signed("EAct1", DEVICE)]

    assert disposition_of(board(), events, NINA) is Disposition.ENDORSED


def test_a_delegates_declination_declines_its_granters_slot():
    """The asymmetry holds through a grant: a no is as much an act as a yes."""
    events = [
        grant("EGrant", issuer=NINA, issuee=DEVICE),
        signed("EAct1", DEVICE, disp="decline"),
    ]

    assert disposition_of(board(), events, NINA) is Disposition.DECLINED


def test_a_delegate_with_no_grant_fills_nothing():
    """The bare act, with the grant taken away — the case the arm must not widen."""
    assert disposition_of(board(), [signed("EAct1", DEVICE)], NINA) is Disposition.PENDING


def test_a_grant_from_somebody_else_does_not_fill_this_slot():
    """Marta cannot grant away seat 3's authority; she does not hold it."""
    events = [grant("EGrant", issuer=MARTA, issuee=DEVICE), signed("EAct1", DEVICE)]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


def test_a_grant_to_somebody_else_does_not_let_this_actor_in():
    """The issuee is the whole of who may act under it."""
    events = [grant("EGrant", issuer=NINA, issuee="acme:other-device"), signed("EAct1", DEVICE)]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


def test_a_grant_revoked_before_the_act_fills_nothing():
    """What makes delegated authority revocable at all (``this.i`` @cglayqvw).

    The KERI delegation underneath is permanent and cannot be undone; this is
    the act that ends the authority, and it ends it going forward.
    """
    events = [
        grant("EGrant", issuer=NINA, issuee=DEVICE),
        revoked("ERev", "EGrant-credential"),
        signed("EAct1", DEVICE),
    ]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


def test_a_grant_revoked_after_the_act_leaves_the_act_standing():
    """Act III's rule, reused rather than reinvented: the grant *did* stand at p.

    A revocation reaches no earlier act, because no earlier act is judged over a
    bundle containing it. Nothing here is a special case for grants.
    """
    events = [
        grant("EGrant", issuer=NINA, issuee=DEVICE),
        signed("EAct1", DEVICE),
        revoked("ERev", "EGrant-credential"),
    ]

    assert disposition_of(board(), events, NINA) is Disposition.ENDORSED


def test_a_grant_issued_after_the_act_does_not_reach_back_to_it():
    """Authority is not granted retroactively: at the act there was none."""
    events = [signed("EAct1", DEVICE), grant("EGrant", issuer=NINA, issuee=DEVICE)]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


def test_a_grant_that_is_not_a_gcd_confers_nothing():
    """A credential of another schema is another kind of statement entirely."""
    events = [
        grant("EGrant", issuer=NINA, issuee=DEVICE, schema="ESomeOtherSchema"),
        signed("EAct1", DEVICE),
    ]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


@pytest.mark.parametrize(
    "acts",
    [
        ["observe record"],
        ["create record"],
        ["modify commitment"],
        [],
        ["nonsense"],
        [42],
        "create commitment",
    ],
    ids=[
        "wrong-effect",
        "wrong-kind",
        "wrong-effect-2",
        "empty",
        "unparseable",
        "nonstring",
        "bare-string",
    ],
)
def test_a_grant_whose_acts_do_not_cover_endorsing_confers_nothing(acts):
    """An endorsement is ``create commitment`` and a grant has to say so.

    "An act is authorized only if EVERY (effect, state-kind) point it occupies
    is covered here" — so a neighbouring point is not a near miss, it is a no.
    """
    events = [grant("EGrant", issuer=NINA, issuee=DEVICE, acts=acts), signed("EAct1", DEVICE)]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


def test_a_grant_covering_endorsing_among_others_confers_it():
    """Within one field values are ORed, so a wider grant still covers the point."""
    events = [
        grant(
            "EGrant", issuer=NINA, issuee=DEVICE, acts=["observe record", "create commitment"]
        ),
        signed("EAct1", DEVICE),
    ]

    assert disposition_of(board(), events, NINA) is Disposition.ENDORSED


def test_a_braced_grant_covering_endorsing_confers_it():
    """The cross-product form reaches the point as surely as the bare one does."""
    events = [
        grant("EGrant", issuer=NINA, issuee=DEVICE, acts=["create {record, commitment}"]),
        signed("EAct1", DEVICE),
    ]

    assert disposition_of(board(), events, NINA) is Disposition.ENDORSED


@pytest.mark.parametrize(
    "constraints",
    [
        {"acts": ENDORSING, "jurisdictions": ["US"]},
        {"acts": ENDORSING, "monetaryLimit": "25 CHF"},
        {"acts": ENDORSING, "icals": []},
        {"acts": ENDORSING, "validUntil": "2027-01-01T00:00:00.000000+00:00"},
        {"acts": ENDORSING, "maxDeploysPerDay": 3},
        {},
        "unconstrained",
    ],
    ids=["jurisdictions", "monetary", "icals", "validUntil", "custom", "none", "not-a-mapping"],
)
def test_a_grant_carrying_a_constraint_the_fold_cannot_evaluate_confers_nothing(constraints):
    """GCD rule 1, from the verifier's side, and it is the whole reason this is safe.

    "An unrecognized key inside ``constraints`` is fail-closed — a verifier that
    does not recognize it MUST assume that constraint is unmet and MUST deny."
    utina's fold implements ``acts`` and nothing else, so a grant bounded by a
    clock, a jurisdiction or a custom key is one this engine must refuse rather
    than honour in part. An absent ``constraints`` denies for the same reason
    (bakobo/schema#4 records that the published rules disagree with themselves
    about this, and this is the fail-closed reading of it).
    """
    events = [
        grant("EGrant", issuer=NINA, issuee=DEVICE, constraints=constraints),
        signed("EAct1", DEVICE),
    ]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


def test_an_endorser_acting_as_itself_needs_no_grant():
    """The law slots the seat, so the seat acting is the slotted party acting.

    Its own qualification is the credential its endorsement cites, judged by
    :func:`_qualified` — a grant would be asking it to be delegated to itself.
    """
    assert disposition_of(board(), [signed("EAct1", NINA)], NINA) is Disposition.ENDORSED


def test_an_act_whose_vouched_signer_is_not_its_credentials_issuer_fills_nothing():
    """Evidence attributing an act to two parties attributes it to nobody.

    The check survives the second arm: it is the *actor* the two must agree on,
    not the slot's endorser, because under a grant those are different parties.
    """
    event = signed("EAct1", DEVICE)
    event.body["i"] = NINA
    events = [grant("EGrant", issuer=NINA, issuee=DEVICE), event]

    assert disposition_of(board(), events, NINA) is Disposition.PENDING


# --- a slot that names a qualification (this.i @cglayqvw, tick 652c) ----------

DOMAIN = "acme:gaid"
SEATED = Qualification(schema=slots.GCD_SCHEMA, issuer=DOMAIN)


def office() -> Group:
    """The board, with seat 3's slot naming what its holder must be standing on."""
    return Group(
        "MxN",
        (
            Slot(MARTA, HALF, SCHEMA),
            Slot(DEV, HALF, SCHEMA),
            Slot(NINA, HALF, SCHEMA, SEATED),
        ),
    )


def seating(said: str = "ESeat", *, registry: str = "EAcmeRegistry") -> Ev:
    """The domain's credential for the office, which is what entitles it."""
    return grant(said, issuer=DOMAIN, issuee=NINA, registry=registry)


def test_an_office_with_a_standing_credential_fills_its_slot():
    events = [seating(), signed("EAct1", NINA)]

    assert disposition_of(office(), events, NINA) is Disposition.ENDORSED


def test_an_office_with_no_credential_at_all_fills_nothing():
    """The law names the office; the credential says who is holding it. Without
    one there is no holder, and an act signed by the office AID is an act by
    nobody the law has entitled."""
    assert disposition_of(office(), [signed("EAct1", NINA)], NINA) is Disposition.PENDING


def test_an_office_whose_credential_is_revoked_fills_nothing_afterwards():
    """The whole of tick 652c. Before this, an office could fill its own slot by
    CITING NOTHING, because the only check on its standing was one it opted into."""
    events = [
        seating(),
        revoked("ERev", "ESeat-credential", registry="EAcmeRegistry"),
        signed("EAct1", NINA),
    ]

    assert disposition_of(office(), events, NINA) is Disposition.PENDING


def test_an_office_act_before_the_revocation_still_stands():
    """Act III's rule, and it did not need restating: entitlement is read at the
    coordinate the act was made from, exactly as a citation's standing is."""
    events = [
        seating(),
        signed("EAct1", NINA),
        revoked("ERev", "ESeat-credential", registry="EAcmeRegistry"),
    ]

    assert disposition_of(office(), events, NINA) is Disposition.ENDORSED


def test_a_credential_from_the_wrong_issuer_does_not_seat_the_office():
    """The issuer is committed in the law for this case. A schema alone would let
    a stranger issue a credential of the right shape, into a registry of their
    own, and seat themselves in somebody else's Constitution."""
    events = [
        grant("EForged", issuer=MALLORY, issuee=NINA, registry="EMalloryRegistry"),
        signed("EAct1", NINA),
    ]

    assert disposition_of(office(), events, NINA) is Disposition.PENDING


def test_a_credential_issued_to_somebody_else_does_not_seat_the_office():
    events = [
        grant("ESeat", issuer=DOMAIN, issuee=MALLORY, registry="EAcmeRegistry"),
        signed("EAct1", NINA),
    ]

    assert disposition_of(office(), events, NINA) is Disposition.PENDING


def test_an_office_credential_that_does_not_permit_endorsing_seats_nobody():
    """The same constraint gate the delegate's grant goes through. An office
    credential bounded by a dimension this fold cannot evaluate is refused."""
    events = [
        grant("ESeat", issuer=DOMAIN, issuee=NINA, acts=["observe record"]),
        signed("EAct1", NINA),
    ]

    assert disposition_of(office(), events, NINA) is Disposition.PENDING


def test_a_slot_with_no_qualification_needs_no_credential():
    """Acme's founders are slotted as themselves and the law is all that seats
    them. A fold that required a credential everywhere would have unseated them."""
    assert disposition_of(office(), [signed("EAct1", MARTA)], MARTA) is Disposition.ENDORSED


def test_an_offices_delegate_needs_the_office_seated_as_well_as_its_own_grant():
    """Both halves, and this is the case that would be easy to lose. The device's
    authority derives from the office's, so revoking what seats the OFFICE stops
    the device too — without anything being said about the device at all."""
    device_grant = grant("EDev", issuer=NINA, issuee=DEVICE, registry="ENinaRegistry")
    seated = [seating(), device_grant, signed("EAct1", DEVICE)]
    assert disposition_of(office(), seated, NINA) is Disposition.ENDORSED

    unseated = [
        seating(),
        device_grant,
        revoked("ERev", "ESeat-credential", registry="EAcmeRegistry"),
        signed("EAct1", DEVICE),
    ]
    assert disposition_of(office(), unseated, NINA) is Disposition.PENDING


@pytest.mark.parametrize("term", ["schema", "issuer"])
def test_a_qualification_missing_either_term_is_refused(term):
    """Not read as absent. "Requires nothing" and "requires something I could not
    parse" are different statements and must not collapse into one."""
    terms = {"schema": slots.GCD_SCHEMA, "issuer": DOMAIN}
    terms[term] = ""

    with pytest.raises(BakoboError) as caught:
        Qualification(**terms)

    assert caught.value.code == "e.input.missing.qualification-term.f"


# --- a slot that seats an OFFICE, and the record says who fills it -------------
#
# The law creates a seat; a credential fills it (this.i @ftjpdph5). So a slot may
# commit no AID at all: appointing a director is an issuance, removing one is a
# revocation, and neither is an amendment. These are the cases that distinguish a
# vacancy from a fault, and both from an ambiguity the fold will not adjudicate.

OFFICE = "board-seat-3-device"
"""The office the shared ``grant`` builder above happens to seat, so these cases
reuse it rather than introducing a second credential shape."""


def seated_office() -> Group:
    """The board, with seat 3 seating an office rather than naming a party."""
    return Group(
        "MxN",
        (
            Slot(MARTA, HALF, SCHEMA),
            Slot(DEV, HALF, SCHEMA),
            Slot("", HALF, SCHEMA, SEATED, office=OFFICE),
        ),
    )


def test_an_office_slot_is_filled_by_whoever_holds_its_credential():
    """The law never names Nina, and her endorsement fills the seat anyway.

    The mapping is addressed by the SEAT and the classification reports the party in
    it, which are two different questions (``this.i`` @qjjlkrxt). An earlier version
    of this case asserted ``dispositions(...)[NINA]`` — the holder as the key — and
    it passed while the slot contributed no weight to any threshold, because
    ``Group._where`` was looking the same slot up under the empty string.
    """
    events = [seating(), signed("EAct1", NINA)]

    assert slots.dispositions(seated_office(), events, SUBJECT)[OFFICE] is (
        Disposition.ENDORSED
    )
    classified = slots.classify(seated_office(), events, SUBJECT)
    filled = [one for one in classified if one.key == OFFICE]
    assert [one.endorser for one in filled] == [NINA], "the row names who is in the seat"


def test_a_filled_office_slot_carries_its_weight():
    """The assertion M2 owed and did not make, and the whole of ``this.i`` @qjjlkrxt.

    Testing that an office is FILLED is a claim about the slot predicate. Whether the
    group then counts it is a different claim, and for as long as nothing asserted it
    the office machinery was arithmetically inert: every office slot read pending in
    ``satisfied``, ``reachable`` and ``outstanding`` however the record stood.
    """
    group = seated_office()
    events = [seating(), signed("EAct1", MARTA), signed("EAct2", NINA)]

    held = slots.dispositions(group, events, SUBJECT)

    assert group.endorsed_weight(held) == HALF + HALF
    assert group.satisfied(held), "Marta's half and the seat's half reach unity"


def test_a_vacant_office_is_pending_under_its_own_name():
    """Nobody holds it, which is ordinary rather than a fault.

    The row is named for the office, because "board-seat-3-device, pending" tells a
    reader what to go and do and an empty string does not.
    """
    held = slots.dispositions(seated_office(), [signed("EAct1", NINA)], SUBJECT)

    assert held[OFFICE] is Disposition.PENDING
    assert NINA not in held, "an endorsement from an unseated party fills nothing"


def test_revoking_the_seating_empties_the_office_for_anything_asked_after_it():
    """The whole point of the separation: personnel is not constitutional law.

    The revocation bites the NEXT question and never a settled one. Nina's endorsement
    was made while she held the seat, so it still counts afterwards; a question tabled
    over a bundle the revocation is already in finds the office empty.
    """
    before = [seating(), signed("EAct1", NINA)]
    after = [*before, revoked("ERevoke", "ESeat-credential", registry="EAcmeRegistry")]

    assert slots.dispositions(seated_office(), before, SUBJECT)[OFFICE] is (
        Disposition.ENDORSED
    )
    assert slots.dispositions(seated_office(), after, OTHER_SUBJECT)[OFFICE] is (
        Disposition.PENDING
    )


def test_a_revocation_does_not_un_count_an_endorsement_that_already_stood():
    """"What was affirmed above stands at its coordinate forever" (``:1805``).

    The defect this replaced (``this.i`` @djyj2bc2) resolved the office once, against
    the whole bundle, so a revocation reached backwards and deleted every endorsement
    the seat had ever made. It is the same reversal ``:1741`` forbids — the revocation
    is a new fact and never a rewrite — and it is the demo's answer to the sharpest
    objection the 4.1 KERI panel raised.
    """
    events = [seating(), signed("EAct1", NINA)]
    revoked_after = [*events, revoked("ERevoke", "ESeat-credential", registry="EAcmeRegistry")]

    settled = slots.classify(seated_office(), revoked_after, SUBJECT)
    seat = [one for one in settled if one.key == OFFICE]

    assert [one.disposition for one in seat] == [Disposition.ENDORSED]
    assert [one.endorser for one in seat] == [NINA], "the party who held the seat then"
    assert [one.said for one in seat] == ["EAct1"]


def test_two_standing_seatings_of_one_office_are_reported_as_ambiguous():
    """One office, one holder. Two is a defect the fold refuses over.

    Not resolved here: nothing committed says which seating supersedes, so choosing
    would be legislating. An office held by many BY DESIGN is the dossier's MxQ
    operator and a different question (tick 5psg).
    """
    events = [seating(), grant("ESeat2", issuer=DOMAIN, issuee=DEV)]

    assert slots.seating_is_ambiguous(seated_office(), events) == OFFICE


def test_one_seating_is_not_ambiguous_and_neither_is_none():
    assert slots.seating_is_ambiguous(seated_office(), [seating()]) is None
    assert slots.seating_is_ambiguous(seated_office(), []) is None


def test_a_revoked_seating_does_not_count_towards_ambiguity():
    """Two credentials, one standing: that is a succession, not a contested seat."""
    events = [
        seating(),
        revoked("ERevoke", "ESeat-credential", registry="EAcmeRegistry"),
        grant("ESeat2", issuer=DOMAIN, issuee=DEV),
    ]

    assert slots.seating_is_ambiguous(seated_office(), events) is None

    # And the office is Dev's now, which is what a succession looks like: the seat
    # never moved in the law, only who is standing in it. So the key is the office
    # in both states — that is what makes it stable across a change of holder — and
    # it is the classification's endorser that moved.
    classified = slots.classify(seated_office(), events, SUBJECT)
    seat = [one for one in classified if one.key == OFFICE]
    assert [one.endorser for one in seat] == [DEV]


def test_a_slot_naming_a_party_is_unaffected_by_any_of_this():
    """The founders are slotted as themselves and nothing about them moves."""
    assert slots.seating_is_ambiguous(board(), [seating()]) is None


def test_a_grant_whose_attributes_carry_no_facet_seats_nobody():
    """The office lives in the facet, so a grant without one names no office.

    Read fail-closed rather than treated as a wildcard: a credential that says
    nothing about which seat it confers confers none.
    """
    plain = grant("EPlain", issuer=DOMAIN, issuee=NINA, registry="EAcmeRegistry")
    del plain.body["acdc"]["a"]["facet"]

    assert slots.holders_of(
        [plain], schema=slots.GCD_SCHEMA, issuer=DOMAIN, office=OFFICE
    ) == ()


def test_a_grant_naming_the_same_holder_twice_counts_them_once():
    """Two credentials, one person: the office has one holder, not two.

    Otherwise reissuing a seating to the same director would read as a contested
    seat and refuse the very clause it was meant to keep working.
    """
    events = [
        seating(),
        grant("ESeat2", issuer=DOMAIN, issuee=NINA, registry="EAcmeRegistry"),
    ]

    assert slots.holders_of(
        events, schema=slots.GCD_SCHEMA, issuer=DOMAIN, office=OFFICE
    ) == (NINA,)
    assert slots.seating_is_ambiguous(seated_office(), events) is None


def test_a_slot_disposition_keys_itself_by_its_endorser_when_given_no_seat():
    """The shape an outside caller gets, and why the default is the endorser.

    ``classify`` always passes the key explicitly. For a slot the law entitles directly
    the seat and its occupant are the same identifier, so a two-argument construction
    still means what it did before the key existed (``this.i`` @qjjlkrxt).
    """
    direct = slots.SlotDisposition(MARTA, Disposition.ENDORSED, "EAct1")
    seated = slots.SlotDisposition(NINA, Disposition.ENDORSED, "EAct1", key=OFFICE)

    assert direct.key == MARTA
    assert (seated.key, seated.endorser) == (OFFICE, NINA)


def test_a_contested_office_fills_nothing_at_the_coordinate_it_was_contested():
    """The reachability a substitute reviewer found, and it was mine to create.

    ``seating_is_ambiguous`` refuses where the office is contested at the coordinate the
    QUESTION is asked from, and that was the only coordinate ``_holder`` was ever called
    at until ``this.i`` @djyj2bc2 made it per-act. After that there were coordinates the
    refusal cannot see: a seating contested when an endorsement was made and resolved by
    a revocation before the question is asked. That endorsement would have counted on a
    first-of-two guess. @djyj2bc2's own note claimed the gap had not been widened, and it
    had.
    """
    contested = [
        seating(),
        grant("ESeat2", issuer=DOMAIN, issuee=DEV),
        signed("EAct1", NINA),
    ]
    # The contest resolves in Dev's favour, so afterwards the office has exactly one
    # holder and nothing refuses. Nina's endorsement was made while it was contested.
    settled = [*contested, revoked("ERevoke", "ESeat-credential", registry="EAcmeRegistry")]

    # Asked over the contested bundle, the fold refuses the whole question.
    assert slots.seating_is_ambiguous(seated_office(), contested) == OFFICE

    # Asked after the contest is resolved, it does not refuse — and the endorsement made
    # while the office was contested must still count for nothing.
    assert slots.seating_is_ambiguous(seated_office(), settled) is None
    assert slots.dispositions(seated_office(), settled, SUBJECT)[OFFICE] is (
        Disposition.PENDING
    )
