"""Acme's story, told by driving the constructor's verb.

Every event below is produced by ``utina.enact``, signed, and committed in
order. Nothing is a literal, because a hand-written log would only prove that
its author can write down what they expect the fold to say.

The beats are ``docs/demo-script.md`` in order, and the labels this records are
the names the acceptance oracle addresses the log through. Where a beat needs a
slot to be untouched that an earlier beat left endorsed, the act is tabled
again rather than the log rewritten — dispositions only ever advance, so the
second budget vote is a second committed act (this.i @w5yqab).
"""

from __future__ import annotations

from utina.enact import Constructor
from utina.substrate import FacadeSubstrate, FoldValues, Substrate

from .law import (
    AMENDMENT_ACTS,
    CAPITAL_PLAN,
    DEV,
    DEVICE,
    DEVICE_ROLE,
    EQUITY_ACTS,
    GAID,
    GOVERNANCE_REGISTRY,
    MARTA,
    NINA,
    ORDINARY_ACTS,
    Q2_FORECAST,
    Q3_BUDGET,
    QUINN,
    SEAT,
    SEAT_ACTS,
    SEAT_OFFICE,
    SEAT_REGISTRY,
    UNGOVERNED_ACT,
    board_law,
    founding_law,
)
from .record import Acme

BANK_ACCOUNT, HIRE, LEASE, BUDGET = ORDINARY_ACTS
AMEND = AMENDMENT_ACTS[0]
EQUITY = EQUITY_ACTS[0]


def build(*, values: FoldValues, substrate: Substrate | None = None) -> Acme:
    """Drive Acme's whole story and return the record it produced.

    This is the composition root, and inception happens here rather than inside
    the constructor's first verb: under keripy an identifier is a digest of its
    own inception event, so it cannot be named before it exists (this.i @crrtzf).
    The order of these four calls is load-bearing — keripy derives each party's
    keys from the salt and a sequentially assigned index — so it is written once,
    here, and never varied.
    """
    substrate = FacadeSubstrate() if substrate is None else substrate
    aids = {alias: substrate.incept(alias) for alias in (GAID, MARTA, DEV, NINA)}
    marta, dev = aids[MARTA], aids[DEV]
    # Nina is incepted and aliased and commits no act. She holds board seat 3's
    # keys in the story; in the record the seat signs, because the law slots the
    # office and the substrate holds every party's keys anyway (@z373ew7j).

    # Board seat 3 is an office, not a person: a delegated identifier of the
    # domain, whose keys Nina holds (custos-4.2.md:2139-2148, this.i @2a25xudi).
    # It is delegated after the four self-incepted parties so that their key
    # material, derived from the pinned salt by index, does not move.
    seat3 = aids[SEAT] = substrate.delegate(aids[GAID], SEAT)

    # Beat 15's device: delegated from the SEAT, not from Nina and not from the
    # domain, and delegated last so that nothing already incepted moves. The
    # delegation is what lets DI2I resolve; it is not what lets the device act.
    device = aids[DEVICE] = substrate.delegate(seat3, DEVICE)

    # Quinn, incepted last so nothing already incepted moves. He commits no act:
    # beat 14's endorsement is refused at commitment, so the record's own story
    # about Quinn is that he is a real party who never got into it.
    aids[QUINN] = substrate.incept(QUINN)
    constructor = Constructor(substrate, aids[GAID], values=values)

    saids: dict[str, str] = {}
    labels: dict[str, int] = {}

    def name(key: str, event: object) -> str:
        said: str = event.said  # type: ignore[attr-defined]
        saids[key] = said
        return said

    def mark(label: str, event: object) -> None:
        labels[label] = event.position.seq  # type: ignore[attr-defined]

    # Inception. The founding law commits A1, A2 and A3, all three unanimous.
    mark("inception", constructor.incept_domain(founding_law(aids)))
    name("inception", constructor.emitted[0])

    # D1 — both founders endorse opening a bank account.
    bank = name(BANK_ACCOUNT, constructor.propose(BANK_ACCOUNT))
    constructor.endorse(marta, bank)
    mark("d1", constructor.endorse(dev, bank))

    # D2 — Marta endorses the hire and nobody else acts on it, ever. It is left
    # pending on purpose: it is the act whose governing clause the amendment
    # repeals, which closes its cure path (this.i @4tcsbw72).
    hire = name(HIRE, constructor.propose(HIRE))
    mark("d2", constructor.endorse(marta, hire))

    # D3 — the office lease carries the signed no. Two slots at a half, one of
    # them spent, so unity is unreachable and the finding is a defeat.
    lease = name(LEASE, constructor.propose(LEASE))
    constructor.endorse(marta, lease)
    declined = constructor.decline(dev, lease)
    name(f"{LEASE}-declined", declined)
    mark("d3", declined)

    # Demo 2 beat 5 — release of escrowed founder equity, under A3. Marta
    # endorses and Dev does not, and it is left that way on purpose: it is the
    # act that has to still be pending when the amendment lands, so that beat 10
    # can show a cure path staying open under a clause the amendment did not move.
    equity = name(EQUITY, constructor.propose(EQUITY))
    mark("b5", constructor.endorse(marta, equity))

    # D4 — the amendment that seats the board, judged under the law it replaces
    # and anchored in an establishment event (custos-4.2.md:2085-2087).
    # The amendment declares what it disturbs, truthfully: the hire is the one
    # act in flight whose clause it replaces, and the equity release is not,
    # because A3 is carried across byte-identical. A declaration that omitted the
    # hire would convict this amendment on its own bytes (this.i @<disturbance>).
    seat = name(
        "seat-the-board",
        constructor.enact_amendment(board_law(aids), act=AMEND, disturbs=[hire]),
    )
    constructor.endorse(marta, seat)
    seated = constructor.endorse(dev, seat)
    mark("d4", seated)
    mark("board-seated", seated)

    # Demo 2 beat 8's other binding: the seat credential, issued by the domain
    # under its own registry to the seat itself. The registry is opened here
    # rather than at inception because nothing before this beat is issued under
    # it, and opening it writes no committed event.
    constructor.open_registry(GOVERNANCE_REGISTRY)
    seating = constructor.confer(aids[SEAT], role=SEAT_OFFICE, acts=SEAT_ACTS)
    name("seat-credential", seating)
    mark("b8", seating)
    seat_credential = str(seating.body["acdc"]["d"])

    # Demo 2 beat 11 — Dev endorses the equity release on the far side of the
    # amendment, curing it under the same clause A3 it was tabled under. Beat 10
    # is asked at board-seated, between this event and Marta's, and needs no
    # event of its own.
    mark("b11", constructor.endorse(dev, equity))

    # D5 — the budget carries on Marta and the seat, with Dev never acting. The
    # organ signs: the seat is what the law slots, and Nina holds its keys in the
    # story rather than in the record (this.i @z373ew7j). The seat's endorsement
    # cites its own seat credential, so the DI2I edge is checked by the existing
    # toolchain before the endorsement is committed at all (@x7crwavm).
    budget = name(BUDGET, constructor.propose(BUDGET))
    constructor.endorse(marta, budget)
    mark("d5", constructor.endorse(seat3, budget, qualification=seat_credential))

    # D6 — the budget is tabled again and Dev declines it. Same signed no as
    # D3, three slots instead of two, and the fold draws the difference.
    retabled = name(f"{BUDGET}-retabled", constructor.propose(BUDGET))
    constructor.endorse(marta, retabled)
    mark("d6", constructor.decline(dev, retabled))

    # D7 — both founders want the amendment; the seated organ does not, and under
    # B2 that is enough, because amendment authority was never distributed.
    amend = name(AMEND, constructor.propose(AMEND))
    constructor.endorse(marta, amend)
    constructor.endorse(dev, amend)
    mark("d7", constructor.decline(seat3, amend, qualification=seat_credential))

    # D8 — a question the law is silent about. D9 re-asks D1 from here.
    dividend = constructor.propose(UNGOVERNED_ACT)
    name(UNGOVERNED_ACT, dividend)
    mark("d8", dividend)
    mark("d9", dividend)

    # Beats 13 and 15 — the Q2 forecast, a second act of the budget class, tabled
    # after D8 so that nothing demo 1 asks about moves. Marta yes, Dev no: the
    # same signed no as D3 and D6, and with three slots it delays rather than
    # defeats, because seat 3's slot is still reachable.
    forecast = name(Q2_FORECAST, constructor.propose(BUDGET))
    constructor.endorse(marta, forecast)
    mark("b13", constructor.decline(dev, forecast))

    # The seat opens its OWN registry. A transaction log accepts issuances only
    # from the identifier that controls it, and the governance consequence is the
    # point rather than the mechanism: revocation authority follows the
    # registry's controller, so a grant the seat kept in ACME's registry would be
    # one the seat could never take back.
    constructor.open_registry(SEAT_REGISTRY, controller=seat3)
    granting = constructor.confer(
        device, role=DEVICE_ROLE, acts=SEAT_ACTS, issuer=seat3, presents_as=seat3
    )
    name("device-grant", granting)
    mark("device-granted", granting)

    # Beat 15 — Nina signs from her device, and the forecast reaches unity. Two
    # committed things make it fill seat 3's slot, and neither is the delegation:
    # the seat's GCD grant, which the fold finds by searching rather than by
    # following a citation, and the seat credential the endorsement cites, which
    # is what DI2I resolves against. Revoke either and the device stops filling
    # the slot at the next coordinate.
    mark("b15", constructor.endorse(device, forecast, qualification=seat_credential))

    # Beat 16 — Acme revokes the seat credential in its own registry. Seat 3's
    # key log is untouched and its keys are still valid: what moved is what the
    # registry says about a credential, which is evidence and never authority.
    mark("b16", constructor.revoke(seat_credential))

    # Beat 17 — a NEW question, asked over a bundle the revocation is already in.
    # Marta endorses and seat 3 does not, so the slot is unfilled and the fold
    # names it as a typed requirement rather than treating the revocation as a
    # verdict. Beats 18 and 19 re-ask beat 12's question from here.
    q3 = name(Q3_BUDGET, constructor.propose(BUDGET))
    mark("b17", constructor.endorse(marta, q3))

    # Beat 21 — the capital plan, a SECOND question pending under B1 alongside
    # beat 17's Q3 budget. Two acts in flight under one clause is the whole point
    # of it: beat 23's computed disturbance set has to contain both, and an
    # amendment that names only one of them is the lie Act IV is about.
    plan = name(CAPITAL_PLAN, constructor.propose(BUDGET))
    mark("b21", constructor.endorse(marta, plan))

    events = constructor.emitted
    return Acme(
        events=events,
        corpus=values.corpus(events),
        labels=labels,
        saids=saids,
        aids=aids,
        substrate=substrate,
        values=values,
        registry=constructor.registry,
    )
