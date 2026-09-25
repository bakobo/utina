"""A recognition cue for the one identifier this CLI shows whole.

An entviz **whois line** on the ``subject`` field of an eval screen, and nowhere else:
the four-cell entropy-band prefix, a space, and then the value's own cells. The goal is
**recognition** — "have I seen this one before, is this the one I meant?" — and never
comparison. An equality decision routes to the full value, which this line carries, or
to a real entviz. That seam is entviz's own §1 and ``pill-design.md`` §2.1.

**This module reports a capability and states no preference.** ``entviz.terminal.ansi``
takes ``color="256"`` or ``color="none"``, and its docstring is explicit that capability
detection belongs to the host: ``NO_COLOR``, ``FORCE_COLOR`` and ``isatty`` are read
here and reach entviz only as that argument. So :func:`posture` is handed whether this
stream takes colour — the same bit every other painted thing on the screen is handed —
and passes it through truthfully. It does not choose a rung on policy grounds. Entviz
decides what to draw from the truth about the environment, using measurements and
tradeoffs recorded in its own ``docs/terminal-pill.md`` rather than re-derived here, and
a host that lied to it about the terminal in order to obtain a preferred rendering would
be gaming a decision it does not understand.

For the same reason nothing here second-guesses what entviz does with a value. Entviz
knows the encoding rules of real entropy — which alphabets are case-sensitive and which
are not — so a committed identifier is rendered correctly by construction, and utina's
subject is always a committed identifier. A wrapper that checked entviz's answer and
overrode it would be substituting a guess for a rule.
"""

from __future__ import annotations

from entviz.terminal import ansi, whois  # type: ignore[import-untyped]

__all__ = ["MONO", "PAINTED", "posture"]

#: What entviz is told when this stream takes colour, and when it does not. The two
#: rungs entviz offers (``terminal-pill.md`` §2: 256 is available on the target terminal
#: and truecolor is not, so there are exactly these two).
PAINTED = "256"
MONO = "none"


def posture(value: str, *, color: bool) -> str:
    """``value``'s cells, preceded by its entropy bands, drawn for this stream.

    ``color`` is what the console determined about the stream it is writing to, not a
    request. Passed through to entviz as the rung, which is the argument that function
    exists to take.
    """
    return str(ansi(whois(value), color=PAINTED if color else MONO))
