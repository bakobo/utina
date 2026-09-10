"""Registry state as the fold computes it: from committed events, and only those.

The doctrine under test is issue #82's third rule — registry state is a member
of the evidence bundle rather than an ambient condition read against it — so
every case here hands in events and nothing else. There is no substrate in this
file on purpose: if any of these could be answered by asking one, the fold would
have an ambient input.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from utina.fold import standing
from utina.substrate import ISSUED, REVOKED

REGISTRY = "E" + "g" * 43
OTHER_REGISTRY = "E" + "h" * 43
SEAT_CREDENTIAL = "E" + "s" * 43
OTHER_CREDENTIAL = "E" + "o" * 43
GAID = "acme:gaid"


@dataclass(frozen=True)
class Ev:
    """A stand-in for a committed event, carrying what this module reads."""

    said: str
    kind: str = standing.ISSUANCE_KIND
    body: dict[str, Any] = field(default_factory=dict)


def issuance(said: str, credential: str = SEAT_CREDENTIAL, registry: str = REGISTRY) -> Ev:
    """An issuance event, embedding its credential as the constructor writes it."""
    return Ev(
        said=said,
        kind=standing.ISSUANCE_KIND,
        body={"t": "iss", "i": GAID, "ri": registry, "acdc": {"d": credential, "i": GAID}},
    )


def revocation(said: str, credential: str = SEAT_CREDENTIAL, registry: str = REGISTRY) -> Ev:
    """A revocation event, naming the credential rather than embedding it."""
    return Ev(
        said=said,
        kind=standing.REVOCATION_KIND,
        body={"t": "rev", "i": GAID, "ri": registry, "said": credential},
    )


def test_nothing_committed_leaves_a_credential_with_no_state():
    assert standing.state_over((), REGISTRY, SEAT_CREDENTIAL) is None


def test_an_issuance_makes_a_credential_stand():
    assert standing.state_over([issuance("E1")], REGISTRY, SEAT_CREDENTIAL) == ISSUED


def test_a_revocation_after_the_issuance_moves_the_state():
    events = [issuance("E1"), revocation("E2")]
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) == REVOKED


def test_the_state_is_the_last_committed_transition_not_the_first():
    """A state machine, not a threshold.

    The fold's other crossings take the first — an enactment's effectuation, an
    act's settlement — because those ask when something was *reached*. This asks
    what a registry says now, and the revocation is the later fact. What the
    revocation does not touch is a finding appraised over a bundle that does not
    contain it, which is a fact about positions and not about this function.
    """
    events = [issuance("E1"), revocation("E2"), issuance("E3")]
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) == ISSUED


def test_a_bundle_that_stops_before_the_revocation_still_reads_issued():
    """The prospective-revocation beat, at the layer where it is decided.

    Beat 19 re-asks a question at a position after a revocation and the earlier
    finding stands, because the bundle it cites is the one that was appraised.
    Here that is simply the events handed in: a caller holding the bundle up to
    the earlier coordinate reads ISSUED, and holding the later one reads REVOKED,
    with no special case anywhere.
    """
    events = [issuance("E1"), revocation("E2")]
    assert standing.state_over(events[:1], REGISTRY, SEAT_CREDENTIAL) == ISSUED
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) == REVOKED


def test_state_is_read_per_registry_and_never_across_them():
    """The law names which registry confers standing, so the pair is the key."""
    events = [issuance("E1", registry=OTHER_REGISTRY)]
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) is None
    assert standing.state_over(events, OTHER_REGISTRY, SEAT_CREDENTIAL) == ISSUED


def test_a_revocation_in_another_registry_does_not_reach_this_one():
    events = [issuance("E1"), revocation("E2", registry=OTHER_REGISTRY)]
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) == ISSUED


def test_another_credentials_events_do_not_move_this_ones_state():
    events = [issuance("E1"), revocation("E2", credential=OTHER_CREDENTIAL)]
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) == ISSUED


def test_an_event_of_another_kind_is_not_a_transition_however_it_reads():
    """An endorsement event carrying a registry field is still an endorsement."""
    posing = Ev(
        said="E1",
        kind="endorsement",
        body={"t": "end", "i": GAID, "ri": REGISTRY, "acdc": {"d": SEAT_CREDENTIAL}},
    )
    assert standing.state_over([posing], REGISTRY, SEAT_CREDENTIAL) is None


def test_an_issuance_embedding_no_credential_contributes_nothing():
    empty = Ev(said="E1", kind=standing.ISSUANCE_KIND, body={"t": "iss", "ri": REGISTRY})
    assert standing.state_over([empty], REGISTRY, SEAT_CREDENTIAL) is None


def test_a_revocation_naming_no_credential_leaves_the_state_alone():
    """Fail closed without raising: an unreadable transition is not a transition."""
    nameless = Ev(said="E2", kind=standing.REVOCATION_KIND, body={"t": "rev", "ri": REGISTRY})
    events = [issuance("E1"), nameless]
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) == ISSUED


def test_a_registry_field_that_is_not_the_registry_contributes_nothing():
    events = [Ev(said="E1", body={"t": "iss", "ri": 7, "acdc": {"d": SEAT_CREDENTIAL}})]
    assert standing.state_over(events, REGISTRY, SEAT_CREDENTIAL) is None
