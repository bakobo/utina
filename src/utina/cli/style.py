"""Color, and the rule that it never carries a meaning on its own.

Every semantic on a screen is a word first — ``DEFEATED``, ``declined``, ``unity
unreachable`` — and a color second. So the plain form is the whole form, which is what
lets ``tests/test_cli.py`` assert that stripping the escape sequences from the colored
output yields the uncolored output exactly.

Padding happens before painting, never after: an escape sequence has width in bytes and
none on the screen, so a field padded around its own color codes would be aligned in
neither form. Every helper here therefore takes text that is already the width it should
occupy — and the one column that is *last* on its line is painted unpadded, because
:func:`~utina.cli.render._row` and ``_screen`` both ``rstrip`` and cannot reach inside an
escape sequence to do it.

**The values are 256-palette indices, never the sixteen SGR color slots** (this.i
@qi3inaua). Indices 0-15 are the terminal's own theme and every terminal remaps them, so
a verdict painted with ``32`` is whatever green the machine in the room is configured
for. Indices 16-255 are fixed by the xterm cube and render identically everywhere. There
are two rungs, 256 and none; there is no 16-color rung, because every slot in it is the
thing being escaped, and no truecolor, which the terminal this is demoed from does not
support (both measured 2026-08-15, ``entviz/docs/terminal-pill.md`` §2).

**Six roles, and each one means the same thing on every screen** (this.i @w6bpgbwi). A
color names a health state rather than a screen element, so ``endorsed`` in the
disposition column, "unity reached" on the sums row and an ``AFFIRMED`` banner are the
same claim at three altitudes. What that rules out is the reflex reading: a defeat is
healthy governance — a signed no correctly spending a slot — and a revocation is ordinary
and bounded, so neither is painted as a malfunction.
"""

from __future__ import annotations

from dataclasses import dataclass

from utina.fold.finding import PendingSpecies, Verdict
from utina.fold.group import Disposition

__all__ = [
    "AWAITING",
    "CONVICTED",
    "DISPOSITION_COLOR",
    "NOT_EVALUABLE",
    "REACHED",
    "REFUSAL_COLOR",
    "SCAFFOLD",
    "SPECIES_COLOR",
    "SPENT",
    "VERDICT_COLOR",
    "Style",
]

_RESET = "\x1b[0m"

BOLD = "1"

#: Unity is reached, or the weight that reaches it is in hand.
REACHED = "38;5;40"

#: The path is dead: a slot is spent, or the record closed the cure path.
SPENT = "38;5;196"

#: In flight. Not finished, and not blocked either.
AWAITING = "38;5;220"

#: The record contradicts itself, and no further evidence cures it.
CONVICTED = "38;5;170"

#: Outside the codomain: there is no answer to be had here, not a negative one.
NOT_EVALUABLE = "38;5;39"

#: Labels, table headers, rules, the shell prompt — everything that is not content.
#: An explicit index rather than SGR 2, which terminals implement least consistently of
#: all and which some ignore outright, and which can vanish under projection.
SCAFFOLD = "38;5;245"

#: What each of the four findings is painted in. A refusal is deliberately absent: it is
#: not a member of the codomain, and giving it an entry here would be the first step
#: towards rendering it as a fifth verdict (this.i @clrfsl).
#:
#: Affirmed and defeated share the screen with nothing else, but the three dispositions
#: below sit in one column beside each other, so REACHED, SPENT and AWAITING carry a
#: monotone Oklab lightness spacing — 0.628, 0.762, 0.887 — and read as dark, mid, light
#: for a viewer with a color deficiency or a photograph of the screen (this.i @b3nr4mq3).
VERDICT_COLOR = {
    Verdict.AFFIRMED: REACHED,
    Verdict.DEFEATED: SPENT,
    Verdict.PENDING: AWAITING,
    Verdict.SELF_CONVICTED: CONVICTED,
}

#: What a refusal's banner is painted in, which is a color no verdict uses.
REFUSAL_COLOR = NOT_EVALUABLE

#: What each slot disposition is painted in, which is the row-level form of the same
#: three claims the two sums rows make about the clause as a whole.
DISPOSITION_COLOR = {
    Disposition.ENDORSED: REACHED,
    Disposition.DECLINED: SPENT,
    Disposition.PENDING: AWAITING,
}

#: What each discharge species is painted in — the finest-grained statement the engine
#: makes about whether a pending act is blocked. ``absent`` and ``window-open`` are
#: waiting on evidence that can still arrive; ``expired/abandoned`` is the species issue
#: #82 widened to carry a cure path the *record* closed; ``unresolved-conflict`` is cured
#: by nothing but an act of the conflicted party's own, which is a conviction's shape
#: rather than a delay's.
SPECIES_COLOR = {
    PendingSpecies.ABSENT: AWAITING,
    PendingSpecies.WINDOW_OPEN: AWAITING,
    PendingSpecies.EXPIRED_ABANDONED: SPENT,
    PendingSpecies.UNRESOLVED_CONFLICT: CONVICTED,
}


@dataclass(frozen=True)
class Style:
    """Whether this stream takes color, and how to apply it if it does."""

    enabled: bool

    def paint(self, text: str, sgr: str) -> str:
        """``text`` in the given SGR parameters, or ``text`` unchanged."""
        if not self.enabled:
            return text
        return f"\x1b[{sgr}m{text}{_RESET}"

    def banner(self, text: str, sgr: str) -> str:
        """A verdict or a refusal headline: bold, and in its own color."""
        return self.paint(text, f"{BOLD};{sgr}")

    def label(self, text: str) -> str:
        """A field label, which is scaffolding rather than content."""
        return self.paint(text, SCAFFOLD)

    def strong(self, text: str) -> str:
        """A heading that is not a verdict."""
        return self.paint(text, BOLD)
