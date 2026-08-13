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

from utina import coia
from utina.acme import DEV, GAID, MARTA, NINA
from utina.cli.aliases import PARTIES, SCOPE, Aliases, aliases_over
from utina.cli.world import world

#: What the demo's three people must be called on screen, in both forms. Written out
#: rather than computed, because a test that built its expectation the way the code
#: does would pass against any self-consistent mistake.
FULL = {
    MARTA: "9-marta-as-founder-at-acme",
    DEV: "9-dev-as-founder-at-acme",
    NINA: "9-nina-as-director-at-acme",
}

SHORT = {
    MARTA: "9-marta-as-founder",
    DEV: "9-dev-as-founder",
    NINA: "9-nina-as-director",
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
    return aliases_over(facade_aids)


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
        assert full == f"{SHORT[party]}-at-{SCOPE.lower()}"
        assert "..." not in full and "..." not in SHORT[party]


def test_the_short_form_fits_the_slot_column() -> None:
    """@clscop: eighteen characters is the column budget the table already had."""
    assert max(len(short) for short in SHORT.values()) <= 18


def test_both_substrates_render_the_same_aliases(
    facade_aids: dict[str, str], keripy_aids: dict[str, str]
) -> None:
    """The whole point: a screen must not betray which substrate is underneath."""
    assert aliases_over(facade_aids).every_alias() == aliases_over(keripy_aids).every_alias()
    # And the identifiers really do differ, or the assertion above is vacuous.
    assert facade_aids[MARTA] != keripy_aids[MARTA]
    assert len(keripy_aids[MARTA]) == 44


def test_every_alias_is_a_well_formed_coia_alias(table: Aliases) -> None:
    for alias in table.every_alias():
        assert coia.matches_alias(alias), alias


def test_every_alias_carries_the_demo_flag(table: Aliases) -> None:
    """@clflg9: flag 9 is deliberate, and a missing one would claim production use."""
    for alias in table.every_alias():
        assert alias.startswith(f"{coia.FLAG_TEST}-"), alias


def test_the_party_table_covers_exactly_what_acme_incepts(facade_aids: dict[str, str]) -> None:
    """A party with no entry would render as a raw identifier, which is a gap."""
    assert set(PARTIES) == set(facade_aids) == {GAID, MARTA, DEV, NINA}


def test_the_domain_itself_is_aliased_too(table: Aliases, facade_aids: dict[str, str]) -> None:
    assert table.full(facade_aids[GAID]).startswith("9-acme-as-")


# --- the fallback, which must never truncate ----------------------------------


def test_an_identifier_with_no_alias_renders_as_itself_in_full() -> None:
    """An unlabelled party is shown whole, never shortened.

    A party outside the committed law cannot reach a screen today, because every slot
    names one of the four identifiers inception returned. The branch exists because
    both alternatives — inventing a label, or truncating the identifier — would
    reintroduce exactly what this commission removed.
    """
    stranger = "E" + "x" * 43
    empty = aliases_over({})
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
        "9-marta-as-founder-at-acme",
        "9 Marta as Founder at Acme",
        "  9-MARTA-AS-FOUNDER-AT-ACME  ",
        "9, marta. as founder at acme",
        # En dashes on purpose: the spec's permissive regex tolerates them because a
        # keyboard or an autocorrect will produce one where a hyphen was meant.
        "9–marta–as–founder–at–acme",  # noqa: RUF001
        "Marta as Founder at Acme",
        "marta-as-founder",
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
    assert table.resolve("marta-as-founder-at-acme") == facade_aids[MARTA]
    assert all(alias.startswith("9-") for alias in table.every_alias())
    assert "marta-as-founder-at-acme" not in table.every_alias()


def test_a_query_naming_nothing_resolves_to_nothing(table: Aliases) -> None:
    """None rather than an exception: the caller decides what a miss means."""
    assert table.resolve("9-nobody-as-nothing") is None
    assert table.resolve("") is None


def test_the_aliases_come_back_in_a_stable_order(table: Aliases) -> None:
    """The law screen header lists them, so the order may not depend on a dict's luck."""
    listed = table.every_alias()
    assert listed == tuple(sorted(listed))
    assert len(listed) == len(set(listed)) == 4


def test_the_table_is_built_from_identifiers_and_carries_no_record(
    table: Aliases, facade_aids: dict[str, str]
) -> None:
    """@cldspl, behaviourally: aliases_over sees identifiers, never committed events."""
    rebuilt: Any = aliases_over(dict(facade_aids))
    assert rebuilt.every_alias() == table.every_alias()
    assert rebuilt.scope == SCOPE
