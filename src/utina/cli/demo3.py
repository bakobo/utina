"""Demo 3's run-of-show: demo 2 with beats subtracted, and nothing added.

Demo 2 does not fit its slot: Daniel took 20 minutes to narrate its first eight beats,
so the whole of it runs near an hour. Demo 3 plays eight of its beats in the record's
order, at about 2.5 minutes a beat, measured rather than computed (``this.i`` @ij2rkusn).

Nothing here is a beat of demo 3's own. Every beat is demo 2's object, imported by id,
walked through demo 2's loop under demo 2's kernel cards, so a demo-3 beat cannot drift
from its demo-2 form without ``tests/test_demo3.py`` noticing. Beat numbers keep their
demo-2 values, gaps and all, because the narrations cite each other by those numbers.

The one exception is beat 28's narration. Demo 2's cites "beat 12's rule", and beat 12
is not played here, so this module carries its own paragraph for that beat and nothing
else about it differs.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from utina.cli.demo2 import LEAVE_BEHIND, LIVE, OPENER, Beat, named, play
from utina.substrate import FACADE

if TYPE_CHECKING:  # pragma: no cover - the import exists only for the annotation
    from utina.cli.app import Console

__all__ = ["CUT_ORDER", "RUN", "walk3"]

#: Demo 2's beats that demo 3 plays, in playing order, which is also the record's order.
#: Beat 4's defeat comes before the amendment because the record puts it there, and beat
#: 13 is the same signed no after it, now pending (Q-DYVP).
PLAYED = ("1", "2", "4", "7", "13", "27", "28", "29")

#: Where demo 3's narration is not demo 2's, and only there.
_REWORDED = {
    "28": (
        "Unity is reached and the domain has certified the tally, so by Acme's rules this "
        "act would be authorized. It is not. Meridian asked more of itself than a count, "
        "and the screen names exactly what is outstanding: diligence, under Meridian's own "
        "clause, absent. A bank that has not yet looked at the customer's file has not "
        "finished, and the record says so rather than the compliance officer saying so."
    ),
}


def _run() -> tuple[Beat, ...]:
    everything = OPENER + LIVE + LEAVE_BEHIND
    beats = []
    for identifier in PLAYED:
        beat = named(identifier, everything)
        if identifier in _REWORDED:
            beat = replace(beat, narration=_REWORDED[identifier])
        beats.append(beat)
    return tuple(beats)


RUN = _run()

#: What to drop, in order, if the clock still runs out: the two law screens, since
#: neither is a verdict. Beat 1 first, because the room will just have been taught what
#: a committed law is; then beat 27, whose obligation beat 28's narration restates.
CUT_ORDER = ("1", "27")


def walk3(
    console: Console,
    *,
    beat: str | None = None,
    pause: bool = True,
    substrate: str = FACADE,
    store: Path | None = None,
) -> int:
    """Walk demo 3, or one beat of it, echoing each command and running it.

    No substrate is forced, unlike demo 2's recorded opener: demo 3 is one run played
    live, and the cue card says to play it under keripy.
    """
    sequence = RUN if beat is None else (named(beat, RUN),)
    return play(console, sequence, since="", pause=pause, backend=substrate, store=store)
