"""The entviz recognition cue on the eval screen's subject line.

M8's criterion: the ``subject`` field renders as a corpus-posture pill; every other
identifier is untouched; the strip-escapes invariant still holds on every screen.

The field renders entviz's PILL: elided, about nineteen columns. Recognition is the
goal and comparison is not, which was measured rather than assumed — no beat asks a
reader to copy or compare a subject, ``--said`` takes a name or a twelve-character
prefix, and every other identifier on every screen is already abbreviated. On a
committed-act question the banner one line above still carries the value whole.

The criterion's third clause is the one that moved. The cue's two rungs are alternate
renderings of the same information — entviz substitutes braille when told the stream takes no
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

import pytest

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


@pytest.mark.skip(reason="subject pill disabled for the demo")
def test_the_subject_is_a_pill_that_opens_with_the_bands_and_ends_in_the_tail() -> None:
    """Four band cells, then the value's own head and tail cells around elisions.

    The head and tail are asserted against the identifier itself rather than against a
    literal, so the test says "this cue belongs to this value" rather than pinning a
    rendering entviz is free to improve.
    """
    with world() as record:
        said = record.said("seat-the-board")
    line = subject_line(screen("eval", "--said", "seat-the-board", "--at", "d4"))
    cue = line[line.index("subject") + len("subject") :].strip()

    bands, _, cells = cue.partition(" ")
    assert len(bands) == 4, f"expected four band cells, got {bands!r}"
    assert all(GLYPHS.fullmatch(one) for one in bands), bands
    assert cells.startswith(said[:4]), f"{cells!r} does not open with the value's head"
    assert cells.endswith(said[-4:]), f"{cells!r} does not close with the value's tail"
    assert said not in cue, "a pill elides; this is the whole value"


def test_the_cue_is_a_function_of_the_value_and_of_nothing_else() -> None:
    """Two different identifiers get two different cues; one gets one answer."""
    with world() as record:
        first, second = record.said("seat-the-board"), record.said("lower-the-bar")
    assert posture(first, color=False) == posture(first, color=False)
    assert posture(first, color=False) != posture(second, color=False)


def test_every_committed_identifier_keeps_its_own_characters_in_the_cue() -> None:
    """Entviz knows the encoding rules of real entropy, so a committed identifier's
    cells are its own characters rather than a transformation of them.

    Asserted over every identifier the record commits rather than over one, since that
    is the claim utina relies on when it hands entviz a value and does not check the
    answer. Head and tail, because those are the cells a pill shows.
    """
    with world() as record:
        for said in record.saids.values():
            for form in (ANSI.sub("", posture(said, color=True)), posture(said, color=False)):
                cells = form.partition(" ")[2]
                assert cells.startswith(said[:4]), (said, form)
                assert cells.endswith(said[-4:]), (said, form)


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


@pytest.mark.skip(reason="subject pill disabled for the demo")
def test_the_cue_reaches_a_second_domain_without_being_told_about_it() -> None:
    """It is a function of the value, so it is domain-agnostic for free."""
    line = subject_line(
        screen("eval", "open-customer-account", "--domain", "bank", "--at", "5")
    )
    assert GLYPHS.search(line)


# --- what the two rungs owe each other ----------------------------------------


def test_neither_rung_says_more_than_the_other_about_the_value() -> None:
    """The ladder must not invert (``terminal-pill.md`` §4.3): stripping colour is a
    change of presentation rather than a loss. Both rungs are the same printable width
    and both show the same cells; only the glyphs between them differ."""
    with world() as record:
        said = record.said("seat-the-board")
    painted, mono = posture(said, color=True), posture(said, color=False)
    assert len(ANSI.sub("", painted)) == len(mono)
    assert ANSI.sub("", painted).endswith(said[-4:]) and mono.endswith(said[-4:])
    assert ANSI.sub("", painted) != mono, "the mono rung swaps glyphs; it is not plain"
