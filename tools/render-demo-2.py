"""Re-render demo 2's tracked artifacts: three transcripts and the cue card.

The four files under ``docs/`` that this writes are checked in, and
``tests/test_demo_2_artifacts.py`` pins every one of them to what the CLI
actually prints. So they are evidence rather than documentation: a change to a
screen, to the run-of-show, or to the committed record shows up as a diff in a
tracked file, and a change that was not intended fails the suite.

That is the same arrangement ``docs/render-candidates.md`` already has for the
D3 screen (``this.i`` @4tcsbw72 names re-rendering it as a consequence of moving
the record). This extends it from one screen to the whole of demo 2.

Usage:
    uv run python tools/render-demo-2.py            # rewrite all four
    uv run python tools/render-demo-2.py --check     # exit 1 if any is stale

``--check`` is what CI wants and what a maintainer wants before committing; it
writes nothing. The transcripts are generated through ``utina.cli.run`` — the
same entry point a shell reaches — so a transcript cannot be a screen the
command could not produce. The cue card is generated from ``utina.cli.demo2``'s
own ``OPENER``, ``KERNELS``, ``LEAVE_BEHIND`` and ``CUT_ORDER``, so it cannot
name a beat the driver does not have.

**The opener runs under keripy**, because ``walk2`` forces it there: the
opener's job is the this-is-really-KERI claim with real prefixes on screen. Its
identifiers are reproducible — the salt, the inception order and the stretch
tier are all pinned (``this.i`` @7jrbt3) — but they are reproducible *for a
given keripy*. Repinning keripy (tick 4z5c) will move every prefix in that one
file, which is a true fact about the record and not a test failing at random.
Re-render and read the diff.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utina.cli import Console, run  # noqa: E402
from utina.cli.demo2 import CUT_ORDER, KERNELS, LEAVE_BEHIND, OPENER  # noqa: E402

DOCS = ROOT / "docs"

#: Each tracked transcript, and the argv that produces it. ``--no-pause``
#: throughout: a transcript is read, not narrated to.
TRANSCRIPTS = {
    "demo-2-opener.txt": ("demo2", "--part", "opener", "--no-pause"),
    "demo-2-live.txt": ("demo2", "--part", "live", "--no-pause"),
    "demo-2-leave-behind.txt": ("demo2", "--part", "leave-behind", "--no-pause"),
}

CUE_CARD = "demo-2-cue-card.md"


def transcript(argv: tuple[str, ...]) -> str:
    """What the CLI prints for ``argv``, with color off and both streams joined.

    One stream, because beat 14's whole content is the toolchain refusing and a
    transcript that carried it on stderr would show the demo's best moment out
    of order or not at all — which is the reason ``walk2`` redirects it too.
    """
    out = io.StringIO()
    run(argv, Console(out=out, err=out, color=False))
    return out.getvalue()


def widest(transcripts: dict[str, str]) -> int:
    """The longest line any tracked transcript holds, in columns.

    Measured rather than assumed, because the number the cue card tells a narrator is
    only useful if it is true. Prose wraps at ``render.WRAP``, but the echoed ``$ utina
    ...`` line cannot wrap — a wrapped command is not a command anybody can type — so the
    real floor is set by the longest beat command and is a column or two above WRAP.
    """
    return max(len(line) for text in transcripts.values() for line in text.splitlines())


#: The card's fixed prose. It lives in a markdown file rather than in a string literal
#: here, so its paragraphs can each be one line however long — a hard wrap makes a
#: one-word edit reflow a whole paragraph in the diff, and this card is tracked.
TEMPLATE = Path(__file__).resolve().parent / "demo-2-cue-card.md.tmpl"


def _beat_list(beats, suffix: str = "") -> str:
    """One beat per two lines: what it is, and the command that plays it."""
    lines = []
    for beat in beats:
        lines.append(f"- **{beat.id}.** {beat.title}")
        lines.append(f"  `utina {' '.join(beat.argv)}{suffix}`")
    return "\n".join(lines) + "\n"


def _kernels() -> str:
    """The live thirteen, grouped by kernel, numbered in playing order."""
    lines = []
    played = 0
    for kernel in KERNELS:
        lines.extend(
            [
                f"### {kernel.title}",
                "",
                f"- the room expects: {kernel.expects}",
                f"- what happens: {kernel.happens}",
                "",
            ]
        )
        for beat in kernel.beats:
            played += 1
            lines.extend(
                [
                    f"{played}. **Beat {beat.id}** — {beat.title}",
                    "",
                    "   ```",
                    f"   utina {' '.join(beat.argv)}",
                    "   ```",
                ]
            )
            if beat.refuses:
                lines.extend(["", "   " + _REFUSES])
            lines.append("")
    return "\n".join(lines) + "\n"


#: Said on the one beat whose command is meant to fail, because a narrator who typed it
#: and saw a non-zero status would otherwise have to decide on stage whether it broke.
_REFUSES = (
    "**Exits 2 by design.** The toolchain refusing *is* the beat. The driver swallows"
    " the status; typed by hand it exits 2, which is correct and not a break."
)


def cue_card(columns: int) -> str:
    """The operator's half of ``docs/demo-2-script.md``, from the driver itself."""
    return TEMPLATE.read_text(encoding="utf-8").format(
        columns=columns,
        opener=_beat_list(OPENER, suffix=" --substrate keripy"),
        live=_kernels(),
        cuts=" → ".join(f"beat {one}" for one in CUT_ORDER),
        leave_behind=_beat_list(LEAVE_BEHIND),
    )


def artifacts() -> dict[str, str]:
    """Every tracked artifact, by filename, as it should read on disk."""
    rendered = {name: transcript(argv) for name, argv in TRANSCRIPTS.items()}
    rendered[CUE_CARD] = cue_card(widest(rendered))
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if any tracked artifact is stale",
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
            print(
                "Re-render with: uv run python tools/render-demo-2.py",
                file=sys.stderr,
            )
        return 1 if stale else 0

    for name in stale:
        print(f"rewrote docs/{name}")
    if not stale:
        print("every tracked artifact was already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
