"""The display plane's alias table: what a party is called, and what it is not.

Two properties carry the whole decision, and both are asserted here rather than left
to the renderer. An alias is display-only (this.i @cldspl): ``tests/test_purity.py``
enforces the structural half, that nothing below the display plane can import the
machinery, and this file enforces the behavioural half, that the table is a function
of the identifiers inception returned and of nothing else. And both substrates render
identically (this.i @clcoia), which is the point of aliasing at all — under the facade
an identifier reads like a name by coincidence, under keripy it is a 44-character
prefix, and the audience should not be able to tell which from the screen.
"""

from __future__ import annotations

from typing import Any

import pytest
from bakobo.errors import BakoboError  # type: ignore[import-untyped]

from utina import acme, coia
from utina.acme import DEV, DEVICE, GAID, MARTA, QUINN, SEAT
from utina.cli.aliases import PARTIES, SCOPE, Aliases, aliases_over
from utina.cli.render import SLOT
from utina.cli.world import DOMAINS, world
from utina.fold.constitution import Constitution

#: What the demo's three people must be called on screen, in both forms. Written out
#: rather than computed, because a test that built its expectation the way the code
#: does would pass against any self-consistent mistake.
FULL = {
    MARTA: "marta-founder-acme,6",
    DEV: "dev-founder-acme,6",
    SEAT: "nina-board-seat-3-acme,6",
}

SHORT = {
    MARTA: "marta-founder,6",
    DEV: "dev-founder,6",
    SEAT: "nina-board-seat-3,6",
}


@pytest.fixture(scope="session")
def facade_aids() -> dict[str, str]:
    with world("facade") as record:
        return dict(record.aids)


@pytest.fixture(scope="session")
def keripy_aids() -> dict[str, str]:
    with world("keripy") as record:
        return dict(record.aids)


@pytest.fixture
def table(facade_aids: dict[str, str]) -> Aliases:
    return aliases_over(facade_aids, acme.DOMAIN)


# --- the aliases themselves ---------------------------------------------------


@pytest.mark.parametrize("party", sorted(FULL), ids=sorted(FULL))
def test_a_party_carries_the_alias_the_commission_specified(
    table: Aliases, facade_aids: dict[str, str], party: str
) -> None:
    assert table.full(facade_aids[party]) == FULL[party]
    assert table.short(facade_aids[party]) == SHORT[party]


def test_the_short_form_is_the_full_form_with_the_scope_dropped() -> None:
    """Not a truncation of the alias: COIA's empty-scope form is an alias in itself."""
    for party, full in FULL.items():
        # COIA 2.0 puts the flag group last, so the scope is inserted before it
        # rather than appended: marta-founder,6 becomes marta-founder-acme,6.
        body, _, flags = SHORT[party].partition(",")
        assert full == f"{body}-{SCOPE.lower()},{flags}"
        assert "..." not in full and "..." not in SHORT[party]


def test_the_short_form_fits_the_slot_column() -> None:
    """@clscop: eighteen characters is the column budget the table already had."""
    assert max(len(short) for short in SHORT.values()) <= SLOT


@pytest.mark.parametrize("domain", sorted(DOMAINS), ids=sorted(DOMAINS))
def test_every_slot_any_domain_commits_fits_the_slot_column(domain: str) -> None:
    """The guard above is Acme's pinned table; this one is every domain that exists.

    A second domain whose slotted parties overflowed the column would be TRUNCATED on
    screen rather than refused, and a truncated alias beside a name is the thing
    @clcoia exists to remove. Widening ``SLOT`` is not the remedy — it would move every
    tracked demo artifact to make room for a fixture — so a cast that does not fit is a
    cast to reword.

    What is checked is what a slot can NAME, read off each domain's own committed law
    at the end of its record, rather than every party in its cast: the governed domain
    itself is in every cast and is slotted by nobody, and its alias is deliberately the
    long scope-less form (``acme-governed-domain,6``) that no column has to hold.
    """
    with world(domain=domain) as record:
        table = aliases_over(record.aids, record.name)
        law = Constitution.at(record.corpus, record.at(str(record.last)))
        named = [
            slot.office or slot.endorser
            for clause in law.clauses
            for slot in clause.group.slots
        ]
        assert named, f"{domain} commits no slots, so this guard checks nothing"
        for one in named:
            short = table.short(one)
            assert len(short) <= SLOT, f"{short} is {len(short)} against {SLOT}"
            assert "..." not in short


def test_both_substrates_render_the_same_aliases(
    facade_aids: dict[str, str], keripy_aids: dict[str, str]
) -> None:
    """The whole point: a screen must not betray which substrate is underneath."""
    assert (
        aliases_over(facade_aids, acme.DOMAIN).every_alias()
        == aliases_over(keripy_aids, acme.DOMAIN).every_alias()
    )
    # And the identifiers really do differ, or the assertion above is vacuous.
    assert facade_aids[MARTA] != keripy_aids[MARTA]
    assert len(keripy_aids[MARTA]) == 44


def test_every_alias_is_a_well_formed_coia_alias(table: Aliases) -> None:
    for alias in table.every_alias():
        # Well-formed means it survives a parse/normalize round trip unchanged.
        body, flags, _ = coia.parse_alias(alias)
        assert coia.normalize(body) == body and flags == "6", alias


def test_every_alias_carries_the_demo_flag(table: Aliases) -> None:
    """@clflg9: flag 9 is deliberate, and a missing one would claim production use."""
    for alias in table.every_alias():
        assert alias.endswith(",6"), alias


def test_the_party_table_covers_exactly_what_acme_incepts(facade_aids: dict[str, str]) -> None:
    """A party with no entry would render as a raw identifier, which is a gap."""
    assert set(PARTIES) == set(facade_aids) == {GAID, MARTA, DEV, SEAT, DEVICE, QUINN}


def test_the_domain_itself_is_aliased_too(table: Aliases, facade_aids: dict[str, str]) -> None:
    assert table.full(facade_aids[GAID]) == "acme-governed-domain,6"


# --- the fallback, which must never truncate ----------------------------------


def test_an_identifier_with_no_alias_renders_as_itself_in_full() -> None:
    """An unlabelled party is shown whole, never shortened.

    A party outside the committed law cannot reach a screen today, because every slot
    names one of the four identifiers inception returned. The branch exists because
    both alternatives — inventing a label, or truncating the identifier — would
    reintroduce exactly what this commission removed.
    """
    stranger = "E" + "x" * 43
    empty = aliases_over({}, acme.DOMAIN)
    assert empty.full(stranger) == stranger
    assert empty.short(stranger) == stranger
    assert empty.every_alias() == ()


# --- lookup, under COIA's comparison rule -------------------------------------


@pytest.mark.parametrize("party", sorted(FULL), ids=sorted(FULL))
def test_both_forms_of_an_alias_resolve_to_the_same_party(
    table: Aliases, facade_aids: dict[str, str], party: str
) -> None:
    assert table.resolve(FULL[party]) == facade_aids[party]
    assert table.resolve(SHORT[party]) == facade_aids[party]


@pytest.mark.parametrize(
    "typed",
    [
        "marta-founder-acme,6",
        "Marta Founder Acme",
        "  MARTA-FOUNDER-ACME,6  ",
        "marta. founder  acme",
        # En dashes on purpose: the spec's permissive regex tolerates them because a
        # keyboard or an autocorrect will produce one where a hyphen was meant.
        "marta–founder–acme",  # noqa: RUF001
        "marta-founder-acme",
        "marta-founder",
    ],
    ids=[
        "canonical",
        "spaced-and-cased",
        "padded-upper",
        "punctuated",
        "en-dashes",
        "flag-omitted-scoped",
        "flag-omitted-short",
    ],
)
def test_a_typed_query_is_normalized_before_lookup(
    table: Aliases, facade_aids: dict[str, str], typed: str
) -> None:
    """COIA's Comparing section: a query is matched as if it had been normalized."""
    assert table.resolve(typed) == facade_aids[MARTA]


def test_an_identifier_prefix_still_resolves(
    table: Aliases, facade_aids: dict[str, str]
) -> None:
    """@clhndl's surviving half: a prefix is a good thing to type."""
    marta = facade_aids[MARTA]
    assert table.resolve(marta[:8]) == marta
    assert table.resolve(marta) == marta


def test_a_prefix_naming_two_parties_is_refused_rather_than_guessed(table: Aliases) -> None:
    with pytest.raises(BakoboError) as caught:
        table.resolve("acme:")
    assert caught.value.code == "e.input.multi.alias-prefix.f"
    assert not caught.value.retryable
    assert "acme:" in str(caught.value.detail)


def test_an_unflagged_alias_is_accepted_on_input_but_never_displayed(
    table: Aliases, facade_aids: dict[str, str]
) -> None:
    """The flag is part of the alias; dropping it is tolerated only on the query.

    An unflagged alias is what COIA reserves for a verified, public, production
    identifier, which is the one thing Acme's must never appear to claim (@clflg9).
    """
    assert table.resolve("marta-founder-acme") == facade_aids[MARTA]
    assert all(alias.endswith(",6") for alias in table.every_alias())
    assert "marta-founder-acme" not in table.every_alias()


def test_a_query_naming_nothing_resolves_to_nothing(table: Aliases) -> None:
    """None rather than an exception: the caller decides what a miss means."""
    assert table.resolve("nobody-nothing,6") is None
    assert table.resolve("") is None


def test_the_aliases_come_back_in_a_stable_order(table: Aliases) -> None:
    """The law screen header lists them, so the order may not depend on a dict's luck."""
    listed = table.every_alias()
    assert listed == tuple(sorted(listed))
    assert len(listed) == len(set(listed)) == len(PARTIES)


def test_the_table_is_built_from_identifiers_and_carries_no_record(
    table: Aliases, facade_aids: dict[str, str]
) -> None:
    """@cldspl, behaviourally: aliases_over sees identifiers, never committed events."""
    rebuilt: Any = aliases_over(dict(facade_aids), acme.DOMAIN)
    assert rebuilt.every_alias() == table.every_alias()
    assert rebuilt.scope == SCOPE


def test_a_query_with_a_malformed_flag_group_resolves_to_nothing(table: Aliases) -> None:
    """A miss, never an error. The caller decides whether an unmatched query refuses.

    COIA's reader raises on a flag group that is not decimal digits, and a person
    typing at a prompt produces those by accident — a trailing comma, a stray word
    after one. Letting that escape would turn a typo into a traceback.
    """
    assert table.resolve("marta-founder-acme,nonsense") is None
    assert table.resolve("marta-founder-acme,9x") is None

    # A trailing comma is an EMPTY flag group, which is well formed, so it resolves.
    # The distinction matters: one is a typo and the other is a person declining to
    # type a flag they were never required to type.
    assert table.resolve("marta-founder-acme,") is not None
