"""Meridian's story: a bank that checks, and shows its working.

Acme has approved opening a bank account under its own governance — that is beat D1 of
``docs/demo-script.md``, tabled, endorsed by both founders and certified by the domain,
and it is already in the record. Meridian's law obliges it to confirm that a prospective
customer could lawfully take the action before it opens the account. So Meridian folds
Acme's log, commits what it relied on and what it checked, and only then does its own
arithmetic carry.

**The order of the five committed events is the beat.** An account is tabled; both
officers endorse it; the domain certifies the tally — and the act is still *pending*,
because the count is not the whole requirement. Then the evaluation seal lands, and the
same question answers Affirmed. A room watching that sequence sees a bank decline to
take a customer's word for it.

**Acme is built over the same substrate and is not modified.** Its events are read and
copied into Meridian's record; nothing is written back, no coordinate moves, and every
artifact pinned to Acme's record stays pinned. Meridian's parties are incepted after all
of Acme's, so that under keripy — where keys derive from the pinned salt by sequential
index — nothing already incepted shifts.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from fractions import Fraction

from utina.domain import Record
from utina.enact import Constructor
from utina.fold.constitution import Constitution
from utina.substrate import FacadeSubstrate, FoldValues, Substrate

from .law import (
    ACCOUNT_ACTS,
    DISPLAY,
    DOMAIN,
    GAID,
    GOVERNANCE_REGISTRY,
    OFFICERS,
    OPEN_ACCOUNT,
    PRIYA,
    TOMAS,
    charter,
)

#: The one slot weight Meridian's law uses, named here because the certification below
#: states what it counted each disposition as worth and a tally is proof rather than
#: assertion — a verifier walks the edges and recomputes the sum.
HALF = Fraction(1, 2)

#: Which of the customer's own acts Meridian does diligence on, and under which of the
#: customer's clauses. Read off the counterparty's record by NAME rather than hardcoded
#: as an identifier, because an identifier is a digest nobody can write down beforehand
#: (this.i @crrtzf) — and read from the customer's side of the table, since it is the
#: customer's act. Meridian's own law names neither of these (``law.py``).
CUSTOMER_ACT = "open-bank-account"
CUSTOMER_COORDINATE = "d1"


def build(
    *, values: FoldValues, substrate: Substrate | None = None, counterparty: Record
) -> Record:
    """Drive Meridian's story and return the record it produced.

    ``counterparty`` is the customer's already-built record, handed in rather than built
    here: the composition root decides which domains exist and in what order, and a
    fixture that reached out to construct another one would be deciding that for it.
    Meridian reads it and writes nothing to it.
    """
    substrate = FacadeSubstrate() if substrate is None else substrate
    aids = {alias: substrate.incept(alias) for alias in OFFICERS}
    priya, tomas = aids[PRIYA], aids[TOMAS]
    # The gAID is incepted by the verb that founds the domain, after the officers,
    # because its inception seals the charter and the charter names them (the genesis
    # knot, custos-4.2.md:1073-1084, this.i @4b2mmhbf).
    constructor = Constructor.found(substrate, GAID, charter(aids), values=values)
    aids[GAID] = constructor.gaid

    saids: dict[str, str] = {}

    def name(key: str, event: object) -> str:
        said: str = event.said  # type: ignore[attr-defined]
        saids[key] = said
        return said

    constructor.open_registry(GOVERNANCE_REGISTRY)
    name("inception", constructor.emitted[0])

    # Both officers endorse opening the account, and Priya sponsors the tally the domain
    # admits. Who sponsors confers no authority and needs none: only the domain's
    # admission makes a tally consequential (this.i @2e2dncfe).
    account = name(OPEN_ACCOUNT, constructor.propose(OPEN_ACCOUNT))
    priya_opens = constructor.endorse(priya, account)
    tomas_opens = constructor.endorse(tomas, account)
    name(
        f"{OPEN_ACCOUNT}-certified",
        constructor.certify(
            account,
            sponsor=priya,
            counted=[(priya_opens.said, HALF), (tomas_opens.said, HALF)],
        ),
    )

    # And here the act is STILL pending, because Meridian's law asks for more than a
    # count. The diligence lands last, and that placement is the beat: a reader who
    # asks the question one coordinate earlier is told exactly what is missing.
    name("diligence", _diligence(constructor, counterparty))

    events = constructor.emitted
    kel = constructor.key_events
    return Record(
        name=DOMAIN,
        display=DISPLAY,
        gaid=constructor.gaid,
        events=events,
        corpus=values.corpus(events, kel=kel, gaid=constructor.gaid),
        kel=kel,
        labels={},
        saids=saids,
        aids=aids,
        substrate=substrate,
        values=values,
        registry=constructor.registry,
    )


def _diligence(constructor: Constructor, customer: Record) -> object:
    """Meridian folds the customer's log and commits what it relied on.

    The seal's terms are read off the customer's own record at the moment of looking —
    the coordinate, the law head in force there, the clause that governs the act — so
    they are what a stranger re-folding the admitted evidence will find, rather than
    what Meridian would like to be true. No verdict is computed here and none is
    committed (this.i @gsli4bea); the fold re-derives the answer whenever asked
    (@fsbgamvi).

    The evidence admitted is the customer's record **up to that coordinate**, with the
    matching slice of its key log, because that is what Meridian actually relied on and
    a bank does not take a copy of the file it has not read.
    """
    at = customer.at(CUSTOMER_COORDINATE)
    subject = customer.said(CUSTOMER_ACT)
    law = Constitution.at(customer.corpus, at)
    governing = law.governing(CUSTOMER_ACT)
    assert governing is not None, "the customer's law governs the act it committed"
    return constructor.seal_evaluation(
        constructor.emitted[1].said,
        counterparty=customer.gaid,
        clause=governing.id,
        on=subject,
        at=at.seq,
        head=law.law_head.said,
        events=customer.corpus.upto(at),
        kel=_kel_upto(customer.kel, at.seq),
    )


def _kel_upto(
    kel: Sequence[Mapping[str, object]], seq: int
) -> tuple[Mapping[str, object], ...]:
    """The customer's key log as far as the coordinate relied on, and no further.

    Sliced by what each key event SEALS rather than by its own position: the GEL and
    the KEL run on separate clocks, and one key event may seal several GEL events. Kept
    up to and including the one that sealed the coordinate, because the fold derives
    membership from those seals and a slice cut a event early would present a record
    whose last event nothing anchored.
    """
    kept: list[Mapping[str, object]] = []
    for event in kel:
        kept.append(event)
        seals = event.get("a")
        if not isinstance(seals, Sequence) or isinstance(seals, str | bytes):
            continue
        for seal in seals:
            if isinstance(seal, Mapping) and _sealed_sequence(seal) >= seq:
                return tuple(kept)
    return tuple(kept)


def _sealed_sequence(seal: Mapping[str, object]) -> int:
    """The GEL coordinate a key-log seal names, or -1 where it names none."""
    value = seal.get("s")
    if not isinstance(value, str):
        return -1
    try:
        return int(value, 16)
    except ValueError:  # pragma: no cover - the constructor writes hex or nothing
        return -1


__all__ = ["ACCOUNT_ACTS", "CUSTOMER_ACT", "CUSTOMER_COORDINATE", "build"]
