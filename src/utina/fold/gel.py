"""The GEL as the gAID's key log says it is: its members, their order, its genesis.

``custos-4.2.md:1114-1120`` seals every GEL event into the gAID's KEL "by the
same anchoring discipline KERI's registry layer uses for TELs — a seal in the
anchoring event carrying the GEL event's self-addressing identifier". A TEL
event's anchor is an *event seal*, ``{i, s, d}``: which log, where in it, and
what. That is the shape this reads, and it is what makes three things decidable
from committed bytes that were not decidable before (this.i @wsxwkwgv):

- **Order.** 3091-3101: "KEL anchoring order first, intra-anchor order as the
  anchoring event's seal list states". The seals naming the GEL, read in key-log
  order and then seal-list order, must count 0, 1, 2… — and each event's own
  sequence number, and the position it is presented at, must be its seal's.
- **Membership.** 3160-3164 and 3178-3181: every span consumed as GEL is
  derivable from committed bytes, and "any membership rule that can yield a
  proper subset of the GEL without a refusal is a must-reject". Every seal needs
  a presented event and every presented event needs a seal. A digest seal ``{d}``
  cannot say which log it belongs to, so it could never make an omission visible;
  the event seal's ``i`` is what does.
- **Genesis.** 1073-1092: a born-governed domain's inception seals its founding
  law, and its founding law then may not name the gAID; a domain incepted bare
  whose law was anchored afterwards is lawful at a confessed lesser grade.

Which log is the GEL is read from the founding law, which designates it by
identifier (3151-3153, this.i @ryh5orta). The key events are trusted rather than
verified — the fold cannot check a signature and may import no KERI library — so
this is the same posture the fold takes toward every signature a substrate
checked (@f3pmxu3x). Verifying them belongs to an ingestion path (tick 6ofh).

Every failure refuses the stream rather than folding what is left, because what
is left would be a proper subset.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from enum import Enum

from bakobo.errors import ErrorCode  # type: ignore[import-untyped]

from utina.fold.corpus import Corpus, Event

#: Where a founding law names the log it designates as its GEL. The writing plane
#: commits it under the same literal; neither plane imports the other's.
GEL_FIELD = "gel"

#: Where a law event carries its law, and where a law carries its own identifier.
LAW_FIELD = "law"
SAID_FIELD = "d"

#: The event kind that founds a domain, and the kind an establishment event must
#: anchor (2085-2087).
FOUNDING_KIND = "inception"
ENACTMENT_KIND = "enactment"

#: The key-event ilks that establish key state. A designated act anchored in any
#: other is a must-reject (3232).
ESTABLISHMENT = frozenset({"icp", "rot", "dip", "drt"})
INCEPTION = frozenset({"icp", "dip"})

KEY_LOG_FOREIGN = ErrorCode(
    code="e.state.gel-key-log.f",
    title="These key events are not the domain's own key log.",
    detail=(
        "The key events presented beside this GEL are not {gaid}'s key log from its "
        "inception onwards: {problem}. The GEL's order and membership are read off "
        "that log, so without it neither can be derived."
    ),
    args=("gaid", "problem"),
    hint="Present the domain's complete key log, from its inception, in order.",
)

GEL_UNDESIGNATED = ErrorCode(
    code="e.state.gel-undesignated.f",
    title="No founding law says which log is this domain's GEL.",
    detail=(
        "{problem} A domain's founding law commits the identifier of the log it "
        "designates as its GEL, and there is no positional default to fall back "
        "on (custos-4.2.md:3151-3159), so nothing here says which of the seals in "
        "the key log are governance events."
    ),
    args=("problem",),
    hint=(
        "Present the record from its founding law, which must be the GEL's first "
        "event and must name the GEL it designates."
    ),
)

GEL_ORDER = ErrorCode(
    code="e.state.gel-order.f",
    title="The GEL's committed order contradicts itself.",
    detail=(
        "{problem} A GEL event's place is where the key log sealed it, and its own "
        "sequence number and the position it is presented at must say the same "
        "thing (custos-4.2.md:3091-3101)."
    ),
    args=("problem",),
    hint="Present each event at the sequence number its seal commits it at.",
)

GEL_MEMBERSHIP = ErrorCode(
    code="e.state.gel-membership.f",
    title="The events presented are not the GEL the key log seals.",
    detail=(
        "{problem} Every event consumed as GEL must be sealed into the domain's key "
        "log, and every event sealed there must be presented, because folding a "
        "proper subset without refusing is a must-reject (custos-4.2.md:3178-3181)."
    ),
    args=("problem",),
    hint="Present every GEL event the key log seals, and nothing it does not.",
)

GEL_ANCHOR_GRADE = ErrorCode(
    code="e.state.gel-anchor-grade.f",
    title="An enactment was anchored in an interaction event.",
    detail=(
        "The enactment {said} is sealed in the key event {key}, which is an "
        "interaction and not an establishment event. An enactment amending the "
        "law anchors in an establishment event (custos-4.2.md:2085-2087), and one "
        "anchored in an interaction is a must-reject (3232)."
    ),
    args=("said", "key"),
    hint="Anchor the enactment in a rotation.",
)

GENESIS_CYCLE = ErrorCode(
    code="e.state.genesis-cycle.f",
    title="A born-governed founding law names the domain it founds.",
    detail=(
        "The founding law sealed by {gaid}'s inception contains {gaid} itself. The "
        "gAID is a digest over the inception that seals the founding law, so the "
        "law naming it is a cycle, and custos-4.2.md:1085-1087 forbids it outright."
    ),
    args=("gaid",),
    hint=(
        "Refer to the domain in its founding law only through the reserved "
        "sentinel, or found it bare and anchor the law afterwards."
    ),
)


class Genesis(Enum):
    """How a domain came to have its founding law (``custos-4.2.md:1073-1092``)."""

    BORN = "born-governed"
    """The gAID's inception sealed the founding law, so the law is inside the
    bytes the identity digests."""

    ADOPTED = "adopted"
    """The gAID was incepted bare and the law anchored later — lawful, at a
    confessed lesser grade: the identity ranges over keys alone."""


def anchored(
    events: Iterable[Event],
    kel: Sequence[Mapping[str, object]],
    *,
    gaid: str,
) -> Corpus:
    """A corpus whose order and membership are derived from ``gaid``'s key log.

    Refuses rather than folding what it can: see the module docstring for each
    wall, and ``tests/test_gel.py`` for each shown failing.
    """
    given = list(events)
    presented = {event.said: event for event in given}
    _require_own_log(kel, gaid)
    founding = _founding_event(presented.values())
    law = founding.body.get(LAW_FIELD)
    assert isinstance(law, Mapping)  # _founding_event checked it
    gel = law.get(GEL_FIELD)
    sealed = _gel_seals(kel, gel, gaid)
    _require_members(presented, sealed)
    for said, (sn, ilk, key) in sealed.items():
        _require_position(presented[said], sn)
        if presented[said].kind == ENACTMENT_KIND and ilk not in ESTABLISHMENT:
            raise GEL_ANCHOR_GRADE(said=said, key=key)
    if founding.position.seq != 0:
        raise GEL_UNDESIGNATED(
            problem=f"The founding law {founding.said} is not the GEL's first event."
        )
    genesis = _genesis(kel, law)
    if genesis is Genesis.BORN and _names(law, gaid):
        raise GENESIS_CYCLE(gaid=gaid)
    return Corpus.load(given, genesis=genesis)


def _require_own_log(kel: Sequence[Mapping[str, object]], gaid: str) -> None:
    if not kel:
        raise KEY_LOG_FOREIGN(gaid=gaid, problem="no key events were presented")
    for index, event in enumerate(kel):
        if event.get("i") != gaid:
            raise KEY_LOG_FOREIGN(
                gaid=gaid, problem=f"key event {index} belongs to {event.get('i')!r}"
            )
        if event.get("s") != format(index, "x"):
            raise KEY_LOG_FOREIGN(
                gaid=gaid,
                problem=f"key event {index} carries sequence number {event.get('s')!r}",
            )
        if not isinstance(event.get("a"), list | tuple):
            raise KEY_LOG_FOREIGN(
                gaid=gaid, problem=f"key event {index} carries no seal list"
            )
    if kel[0].get("t") not in INCEPTION:
        raise KEY_LOG_FOREIGN(gaid=gaid, problem="the log does not begin with an inception")


def _founding_event(events: Iterable[Event]) -> Event:
    founding = [event for event in events if event.kind == FOUNDING_KIND]
    if len(founding) != 1:
        raise GEL_UNDESIGNATED(
            problem=f"The record presents {len(founding)} founding laws, not one."
        )
    law = founding[0].body.get(LAW_FIELD)
    if not isinstance(law, Mapping) or not isinstance(law.get(GEL_FIELD), str):
        raise GEL_UNDESIGNATED(
            problem=f"The founding law {founding[0].said} designates no GEL."
        )
    return founding[0]


def _gel_seals(
    kel: Sequence[Mapping[str, object]], gel: object, gaid: str
) -> dict[str, tuple[int, str, str]]:
    """Each GEL event the key log seals: its sequence number, anchoring ilk and key event."""
    sealed: dict[str, tuple[int, str, str]] = {}
    expected = 0
    for event in kel:
        seals = event.get("a")
        assert isinstance(seals, list | tuple)  # _require_own_log checked it
        for seal in seals:
            if not isinstance(seal, Mapping) or seal.get("i") != gel:
                continue
            sn = _sequence(seal.get("s"), gaid)
            said = str(seal.get("d"))
            if sn != expected:
                raise GEL_ORDER(
                    problem=(
                        f"The key log seals GEL event {said} at sequence number {sn} "
                        f"where the next is {expected}."
                    )
                )
            if said in sealed:
                raise GEL_MEMBERSHIP(
                    problem=f"The key log seals the GEL event {said} more than once."
                )
            sealed[said] = (sn, str(event.get("t")), str(event.get("d")))
            expected += 1
    return sealed


def _sequence(value: object, gaid: str) -> int:
    try:
        if not isinstance(value, str):
            raise ValueError(value)
        sn = int(value, 16)
        if format(sn, "x") != value:
            raise ValueError(value)
        return sn
    except ValueError:
        raise KEY_LOG_FOREIGN(
            gaid=gaid, problem=f"a seal for the GEL carries sequence number {value!r}"
        ) from None


def _require_members(
    presented: Mapping[str, Event], sealed: Mapping[str, tuple[int, str, str]]
) -> None:
    unsealed = sorted(set(presented) - set(sealed))
    if unsealed:
        raise GEL_MEMBERSHIP(
            problem=(
                f"The key log seals none of these presented events: {', '.join(unsealed)}."
            )
        )
    missing = sorted(set(sealed) - set(presented))
    if missing:
        raise GEL_MEMBERSHIP(
            problem=(
                "The key log seals these events and none was presented: "
                f"{', '.join(missing)}."
            )
        )


def _require_position(event: Event, sn: int) -> None:
    if event.position.seq != sn or event.body.get("s") != sn:
        raise GEL_ORDER(
            problem=(
                f"The event {event.said} is sealed at sequence number {sn}, and was "
                f"presented at {event.position.seq} carrying {event.body.get('s')!r}."
            )
        )


def _genesis(kel: Sequence[Mapping[str, object]], law: Mapping[str, object]) -> Genesis:
    said = law.get(SAID_FIELD)
    inception_seals = kel[0].get("a")
    assert isinstance(inception_seals, list | tuple)
    if isinstance(said, str) and any(
        isinstance(seal, Mapping) and dict(seal) == {"d": said} for seal in inception_seals
    ):
        return Genesis.BORN
    return Genesis.ADOPTED


def _names(value: object, gaid: str) -> bool:
    """Whether ``gaid`` appears anywhere in ``value``, transitively (1085)."""
    if isinstance(value, str):
        return gaid in value
    if isinstance(value, Mapping):
        return any(_names(key, gaid) or _names(item, gaid) for key, item in value.items())
    if isinstance(value, list | tuple):
        return any(_names(item, gaid) for item in value)
    return False
