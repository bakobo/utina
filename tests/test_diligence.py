"""Diligence: whether a domain checked that its counterparty could lawfully act.

The whole of this mechanism is that the answer is **recomputed and never retrieved**
(``this.i`` @fsbgamvi). ``custos-4.2.md:2067`` admits an evaluation seal "only over
verifiable algorithms ... Commit predicates, never verdicts. A sealed verdict a stranger
cannot recompute is smuggled authority." So the tests that matter most here are the
tamper cases below: each leaves the seal well-formed and changes one term it names, and
each must stop the act carrying. A seal the fold merely trusted would survive all of
them.

Everything else is the fail-closed surface. A seal that is malformed, whose evidence
does not reconstruct, or whose schema is not the one the law asked for, leaves the
requirement outstanding rather than raising — the effect does not land, and the finding
says what is missing.
"""

from __future__ import annotations

from dataclasses import replace

import pytest
from bakobo.errors import BakoboError

from utina import bank
from utina.cli.appraisal import diligence_behind
from utina.cli.world import world
from utina.fold import diligence
from utina.fold.constitution import Constitution
from utina.fold.corpus import Corpus, Event
from utina.fold.evaluate import evaluate
from utina.fold.finding import Affirmed, Pending
from utina.fold.gel import anchored
from utina.fold.question import Committed, Proposal
from utina.fold.triple import Position

#: Where Meridian's seal sits in its own record, and the act it supports.
SEAL_AT = 5
ASK = Proposal(bank.OPEN_ACCOUNT)


@pytest.fixture(scope="module")
def meridian():
    """Meridian's record, with Acme's built first and handed to it."""
    with world(domain=bank.DOMAIN) as record:
        yield record


def resealed(record, **terms) -> Corpus:
    """Meridian's corpus with the seal's own terms changed and nothing else.

    The event keeps its shape, its kind and its place; only what it CLAIMS moves. That
    is the point: a fold that trusted the seal would answer the same either way.
    """
    events = list(record.events)
    seal = {**events[SEAL_AT].body[diligence.SEAL_FIELD], **terms}
    events[SEAL_AT] = replace(
        events[SEAL_AT], body={**events[SEAL_AT].body, diligence.SEAL_FIELD: seal}
    )
    return anchored(events, record.kel, gaid=record.gaid)


def verdict(corpus: Corpus, record) -> str:
    return type(evaluate(corpus, ASK, at=record.values.position(record.last))).__name__


# --- the claim: the answer is recomputed ---------------------------------------


def test_the_act_carries_once_the_diligence_is_committed(meridian) -> None:
    assert verdict(meridian.corpus, meridian) == "Affirmed"


def test_the_act_is_pending_at_the_coordinate_before_the_seal(meridian) -> None:
    """The certification is already in by then. A count is not the whole requirement."""
    outcome = evaluate(meridian.corpus, ASK, at=Position(seq=SEAL_AT - 1))
    assert isinstance(outcome, Pending)
    assert [one.kind for one in outcome.requirement] == [diligence.DILIGENCE_KIND]


@pytest.mark.parametrize(
    ("term", "value"),
    [
        (diligence.HEAD_FIELD, "0" * 64),
        (diligence.CLAUSE_FIELD, "A2"),
        (diligence.SUBJECT_FIELD, "Enot-a-committed-subject"),
        (diligence.COORDINATE_FIELD, 3),
        (diligence.DOMAIN_FIELD, "somebody-else"),
    ],
    ids=["law-head", "clause", "subject", "coordinate", "counterparty"],
)
def test_a_seal_that_misnames_any_of_its_own_terms_stops_the_act_carrying(
    meridian, term, value
) -> None:
    """The five tampers, and the reason this mechanism is not a rubber stamp.

    ``clause`` is the one that caught a real defect. An earlier draft checked only that
    the named clause EXISTED in the counterparty's edition, so a seal over Acme's bank
    account relabelled to clause A2 still affirmed — A2 is a real clause of that
    edition and nothing tied it to the subject. The check is now that the named clause
    is the one the affirmation actually cites.
    """
    assert verdict(resealed(meridian, **{term: value}), meridian) == "Pending"


def test_the_committed_seal_carries_no_verdict_field_at_all(meridian) -> None:
    """@gsli4bea, and the half of it a later maintainer would undo first.

    Not "the verdict is ignored" but "there is no verdict to ignore". Asserted over the
    whole committed body rather than over a field list, so a verdict smuggled in under
    any name fails here.
    """
    body = meridian.events[SEAL_AT].body
    seal = body[diligence.SEAL_FIELD]
    assert set(seal) == {
        diligence.SCHEMA_FIELD,
        diligence.DOMAIN_FIELD,
        diligence.COORDINATE_FIELD,
        diligence.HEAD_FIELD,
        diligence.CLAUSE_FIELD,
        diligence.SUBJECT_FIELD,
    }
    flattened = repr(body).lower()
    for word in ("affirmed", "verdict", "result", "approved", "outcome"):
        assert word not in flattened, f"the seal says {word!r} somewhere"


def test_the_admitted_evidence_folds_to_the_counterpartys_own_answer(meridian) -> None:
    """The stranger's path, walked: one log, no access to Acme, same answer.

    This is what the beat claims and it is worth asserting separately from the
    evaluator, because the evaluator could be right for the wrong reason.
    """
    recomputed = diligence.recomputable(meridian.events[SEAL_AT])
    assert recomputed is not None
    corpus, subject, at, clause, head = recomputed
    law = Constitution.at(corpus, at)
    assert law.law_head.said == head
    outcome = evaluate(corpus, Committed(subject), at=at)
    assert isinstance(outcome, Affirmed)
    assert clause in outcome.clauses


def test_neither_domain_names_anything_of_the_others_in_its_law(meridian) -> None:
    """@rc5fibel: what crosses the boundary is a result, never a constitution."""
    theirs = Constitution.at(meridian.corpus, meridian.values.position(meridian.last))
    written = repr([(one.id, one.governs, one.group) for one in theirs.clauses])
    with world() as acme:
        assert "open-bank-account" not in written, "Meridian's law names the customer's act"
        assert acme.gaid not in written, "Meridian's law names the customer"
        theirs_law = Constitution.at(acme.corpus, acme.at("d1"))
    ours = repr([(one.id, one.governs, one.group) for one in theirs_law.clauses])
    assert bank.OPEN_ACCOUNT not in ours, "the customer's law names Meridian's act"
    assert meridian.gaid not in ours, "the customer's law names Meridian"


# --- the law's own field --------------------------------------------------------


def test_a_law_naming_no_diligence_schema_owes_none() -> None:
    """Acme's does not, and Acme's acts carry on their certification alone."""
    with world() as acme:
        law = Constitution.at(acme.corpus, acme.at("d1"))
    assert law.diligence is None
    assert not diligence.unreadable_in({})


def test_a_law_whose_diligence_field_is_unreadable_refuses_the_edition() -> None:
    """Present-and-unreadable refuses rather than exempting.

    The same fail-open the certification field already closed: a domain that could
    switch off its own obligation to look at a counterparty with a typo has an
    obligation in name only.
    """
    assert diligence.unreadable_in({diligence.REQUIRES_FIELD: {"schema": "E0"}})
    assert diligence.unreadable_in({diligence.REQUIRES_FIELD: ""})
    assert not diligence.unreadable_in({diligence.REQUIRES_FIELD: "Eschema"})

    founding = Event(
        said="E0-inception",
        kind="inception",
        position=Position(seq=0),
        body={"law": {"clauses": (), diligence.REQUIRES_FIELD: {"schema": "Erequired"}}},
    )
    with pytest.raises(BakoboError) as raised:
        Constitution.at(Corpus.load([founding]), Position(seq=0))
    assert raised.value.code == "e.input.malformed.law.f"


# --- the fail-closed surface ----------------------------------------------------


def seal_event(**body) -> Event:
    return Event(
        said="Eseal", kind=diligence.EVALUATION_KIND, position=Position(seq=1), body=body
    )


def test_a_seal_for_another_subject_or_another_schema_is_not_this_ones(meridian) -> None:
    corpus, at = meridian.corpus, meridian.values.position(meridian.last)
    schema = Constitution.at(corpus, at).diligence
    assert schema is not None
    own = meridian.events[SEAL_AT].body[diligence.SUPPORTS_FIELD]
    assert diligence.sealing(corpus, own, at, schema) is not None
    assert diligence.sealing(corpus, "Esomething-else", at, schema) is None
    assert diligence.sealing(corpus, own, at, "Eanother-schema") is None


@pytest.mark.parametrize(
    "body",
    [
        {},
        {diligence.SEAL_FIELD: "not a mapping"},
        {diligence.SEAL_FIELD: {}, diligence.EVIDENCE_FIELD: "not a mapping"},
        {diligence.SEAL_FIELD: {}, diligence.EVIDENCE_FIELD: {}},
        {
            diligence.SEAL_FIELD: {diligence.DOMAIN_FIELD: 7},
            diligence.EVIDENCE_FIELD: {diligence.EVENTS_FIELD: (), diligence.KEL_FIELD: ()},
        },
        {
            diligence.SEAL_FIELD: {diligence.DOMAIN_FIELD: "Edomain"},
            diligence.EVIDENCE_FIELD: {
                diligence.EVENTS_FIELD: ("not a mapping",),
                diligence.KEL_FIELD: (),
            },
        },
        {
            diligence.SEAL_FIELD: {diligence.DOMAIN_FIELD: "Edomain"},
            diligence.EVIDENCE_FIELD: {
                diligence.EVENTS_FIELD: ({"said": 1, "kind": "act", "seq": 0, "body": {}},),
                diligence.KEL_FIELD: (),
            },
        },
        {
            diligence.SEAL_FIELD: {diligence.DOMAIN_FIELD: "Edomain"},
            diligence.EVIDENCE_FIELD: {
                diligence.EVENTS_FIELD: (
                    {"said": "E1", "kind": "act", "seq": "0", "body": {}},
                ),
                diligence.KEL_FIELD: (),
            },
        },
        {
            diligence.SEAL_FIELD: {diligence.DOMAIN_FIELD: "Edomain"},
            diligence.EVIDENCE_FIELD: {
                diligence.EVENTS_FIELD: ({"said": "E1", "kind": "act", "seq": 0, "body": {}},),
                diligence.KEL_FIELD: (),
            },
        },
    ],
    ids=[
        "no-seal",
        "seal-not-a-mapping",
        "evidence-not-a-mapping",
        "evidence-block-empty",
        "domain-not-a-string",
        "event-not-a-mapping",
        "said-not-a-string",
        "seq-not-an-integer",
        "evidence-that-will-not-fold",
    ],
)
def test_evidence_that_does_not_reconstruct_supports_nothing(body) -> None:
    """Every shape a malformed seal can take answers ``None`` rather than raising.

    A malformed seal is an act that fails to authorize, never an error in the question
    somebody asked. The last case is the one that matters most: the evidence is
    well-formed and simply does not fold, and ``anchored``'s coded refusal is caught
    where every other refusal here is swallowed.
    """
    assert diligence.evidence_of(seal_event(**body)) is None
    assert diligence.recomputable(seal_event(**body)) is None


@pytest.mark.parametrize(
    "terms",
    [
        {diligence.SUBJECT_FIELD: 7},
        {diligence.COORDINATE_FIELD: "four"},
        {diligence.CLAUSE_FIELD: 7},
        {diligence.HEAD_FIELD: 7},
    ],
    ids=["subject", "coordinate", "clause", "head"],
)
def test_a_seal_whose_terms_are_the_wrong_shape_recomputes_to_nothing(
    meridian, terms
) -> None:
    """Sound evidence, unusable terms. The shape check is separate from the fold's."""
    corpus = resealed(meridian, **terms)
    assert diligence.recomputable(corpus.upto(Position(seq=SEAL_AT))[SEAL_AT]) is None
    assert verdict(corpus, meridian) == "Pending"


# --- the evidence slice ---------------------------------------------------------


def test_the_admitted_key_log_stops_at_the_coordinate_relied_on(meridian) -> None:
    """A bank does not take a copy of the file it has not read.

    And it must not stop one event short either: the fold derives membership from the
    key log's seals, so a slice cut early presents a record whose last event nothing
    anchored.
    """
    evidence = meridian.events[SEAL_AT].body[diligence.EVIDENCE_FIELD]
    admitted = evidence[diligence.EVENTS_FIELD]
    with world() as acme:
        relied_on = acme.at(bank.CUSTOMER_COORDINATE).seq
        assert len(acme.events) > len(admitted), "the whole log was admitted"
    assert [one["seq"] for one in admitted] == list(range(relied_on + 1))
    assert diligence.evidence_of(meridian.events[SEAL_AT]) is not None


def test_the_key_log_slice_keeps_everything_when_nothing_seals_that_far() -> None:
    """Three edges of the slice, none of them reachable through a real record.

    A key event carrying no seal list is skipped rather than read — the GEL and the KEL
    run on separate clocks and a rotation may seal nothing at all. A coordinate no key
    event reaches keeps the whole log, which is the honest answer: everything that
    exists was relied on, and the fold refuses it if that is not enough. And a seal
    list that is not a list is not one.
    """
    from utina.bank.build import _kel_upto

    unsealed = {"t": "icp"}
    sealing = {"t": "ixn", "a": [{"i": "Egel", "s": "2", "d": "Eevent"}]}
    malformed = {"t": "ixn", "a": "not a list"}
    assert _kel_upto([unsealed, sealing], 2) == (unsealed, sealing)
    assert _kel_upto([unsealed, sealing], 99) == (unsealed, sealing)
    assert _kel_upto([sealing], 1) == (sealing,)
    assert _kel_upto([malformed], 0) == (malformed,)


# --- the screen -----------------------------------------------------------------


def test_the_affirmed_screen_shows_what_was_checked_and_what_it_refolds_to() -> None:
    """The composition has to be visible on the screen built to display it.

    Before this block the affirmation named Meridian's own clause and its own two
    endorsements and nothing else, so a room looking at the one screen where two
    organizations meet saw no trace of the second one.
    """
    out = _screen("eval", bank.OPEN_ACCOUNT, "--domain", bank.DOMAIN, "--at", "5")
    assert "diligence - what this domain checked before acting" in out
    assert "acme-customer,6" in out
    assert "under their clause A1" in out
    assert "of their committed events, and their key log" in out
    assert "refolds to    AFFIRMED" in out


def test_the_screen_recomputes_rather_than_printing_what_the_seal_claimed(
    meridian,
) -> None:
    """A seal whose own terms do not hold up shows no block at all.

    Nothing is said twice: the finding is already PENDING and names the requirement, so
    a screen that also printed a diligence block would be reporting a check that did
    not pass as though it were working. And it cannot print the seal's claim instead,
    because the seal makes none (@gsli4bea).
    """
    corpus = resealed(meridian, **{diligence.HEAD_FIELD: "0" * 64})
    law = Constitution.at(corpus, meridian.values.position(meridian.last))
    subject = meridian.events[SEAL_AT].body[diligence.SUPPORTS_FIELD]
    behind = diligence_behind(
        corpus, law, subject, meridian.values.position(meridian.last)
    )
    assert behind is None


def test_a_domain_that_owes_no_diligence_shows_no_block() -> None:
    """Which is every domain but Meridian, so this is most screens."""
    out = _screen("eval", "--said", "open-bank-account", "--at", "d1")
    assert "AFFIRMED" in out
    assert "diligence" not in out


def _screen(*argv: str) -> str:
    from io import StringIO

    from utina.cli import Console, run

    out = StringIO()
    run(argv, Console(out=out, err=StringIO()))
    return out.getvalue()


# --- the law screen ---------------------------------------------------------------


def test_the_law_screen_names_the_terms_the_edition_commits() -> None:
    """A law is not only its clauses, and a screen calling itself "the law in force"
    that showed only clauses was showing part of a law and naming it the whole.

    Missing for certification since certification existed. It surfaced only when Act
    VI's narration promised a term the screen did not contain — a demo where the words
    and the screen disagree being the one failure the generated-and-pinned arrangement
    exists to prevent.
    """
    theirs = _screen("law", "--domain", "bank", "--at", "5")
    assert "a certification of the tally, by the domain itself" in theirs
    assert "diligence" in theirs

    ours = _screen("law", "--at", "inception")
    assert "a certification of the tally, by the domain itself" in ours
    assert "diligence" not in ours, "Acme owes none, and the screen should not imply it"


def test_an_edition_that_asks_for_neither_shows_no_terms_line() -> None:
    """Which keeps the line off every screen whose law has nothing extra to say."""
    from utina.cli.aliases import aliases_over
    from utina.cli.render import law_screen
    from utina.cli.style import Style

    # A real edition with both terms stripped, rather than a hand-built empty one: the
    # screen is exercised over a law that has clauses to draw, so what this asserts is
    # the absence of the line and not the absence of everything.
    with world(domain=bank.DOMAIN) as record:
        law = Constitution.at(record.corpus, record.values.position(record.last))
        bare = replace(law, certification=None, diligence=None)
        drawn = law_screen(
            bare,
            "5",
            record.values.position(record.last),
            aliases_over(record.aids, record.name),
            Style(False),
        )
    assert "clause M1" in drawn, "the screen still drew the law"
    assert "requires" not in drawn
