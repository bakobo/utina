"""``--domain``, and the claim that no command depends on a hardcoded record.

M7's criterion, in the build plan's own words: ``utina eval --domain acme`` and
``--domain bank`` both resolve; no command depends on a hardcoded record; labels are
shown to be per-fixture rather than committed, so a domain with no label table is
addressed by sequence number and says so rather than failing obscurely.

The second domain is Meridian Bank, deliberately minimal and deliberately **not** the
two-constitution bank beat (``this.i`` @qprzacju). What it has to be, for these tests to
mean anything, is a record the fold was not written around: its own gAID, its own
committed law, its own parties, and real events driven through the same constructor
Acme's story drives. What it has to NOT have is labels, because a labelless domain is
the case @qtm5ntkg and @er57yvs7 exist to cover and a fixture that had them would leave
that case untested.
"""

from __future__ import annotations

from io import StringIO

import pytest
from bakobo.errors import BakoboError  # type: ignore[import-untyped]

from utina import acme, bank
from utina.cli import Console, run
from utina.cli.aliases import CASTS, aliases_over
from utina.cli.world import DEFAULT_DOMAIN, DOMAINS, world
from utina.domain import SEQ_DIGITS, Record, is_sequence
from utina.fold.constitution import Constitution

#: Every command that reads a record generically, with argv that works in ANY domain.
#: ``--at`` is a sequence number throughout, because that is the one coordinate every
#: domain can be addressed by; the two demo drivers are absent on purpose and are
#: covered by :func:`test_a_demo_driver_refuses_the_domain_flag`.
GENERIC = (
    ("law", "--at", "1"),
    ("eval", "--said", "1", "--at", "1"),
    ("log", "--at", "1"),
    ("meanwhile", "--from", "0", "--to", "1"),
    ("replay", "--at", "1"),
    ("registry", "--at", "1"),
    ("disturbance", "0", "--at", "1"),
)


def shell(*argv: str) -> tuple[int, str, str]:
    """One command through the same entry point a shell reaches."""
    out, err = StringIO(), StringIO()
    status = run(argv, Console(out=out, err=err))
    return status, out.getvalue(), err.getvalue()


# --- the flag resolves, in both directions ------------------------------------


@pytest.mark.parametrize("domain", sorted(DOMAINS), ids=sorted(DOMAINS))
def test_eval_resolves_in_every_domain(domain: str) -> None:
    """The criterion's first clause, said the way the plan says it."""
    with world(domain=domain) as record:
        act = _an_act_class(record)
        status, out, err = shell("eval", act, "--domain", domain, "--at", str(record.last))
    assert status == 0, err
    assert act in out
    assert record.display in out


@pytest.mark.parametrize("argv", GENERIC, ids=[one[0] for one in GENERIC])
@pytest.mark.parametrize("domain", sorted(DOMAINS), ids=sorted(DOMAINS))
def test_no_generic_command_depends_on_a_hardcoded_record(
    domain: str, argv: tuple[str, ...]
) -> None:
    """The criterion's second clause: every reading command takes whatever it is given.

    Answering is the bar, not answering anything in particular. A ``disturbance`` over
    an event that disturbed nothing renders two empty columns, and a registry that has
    conferred nothing renders an empty table; both are the record having nothing to say,
    which is the honest screen rather than a failure.
    """
    status, out, err = shell(argv[0], *argv[1:], "--domain", domain)
    assert status == 0, err
    assert out.strip()


def test_the_default_domain_is_acme_and_is_what_no_flag_means() -> None:
    """Both demo scripts are Acme's, so a default that could move would break them."""
    assert DEFAULT_DOMAIN == acme.DOMAIN
    with world() as unflagged, world(domain=acme.DOMAIN) as flagged:
        assert unflagged.name == flagged.name == acme.DOMAIN


def test_a_domain_the_registry_does_not_know_is_refused_by_the_parser() -> None:
    """Refused before a substrate is opened, and with the names it does know."""
    status, _, err = shell("law", "--domain", "kremlin", "--at", "0")
    assert status == 2
    assert "e.input.malformed.command.f" in err
    assert "acme" in err and "bank" in err


@pytest.mark.parametrize("command", ("demo", "demo2"))
def test_a_demo_driver_refuses_the_domain_flag(command: str) -> None:
    """@rgfxfkvo: a driver that walks ONE domain's story does not take the flag.

    Refused by argparse rather than by a branch, which is the whole reason ``--domain``
    is a parent parser of its own: a flag a command silently ignored would be worse
    than one it rejects.
    """
    status, _, err = shell(command, "--domain", "bank", "--beat", "d1")
    assert status == 2
    assert "e.input.malformed.command.f" in err
    assert "--domain" in err


def test_every_registered_domain_builds_a_record_that_knows_its_own_name() -> None:
    """A registry keyed by one name and building a record that answers another would
    look up the wrong display cast on every screen, silently."""
    for name in DOMAINS:
        with world(domain=name) as record:
            assert record.name == name
            assert record.display


# --- labels are a fixture's, and a domain may have none -----------------------


def test_the_bank_commits_no_labels_at_all() -> None:
    """The property the rest of this section is about, asserted where it is decided."""
    with world(domain=bank.DOMAIN) as record:
        assert record.labels == {}
    with world(domain=acme.DOMAIN) as record:
        assert record.labels, "Acme's labels are what make the labelless case a contrast"


def test_a_label_against_a_domain_with_none_says_so_rather_than_failing_obscurely() -> None:
    """@er57yvs7, and the criterion's last four words.

    The old error would have answered "that is not one of my labels, and here they are"
    with an empty list of alternatives, which tells a reader nothing about why.
    """
    status, _, err = shell("law", "--domain", "bank", "--at", "d1")
    assert status == 2
    assert "e.state.labels-absent.f" in err
    assert "committed nowhere" in err
    assert "sequence numbers" in err
    assert "Meridian Bank" in err


def test_a_label_against_a_domain_that_has_labels_still_names_them() -> None:
    """The other error did not go away; the two are different obstacles."""
    status, _, err = shell("law", "--domain", "acme", "--at", "nowhere")
    assert status == 2
    assert "e.state.label-unknown.f" in err
    assert "board-seated" in err


@pytest.mark.parametrize("domain", sorted(DOMAINS), ids=sorted(DOMAINS))
def test_a_sequence_number_addresses_any_domain(domain: str) -> None:
    """@qtm5ntkg: the same argument means the same thing everywhere, labels or not."""
    with world(domain=domain) as record:
        assert record.at("0") == record.values.position(0)
        assert record.at(str(record.last)) == record.values.position(record.last)


def test_a_sequence_number_agrees_with_the_label_for_the_same_coordinate() -> None:
    """In Acme, where both ways of addressing a coordinate exist, they are one thing."""
    with world() as record:
        for label, seq in record.labels.items():
            assert record.at(label) == record.at(str(seq)), label


@pytest.mark.parametrize("domain", sorted(DOMAINS), ids=sorted(DOMAINS))
def test_a_sequence_number_past_the_end_is_refused_rather_than_folded_at(
    domain: str,
) -> None:
    """A coordinate the record does not reach would fold to an answer about nothing."""
    with world(domain=domain) as record, pytest.raises(BakoboError) as caught:
        record.at(str(record.last + 1))
    assert caught.value.code == "e.input.range.position.f"
    assert str(record.last) in caught.value.detail


def test_a_digit_string_too_long_to_be_a_coordinate_is_out_of_range_on_its_face() -> None:
    """Size before shape before meaning: the bound keeps it away from ``int``."""
    with world(domain=bank.DOMAIN) as record, pytest.raises(BakoboError) as caught:
        record.at("9" * (SEQ_DIGITS + 1))
    assert caught.value.code == "e.input.range.position.f"


def test_a_label_is_preferred_to_a_sequence_number_and_no_label_is_numeric() -> None:
    """Labels are looked up first, so a numeric label would shadow a coordinate.

    None is numeric today and this is what refuses to let one become numeric quietly:
    a fixture that named a beat ``12`` would make ``--at 12`` mean that beat in one
    domain and seq 12 in every other.
    """
    for name in DOMAINS:
        with world(domain=name) as record:
            numeric = [one for one in record.labels if is_sequence(one)]
            assert not numeric, f"{name} commits numeric labels: {numeric}"


def test_the_sequence_predicate_takes_ascii_digits_and_nothing_else() -> None:
    """``str.isdigit`` is true of forms ``int`` accepts and no reader could type back."""
    assert is_sequence("0") and is_sequence("41")
    assert not is_sequence("d1") and not is_sequence("") and not is_sequence("-1")
    assert not is_sequence("١٢٣"), "Arabic-Indic digits parse as int and must not resolve"


def test_the_meanwhile_card_discloses_only_the_coordinates_that_are_labels() -> None:
    """A note calling a sequence number "this demo's name" would be false on its face."""
    _, both, _ = shell("meanwhile", "--from", "d1", "--to", "d3")
    assert "d1 and d3 are this demo's names for coordinates" in both

    _, one, _ = shell("meanwhile", "--from", "d1", "--to", "12")
    assert "d1 is this demo's name for a coordinate" in one

    _, neither, _ = shell("meanwhile", "--domain", "bank", "--from", "0", "--to", "5")
    assert neither.strip(), "the card itself still renders"
    assert "this demo's name" not in neither


# --- the bank is a real record the fold was not written around ----------------


def test_the_bank_answers_both_verdicts_over_its_own_law() -> None:
    """Pending until the diligence lands, affirmed once it has.

    Not new engine behaviour on the arithmetic, and that is the point: it is Acme's
    machinery answering about a record Acme's fixture did not write. What IS new is
    the requirement the count cannot discharge on its own.
    """
    with world(domain=bank.DOMAIN) as record:
        before = str(record.last - 1)
        after = str(record.last)
        _, pending, _ = shell(
            "eval", bank.OPEN_ACCOUNT, "--domain", bank.DOMAIN, "--at", before
        )
        _, affirmed, _ = shell(
            "eval", bank.OPEN_ACCOUNT, "--domain", bank.DOMAIN, "--at", after
        )
    assert "PENDING" in pending
    assert "diligence" in pending
    assert "AFFIRMED" in affirmed


def test_the_banks_law_is_folded_from_its_own_committed_bytes() -> None:
    """One clause, two slots at a half, and a domain that certifies."""
    with world(domain=bank.DOMAIN) as record:
        law = Constitution.at(record.corpus, record.at(str(record.last)))
        assert [one.id for one in law.clauses] == ["M1"]
        assert len(law.clause("M1").group.slots) == 2
        assert law.clause("M1").governs == bank.ACCOUNT_ACTS
        # A certifying domain leaves an act at unity PENDING until it admits a tally,
        # so the affirmation above rests on the certification and not the arithmetic.
        assert law.certification is not None
        # And Meridian obliges itself to look before it transacts, which Acme does not.
        assert law.diligence is not None


def test_the_bank_is_deterministic_in_its_own_committed_bytes() -> None:
    """Two invocations produce the same log down to the identifier, as Acme's does."""
    with world(domain=bank.DOMAIN) as first, world(domain=bank.DOMAIN) as second:
        assert [one.said for one in first.events] == [one.said for one in second.events]


def test_the_bank_record_holds_a_registry_rather_than_the_string_none() -> None:
    """An identifier is what the registry screen's field is for (this.i @qprzacju)."""
    with world(domain=bank.DOMAIN) as record:
        assert record.registry
    # Seq 5 is the record's last event; 6 was past the end, so the command refused and
    # printed nothing, and "None" not in nothing could never fail (ds and glm, #10).
    status, out, _ = shell("registry", "--domain", "bank", "--at", "5")
    assert status == 0
    assert "REGISTRY E" in out
    assert "None" not in out


# --- the display cast is per domain, and a domain may have none ---------------


def test_each_domain_renders_its_own_cast_and_never_anothers() -> None:
    with world(domain=bank.DOMAIN) as record:
        table = aliases_over(record.aids, record.name)
        assert table.short(record.aids[bank.PRIYA]) == "priya-officer,6"
        assert table.scope == "Meridian"
    with world(domain=acme.DOMAIN) as record:
        table = aliases_over(record.aids, record.name)
        assert table.short(record.aids[acme.MARTA]) == "marta-founder,6"
        assert table.scope == "Acme"


def test_a_domain_with_no_cast_renders_its_parties_as_identifiers() -> None:
    """@6exkxbbv: the display plane may not refuse to draw a record the fold can read,
    and it may not invent a name for a party nobody told it about."""
    table = aliases_over({"whoever": "Eidentifier"}, "a-domain-with-no-cast")
    assert table.full("Eidentifier") == "Eidentifier"
    assert table.short("Eidentifier") == "Eidentifier"
    assert table.every_alias() == ()
    assert table.scope == ""


def test_every_registered_domain_has_a_cast() -> None:
    """Not required by the machinery, and required by anybody reading a screen: a
    domain with no cast renders identifiers, which is honest and looks like a bug."""
    assert set(DOMAINS) <= set(CASTS)


def _an_act_class(record: Record) -> str:
    """An act class this record's law actually governs, read off the law itself."""
    law = Constitution.at(record.corpus, record.at(str(record.last)))
    return law.clauses[0].governs[0]
