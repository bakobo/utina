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
    DEV,
    EQUITY_ACTS,
    GAID,
    GOVERNANCE_REGISTRY,
    MARTA,
    NINA,
    ORDINARY_ACTS,
    SEAT,
    SEAT_OFFICE,
    SEAT_SCHEMA,
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
    seat = name("seat-the-board", constructor.enact_amendment(board_law(aids), act=AMEND))
    constructor.endorse(marta, seat)
    seated = constructor.endorse(dev, seat)
    mark("d4", seated)
    mark("board-seated", seated)

    # Demo 2 beat 8's other binding: the seat credential, issued by the domain
    # under its own registry to the seat itself. The registry is opened here
    # rather than at inception because nothing before this beat is issued under
    # it, and opening it writes no committed event.
    constructor.open_registry(GOVERNANCE_REGISTRY)
    seating = constructor.seat(aids[SEAT], schema=SEAT_SCHEMA, office=SEAT_OFFICE)
    name("seat-credential", seating)
    mark("b8", seating)

    # Demo 2 beat 11 — Dev endorses the equity release on the far side of the
    # amendment, curing it under the same clause A3 it was tabled under. Beat 10
    # is asked at board-seated, between this event and Marta's, and needs no
    # event of its own.
    mark("b11", constructor.endorse(dev, equity))

    # D5 — the budget carries on Marta and the seat, with Dev never acting. The
    # organ signs: the seat is what the law slots, and Nina holds its keys in the
    # story rather than in the record (this.i @z373ew7j).
    budget = name(BUDGET, constructor.propose(BUDGET))
    constructor.endorse(marta, budget)
    mark("d5", constructor.endorse(seat3, budget))

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
    mark("d7", constructor.decline(seat3, amend))

    # D8 — a question the law is silent about. D9 re-asks D1 from here.
    dividend = constructor.propose(UNGOVERNED_ACT)
    name(UNGOVERNED_ACT, dividend)
    mark("d8", dividend)
    mark("d9", dividend)

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
