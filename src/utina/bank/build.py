"""Meridian's story, told by driving the same constructor Acme's story drives.

Five committed events and no labels. Every one of them is produced by ``utina.enact``,
signed, and committed in order, for the reason Acme's are: a hand-written log would only
prove that its author can write down what they expect the fold to say.

The story is the smallest one that asks a real question twice and gets two different
answers. A credit line is tabled, both officers endorse it, and the domain certifies the
tally, so a question about that act is **affirmed**. A second credit line is tabled and
only one officer endorses it, so a question about the class — which binds to the latest
tabling (``this.i`` @kb4ymt) — is **pending**, with the other officer's slot named as the
requirement. Nothing here is new engine behaviour; that is the point. It is Acme's
machinery answering about a record Acme's fixture did not write.

**There is deliberately no label table.** ``d1`` and ``b17`` are a demo's names for
coordinates and are committed nowhere; a domain with none is addressed by sequence
number, and is the case ``this.i`` @qtm5ntkg and @er57yvs7 exist to cover.
"""

from __future__ import annotations

from fractions import Fraction

from utina.domain import Record
from utina.enact import Constructor
from utina.substrate import FacadeSubstrate, FoldValues, Substrate

from .law import (
    CREDIT_ACTS,
    DISPLAY,
    DOMAIN,
    GAID,
    GOVERNANCE_REGISTRY,
    OFFICERS,
    PRIYA,
    TOMAS,
    charter,
)

CREDIT_LINE = CREDIT_ACTS[0]

#: The one slot weight Meridian's law uses, named here because the certification below
#: states what it counted each disposition as worth and a tally is proof rather than
#: assertion — a verifier walks the edges and recomputes the sum.
HALF = Fraction(1, 2)


def build(*, values: FoldValues, substrate: Substrate | None = None) -> Record:
    """Drive Meridian's whole story and return the record it produced.

    The composition root, and inception happens here rather than inside the
    constructor's first verb, for the reason it does in Acme's: under keripy an
    identifier is a digest of its own inception event, so it cannot be named before it
    exists (this.i @crrtzf). The order of these calls is load-bearing under keripy,
    which derives each party's keys from the salt and a sequentially assigned index, so
    it is written once, here, and never varied.
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

    # Opened and issued into by nobody. A registry with nothing in it is a true thing
    # for a domain that confers no standing, and opening it writes no committed event.
    constructor.open_registry(GOVERNANCE_REGISTRY)

    name("inception", constructor.emitted[0])

    # Both officers endorse the first credit line, and Priya sponsors the tally the
    # domain then admits. Who sponsors confers no authority and needs none: only the
    # domain's admission makes a tally consequential (this.i @2e2dncfe).
    granted = name(CREDIT_LINE, constructor.propose(CREDIT_LINE))
    priya_grants = constructor.endorse(priya, granted)
    tomas_grants = constructor.endorse(tomas, granted)
    name(
        f"{CREDIT_LINE}-certified",
        constructor.certify(
            granted,
            sponsor=priya,
            counted=[(priya_grants.said, HALF), (tomas_grants.said, HALF)],
        ),
    )

    # A second credit line, endorsed by one officer and left there. Tomas has not
    # declined it — an untouched slot is not an act (this.i @7szbfw) — so the finding
    # is pending with his slot named, rather than defeated.
    retabled = name(f"{CREDIT_LINE}-retabled", constructor.propose(CREDIT_LINE))
    constructor.endorse(priya, retabled)

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
