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
from utina.substrate import FacadeSubstrate, FoldValues

from .law import (
    AMENDMENT_ACTS,
    BOARD_LAW,
    DEV,
    FOUNDING_LAW,
    GAID,
    MARTA,
    NINA,
    ORDINARY_ACTS,
    UNGOVERNED_ACT,
)
from .record import Acme

BANK_ACCOUNT, HIRE, BUDGET = ORDINARY_ACTS
AMEND = AMENDMENT_ACTS[0]


def build(*, values: FoldValues) -> Acme:
    """Drive Acme's whole story and return the record it produced."""
    substrate = FacadeSubstrate(values=values)
    for party in (MARTA, DEV, NINA):
        substrate.incept(party)
    constructor = Constructor(substrate, GAID, values=values)

    saids: dict[str, str] = {}
    labels: dict[str, int] = {}

    def name(key: str, event: object) -> str:
        said: str = event.said  # type: ignore[attr-defined]
        saids[key] = said
        return said

    def mark(label: str, event: object) -> None:
        labels[label] = event.position.seq  # type: ignore[attr-defined]

    # Inception. The founding law commits A1 and A2, both unanimous.
    mark("inception", constructor.incept_domain(FOUNDING_LAW))
    name("inception", constructor.emitted[0])

    # D1 — both founders endorse opening a bank account.
    bank = name(BANK_ACCOUNT, constructor.propose(BANK_ACCOUNT))
    constructor.endorse(MARTA, bank)
    mark("d1", constructor.endorse(DEV, bank))

    # D2, D3 — Marta endorses the hire; Dev signs a declination against it.
    # One committed act, two beats, because a slot may go from pending to
    # declined without the act being retabled.
    hire = name(HIRE, constructor.propose(HIRE))
    mark("d2", constructor.endorse(MARTA, hire))
    mark("d3", constructor.decline(DEV, hire))

    # D4 — the amendment that seats the board, judged under the law it replaces
    # and anchored in an establishment event (custos-4.2.md:2085-2087).
    seat = name("seat-the-board", constructor.enact_amendment(BOARD_LAW, act=AMEND))
    constructor.endorse(MARTA, seat)
    seated = constructor.endorse(DEV, seat)
    mark("d4", seated)
    mark("board-seated", seated)

    # D5 — the budget carries on Marta and Nina, with Dev never acting.
    budget = name(BUDGET, constructor.propose(BUDGET))
    constructor.endorse(MARTA, budget)
    mark("d5", constructor.endorse(NINA, budget))

    # D6 — the budget is tabled again and Dev declines it. Same signed no as
    # D3, three slots instead of two, and the fold draws the difference.
    retabled = name(f"{BUDGET}-retabled", constructor.propose(BUDGET))
    constructor.endorse(MARTA, retabled)
    mark("d6", constructor.decline(DEV, retabled))

    # D7 — both founders want the amendment; the seated director does not, and
    # under B2 that is enough, because amendment authority was never distributed.
    amend = name(AMEND, constructor.propose(AMEND))
    constructor.endorse(MARTA, amend)
    constructor.endorse(DEV, amend)
    mark("d7", constructor.decline(NINA, amend))

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
        substrate=substrate,
        values=values,
    )
