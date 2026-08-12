"""The command-line interface: what a person types, and what the projector shows.

Rendering is tested by asserting on the plain-text form, never by eyeballing it. The
colour path is tested by the one property that matters — that stripping the escape
sequences from the coloured form yields the uncoloured form exactly — so colour can
never become the sole carrier of a meaning.

Two tests here are load-bearing beyond their own assertions:

``test_the_d3_screen_is_the_committed_candidate`` pins the default rendering to the
fenced block in ``docs/render-candidates.md``, so the document the maintainer chooses
from cannot drift away from the screen the command prints.

``test_the_rendered_arithmetic_implies_the_folds_verdict`` is the guard on this.i
@clxchk. The CLI derives the slot table itself, because no finding carries one, and a
second path to a governance fact can diverge in silence. This walks every beat and
asserts the table implies the verdict.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from io import StringIO
from pathlib import Path

import pytest
from bakobo.errors import BakoboError  # type: ignore[import-untyped]

from utina.cli import Console, main, run
from utina.cli.world import world

ANSI = re.compile(r"\x1b\[[0-9;]*m")

DOCS = Path(__file__).resolve().parents[1] / "docs"

BEATS = [
    ("d1", ["eval", "open-bank-account", "--at", "d1"], "AFFIRMED"),
    ("d2", ["eval", "hire-vp-sales", "--at", "d2"], "PENDING"),
    ("d3", ["eval", "hire-vp-sales", "--at", "d3"], "DEFEATED"),
    ("d4", ["eval", "--said", "seat-the-board", "--at", "d4"], "AFFIRMED"),
    ("d5", ["eval", "approve-budget", "--at", "d5"], "AFFIRMED"),
    ("d6", ["eval", "approve-budget", "--at", "d6"], "PENDING"),
    ("d7", ["eval", "amend-operating-agreement", "--at", "d7"], "DEFEATED"),
    ("d9", ["eval", "--said", "open-bank-account", "--at", "d9"], "AFFIRMED"),
]


def shell(*argv: str, color: bool = False) -> tuple[int, str, str]:
    """Run one command as a person would, and return status, stdout, stderr."""
    out, err = StringIO(), StringIO()
    status = run(argv, Console(out=out, err=err, color=color))
    return status, out.getvalue(), err.getvalue()


def screen(*argv: str) -> str:
    status, out, err = shell(*argv)
    assert status == 0, f"{argv} exited {status}: {err}"
    return out


def _question(record, argv):
    """The question a beat's argv asks, built the way the eval command builds it."""
    from utina.cli.appraisal import question_from

    if argv[1] == "--said":
        return question_from(record.saids, record.events, None, argv[2])
    return question_from(record.saids, record.events, argv[1], None)


def fenced(document: str, index: int) -> list[str]:
    """The lines of the ``index``-th fenced block in a markdown document."""
    blocks = (DOCS / document).read_text(encoding="utf-8").split("```")
    return blocks[1 + index * 2].strip("\n").splitlines()


# --- the surface --------------------------------------------------------------


def test_bare_utina_prints_help_and_succeeds():
    """The tick this commission closes: the console script must run at all."""
    status, out, _ = shell()
    assert status == 0
    for command in ("law", "eval", "log", "replay", "enact", "demo"):
        assert command in out


def test_help_names_every_command():
    status, out, _ = shell("--help")
    assert status == 0
    assert "utina" in out


def test_main_is_the_console_script_entry_point(capsys):
    assert main(["law", "--at", "inception"]) == 0
    assert "clause A1" in capsys.readouterr().out


def test_main_defaults_to_the_process_arguments(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["utina", "law", "--at", "inception"])
    assert main() == 0
    assert "clause A1" in capsys.readouterr().out


# --- utina law ----------------------------------------------------------------


def test_law_at_inception_shows_both_founding_clauses_with_slots_and_weights():
    out = screen("law", "--at", "inception")
    assert "LAW IN FORCE AT inception" in out
    assert "clause A1" in out and "clause A2" in out
    assert "acme:marta 1/2, acme:dev 1/2" in out
    assert "open-bank-account, hire-vp-sales, approve-budget" in out
    assert "unity 1" in out


def test_law_shows_the_head_that_identifies_the_edition():
    out = screen("law", "--at", "inception")
    head = world().values  # touched so the fixture cost is visible in the test
    assert head is not None
    assert "932f0ab892df" in out


def test_law_after_the_amendment_shows_the_board_clauses_and_the_retained_bar():
    out = screen("law", "--at", "board-seated")
    assert "clause B1" in out and "clause B2" in out
    assert "acme:marta 1/2, acme:dev 1/2, acme:nina 1/2" in out
    assert "acme:marta 1/3, acme:dev 1/3, acme:nina 1/3" in out
    # B1's slots oversum, so unity does not need everyone; B2's do not.
    assert "sum to 3/2" in out
    assert "every slot is required" in out


def test_law_refuses_an_unknown_position_with_a_declared_code():
    status, _, err = shell("law", "--at", "nowhere")
    assert status == 2
    assert "e.state.label-unknown.f" in err
    assert "nowhere" in err
    assert "d1" in err


# --- utina eval, the four findings and the refusal -----------------------------


@pytest.mark.parametrize(("beat", "argv", "verdict"), BEATS, ids=[b[0] for b in BEATS])
def test_every_beat_renders_its_verdict(beat: str, argv: Sequence[str], verdict: str):
    out = screen(*argv)
    assert verdict in out
    assert beat.startswith("d")


def test_an_affirmed_screen_carries_its_clause_endorsements_and_bundle():
    out = screen("eval", "open-bank-account", "--at", "d1")
    assert "AFFIRMED" in out
    assert "clauses" in out and "A1" in out
    assert "reached by" in out
    assert "ElO0tE7Ry0ZP" in out and "ETR_6FPPeGzR" in out
    assert "evidence" in out
    assert "unity reached" in out


def test_a_pending_screen_names_the_slot_that_would_discharge_it_and_the_cure():
    out = screen("eval", "hire-vp-sales", "--at", "d2")
    assert "PENDING" in out
    assert "acme:dev" in out
    assert "endorsement under clause A1" in out
    assert "absent" in out
    assert "cured by the arrival of the missing evidence" in out
    assert "unity still reachable" in out


def test_a_defeated_screen_carries_the_clause_class_subcode_and_declination():
    out = screen("eval", "hire-vp-sales", "--at", "d3")
    assert "DEFEATED" in out
    assert "authority (the actor lacked the invoked power)" in out
    assert "subcode" in out and "acme:dev" in out
    assert "Ei1G09hY6yu2" in out
    assert "unity unreachable" in out


def test_the_centerpiece_contrast_differs_only_on_the_reachable_row():
    """D3 and D6 both show 1/2 endorsed. The reachable row is what separates them."""
    three = screen("eval", "hire-vp-sales", "--at", "d3")
    six = screen("eval", "approve-budget", "--at", "d6")
    assert "unity unreachable" in three
    assert "unity still reachable" in six
    assert "endorsed             1/2   of 1" in three
    assert "endorsed             1/2   of 1" in six


def test_a_refusal_looks_different_in_kind_from_a_finding():
    out = screen("eval", "declare-dividend", "--at", "d8")
    assert "REFUSED" in out
    assert "NOT EVALUABLE" in out
    assert "This is not a verdict" in out
    assert "declare-dividend" in out
    # No verdict word, and no arithmetic: there is no clause, so there is no sum.
    for verdict in ("AFFIRMED", "DEFEATED", "PENDING", "SELF-CONVICTED"):
        assert verdict not in out
    assert "disposition" not in out
    assert "reachable" not in out
    # It shows what the law does govern, so the silence is visible rather than claimed.
    assert "the law in force here governs" in out
    assert "B1" in out and "B2" in out


def test_a_committed_question_is_judged_under_the_law_it_replaces():
    out = screen("eval", "--said", "seat-the-board", "--at", "d4")
    assert "AFFIRMED" in out
    assert "clause A2" in out
    assert "was the committed act" in out


def test_a_said_may_be_given_as_a_prefix_of_the_identifier():
    out = screen("eval", "--said", "E7hG2mIUMDWp", "--at", "d4")
    assert "AFFIRMED" in out and "A2" in out


def test_a_said_may_be_given_in_full():
    full = world().said("seat-the-board")
    out = screen("eval", "--said", full, "--at", "d4")
    assert "AFFIRMED" in out


def test_an_ambiguous_prefix_is_refused_rather_than_guessed():
    status, _, err = shell("eval", "--said", "E", "--at", "d9")
    assert status == 2
    assert "e.input.multi.said-prefix.f" in err


def test_a_said_nothing_committed_is_a_refusal_not_an_error():
    """Ill-posed, not unproven: the fold answers, and the answer is a refusal."""
    status, out, _ = shell("eval", "--said", "Zzz-nothing-committed", "--at", "d9")
    assert status == 0
    assert "REFUSED" in out
    assert "Zzz-nothing-committed" in out


def test_a_said_committed_after_the_position_is_refused():
    out = screen("eval", "--said", "declare-dividend", "--at", "d1")
    assert "REFUSED" in out


def test_an_endorsement_is_not_an_act_and_cannot_be_appraised():
    endorsement = world().events[2].said
    out = screen("eval", "--said", endorsement, "--at", "d9")
    assert "REFUSED" in out
    assert "act class" in out


def test_eval_needs_exactly_one_of_an_act_class_and_a_said():
    for argv in (
        ("eval", "--at", "d1"),
        ("eval", "hire-vp-sales", "--said", "E7hG2mIUMDWp", "--at", "d4"),
    ):
        status, _, err = shell(*argv)
        assert status == 2, argv
        assert "e.input.malformed.command.f" in err


def test_an_unparseable_command_carries_a_declared_code_and_says_it_will_not_retry():
    status, _, err = shell("law", "--at")
    assert status == 2
    assert "e.input.malformed.command.f" in err
    assert "retrying" in err.lower()


def test_an_unknown_subcommand_is_refused():
    status, _, err = shell("legislate")
    assert status == 2
    assert "e.input.malformed.command.f" in err


# --- the guard on the derived arithmetic --------------------------------------


@pytest.mark.parametrize(("beat", "argv", "verdict"), BEATS, ids=[b[0] for b in BEATS])
def test_the_rendered_arithmetic_implies_the_folds_verdict(
    beat: str, argv: Sequence[str], verdict: str
):
    """this.i @clxchk: the table the CLI derives may never disagree with the fold."""
    from utina.cli.appraisal import appraise
    from utina.fold.group import Disposition

    record = world()
    label = argv[argv.index("--at") + 1]
    appraisal = appraise(
        record.corpus, _question(record, argv), at=record.at(label), label=label
    )
    assert appraisal.clause is not None
    held = {one.endorser: one.disposition for one in appraisal.slots}
    satisfied = appraisal.clause.group.satisfied(held)
    reachable = appraisal.clause.group.reachable(held)

    assert satisfied is (verdict == "AFFIRMED")
    assert (not reachable) is (verdict == "DEFEATED")
    assert Disposition.PENDING in held.values() or satisfied or not reachable
    assert appraisal.clause.id in screen(*argv)
    assert beat


def test_the_clause_the_screen_shows_is_the_clause_the_finding_cites():
    from utina.cli.appraisal import appraise
    from utina.fold.finding import Affirmed, Defeated, Pending

    record = world()
    for _, argv, _ in BEATS:
        label = argv[argv.index("--at") + 1]
        appraisal = appraise(
            record.corpus, _question(record, argv), at=record.at(label), label=label
        )
        outcome = appraisal.outcome
        assert appraisal.clause is not None
        if isinstance(outcome, Affirmed):
            cited = outcome.clauses[0]
        elif isinstance(outcome, Defeated):
            cited = outcome.citation.clause
        else:
            assert isinstance(outcome, Pending)
            cited = outcome.requirement[0].clause
        assert cited == appraisal.clause.id


# --- the committed rendering ---------------------------------------------------


def test_the_d3_screen_is_the_committed_candidate():
    """docs/render-candidates.md is what the maintainer picks from. Keep it true."""
    block = fenced("render-candidates.md", 0)
    assert block[0] == "utina eval hire-vp-sales --at d3"
    expected = [line.rstrip() for line in block[2:]]
    actual = screen("eval", "hire-vp-sales", "--at", "d3")
    printed = [line.rstrip() for line in actual.splitlines()]
    assert printed == expected


def test_no_screen_is_wider_than_the_projector():
    for argv in (
        ["law", "--at", "board-seated"],
        ["eval", "hire-vp-sales", "--at", "d3"],
        ["eval", "declare-dividend", "--at", "d8"],
        ["eval", "open-bank-account", "--at", "d1"],
        ["log"],
        ["replay", "--at", "board-seated"],
        ["enact", "endorse", "--as", "acme:nina", "--on", "approve-budget-retabled"],
        ["demo", "--no-pause"],
    ):
        for line in screen(*argv).splitlines():
            assert len(line) <= 96, (argv, line)


def test_screens_carry_no_emoji_and_no_box_drawing():
    out = screen("eval", "hire-vp-sales", "--at", "d3") + screen("law", "--at", "d3")
    assert out.isascii()


# --- colour --------------------------------------------------------------------


def test_colour_is_never_the_only_carrier_of_meaning():
    _, plain, _ = shell("eval", "hire-vp-sales", "--at", "d3", color=False)
    _, painted, _ = shell("eval", "hire-vp-sales", "--at", "d3", color=True)
    assert "\x1b[" in painted
    assert "\x1b[" not in plain
    assert ANSI.sub("", painted) == plain


def test_a_console_over_a_pipe_is_not_coloured():
    console = Console.over(StringIO(), StringIO(), environ={})
    assert console.color is False


def test_force_colour_overrides_the_stream(monkeypatch):
    console = Console.over(StringIO(), StringIO(), environ={"FORCE_COLOR": "1"})
    assert console.color is True


def test_no_colour_beats_force_colour():
    console = Console.over(
        StringIO(), StringIO(), environ={"FORCE_COLOR": "1", "NO_COLOR": "1"}
    )
    assert console.color is False


class Terminal(StringIO):
    def isatty(self) -> bool:
        return True


def test_a_terminal_is_coloured():
    assert Console.over(Terminal(), StringIO(), environ={}).color is True


# --- the finding renderer, over the whole codomain -----------------------------


def test_a_self_convicted_finding_renders_its_proof():
    from utina.cli.render import ground_of
    from utina.cli.style import Style
    from utina.fold.finding import Proof, SelfConvicted

    lines = ground_of(SelfConvicted(proof=Proof(package="Eproof")), Style(False))
    assert any("Eproof" in line for line in lines)
    assert any("none carried" in line for line in lines)


def test_a_self_convicted_finding_renders_the_contradicting_pair():
    from utina.cli.render import ground_of
    from utina.cli.style import Style
    from utina.fold.finding import Proof, SelfConvicted

    lines = ground_of(
        SelfConvicted(proof=Proof(package="Eproof", pair=("Eone", "Etwo"))), Style(False)
    )
    assert any("Eone" in line and "Etwo" in line for line in lines)


def test_a_defeat_with_no_declination_still_carries_its_ground():
    """A group whose slots cannot sum to unity is defeated by arithmetic, not by a no."""
    from utina.cli.render import ground_of
    from utina.cli.style import Style
    from utina.fold.finding import Citation, Defeated

    lines = ground_of(
        Defeated(citation=Citation(clause="A1", reason="The slots cannot reach unity.")),
        Style(False),
    )
    assert any("A1" in line for line in lines)
    assert any("no discriminator" in line for line in lines)
    assert not any("citation" in line for line in lines)


# --- utina log ----------------------------------------------------------------


def test_log_shows_every_committed_event_in_canonical_order():
    out = screen("log")
    assert "COMMITTED LOG AT the end of the record" in out
    assert "21 events" in out
    assert "Arrival order is not consulted" in out
    seqs = [
        int(line.split()[0])
        for line in out.splitlines()
        if line.startswith("    ") and line.split()[0].isdigit()
    ]
    assert seqs == sorted(seqs)


def test_log_at_a_position_shows_only_what_was_committed_by_then():
    out = screen("log", "--at", "d1")
    assert "4 events" in out
    assert "declare-dividend" not in out


def test_log_glosses_each_kind_of_committed_event():
    out = screen("log")
    assert "the founding law of the domain" in out
    assert "an act of the class open-bank-account" in out
    assert "a successor law, enacted as amend-operating-agreement" in out
    assert "acme:marta endorses" in out
    assert "acme:dev declines" in out


# --- utina replay -------------------------------------------------------------


def test_replay_folds_the_permuted_log_to_the_same_bytes():
    out = screen("replay", "--at", "board-seated")
    assert "REPLAY AT board-seated" in out
    assert "IDENTICAL" in out
    assert "custos-4.2.md:3101" in out
    assert out.count("932f0ab8") == 0  # the board law is in force here, not the founding one
    assert "clause sub-blocks" in out
    assert "B1" in out and "B2" in out


def test_replay_takes_the_permutation_seed():
    assert "IDENTICAL" in screen("replay", "--at", "d3", "--seed", "11")


def test_replay_names_a_disagreement_rather_than_hiding_it():
    from utina.cli.render import replay_verdict

    assert replay_verdict(b"same", b"same") == "IDENTICAL"
    assert "not committed" in replay_verdict(b"one", b"other")


# --- utina enact ---------------------------------------------------------------


def test_enact_commits_a_signed_endorsement_and_shows_what_it_changed():
    out = screen("enact", "endorse", "--as", "acme:nina", "--on", "approve-budget-retabled")
    assert "ENACTED" in out
    assert "acme:nina endorses" in out
    assert "the substrate verified it before recording" in out
    assert "said=E978mpa1QdIW..." in out
    assert "before" in out and "PENDING" in out
    assert "after" in out and "AFFIRMED" in out
    assert "nothing here is written to disk" in out


def test_enact_can_commit_a_declination_that_defeats():
    out = screen("enact", "decline", "--as", "acme:nina", "--on", "approve-budget-retabled")
    assert "acme:nina declines" in out
    assert "DEFEATED" in out


def test_enact_against_an_ungoverned_act_is_refused_by_the_fold_not_by_the_verb():
    """The verb commits; the judgment is the fold's, and here the fold refuses."""
    out = screen("enact", "endorse", "--as", "acme:nina", "--on", "declare-dividend")
    assert "ENACTED" in out
    assert "REFUSED" in out


def test_enact_by_a_party_with_no_key_state_is_refused():
    status, _, err = shell("enact", "endorse", "--as", "acme:stranger", "--on", "hire-vp-sales")
    assert status == 2
    assert "e.id.aid-unknown.f" in err


def test_enact_against_nothing_committed_is_refused():
    status, _, err = shell("enact", "endorse", "--as", "acme:nina", "--on", "Znothing")
    assert status == 2
    assert "e.state.subject-unknown.f" in err


def test_the_constructor_adapter_continues_the_committed_record():
    """this.i @cladpt: the deviation is pinned, so it cannot rot unnoticed."""
    from utina.cli.world import constructor_over

    record = world()
    constructor = constructor_over(record)
    assert constructor.emitted == record.events

    event = constructor.endorse("acme:nina", record.said("approve-budget-retabled"))
    assert event.position.seq == len(record.events)
    sealed = {key: value for key, value in event.body.items() if key != "sig"}
    assert record.substrate.verify("acme:nina", sealed, event.body["sig"])


# --- utina demo ----------------------------------------------------------------


def test_demo_walks_all_ten_beats_through_the_query_commands():
    out = screen("demo", "--no-pause")
    for number in range(1, 11):
        assert f"BEAT D{number} " in out or f"BEAT D{number}  " in out
    assert "$ utina eval hire-vp-sales --at d3" in out
    assert "$ utina replay --at board-seated" in out
    # The prologue shows the law before anything is judged under it.
    assert "BEAT LAW" in out
    # And every beat's screen is one the query CLI produced.
    assert "DEFEATED" in out and "AFFIRMED" in out and "PENDING" in out
    assert "REFUSED - NOT EVALUABLE" in out
    assert "IDENTICAL" in out


def test_demo_can_jump_to_one_beat():
    out = screen("demo", "--beat", "d3", "--no-pause")
    assert "BEAT D3" in out
    assert "BEAT D1 " not in out
    assert "unity unreachable" in out


def test_demo_pauses_between_beats_and_not_after_the_last():
    stops = []
    out, err = StringIO(), StringIO()
    console = Console(out=out, err=err, pause=lambda: stops.append(1))
    assert run(["demo"], console) == 0
    from utina.cli.demo import BEATS, PROLOGUE

    assert len(stops) == len(BEATS) + len(PROLOGUE) - 1


def test_demo_refuses_a_beat_the_script_does_not_have():
    status, _, err = shell("demo", "--beat", "d99")
    assert status == 2
    assert "e.state.label-unknown.f" in err
    assert "d10" in err


def test_the_demo_driver_computes_nothing_the_query_cli_cannot():
    """this.i @cldemo: every beat is argv for a command a person could type."""
    from utina.cli.app import COMMANDS
    from utina.cli.demo import BEATS, PROLOGUE

    for beat in PROLOGUE + BEATS:
        assert beat.argv[0] in COMMANDS
        assert beat.argv[0] != "demo"
        assert screen(*beat.argv)


# --- how an error reads ---------------------------------------------------------


class _Bare:
    """An error carrying only what the standard makes mandatory."""

    code = "e.env.unreachable.r"
    title = "The record could not be reached."
    detail = None
    hint = None
    retryable = True


def test_an_error_that_may_be_retried_says_so():
    from utina.cli.app import render_error
    from utina.cli.style import Style

    rendered = render_error(_Bare(), Style(False))
    assert "e.env.unreachable.r" in rendered
    assert "Retrying may help" in rendered
    assert "None" not in rendered


def test_a_permanent_error_carries_its_detail_and_its_hint():
    from utina.cli.app import render_error
    from utina.cli.style import Style

    try:
        world().at("nowhere")
    except BakoboError as error:
        rendered = render_error(error, Style(False))
    assert "Retrying will not help" in rendered
    assert "nowhere" in rendered
    assert "The labels are inception" in rendered
