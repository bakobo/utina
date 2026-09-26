"""``utina demo3``: demo 2 with beats subtracted, and nothing added (this.i @ij2rkusn).

Demo 3 exists because demo 2 does not fit its slot, and the whole of its design is that
it is demo 2 played shorter. So most of what is asserted here is sameness: the beats are
demo 2's beats, the kernel cards are demo 2's cards, and the one paragraph that differs
is named and differs for a stated reason.
"""

from __future__ import annotations

import io
import re
from io import StringIO

from utina.cli import Console, run


def shell(*argv: str) -> tuple[int, str, str]:
    out, err = StringIO(), StringIO()
    status = run(argv, Console(out=out, err=err, color=False))
    return status, out.getvalue(), err.getvalue()


def screen(*argv: str) -> str:
    status, out, err = shell(*argv)
    assert status == 0, f"{argv} exited {status}: {err}"
    return out


def _demo2() -> dict:
    from utina.cli.demo2 import LEAVE_BEHIND, LIVE, OPENER

    return {beat.id: beat for beat in OPENER + LIVE + LEAVE_BEHIND}


def test_demo3_plays_eight_of_demo2s_beats_in_the_records_order():
    """Q-DYVP: beat 4's defeat before the amendment, beat 13's pending after it."""
    from utina.cli.demo3 import RUN

    assert [beat.id for beat in RUN] == ["1", "2", "4", "7", "13", "27", "28", "29"]


def test_every_beat_is_demo2s_own_object_except_beat_28():
    """Imported, not copied, so a beat cannot drift from its demo-2 form in silence."""
    from utina.cli.demo3 import RUN

    demo2 = _demo2()
    for beat in RUN:
        if beat.id != "28":
            assert beat is demo2[beat.id], beat.id


def test_beat_28_differs_from_demo2_only_in_its_narration():
    """Demo 2's wording cites beat 12's rule, and demo 3 does not play beat 12."""
    from dataclasses import replace

    from utina.cli.demo3 import RUN

    ours = next(beat for beat in RUN if beat.id == "28")
    theirs = _demo2()["28"]

    assert ours.narration != theirs.narration
    assert replace(ours, narration=theirs.narration) == theirs
    assert "beat 12" not in ours.narration


def test_no_narration_cites_a_beat_demo3_does_not_play():
    """A narrator reading "as beat 12 showed" to a room that never saw beat 12 is the
    failure the one reworded paragraph exists to prevent, so it is checked for all."""
    from utina.cli.demo3 import RUN

    played = {beat.id for beat in RUN}
    for beat in RUN:
        cited = set(re.findall(r"\b[Bb]eat (\d+)", beat.narration))
        assert cited <= played, f"beat {beat.id} cites {cited - played}"


def test_the_cut_order_names_beats_demo3_plays():
    from utina.cli.demo3 import CUT_ORDER, RUN

    assert CUT_ORDER == ("1", "27")
    assert set(CUT_ORDER) <= {beat.id for beat in RUN}


def test_demo3_runs_end_to_end_under_demo2s_kernel_cards():
    """Three of demo 2's cards open a beat demo 3 still plays, and they come with it."""
    out = screen("demo3", "--no-pause")

    for beat in ("1", "2", "4", "7", "13", "27", "28", "29"):
        assert f"BEAT {beat} " in out, beat
    assert "BEAT 14" not in out and "BEAT 12" not in out
    assert out.count("KERNEL  ") == 3
    assert "Same signed no, two answers" in out
    assert "Governance that composes" in out


def test_demo3_does_not_force_a_substrate():
    """Unlike demo 2's opener, which is recorded: demo 3 is played live, as asked."""
    out = screen("demo3", "--no-pause")

    assert "--substrate keripy" not in out


def test_one_beat_prints_exactly_what_it_prints_inside_the_whole_run():
    """The recovery path: a fumble costs one command rather than the demo.

    Compared from the beat's own card onward. In the whole run a meanwhile span sits
    between a kernel card and the beat it opens, and a single beat has no predecessor to
    measure a span from, so the kernel card and the beat are not adjacent there.
    """
    whole = screen("demo3", "--no-pause")
    for beat in ("4", "13", "28"):
        one = screen("demo3", "--beat", beat, "--no-pause")
        card = one[one.rindex("\n\n\n") :]
        assert f"BEAT {beat} " in card
        assert card in whole, beat


def test_a_demo2_beat_demo3_does_not_play_is_refused_by_name():
    """Beat 14 exists in demo 2. Asking demo 3 for it names demo 3's beats instead."""
    status, _, err = shell("demo3", "--beat", "14", "--no-pause")

    assert status != 0
    assert "e.state.beat-unknown.f" in err
    assert "1, 2, 4, 7, 13, 27, 28, 29" in " ".join(err.split())


def test_the_demo3_walk_pauses_between_beats_and_not_after_the_last():
    from utina.cli.app import Console
    from utina.cli.demo3 import RUN, walk3

    pauses = []
    console = Console(out=io.StringIO(), err=io.StringIO(), pause=lambda: pauses.append(1))

    walk3(console, pause=True)

    assert len(pauses) == len(RUN) - 1


def test_demo2_is_unchanged_by_the_walk_being_shared():
    """The loop moved so both demos use it. Demo 2's own pins are its transcripts
    (tests/test_demo_2_artifacts.py); this only asserts demo 3 did not take a beat
    out of demo 2's run while subtracting from its own."""
    from utina.cli.demo2 import LEAVE_BEHIND, LIVE, OPENER

    assert len(OPENER + LIVE + LEAVE_BEHIND) == 29
