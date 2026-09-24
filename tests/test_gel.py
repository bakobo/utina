"""An anchored GEL: order and membership derived from the gAID's key log.

``custos-4.2.md:1114-1120`` seals every GEL event into the gAID's KEL "by the
same anchoring discipline KERI's registry layer uses for TELs", 3091-3101 derives
the fold's order from that anchoring, and 3151-3188 makes membership fail loud:
"any membership rule that can yield a proper subset of the GEL without a refusal
is a must-reject". Each refusal below is one of those walls, shown failing, which
is what 3251 asks of a guard (this.i @wsxwkwgv, @ryh5orta, @4b2mmhbf).

The key events here are built by hand in the shape a substrate returns them:
``t``, ``i``, ``s`` in hex, ``d``, and the seal list ``a``.
"""

from __future__ import annotations

import pytest
from bakobo.errors import BakoboError

from utina.cli.world import RealValues
from utina.enact import Constructor
from utina.fold.corpus import Corpus, Event
from utina.fold.gel import Genesis, anchored
from utina.fold.triple import Position
from utina.substrate.select import NAMES, substrate_named

GAID = "Egaid" + "a" * 39
GEL = "Egel" + "g" * 40
LAW = "Elaw" + "l" * 40


def founding(**law: object) -> Event:
    body: dict[str, object] = {"clauses": [], "gel": GEL, "d": LAW, "version": 1, **law}
    return Event(said="E0-inception", kind="inception", position=Position(0),
                 body={"t": "icp", "i": GAID, "s": 0, "law": body})


def event(seq: int, kind: str = "act", said: str | None = None) -> Event:
    return Event(
        said=said or f"E{seq}-{kind}",
        kind=kind,
        position=Position(seq),
        body={"t": kind, "i": GAID, "s": seq},
    )


def seal(e: Event, sn: int | None = None, log: str = GEL) -> dict[str, str]:
    return {"i": log, "s": format(e.position.seq if sn is None else sn, "x"), "d": e.said}


def key(sn: int, ilk: str, *seals: dict[str, str]) -> dict[str, object]:
    return {"t": ilk, "i": GAID, "s": format(sn, "x"), "d": f"Ekel{sn}", "a": list(seals)}


Record = tuple[list[Event], list[dict[str, object]]]


def born(*rest: Event, ilks: tuple[str, ...] = ()) -> Record:
    """A born-governed record: the inception seals the law, then one key event per GEL event."""
    events = [founding(), *rest]
    kel = [key(0, "icp", {"d": LAW})]
    for index, member in enumerate(events):
        ilk = ilks[index] if index < len(ilks) else "ixn"
        kel.append(key(index + 1, ilk, seal(member)))
    return events, kel


# --- the happy paths ------------------------------------------------------------


def test_a_born_governed_record_folds_in_its_anchored_order():
    events, kel = born(event(1), event(2))
    corpus = anchored(list(reversed(events)), kel, gaid=GAID)
    assert [one.said for one in corpus.upto(Position(2))] == [e.said for e in events]
    assert corpus.genesis is Genesis.BORN


def test_a_founding_law_the_inception_did_not_seal_is_adopted():
    """1088-1092: incepting bare and anchoring the law later is lawful, at a
    confessed lesser grade."""
    events, kel = born(event(1))
    kel[0] = key(0, "icp")
    assert anchored(events, kel, gaid=GAID).genesis is Genesis.ADOPTED


def test_several_gel_events_may_ride_one_key_event_in_seal_list_order():
    """3095: intra-anchor order is "as the anchoring event's seal list states"."""
    first, second = event(1), event(2)
    events = [founding(), first, second]
    kel = [key(0, "icp", {"d": LAW}), key(1, "ixn", seal(events[0])),
           key(2, "ixn", seal(first), seal(second))]
    corpus = anchored(events, kel, gaid=GAID)
    assert [one.said for one in corpus.upto(Position(2))] == [e.said for e in events]


def test_seals_for_other_logs_are_not_gel_members():
    """A credential's digest seal, or a registry's event seal, is not a GEL seal."""
    events, kel = born(event(1))
    kel[1]["a"] = [{"d": "Ecredential"}, {"i": "Eother", "s": "0", "d": "Etel"}, *kel[1]["a"]]
    assert len(anchored(events, kel, gaid=GAID).upto(Position(1))) == 2


def test_an_enactment_may_ride_a_rotation():
    events, kel = born(event(1, "enactment"), ilks=("ixn", "rot"))
    assert len(anchored(events, kel, gaid=GAID).upto(Position(1))) == 2


# --- the walls ------------------------------------------------------------------


def refused(events, kel, code: str) -> str:
    with pytest.raises(BakoboError) as raised:
        anchored(events, kel, gaid=GAID)
    assert raised.value.is_exactly(code), raised.value.code
    return str(raised.value)


def test_an_event_nothing_seals_is_refused():
    events, kel = born(event(1))
    refused([*events, event(2)], kel, "e.state.gel-membership.f")


def test_a_sealed_event_nobody_presented_is_refused():
    """Withholding an event is the proper subset 3180-3181 names as a must-reject."""
    events, kel = born(event(1), event(2))
    message = refused([events[0], events[2]], kel, "e.state.gel-membership.f")
    assert "E1-act" in message


def test_a_gap_in_the_sealed_sequence_is_refused():
    events, kel = born(event(1))
    kel[2]["a"] = [seal(events[1], sn=2)]
    refused(events, kel, "e.state.gel-order.f")


def test_seals_out_of_order_are_refused():
    first, second = event(1), event(2)
    events = [founding(), first, second]
    kel = [key(0, "icp", {"d": LAW}), key(1, "ixn", seal(events[0])),
           key(2, "ixn", seal(second), seal(first))]
    refused(events, kel, "e.state.gel-order.f")


def test_an_event_whose_position_disagrees_with_its_seal_is_refused():
    events, kel = born(event(1))
    kel[2]["a"] = [{"i": GEL, "s": "1", "d": events[1].said}]
    moved = Event(said=events[1].said, kind="act", position=Position(5), body=events[1].body)
    refused([events[0], moved], kel, "e.state.gel-order.f")


def test_an_event_whose_own_sequence_disagrees_with_its_seal_is_refused():
    events, kel = born(event(1))
    lying = Event(said=events[1].said, kind="act", position=Position(1),
                  body={**events[1].body, "s": 7})
    refused([events[0], lying], kel, "e.state.gel-order.f")


def test_one_event_sealed_twice_is_refused():
    events, kel = born(event(1))
    kel.append(key(3, "ixn", seal(events[1], sn=2)))
    refused(events, kel, "e.state.gel-membership.f")


def test_an_enactment_sealed_in_an_interaction_is_refused():
    """3232: "designated-class act anchored in an interaction event" is a must-reject."""
    events, kel = born(event(1, "enactment"))
    refused(events, kel, "e.state.gel-anchor-grade.f")


def test_a_record_with_no_founding_law_is_refused():
    events, kel = born(event(1))
    refused(events[1:], kel, "e.state.gel-undesignated.f")


def test_a_founding_law_that_designates_no_gel_is_refused():
    events, kel = born(event(1))
    law = dict(events[0].body["law"])
    del law["gel"]
    bare = Event(said=events[0].said, kind="inception", position=Position(0),
                 body={**events[0].body, "law": law})
    refused([bare, events[1]], kel, "e.state.gel-undesignated.f")


def test_a_founding_law_for_another_domain_is_refused():
    """The key log is the gAID's; a founding event naming another domain is not its law."""
    events, kel = born(event(1))
    other = Event(said=events[0].said, kind="inception", position=Position(0),
                  body={**events[0].body, "i": "Esomeone-else"})
    refused([other, events[1]], kel, "e.state.gel-undesignated.f")


def test_two_founding_laws_are_refused():
    events, kel = born(event(1, "inception"))
    refused(events, kel, "e.state.gel-undesignated.f")


def test_a_founding_law_not_at_the_head_of_the_gel_is_refused():
    act, law = event(0), founding()
    moved = Event(said=law.said, kind="inception", position=Position(1),
                  body={**law.body, "s": 1})
    kel = [key(0, "icp", {"d": LAW}), key(1, "ixn", seal(act)), key(2, "ixn", seal(moved))]
    refused([act, moved], kel, "e.state.gel-undesignated.f")


def test_a_born_governed_founding_law_naming_the_gaid_is_refused():
    """1085: "The gAID SHALL NOT appear in C or in any body C cites, transitively"."""
    events, kel = born(event(1))
    law = {**events[0].body["law"], "clauses": [{"slots": [{"endorser": GAID}]}]}
    naming = Event(said=events[0].said, kind="inception", position=Position(0),
                   body={**events[0].body, "law": law})
    refused([naming, events[1]], kel, "e.state.genesis-cycle.f")


def test_an_adopted_founding_law_may_name_the_gaid():
    """The exclusion is a cut in the born-governed cycle; an adopted law has none."""
    events, kel = born(event(1))
    kel[0] = key(0, "icp")
    law = {**events[0].body["law"], "clauses": [{"slots": [{"endorser": GAID}]}]}
    naming = Event(said=events[0].said, kind="inception", position=Position(0),
                   body={**events[0].body, "law": law})
    assert anchored([naming, events[1]], kel, gaid=GAID).genesis is Genesis.ADOPTED


@pytest.mark.parametrize(
    "damage",
    [
        lambda kel: kel[1].update(i="Esomeone-else"),
        lambda kel: kel[1].update(s="5"),
        lambda kel: kel[0].update(t="ixn"),
        lambda kel: kel[1].update(a="not a list"),
        lambda kel: kel[1].update(a=[{"i": GEL, "s": "zz", "d": "E0-inception"}]),
        lambda kel: kel[1].update(a=[{"i": GEL, "s": 0, "d": "E0-inception"}]),
        lambda kel: kel[1].update(a=[{"i": GEL, "s": "00", "d": "E0-inception"}]),
        lambda kel: kel.clear(),
    ],
    ids=["foreign", "gap", "no-inception", "seal-list", "bad-sn", "int-sn", "padded-sn",
         "empty"],
)
def test_a_key_log_that_is_not_the_gaids_own_is_refused(damage):
    events, kel = born(event(1))
    damage(kel)
    refused(events, kel, "e.state.gel-key-log.f")


def test_two_different_events_under_one_identifier_are_still_refused():
    """The anchored door keeps the hand-positioned one's collision wall (Q13)."""
    events, kel = born(event(1))
    twin = Event(said=events[1].said, kind="act", position=Position(1),
                 body={**events[1].body, "act": "something else"})
    refused([*events, twin], kel, "e.state.order-ambient.f")


def test_a_hand_positioned_corpus_has_no_genesis_grade():
    """Corpus.load is the door fold unit tests use; it claims no anchoring."""
    assert Corpus.load([event(0)]).genesis is None


# --- what the constructor writes, the fold admits -------------------------------

LAW_BODY: dict[str, object] = {"clauses": []}


@pytest.fixture(params=NAMES)
def backend(request):
    with substrate_named(request.param) as substrate:
        yield substrate


def admitted(constructor: Constructor) -> Corpus:
    return anchored(constructor.emitted, constructor.key_events, gaid=constructor.gaid)


def test_a_founded_domain_is_born_governed(backend):
    """1079-1082: the gAID's inception seals the founding law's identifier."""
    constructor = Constructor.found(backend, "acme:gaid", LAW_BODY, values=RealValues())
    constructor.propose("hire")
    inception = constructor.key_events[0]
    law = constructor.emitted[0].body["law"]
    assert {"d": law["d"]} in list(inception["a"])
    assert law["gel"] == constructor.gel
    corpus = admitted(constructor)
    assert corpus.genesis is Genesis.BORN
    assert [e.said for e in corpus.upto(Position(1))] == [e.said for e in constructor.emitted]


def test_a_domain_incepted_bare_is_adopted(backend):
    constructor = Constructor(backend, backend.incept("acme:gaid"), values=RealValues())
    constructor.incept_domain(LAW_BODY)
    assert admitted(constructor).genesis is Genesis.ADOPTED


def test_an_enactment_the_constructor_writes_rides_a_rotation(backend):
    constructor = Constructor.found(backend, "acme:gaid", LAW_BODY, values=RealValues())
    enactment = constructor.enact_amendment(LAW_BODY, act="amend")
    assert constructor.key_events[-1]["t"] == "rot"
    assert constructor.anchoring_event(enactment.said) == constructor.key_events[-1]["d"]
    assert len(admitted(constructor).upto(Position(1))) == 2


def test_withholding_one_event_the_constructor_wrote_is_refused(backend):
    constructor = Constructor.found(backend, "acme:gaid", LAW_BODY, values=RealValues())
    constructor.propose("hire")
    constructor.propose("lease")
    events = list(constructor.emitted)
    del events[1]
    refused_by = pytest.raises(BakoboError)
    with refused_by as raised:
        anchored(events, constructor.key_events, gaid=constructor.gaid)
    assert raised.value.is_exactly("e.state.gel-membership.f")


def test_acme_folds_as_a_born_governed_domain_on_every_substrate(acme):
    """The record the demo shows is admitted through the anchored door, and a
    permuted arrival order is admitted to the same order (3099-3101)."""
    assert acme.corpus.genesis is Genesis.BORN
    permuted = acme.permuted_corpus(seed=7)
    last = acme.values.position(len(acme.events) - 1)
    assert [e.said for e in permuted.upto(last)] == [e.said for e in acme.corpus.upto(last)]
