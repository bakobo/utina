"""The entviz recognition cue on the eval screen's subject line.

M8's criterion: the ``subject`` field renders as a corpus-posture pill; every other
identifier is untouched; the strip-escapes invariant still holds on every screen.

The third clause is the one that moved. The cue's two rungs are alternate renderings of
the same information — entviz substitutes braille when it is told the stream takes no
colour, precisely so that what colour carried is carried by glyph count instead
(``terminal-pill.md`` §4.3) — so stripping the escapes from the painted form does not
yield the plain form, and nothing is lost either way. The invariant holds on every
screen *except* this one line, and ``tests/test_cli.py`` drops that line before
asserting it. Whether that invariant should survive at all is Daniel's to rule (Q-PX2Q).

What this module mostly pins is the seam: utina tells entviz the truth about the stream
and nothing else. It does not ask for a rung, does not inspect what comes back, and does
not second-guess how a value is encoded — entviz knows the encoding rules of real
entropy and utina's subject is always a committed identifier.
"""

from __future__ import annotations

import re
from io import StringIO

from utina.cli import Console, run
from utina.cli.pill import MONO, PAINTED, posture
from utina.cli.world import world

ANSI = re.compile(r"\x1b\[[0-9;]*m")

#: The glyphs a cue is drawn from on either rung: the block elements, and braille.
GLYPHS = re.compile(r"[▀-▟⠀-⣿]")


def screen(*argv: str, color: bool = False) -> str:
    out, err = StringIO(), StringIO()
    run(argv, Console(out=out, err=err, color=color))
    return out.getvalue()


def subject_line(text: str) -> str:
    """The one line of an eval screen this commission touches, escapes and all."""
    lines = [
        one for one in text.splitlines() if ANSI.sub("", one).strip().startswith("subject")
    ]
    assert len(lines) == 1, f"expected exactly one subject field, got {len(lines)}"
    return lines[0]


# --- the seam: a capability is reported, a preference is not ------------------


def test_the_rung_follows_the_stream_rather_than_a_preference() -> None:
    """utina tells entviz whether this stream takes colour. That is the whole contract.

    ``entviz.terminal.ansi``'s own docstring puts capability detection on the host:
    ``NO_COLOR``, ``FORCE_COLOR`` and ``isatty`` are read there and reach it only as
    this argument. A host that named a rung on policy grounds would be steering a
    decision entviz makes from measurements the host has not read.
    """
    with world() as record:
        said = record.said("seat-the-board")
    assert "\x1b[" in posture(said, color=True)
    assert "\x1b[" not in posture(said, color=False)


def test_the_two_rungs_are_the_ones_entviz_offers() -> None:
    """256 is available on the target terminal and truecolor is not, so there are
    exactly two (``terminal-pill.md`` §2)."""
    from entviz.terminal import palette

    assert set(palette.COLOR_MODES) == {PAINTED, MONO}


def test_a_screen_asks_for_the_rung_its_own_console_decided() -> None:
    """The console already decides colour per stream; the cue inherits that and does
    not re-derive it."""
    argv = ("eval", "--said", "seat-the-board", "--at", "d4")
    assert "\x1b[" in subject_line(screen(*argv, color=True))
    assert "\x1b[" not in subject_line(screen(*argv, color=False))


# --- the cue itself -----------------------------------------------------------


def test_the_subject_carries_its_entropy_bands_and_then_the_value_whole() -> None:
    """A whois line rather than a pill: every cell, so the value stays copyable."""
    with world() as record:
        said = record.said("seat-the-board")
    line = subject_line(screen("eval", "--said", "seat-the-board", "--at", "d4"))
    assert line.endswith(said), "the value is not whole, or not last"
    prefix = line[line.index("subject") + len("subject") :].strip()[: -len(said)].strip()
    assert len(prefix) == 4, f"expected four band cells, got {prefix!r}"
    assert all(GLYPHS.fullmatch(one) for one in prefix), prefix


def test_the_cue_is_a_function_of_the_value_and_of_nothing_else() -> None:
    """Two different identifiers get two different cues; one gets one answer."""
    with world() as record:
        first, second = record.said("seat-the-board"), record.said("lower-the-bar")
    assert posture(first, color=False) == posture(first, color=False)
    assert posture(first, color=False) != posture(second, color=False)


def test_a_real_identifier_is_carried_back_character_for_character() -> None:
    """Entviz knows the encoding rules of real entropy, so a committed identifier
    survives it byte for byte. Asserted over every identifier the record commits
    rather than over one, since that is the claim utina relies on."""
    with world() as record:
        for said in record.saids.values():
            assert ANSI.sub("", posture(said, color=True)).endswith(said)
            assert posture(said, color=False).endswith(said)


def test_every_other_identifier_is_untouched() -> None:
    """The criterion's second clause. A recognition cue belongs on the value a reader
    is asked to recognize, and on no other."""
    out = screen("eval", "--said", "seat-the-board", "--at", "d4")
    for line in out.splitlines():
        if line.strip().startswith("subject"):
            continue
        assert not GLYPHS.search(line), f"a cue leaked onto {line!r}"


def test_a_screen_with_nothing_tabled_says_so_rather_than_drawing_a_cue() -> None:
    """There is no value to recognize, so there is nothing to summarize."""
    line = subject_line(screen("eval", "approve-budget", "--at", "d1"))
    assert "nothing of this class has been tabled" in line
    assert not GLYPHS.search(line)


def test_the_cue_reaches_a_second_domain_without_being_told_about_it() -> None:
    """It is a function of the value, so it is domain-agnostic for free."""
    line = subject_line(
        screen("eval", "approve-credit-line", "--domain", "bank", "--at", "6")
    )
    assert GLYPHS.search(line)


# --- what the two rungs owe each other ----------------------------------------


def test_neither_rung_says_more_than_the_other_about_the_value() -> None:
    """The ladder must not invert (``terminal-pill.md`` §4.3): stripping colour is a
    change of presentation, not a loss of the value. Both rungs are the same printable
    width and both end in the identifier entire, which is what a reader copies."""
    with world() as record:
        said = record.said("seat-the-board")
    painted, mono = posture(said, color=True), posture(said, color=False)
    assert len(ANSI.sub("", painted)) == len(mono)
    assert ANSI.sub("", painted).endswith(said) and mono.endswith(said)
    assert ANSI.sub("", painted) != mono, "the mono rung swaps glyphs; it is not plain"
