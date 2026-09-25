"""The tracked demo-2 artifacts are what the CLI prints, and a test says so.

``docs/demo-2-opener.txt``, ``demo-2-live.txt``, ``demo-2-leave-behind.txt`` and
``demo-2-cue-card.md`` are checked in. Checking in a transcript is only worth doing if
something notices when it stops being true, so this is that something: it re-renders
every artifact through the same code ``tools/render-demo-2.py`` uses and asserts the
files on disk match.

Why they are tracked rather than generated on demand. A transcript in the tree is
**regression evidence** — it turns "did that render change?" from a question somebody has
to think to ask into a diff in a pull request. It is also the lectern copy, and a demo
reference that lives outside the repo is one nobody can find under time pressure. The
repo already had exactly this arrangement for one screen (``docs/render-candidates.md``,
pinned by ``tests/test_cli.py``, with ``this.i`` @4tcsbw72 naming its re-rendering as a
consequence of moving the record); these four extend it to the whole of demo 2.

**When one of these fails, it is usually right and the fix is to re-render.** Run
``uv run python tools/render-demo-2.py`` and read the diff: it is telling you a screen
moved, or the run-of-show changed, or the committed record gained an event and every
coordinate after it shifted. The failure to take seriously is a diff you cannot explain.

The opener is the one with a standing maintenance cost, and it is disclosed rather than
hidden: it runs under keripy, so its prefixes are pinned to a keripy version, and
repinning keripy (tick 4z5c) will move every one of them.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _renderer():
    """``tools/render-demo-2.py`` as a module, since ``tools`` is not a package.

    Importing the tool rather than reimplementing it is the point: a test that rendered
    the artifacts its own way would pass while the tool a maintainer actually runs
    produced something else.
    """
    path = ROOT / "tools" / "render-demo-2.py"
    spec = importlib.util.spec_from_file_location("render_demo_2", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RENDERER = _renderer()

ARTIFACTS = [*RENDERER.TRANSCRIPTS, RENDERER.CUE_CARD, RENDERER.SEQUENCE]


@pytest.fixture(scope="module")
def rendered() -> dict[str, str]:
    """Every artifact rendered once, because the opener costs a keripy run."""
    return RENDERER.artifacts()


@pytest.mark.parametrize("name", ARTIFACTS)
def test_the_tracked_artifact_is_what_the_cli_prints(name, rendered):
    path = DOCS / name
    assert path.exists(), f"docs/{name} is tracked; re-render it"
    assert path.read_text(encoding="utf-8") == rendered[name], (
        f"docs/{name} is stale. Re-render with:\n"
        f"    uv run python tools/render-demo-2.py\n"
        "then read the diff — it is telling you a screen, the run-of-show or the "
        "committed record moved."
    )


def test_the_check_mode_agrees_with_the_files_on_disk():
    """``--check`` is what a maintainer and CI run, so it is exercised here too."""
    assert RENDERER.main(["--check"]) == 0


def test_every_live_beat_appears_in_the_transcript_and_the_cue_card():
    """The two artifacts a narrator holds have to name the same thirteen beats.

    A cue card that dropped a beat the transcript still shows would send somebody to
    the lectern with an incomplete list, which is the failure a generated card exists
    to prevent — so it is asserted rather than assumed.
    """
    from utina.cli.demo2 import LIVE

    transcript = (DOCS / "demo-2-live.txt").read_text(encoding="utf-8")
    card = (DOCS / RENDERER.CUE_CARD).read_text(encoding="utf-8")
    assert len(LIVE) == 13
    for beat in LIVE:
        assert f"BEAT {beat.id}" in transcript, f"beat {beat.id} is not in the transcript"
        assert f"**Beat {beat.id}**" in card, f"beat {beat.id} is not on the cue card"
        assert f"utina {' '.join(beat.argv)}" in card


def test_the_cue_card_carries_the_cut_order_the_driver_declares():
    """The clock decision is made in advance, so the card cannot disagree with it."""
    from utina.cli.demo2 import CUT_ORDER

    card = (DOCS / RENDERER.CUE_CARD).read_text(encoding="utf-8")
    assert " → ".join(f"beat {one}" for one in CUT_ORDER) in card


def test_the_refusing_beat_is_marked_as_exiting_non_zero():
    """Beat 14 exits 2 on purpose, and a narrator typing it needs to know that."""
    from utina.cli.demo2 import LIVE

    refusing = [beat for beat in LIVE if beat.refuses]
    assert [beat.id for beat in refusing] == ["14"]
    card = (DOCS / RENDERER.CUE_CARD).read_text(encoding="utf-8")
    assert "Exits 2 by design" in card


def test_the_transcripts_carry_no_escape_sequences():
    """A transcript is read on paper and diffed in a pull request, so it is plain."""
    for name in RENDERER.TRANSCRIPTS:
        assert "\x1b[" not in (DOCS / name).read_text(encoding="utf-8")


def test_the_cue_cards_column_budget_is_the_one_the_screens_actually_need():
    """The number on the card is measured, so this asserts it has not drifted.

    A narrator sets the terminal from that number, so a screen that grew a wider column
    while the card still claimed the old width would send somebody on stage with a
    terminal one column too narrow. Measured rather than chosen, and checked rather
    than trusted: the first run of this test found the card claiming 88 while beat 14's
    echoed command was 89, because a command line cannot wrap and the prose width does
    not bound it.
    """
    transcripts = {
        name: (DOCS / name).read_text(encoding="utf-8") for name in RENDERER.TRANSCRIPTS
    }
    measured = RENDERER.widest(transcripts)
    card = (DOCS / RENDERER.CUE_CARD).read_text(encoding="utf-8")
    assert f"At least {measured} columns" in card

    # And it stays inside the hundred the layout targets, which is the real ceiling:
    # past that, a projector's terminal wraps and every column on the screen lies.
    assert measured <= 100, f"the widest screen line is now {measured} columns"


def test_an_error_is_wrapped_like_every_other_paragraph():
    """Beat 14's refusal is a live beat, and its detail is the longest text the CLI has.

    Unwrapped it reached 529 columns, which a terminal breaks wherever it runs out —
    unindented, aligned with nothing, on the beat whose whole content is the toolchain
    correctly refusing. Found by the column test above rather than by eye.
    """
    live = (DOCS / "demo-2-live.txt").read_text(encoding="utf-8")
    assert "ERROR  e.proof.edge-unvalidated.f" in live, "beat 14 is not in this transcript"
    for line in live.splitlines():
        assert len(line) <= 100


# --- the collapsed sequence diagram (this.i @y7ytqzyj) -------------------------


def test_every_marked_beat_has_exactly_one_entry_in_the_diagram():
    """A beat with no arrow would be a lifeline the diagram silently drops.

    The generator raises a ``KeyError`` on a beat it has no arrows for rather than
    skipping it, so this asserts the other direction: that the table has not grown an
    entry for a beat the driver no longer has.
    """
    from utina.cli.demo2 import KERNELS, LEAVE_BEHIND

    marked = {beat.id for kernel in KERNELS for beat in kernel.beats}
    marked |= {beat.id for beat in LEAVE_BEHIND}

    assert set(RENDERER.ARROWS) == marked


def test_the_diagram_is_collapsed_and_not_one_arrow_per_event():
    """The whole of the milestone: forty-nine arrows is unreadable and says less than
    ``utina log`` already says in a table."""
    from utina.acme import build
    from utina.cli.world import RealValues

    diagram = (DOCS / RENDERER.SEQUENCE).read_text(encoding="utf-8")
    arrows = [line for line in diagram.splitlines() if "->>" in line]
    committed = len(build(values=RealValues()).events)

    assert len(arrows) < committed, "a diagram with an arrow per event is not collapsed"
    assert diagram.startswith("# Demo 2, as a sequence")
    assert "```mermaid" in diagram and "sequenceDiagram" in diagram


def test_the_diagram_names_parties_by_alias_and_never_by_identifier():
    """this.i @clcoia, on the artifact read at the most glancing pace of any of them."""
    from utina.acme import build
    from utina.cli.world import RealValues

    diagram = (DOCS / RENDERER.SEQUENCE).read_text(encoding="utf-8")
    record = build(values=RealValues())

    for identifier in record.aids.values():
        assert identifier not in diagram, f"{identifier} is an identifier, not an alias"
    for short, alias in RENDERER.LIFELINES:
        assert f"participant {short} as " in diagram
        assert alias not in diagram, "the alias CONSTANT is not the minted alias either"
