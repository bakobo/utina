"""The run-of-show: ten beats, each one a command a person could have typed.

This module computes nothing (this.i @cldemo). A beat is a title, a line of narration
and the argv of a query command, and the walk echoes the command and dispatches it
through the same entry point a shell reaches. If a screen appears here that
``utina eval`` cannot produce, then Friday's audience is watching a slideshow with an
engine somewhere behind it, and the demo's own claim is the first thing it fails to
show.

The beats are ``docs/demo-script.md`` in order, and the narration is that document's own
account of what each beat is for. The prologue is not a beat: it is the law screen, so
that the audience has seen the rules before the first decision is judged under them.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import TYPE_CHECKING

from utina.acme import LABEL_UNKNOWN
from utina.cli.render import MARGIN, RULE, WRAP

if TYPE_CHECKING:  # pragma: no cover - the import exists only for the annotation
    from utina.cli.app import Console

__all__ = ["BEATS", "PROLOGUE", "Beat", "walk"]


@dataclass(frozen=True)
class Beat:
    """One beat: what to call it, what it is for, and what to run."""

    id: str
    title: str
    narration: str
    argv: tuple[str, ...]


PROLOGUE = (
    Beat(
        "law",
        "The law Acme committed at inception",
        "Two clauses, two founders, half the weight each. Nothing is judged yet; this "
        "is the rule set every judgment below is computed against.",
        ("law", "--at", "inception"),
    ),
)

BEATS = (
    Beat(
        "d1",
        "Open a bank account",
        "Both founders endorse. Unity is reached, and the affirmation carries the "
        "endorsements that reached it rather than merely asserting that they did.",
        ("eval", "open-bank-account", "--at", "d1"),
    ),
    Beat(
        "d2",
        "Hire a VP of Sales",
        "Marta has endorsed and Dev has not acted. Pending is not a hedge: it names "
        "the slot whose act would discharge it, and how that act would cure it.",
        ("eval", "hire-vp-sales", "--at", "d2"),
    ),
    Beat(
        "d3",
        "Hire a VP of Sales, after Dev declines",
        "The centerpiece, first half. A signed no spends its slot, so the weight that "
        "can still arrive no longer reaches unity. Watch the reachable row.",
        ("eval", "hire-vp-sales", "--at", "d3"),
    ),
    Beat(
        "d4",
        "Seat the board: the amendment itself",
        "The enactment that changes the law is judged under the law it replaces, which "
        "is clause A2 and not the B2 it commits. Succession is never retroactive.",
        ("eval", "--said", "seat-the-board", "--at", "d4"),
    ),
    Beat(
        "d5",
        "Approve the annual budget",
        "Affirmed while a party has never acted at all. Presence is not the question; "
        "reachable weight is.",
        ("eval", "approve-budget", "--at", "d5"),
    ),
    Beat(
        "d6",
        "Approve the annual budget, after Dev declines",
        "The centerpiece, second half. The same signed no from the same person, and "
        "the finding is pending, because with three slots the ceiling still clears "
        "unity. The Constitution changed and the arithmetic did the rest.",
        ("eval", "approve-budget", "--at", "d6"),
    ),
    Beat(
        "d7",
        "Amend the operating agreement",
        "Seating a board distributed ordinary authority and did not distribute the "
        "authority to change the rules. Under B2 the retained bar bites.",
        ("eval", "amend-operating-agreement", "--at", "d7"),
    ),
    Beat(
        "d8",
        "May the board declare a dividend?",
        "No clause governs distributions. The engine refuses rather than legislating, "
        "and names what is missing. This is not a fifth verdict and the screen says so.",
        ("eval", "declare-dividend", "--at", "d8"),
    ),
    Beat(
        "d9",
        "Re-ask the first decision from the end of the record",
        "The past is recomputable under the law in force then: still affirmed, still "
        "under A1, asked from a position where A1 is no longer the law.",
        ("eval", "--said", "open-bank-account", "--at", "d9"),
    ),
    Beat(
        "d10",
        "Refold the log with events in permuted arrival order",
        "Binding at custos-4.2.md:3101, and one command. The same committed bytes in a "
        "different arrival order fold to a byte-identical Constitution.",
        ("replay", "--at", "board-seated"),
    ),
)


def _named(identifier: str) -> Beat:
    """The beat that identifier names, or a refusal that names the ones that exist."""
    for beat in PROLOGUE + BEATS:
        if beat.id == identifier:
            return beat
    raise LABEL_UNKNOWN(
        label=identifier,
        known=", ".join(beat.id for beat in PROLOGUE + BEATS),
    )


def walk(console: Console, *, beat: str | None = None, pause: bool = True) -> int:
    """Walk the beats, echoing each command and running it through the query CLI."""
    from utina.cli.app import run

    sequence = PROLOGUE + BEATS if beat is None else (_named(beat),)
    status = 0
    for index, one in enumerate(sequence):
        for line in _announce(one):
            console.out.write(line + "\n")
        status = max(status, run(one.argv, console))
        if pause and index < len(sequence) - 1:
            console.pause()
    return status


def _announce(beat: Beat) -> list[str]:
    """The card that introduces a beat, and the command as though it were typed."""
    return [
        "",
        MARGIN + RULE,
        f"{MARGIN}BEAT {beat.id.upper():<6}{beat.title}",
        *textwrap.wrap(
            beat.narration, width=WRAP, initial_indent=MARGIN, subsequent_indent=MARGIN
        ),
        "",
        f"{MARGIN}$ utina {' '.join(beat.argv)}",
        "",
    ]
