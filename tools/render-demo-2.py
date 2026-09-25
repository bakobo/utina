"""Re-render demo 2's tracked artifacts: three transcripts, the cue card, the diagram.

The five files under ``docs/`` that this writes are checked in, and
``tests/test_demo_2_artifacts.py`` pins every one of them to what the CLI
actually prints. So they are evidence rather than documentation: a change to a
screen, to the run-of-show, or to the committed record shows up as a diff in a
tracked file, and a change that was not intended fails the suite.

That is the same arrangement ``docs/render-candidates.md`` already has for the
D3 screen (``this.i`` @4tcsbw72 names re-rendering it as a consequence of moving
the record). This extends it from one screen to the whole of demo 2.

Usage:
    uv run python tools/render-demo-2.py            # rewrite all five
    uv run python tools/render-demo-2.py --check     # exit 1 if any is stale

``--check`` is what CI wants and what a maintainer wants before committing; it
writes nothing. The transcripts are generated through ``utina.cli.run`` — the
same entry point a shell reaches — so a transcript cannot be a screen the
command could not produce. The cue card is generated from ``utina.cli.demo2``'s
own ``OPENER``, ``KERNELS``, ``LEAVE_BEHIND`` and ``CUT_ORDER``, so it cannot
name a beat the driver does not have. The sequence diagram is generated from the
same kernels plus the record's own labels, and is collapsed on purpose: one
message per ACT a beat comprises, never one per committed event (``this.i``
@y7ytqzyj). A beat is several speech acts where it is several — beat 7 is two
endorsements and a certification — and flattening those to one arrow would delete
the thing the diagram is for, which is who spoke to whom.

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

from utina.acme import DEV, DEVICE, GAID, MARTA, QUINN, SEAT  # noqa: E402
from utina.cli import Console, run  # noqa: E402
from utina.cli.demo2 import (  # noqa: E402
    CUT_ORDER,
    KERNELS,
    LEAVE_BEHIND,
    LIVE,
    OPENER,
    coordinate_of,
)

DOCS = ROOT / "docs"

#: Each tracked transcript, and the argv that produces it. ``--no-pause``
#: throughout: a transcript is read, not narrated to.
TRANSCRIPTS = {
    "demo-2-opener.txt": ("demo2", "--part", "opener", "--no-pause"),
    "demo-2-live.txt": ("demo2", "--part", "live", "--no-pause"),
    "demo-2-leave-behind.txt": ("demo2", "--part", "leave-behind", "--no-pause"),
}

CUE_CARD = "demo-2-cue-card.md"

SEQUENCE = "demo-2-sequence.md"

#: What each party's lifeline is called, and which alias labels it. Mermaid participant
#: ids may not carry the comma a COIA alias ends in, so each gets a short id and the
#: alias is its display label — which keeps the rule that a party is named by its alias
#: and never by its identifier (``this.i`` @clcoia, @y7ytqzyj).
LIFELINES = (
    ("Acme", GAID),
    ("Marta", MARTA),
    ("Dev", DEV),
    ("Seat3", SEAT),
    ("Device", DEVICE),
    ("Quinn", QUINN),
)

#: Who speaks to whom at each marked beat. Written here rather than derived from the
#: record, and the distinction is the point: an arrow says what the BEAT is about, while
#: the record says what was committed. One arrow per beat is a claim about the story, and
#: the events are already counted in the note above it.
ARROWS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "7": (
        ("Marta", "Acme", "endorse the amendment that seats the board"),
        ("Dev", "Acme", "endorse"),
        ("Acme", "Acme", "certify: the board law takes force here"),
    ),
    "8": (("Acme", "Seat3", "seat credential, issued under Acme's registry"),),
    "9": (("Acme", "Acme", "re-ask the hire: its cure path was shut by the amendment"),),
    "10": (("Acme", "Acme", "re-ask the equity release: its cure path is still open"),),
    "12": (
        ("Marta", "Acme", "endorse the budget"),
        ("Seat3", "Acme", "endorse, citing the seat credential"),
        ("Acme", "Acme", "certify"),
    ),
    "13": (
        ("Marta", "Acme", "endorse the Q2 forecast"),
        ("Dev", "Acme", "decline — but seat 3's slot is still reachable"),
    ),
    "14": (("Quinn", "Acme", "endorse citing a seat he does not hold — refused"),),
    "16": (("Acme", "Acme", "revoke the seat credential"),),
    "17": (("Marta", "Acme", "endorse the Q3 budget"),),
    "19": (("Acme", "Acme", "re-ask beat 12: the credential did stand at that position"),),
    "20": (("Acme", "Acme", "admit an observed duplicity at seat 3's signing position"),),
    "22": (
        ("Marta", "Acme", "endorse the second amendment"),
        ("Dev", "Acme", "endorse"),
        ("Seat3", "Acme", "endorse"),
        ("Acme", "Acme", "certify"),
    ),
    "23": (("Acme", "Acme", "compute which acts in flight the amendment ended"),),
    "26": (
        ("Marta", "Acme", "endorse the equity release, tabled again"),
        ("Dev", "Acme", "decline"),
        ("Marta", "Acme", "certify, citing her own half at full weight"),
        ("Acme", "Acme", "admit it: the cited weights do add to one"),
    ),
    # The leave-behind four. Beat 15 is the only place the device speaks, which is why
    # the diagram carries them rather than stopping at the live run: a reader who
    # was not in the room is exactly the reader the leave-behind is for.
    "11": (
        ("Dev", "Acme", "endorse the equity release, on the far side of the amendment"),
        ("Acme", "Acme", "certify: cured under the clause that never moved"),
    ),
    "15": (
        ("Device", "Acme", "endorse the forecast, citing the seat credential"),
        ("Acme", "Acme", "certify"),
    ),
    "18": (("Acme", "Acme", "re-ask beat 12 at beat 12's own position: byte-identical"),),
    "21": (("Marta", "Acme", "endorse the capital plan"),),
    "24": (("Acme", "Acme", "re-ask beat 2 from the end: still affirmed, still under A1"),),
    "25": (("Acme", "Acme", "refold in permuted arrival order: byte-identical"),),
}


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
    """The live beats, grouped by kernel, numbered in playing order."""
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
        live_shape=f"{_count(len(LIVE))} beats in {_count(len(KERNELS))} kernels",
        opener=_beat_list(OPENER, suffix=" --substrate keripy"),
        live=_kernels(),
        cuts=" → ".join(f"beat {one}" for one in CUT_ORDER),
        leave_behind=_beat_list(LEAVE_BEHIND),
    )


def sequence() -> str:
    """The collapsed sequence diagram, from the driver's kernels and the record's labels.

    Generated rather than drawn, for the reason every other artifact here is: a hand-drawn
    diagram is a second account of the record and it drifts in silence. This one cannot
    name a beat the driver does not have or a coordinate the record does not carry.

    **Collapsed on purpose** (``this.i`` @y7ytqzyj), and collapsed against the EVENTS
    rather than against the acts. One participant per party, one message per act a beat
    comprises, and the events between beats as notes. An arrow per committed event would
    be unreadable on a projector and would say less than ``utina log`` already says in a
    table; an arrow per *beat* would be the opposite mistake, flattening beat 7's two
    endorsements and its certification into one line and deleting the thing a sequence
    diagram is for. The count is not written here: the prose below derives it from the
    record, and a second copy in a docstring is a copy that goes stale at the next
    fixture rebuild — as this one had.
    """
    from utina.acme import build
    from utina.cli.aliases import aliases_over
    from utina.cli.world import RealValues

    record = build(values=RealValues())
    aliases = aliases_over(record.aids, record.name)
    lines = [
        "# Demo 2, as a sequence",
        "",
        # Each paragraph is emitted as ONE line however long, per the repo's markdown
        # rule: a hard wrap makes a one-word edit reflow the whole paragraph in the
        # diff, and this file is tracked. The source is split across adjacent literals
        # only so that the Python stays inside its own line budget.
        (
            "One participant per party, one message per act a beat comprises, and the"
            " events between beats as notes. **Collapsed on purpose** — the record"
            " commits"
            f" {len(record.events)} events, and a diagram with one arrow each would be"
            " unreadable and would say less than `utina log` already says in a table"
            " (`this.i` @y7ytqzyj)."
        ),
        "",
        # Both counts are derived. Written out, they said "thirteen" and "four" into a
        # PINNED artifact and contradicted the driver the moment beat 26 landed — which
        # is the failure the whole generate-and-pin arrangement exists to prevent, so
        # committing it in the generator was the worst possible place for it.
        (
            f"The live {_count(len(LIVE))} come first, grouped by kernel in playing"
            f" order, then the {_count(len(LEAVE_BEHIND))} leave-behind beats. Generated"
            " by `tools/render-demo-2.py` and pinned by"
            " `tests/test_demo_2_artifacts.py`: edit the driver or the record, never"
            " this file."
        ),
        "",
        "```mermaid",
        "sequenceDiagram",
        "    autonumber",
    ]
    lines.extend(
        f"    participant {short} as {aliases.short(record.aid(alias))}"
        for short, alias in LIFELINES
    )

    previous = ""
    for kernel in KERNELS:
        lines.append(f"    Note over Acme,Quinn: {kernel.title}")
        for beat in kernel.beats:
            lines.extend(_beat(record, beat, previous))
            previous = coordinate_of(beat) or previous

    lines.append("    Note over Acme,Quinn: The leave-behind, sent afterwards")
    for beat in LEAVE_BEHIND:
        lines.extend(_beat(record, beat, previous))
        previous = coordinate_of(beat) or previous
    lines.extend(["```", ""])
    return "\n".join(lines)


#: The counts the diagram's prose spells out, as words, up to the largest the
#: run-of-show could plausibly reach. Beyond that the digits are clearer than a word
#: nobody reads at a glance, which is the only reason the table ends.
_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
    8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty",
}


def _count(number: int) -> str:
    """``number`` as the word the prose wants, or as digits past the table's end."""
    return _WORDS.get(number, str(number))


def _beat(record, beat, previous: str) -> list[str]:
    """One beat: what came before it that nobody saw, where it is asked, and its arrows."""
    label = coordinate_of(beat)
    seq = record.labels.get(label) if label else None
    where = f"{label}, seq {seq}" if seq is not None else "live, nothing committed"
    return [
        *_between(record, previous, label),
        f"    Note right of Acme: beat {beat.id} — {beat.title} ({where})",
        *(f"    {source}->>{target}: {text}" for source, target, text in ARROWS[beat.id]),
    ]


def _between(record, previous: str, label: str) -> list[str]:
    """The note counting what was committed since the last marked beat, where any was.

    Nothing where the play order steps back — beat 8 is asked at a coordinate beat 13 has
    already passed — for the same reason ``utina meanwhile`` prints nothing there: going
    back is not something that happened while nobody was looking (``this.i`` @eelnh6dn).
    """
    if not previous or not label:
        return []
    before = record.labels[previous]
    between = [
        one for one in record.corpus.upto(record.at(label)) if one.position.seq > before
    ]
    if not between:
        return []
    admitted = sum(1 for one in between if one.kind == "certification")
    tally = f", {admitted} of them certifications" if admitted else ""
    return [f"    Note over Acme,Quinn: meanwhile: {len(between)} events committed{tally}"]


def artifacts() -> dict[str, str]:
    """Every tracked artifact, by filename, as it should read on disk."""
    rendered = {name: transcript(argv) for name, argv in TRANSCRIPTS.items()}
    rendered[CUE_CARD] = cue_card(widest(rendered))
    rendered[SEQUENCE] = sequence()
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
