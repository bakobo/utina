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

from utina.fold import slots
from utina.fold.group import Disposition, Group, Slot

HALF = Fraction(1, 2)

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
    return Group("MxN", (Slot(MARTA, HALF), Slot(DEV, HALF)))


def board() -> Group:
    return Group("MxN", (Slot(MARTA, HALF), Slot(DEV, HALF), Slot(NINA, HALF)))


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


def test_a_revoked_endorsement_leaves_the_slot_pending():
    events = [
        signed("EAct1", MARTA),
        Ev(said="EAct2", body={"i": MARTA, "revokes": "EAct1"}),
    ]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


def test_only_the_issuer_can_revoke_their_own_act():
    events = [
        signed("EAct1", MARTA),
        Ev(said="EAct2", body={"i": MALLORY, "revokes": "EAct1"}),
    ]
    assert disposition_of(founders(), events, MARTA) is Disposition.ENDORSED


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
        Group("MxN", (Slot(MALLORY, HALF),)), [wrapped], MALLORY
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


def test_a_revoked_declination_releases_the_slot_again():
    """custos-questions.md Q18, reading A: a retracted act is as if never committed."""
    events = [
        signed("EAct1", MARTA, disp="decline"),
        Ev(said="EAct2", body={"i": MARTA, "revokes": "EAct1"}),
    ]
    assert disposition_of(founders(), events, MARTA) is Disposition.PENDING


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
