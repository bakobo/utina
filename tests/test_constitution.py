"""The law in force at a position, and the succession that changes it.

The mechanism under test is the one the demo exists to show. Custos states it
four times and rules it once: "law never applies to itself at a coordinate, only
to its successor at the next, and succession is never retroactive"
(``custos-4.2.md:2270-2272``), and at keyword force "this document's clauses are
the GARD's law for every position at and after the effectuation coordinate, and
SHALL bind no position before it" (3001-3003).

So the amendment that changes the law is itself an event in the log this fold
reads, and it is appraised under the law in force immediately *before* its own
coordinate. ``test_the_amendment_is_judged_under_the_law_it_replaces`` is that
sentence as a test, and it is the one to read first.

The other binding obligation here is 3101: streams presented in permuted arrival
order "SHALL fold to byte-identical Constitutions" — byte-identical, which is
stricter than semantic equality and is why ``canonical_bytes`` exists.
"""

import itertools
import sys
import types
from dataclasses import dataclass
from fractions import Fraction

import pytest


def _ensure_siblings() -> None:
    """Stub the sibling modules only while they are still unbuilt.

    ``docs/interfaces.md`` owns ``Position``, ``LawHead``, ``Slot`` and
    ``Group``; this file must never become their second definition. Each stub is
    installed only when the real module cannot be imported, so it retires itself
    the moment the sibling lands.
    """
    try:
        import utina.fold.triple
    except ImportError:
        triple = types.ModuleType("utina.fold.triple")

        @dataclass(frozen=True)
        class Position:
            seq: int

            def __lt__(self, other: Position) -> bool:
                return self.seq < other.seq

        @dataclass(frozen=True)
        class LawHead:
            said: str

        triple.Position = Position  # type: ignore[attr-defined]
        triple.LawHead = LawHead  # type: ignore[attr-defined]
        sys.modules["utina.fold.triple"] = triple

    try:
        import utina.fold.group  # noqa: F401
    except ImportError:
        group = types.ModuleType("utina.fold.group")

        @dataclass(frozen=True)
        class Slot:
            endorser: str
            weight: Fraction

        @dataclass(frozen=True)
        class Group:
            operator: str
            slots: tuple[Slot, ...]

            def satisfied_by(self, endorsers) -> bool:
                reached = sum(
                    (slot.weight for slot in self.slots if slot.endorser in endorsers),
                    Fraction(0),
                )
                return reached >= 1

        group.Slot = Slot  # type: ignore[attr-defined]
        group.Group = Group  # type: ignore[attr-defined]
        sys.modules["utina.fold.group"] = group


_ensure_siblings()

from bakobo.errors import BakoboError  # noqa: E402

from utina.fold.constitution import Constitution  # noqa: E402
from utina.fold.corpus import Corpus, Event  # noqa: E402
from utina.fold.triple import Position  # noqa: E402
from utina.substrate import ENDORSEMENT_SCHEMA  # noqa: E402


def slots(*pairs):
    """Committed slots. Each names the schema its evidence must satisfy, which is
    committed law rather than an engine constant (custos-4.2.md:1946-1951)."""
    return [
        {"endorser": endorser, "weight": weight, "schema": SCHEMA}
        for endorser, weight in pairs
    ]


def clause(ident, governs, *pairs):
    group = {"operator": "MxN", "slots": slots(*pairs)}
    return {"id": ident, "governs": governs, "group": group}


GAID = "acme:gaid"
MARTA, DEV, NINA = "acme:marta", "acme:dev", "acme:nina"

#: What every slot below names as the schema its evidence must satisfy.
SCHEMA = ENDORSEMENT_SCHEMA

#: The act class Acme's amendment clause governs, in both editions.
AMEND = "amend-operating-agreement"

#: What the ordinary-acts clause governs once the board is seated.
ORDINARY = ["open-bank-account", "hire-vp-sales", "approve-budget"]


def enactment(said, position, clauses, act=AMEND):
    """A law event that commits ``clauses`` and performs the act class ``act``.

    ``act`` is the field the law fold now reads: an enactment is an act, judged
    like any other, so it names a class of act for a clause to govern. Passing
    ``None`` omits the field, which is the fail-closed case.
    """
    body = {"i": GAID, "law": {"clauses": clauses}}
    if act is not None:
        body["act"] = act
    return Event(said=said, kind="enactment", position=position, body=body)


def endorsement(said, position, endorser, subject, disposition="endorse"):
    """A committed endorsement of ``subject``, shaped as the slot predicate reads it.

    Every conjunct of ``utina.fold.slots`` has to hold or the slot classifies
    PENDING and the amendment below never takes force, so this helper is the
    predicate's shape rather than a sketch of it.
    """
    return Event(
        said=said,
        kind="endorsement",
        position=position,
        body={
            "i": endorser,
            "acdc": {
                "i": endorser,
                "s": ENDORSEMENT_SCHEMA,
                "a": {"said": subject, "act": "issue", "disp": disposition},
            },
        },
    )


def retraction(said, position, endorser, target):
    """``endorser`` withdrawing the act ``target``."""
    return Event(
        said=said, kind="retraction", position=position, body={"i": endorser, "revokes": target}
    )


#: Acme's founding law: two founders, both required, for ordinary acts and for
#: amending the operating agreement alike.
STATE_ONE = [
    clause("A1", ORDINARY[:2], (MARTA, "1/2"), (DEV, "1/2")),
    clause("A2", [AMEND], (MARTA, "1/2"), (DEV, "1/2")),
]

#: After the board is seated: ordinary authority is distributed so any two reach
#: unity, and the bar for amending the agreement is retained at all three. That
#: retained bar is the point of the whole demo.
STATE_TWO = [
    clause("B1", ORDINARY, (MARTA, "1/2"), (DEV, "1/2"), (NINA, "1/2")),
    clause("B2", [AMEND], (MARTA, "1/3"), (DEV, "1/3"), (NINA, "1/3")),
]

#: The five coordinates the succession turns on. ``AMENDMENT`` is where the
#: amendment is committed, ``HALF_ENDORSED`` where one founder has endorsed it and
#: unity is not yet reached, and ``AFFIRMED`` where the second endorsement reaches
#: it — the effectuation coordinate, and the first position the board law governs.
INCEPTION, AMENDMENT = Position(0), Position(4)
HALF_ENDORSED, AFFIRMED, LATER = Position(5), Position(6), Position(7)

SEAT_BOARD = "E4-seat-board"

EVENTS = [
    Event(
        said="E0-inception",
        kind="inception",
        position=INCEPTION,
        body={"law": {"clauses": STATE_ONE}},
    ),
    enactment(SEAT_BOARD, AMENDMENT, STATE_TWO),
    endorsement("E5-marta-endorses", HALF_ENDORSED, MARTA, SEAT_BOARD),
    endorsement("E6-dev-endorses", AFFIRMED, DEV, SEAT_BOARD),
]


def corpus(events=None):
    return Corpus.load(events if events is not None else EVENTS)


def amended_by(amendment):
    """The standard record with ``amendment`` in place of the one that seats the board.

    Both endorsements are kept, so what each case below varies is the amendment
    itself and never the evidence for it.
    """
    return corpus([EVENTS[0], amendment, *EVENTS[2:]])


def ids(law):
    return [clause.id for clause in law.clauses]


# --- Succession: the centerpiece ---------------------------------------------


def test_the_founding_law_is_in_force_at_its_own_coordinate():
    """Genesis is constructed rather than judged (2272-2274), so it binds at once."""
    assert ids(Constitution.at(corpus(), INCEPTION)) == ["A1", "A2"]


def test_the_amendment_is_judged_under_the_law_it_replaces():
    """2270-2272: law never applies to itself at a coordinate, only to its successor."""
    law = Constitution.at(corpus(), AMENDMENT)
    assert ids(law) == ["A1", "A2"]
    assert law.governing(AMEND).id == "A2"


def test_the_amendment_binds_every_position_after_it_is_affirmed():
    """3001-3003, at keyword force: law for every position at and after effectuation."""
    assert ids(Constitution.at(corpus(), LATER)) == ["B1", "B2"]


# --- Effectuation: force follows affirmation, never commitment (Q33) ---------


def test_an_enactment_does_not_take_force_until_it_is_affirmed():
    """The bug this pins shut: at HALF_ENDORSED the amendment is committed and short.

    Marta has endorsed it and Dev has not, so it holds 1/2 of a clause needing
    unity. An engine keying force on commitment has the board law governing here —
    one event before the amendment enacting it carries — and every question asked
    at this coordinate is then answered under a law nobody has yet enacted.
    """
    law = Constitution.at(corpus(), HALF_ENDORSED)
    assert ids(law) == ["A1", "A2"]
    assert law.governing("hire-vp-sales").id == "A1"


def test_an_enactment_takes_force_at_the_coordinate_it_is_affirmed():
    """Q33 reading B: the effectuation coordinate is where unity is reached, not after it.

    Dev's endorsement at AFFIRMED brings the amendment to unity, so the board law
    governs from that coordinate. Under the reading that binds strictly afterwards
    the coordinate seating the board is a coordinate the board's law does not
    govern, and nothing committed marks that distinction.
    """
    law = Constitution.at(corpus(), AFFIRMED)
    assert ids(law) == ["B1", "B2"]
    assert law.governing("approve-budget").id == "B1"


def test_an_enactment_nobody_endorses_never_takes_force():
    """The unilateral amendment. 214-215: an enactment is judged like any other act."""
    assert ids(Constitution.at(corpus(EVENTS[:2]), LATER)) == ["A1", "A2"]


def test_a_defeated_enactment_never_takes_force():
    """Dev signs a declination, unity is unreachable, and the law does not move.

    1796-1800's defeat annihilating upward, applied to the one thing an enactment
    builds: a defeated amendment leaves no edition behind it.
    """
    declined = endorsement("E6-dev-declines", AFFIRMED, DEV, SEAT_BOARD, "decline")
    defeated = corpus([*EVENTS[:3], declined])
    assert ids(Constitution.at(defeated, LATER)) == ["A1", "A2"]


def test_an_enactment_naming_no_act_class_never_takes_force():
    """Fail closed: no act class means no clause can govern it, so nothing judged it."""
    classless = amended_by(enactment(SEAT_BOARD, AMENDMENT, STATE_TWO, act=None))
    assert ids(Constitution.at(classless, LATER)) == ["A1", "A2"]
    empty = amended_by(enactment(SEAT_BOARD, AMENDMENT, STATE_TWO, act=""))
    assert ids(Constitution.at(empty, LATER)) == ["A1", "A2"]


def test_an_enactment_no_clause_governs_never_takes_force():
    """An amendment claiming an act class the law in force rules nowhere.

    The engine refuses to legislate the missing rule here exactly as the evaluator
    does (1896-1902): with no clause there is no threshold, so there is nothing an
    endorsement could satisfy, and an edition that could take force on an
    ungoverned class would be a law changed by an act no law authorized.
    """
    ungoverned = amended_by(enactment(SEAT_BOARD, AMENDMENT, STATE_TWO, "declare-dividend"))
    assert ids(Constitution.at(ungoverned, LATER)) == ["A1", "A2"]


def test_an_amendment_that_carried_stays_in_force_when_its_endorser_withdraws():
    """1698-1712: evidence does not un-arrive, and an edition in force stays in force.

    The amendment reaches unity at AFFIRMED. Dev then withdraws the endorsement
    that carried it, and the board law is still the law — twice over. The
    withdrawal never reaches the enactment, because the enactment had settled
    (@nuxitore); and force is keyed to the first coordinate at which unity was
    reached, so even an honored withdrawal would not unmake it (@xhtvuxnc).
    """
    withdrawn = corpus([*EVENTS, retraction("E7-dev-retracts", LATER, DEV, "E6-dev-endorses")])
    assert ids(Constitution.at(withdrawn, Position(8))) == ["B1", "B2"]


def test_an_amendment_that_carried_stays_in_force_when_an_endorser_then_declines():
    """Effectuation is a coordinate the record fixes, not a condition law keeps meeting.

    A signed declination is decisive whatever the committed order, so over the
    bundle at Position(8) the amendment's group does not hold unity: Dev's slot
    is spent rather than endorsed. The board law is in force regardless, because
    the enactment carried at a coordinate and nothing later moves that fact. The
    withdrawal above cannot make this case, since a withdrawal after settlement
    never reaches the slot at all — a declination does.
    """
    reversed_later = corpus(
        [*EVENTS, endorsement("E7-dev-declines", LATER, DEV, SEAT_BOARD, "decline")]
    )
    assert ids(Constitution.at(reversed_later, Position(8))) == ["B1", "B2"]


def test_an_enactment_is_judged_under_the_law_in_force_at_its_own_coordinate():
    """The retained bar doing work, one edition deeper.

    A second amendment, committed after the board is seated, is judged under B2 —
    three slots at a third, so both founders together do not reach unity — and not
    under the A2 it would have cleared before the board existed. So the law that
    judges an enactment is itself computed from an affirmation, which is the
    recursion the succession rule now carries.
    """
    third = [
        clause("C1", ORDINARY, (MARTA, "1/1")),
        clause("C2", [AMEND], (MARTA, "1/1")),
    ]
    second = "E7-second-amendment"
    founders_only = [
        *EVENTS,
        enactment(second, LATER, third),
        endorsement("E8-marta-endorses-again", Position(8), MARTA, second),
        endorsement("E9-dev-endorses-again", Position(9), DEV, second),
    ]
    assert ids(Constitution.at(corpus(founders_only), Position(9))) == ["B1", "B2"]

    seated = endorsement("Ea-nina-endorses", Position(10), NINA, second)
    assert ids(Constitution.at(corpus([*founders_only, seated]), Position(10))) == ["C1", "C2"]


def test_succession_is_never_retroactive():
    """The same corpus, read at an earlier position, still yields the earlier law."""
    assert Constitution.at(corpus(), Position(3)).clauses == Constitution.at(
        corpus(), INCEPTION
    ).clauses


def test_an_amendment_replaces_the_edition_rather_than_adding_to_it():
    """Otherwise A1 and B1 both govern ordinary acts and governing() has two answers."""
    law = Constitution.at(corpus(), LATER)
    assert law.governing("open-bank-account").id == "B1"
    assert ids(law) == ["B1", "B2"]


def test_the_retained_bar_survives_the_amendment():
    before = Constitution.at(corpus(), AMENDMENT)
    after = Constitution.at(corpus(), LATER)
    assert before.clause("A2").group.satisfied_by({MARTA, DEV})
    assert after.clause("B1").group.satisfied_by({MARTA, NINA})
    assert not after.clause("B2").group.satisfied_by({MARTA, NINA})
    assert after.clause("B2").group.satisfied_by({MARTA, DEV, NINA})


# --- governing(): the refusal hinge, so it must be exact ----------------------


def test_governing_names_the_clause_ruling_an_act_kind():
    assert Constitution.at(corpus(), INCEPTION).governing("hire-vp-sales").id == "A1"


def test_an_ungoverned_act_kind_is_none_not_a_clause():
    """None is what makes an ungoverned question a refusal rather than a finding."""
    assert Constitution.at(corpus(), LATER).governing("declare-dividend") is None


def test_a_corpus_with_no_committed_law_governs_nothing():
    empty = Corpus.load([Event(said="E1", kind="act", position=Position(1), body={})])
    law = Constitution.at(empty, LATER)
    assert law.clauses == ()
    assert law.governing("open-bank-account") is None


# --- clause() ------------------------------------------------------------------


def test_clause_returns_the_clause_in_force():
    assert Constitution.at(corpus(), INCEPTION).clause("A1").id == "A1"


def test_a_clause_the_law_in_force_does_not_define_refuses():
    """B2 exists, but not yet.

    The code is the contract's, ``e.rule.clause-unknown.f``: governance rules
    live under ``rule``, and a clause id is the identity of a governance rule.
    """
    with pytest.raises(BakoboError) as raised:
        Constitution.at(corpus(), INCEPTION).clause("B2")
    assert raised.value.code == "e.rule.clause-unknown.f"
    assert "B2" in str(raised.value)


# --- Canonical bytes: binding at 3101 ------------------------------------------


def test_permuted_arrival_folds_to_byte_identical_constitutions():
    """The binding obligation of 3101. Byte-identical, not merely equivalent."""
    straight = Constitution.at(corpus(EVENTS), LATER).canonical_bytes()
    for permutation in itertools.permutations(EVENTS):
        assert Constitution.at(corpus(list(permutation)), LATER).canonical_bytes() == straight


def test_the_law_head_is_derived_from_the_canonical_bytes():
    """C14/G7: a law head is derivable as the fold of the designated GEL."""
    law = Constitution.at(corpus(), LATER)
    assert law.law_head.said
    assert law.law_head == Constitution.at(corpus(), LATER).law_head


def test_a_different_law_has_a_different_head():
    before = Constitution.at(corpus(), AMENDMENT)
    after = Constitution.at(corpus(), LATER)
    assert before.law_head != after.law_head
    assert before.canonical_bytes() != after.canonical_bytes()


def test_clause_sub_blocks_are_ordered_by_clause_said():
    """Our concatenation order, and 1478-1481 confesses that it is ours to choose."""
    law = Constitution.at(corpus(), LATER)
    by_said = sorted(law.clauses, key=lambda c: c.said())
    assert law.canonical_bytes() == b"\x1e".join(c.sub_block() for c in by_said)
    # The order is the SAIDs' order, which is not the order the clauses were
    # committed in unless the digests happen to agree with it.
    assert [c.said() for c in by_said] == sorted(c.said() for c in law.clauses)


# --- A committed edition that cannot be read as law ---------------------------


def test_two_clauses_governing_one_act_kind_refuse():
    """An uncommitted precedence seam. 1874-1876: refuse, never legislate."""
    both = [
        clause("C1", ["approve-budget"], (MARTA, "1/1")),
        clause("C2", ["approve-budget"], (DEV, "1/1")),
    ]
    conflicted = Corpus.load(
        [
            Event(
                said="E0",
                kind="inception",
                position=INCEPTION,
                body={"law": {"clauses": both}},
            )
        ]
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(conflicted, INCEPTION)
    assert raised.value.code == "e.state.clause-ambiguous.f"
    assert "approve-budget" in str(raised.value)


def test_one_clause_id_committed_twice_refuses():
    twice = [
        clause("C1", ["approve-budget"], (MARTA, "1/1")),
        clause("C1", ["hire-vp-sales"], (DEV, "1/1")),
    ]
    conflicted = Corpus.load(
        [
            Event(
                said="E0",
                kind="inception",
                position=INCEPTION,
                body={"law": {"clauses": twice}},
            )
        ]
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(conflicted, INCEPTION)
    assert raised.value.code == "e.state.clause-ambiguous.f"
    assert "C1" in str(raised.value)


def test_a_law_event_whose_clauses_are_not_a_list_refuses():
    broken = Corpus.load(
        [
            Event(
                said="E0",
                kind="inception",
                position=INCEPTION,
                body={"law": {"clauses": "A1"}},
            )
        ]
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(broken, INCEPTION)
    assert raised.value.code == "e.input.malformed.law.f"


def test_a_law_event_with_no_clauses_field_refuses():
    broken = Corpus.load(
        [Event(said="E0", kind="inception", position=INCEPTION, body={"law": {}})]
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(broken, INCEPTION)
    assert raised.value.code == "e.input.malformed.law.f"
    assert "clauses" in str(raised.value)


def test_a_law_event_carrying_no_law_at_all_refuses():
    """The envelope seam: the law body sits under ``law``, not at the body's root.

    A law event that carries no law is bytes claiming to be an enactment and
    committing nothing, which is refused rather than read as an empty edition —
    an empty edition governs nothing and would silently turn every question into
    a refusal.
    """
    broken = Corpus.load([Event(said="E0", kind="inception", position=INCEPTION, body={})])
    with pytest.raises(BakoboError) as raised:
        Constitution.at(broken, INCEPTION)
    assert raised.value.code == "e.input.malformed.law.f"
    assert "law" in str(raised.value)
