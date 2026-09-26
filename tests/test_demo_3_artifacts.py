"""The tracked demo-3 artifacts are what the CLI prints, and a test says so.

The same arrangement as ``tests/test_demo_2_artifacts.py`` (``this.i`` @gizauc3r), for
the shortened run (``this.i`` @ij2rkusn). When one of these fails it is usually right:
re-render with ``uv run python tools/render-demo-3.py`` and read the diff.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _renderer():
    """``tools/render-demo-3.py`` as a module, so the test runs the tool a maintainer runs."""
    path = ROOT / "tools" / "render-demo-3.py"
    spec = importlib.util.spec_from_file_location("render_demo_3", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RENDERER = _renderer()


@pytest.fixture(scope="module")
def rendered() -> dict[str, str]:
    return RENDERER.artifacts()


@pytest.mark.parametrize("name", [RENDERER.TRANSCRIPT, RENDERER.CUE_CARD])
def test_the_tracked_artifact_is_what_the_cli_prints(name, rendered):
    path = DOCS / name
    assert path.exists(), f"docs/{name} is tracked; re-render it"
    assert path.read_text(encoding="utf-8") == rendered[name], (
        f"docs/{name} is stale. Re-render with:\n"
        f"    uv run python tools/render-demo-3.py\n"
        "then read the diff."
    )


def test_the_check_mode_agrees_with_the_files_on_disk():
    assert RENDERER.main(["--check"]) == 0


def test_every_beat_appears_in_the_transcript_and_on_the_card():
    from utina.cli.demo3 import RUN

    transcript = (DOCS / RENDERER.TRANSCRIPT).read_text(encoding="utf-8")
    card = (DOCS / RENDERER.CUE_CARD).read_text(encoding="utf-8")
    for beat in RUN:
        assert f"BEAT {beat.id} " in transcript, beat.id
        assert f"**Beat {beat.id}**" in card, beat.id
        assert f"utina {' '.join(beat.argv)}" in card


def test_the_card_carries_the_cut_order_the_driver_declares():
    from utina.cli.demo3 import CUT_ORDER

    card = (DOCS / RENDERER.CUE_CARD).read_text(encoding="utf-8")
    assert " → ".join(f"beat {one}" for one in CUT_ORDER) in card


def test_the_cards_column_budget_is_measured_and_inside_the_hundred():
    transcript = (DOCS / RENDERER.TRANSCRIPT).read_text(encoding="utf-8")
    measured = max(len(line) for line in transcript.splitlines())
    card = (DOCS / RENDERER.CUE_CARD).read_text(encoding="utf-8")

    assert f"At least {measured} columns" in card
    assert measured <= 100
    assert "\x1b[" not in transcript
