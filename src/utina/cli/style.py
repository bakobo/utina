"""Colour, and the rule that it never carries a meaning on its own.

Every semantic on a screen is a word first — ``DEFEATED``, ``declined``, ``unity
unreachable`` — and a colour second. So the plain form is the whole form, which is what
lets ``tests/test_cli.py`` assert that stripping the escape sequences from the coloured
output yields the uncoloured output exactly.

Padding happens before painting, never after: an escape sequence has width in bytes and
none on the screen, so a field padded around its own colour codes would be aligned in
neither form. Every helper here therefore takes text that is already the width it should
occupy.
"""

from __future__ import annotations

from dataclasses import dataclass

from utina.fold.finding import Verdict

__all__ = ["VERDICT_COLOUR", "Style"]

_RESET = "\x1b[0m"

BOLD = "1"
DIM = "2"
RED = "31"
GREEN = "32"
YELLOW = "33"
MAGENTA = "35"
CYAN = "36"

#: What each of the four findings is painted in. A refusal is deliberately absent: it is
#: not a member of the codomain, and giving it an entry here would be the first step
#: towards rendering it as a fifth verdict (this.i @clrfsl).
VERDICT_COLOUR = {
    Verdict.AFFIRMED: GREEN,
    Verdict.DEFEATED: RED,
    Verdict.PENDING: YELLOW,
    Verdict.SELF_CONVICTED: MAGENTA,
}

#: What a refusal's banner is painted in, which is a colour no verdict uses.
REFUSAL_COLOUR = CYAN


@dataclass(frozen=True)
class Style:
    """Whether this stream takes colour, and how to apply it if it does."""

    enabled: bool

    def paint(self, text: str, sgr: str) -> str:
        """``text`` in the given SGR parameters, or ``text`` unchanged."""
        if not self.enabled:
            return text
        return f"\x1b[{sgr}m{text}{_RESET}"

    def banner(self, text: str, sgr: str) -> str:
        """A verdict or a refusal headline: bold, and in its own colour."""
        return self.paint(text, f"{BOLD};{sgr}")

    def label(self, text: str) -> str:
        """A field label, which is scaffolding rather than content."""
        return self.paint(text, DIM)

    def strong(self, text: str) -> str:
        """A heading that is not a verdict."""
        return self.paint(text, BOLD)
