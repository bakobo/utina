"""Re-render demo 3's tracked artifacts: its transcript and its cue card.

The same arrangement as ``tools/render-demo-2.py`` (``this.i`` @gizauc3r), for the
shortened run (``this.i`` @ij2rkusn). Both files under ``docs/`` are checked in, and
``tests/test_demo_3_artifacts.py`` pins them to what the CLI prints and to what
``utina.cli.demo3`` declares.

Usage:
    uv run python tools/render-demo-3.py            # rewrite both
    uv run python tools/render-demo-3.py --check     # exit 1 if either is stale

The transcript is rendered on the facade, like demo 2's live transcript, so it does not
move when keripy is repinned. The room sees the same screens with real prefixes, because
the card says to play it under keripy.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utina.cli import Console, run  # noqa: E402
from utina.cli.demo2 import KERNELS  # noqa: E402
from utina.cli.demo3 import CUT_ORDER, RUN  # noqa: E402

DOCS = ROOT / "docs"

TRANSCRIPT = "demo-3.txt"

CUE_CARD = "demo-3-cue-card.md"

#: The card's fixed prose, kept in markdown so each paragraph can be one line.
TEMPLATE = Path(__file__).resolve().parent / "demo-3-cue-card.md.tmpl"


def transcript() -> str:
    """What ``utina demo3`` prints, with color off and both streams joined."""
    out = io.StringIO()
    run(("demo3", "--no-pause"), Console(out=out, err=out, color=False))
    return out.getvalue()


def _beats() -> str:
    """Each beat in playing order, under demo 2's kernel card where one opens it."""
    opens = {kernel.beats[0].id: kernel for kernel in KERNELS}
    lines = []
    for played, beat in enumerate(RUN, start=1):
        kernel = opens.get(beat.id)
        if kernel is not None:
            lines.extend(
                [
                    f"### {kernel.title}",
                    "",
                    f"- the room expects: {kernel.expects}",
                    f"- what happens: {kernel.happens}",
                    "",
                ]
            )
        lines.extend(
            [
                f"{played}. **Beat {beat.id}** — {beat.title}",
                "",
                "   ```",
                f"   utina {' '.join(beat.argv)}",
                "   ```",
                "",
            ]
        )
    return "\n".join(lines)


def cue_card(columns: int) -> str:
    """The lectern copy, from the driver itself."""
    return TEMPLATE.read_text(encoding="utf-8").format(
        columns=columns,
        count=len(RUN),
        beats=_beats(),
        cuts=" → ".join(f"beat {one}" for one in CUT_ORDER),
    )


def artifacts() -> dict[str, str]:
    """Both tracked artifacts, by filename, as they should read on disk."""
    text = transcript()
    widest = max(len(line) for line in text.splitlines())
    return {TRANSCRIPT: text, CUE_CARD: cue_card(widest)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if either tracked artifact is stale",
    )
    args = parser.parse_args(argv)

    stale = []
    for name, content in artifacts().items():
        path = DOCS / name
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        stale.append(name)
        if not args.check:
            path.write_text(content, encoding="utf-8")

    if args.check:
        for name in stale:
            print(f"stale: docs/{name}", file=sys.stderr)
        if stale:
            print("Re-render with: uv run python tools/render-demo-3.py", file=sys.stderr)
        return 1 if stale else 0

    for name in stale:
        print(f"rewrote docs/{name}")
    if not stale:
        print("every tracked artifact was already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
