"""What a person types, and where it goes.

The parser is thin on purpose. Every command resolves its arguments, asks
``utina.fold`` or ``utina.enact`` exactly one question, and hands the answer to a
renderer; nothing in this module decides anything about governance.

Errors leave through one door. Every failure carries a ``bakobo.errors`` code, says
whether retrying could help, and reads as complete sentences — including the ones
argparse would otherwise print as a bare usage line, which is why ``_Parser.error``
raises rather than exits. Exit status says whether the command answered, not what it
answered (this.i @clexit): a defeated finding is a complete answer and exits 0.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path
from typing import TextIO

from bakobo.errors import BakoboError  # type: ignore[import-untyped]

from utina.acme import Acme
from utina.cli.appraisal import appraise, question_from, resolve_subject
from utina.cli.errors import COMMAND_MALFORMED
from utina.cli.render import (
    enact_screen,
    eval_screen,
    law_screen,
    log_screen,
    replay_screen,
)
from utina.cli.style import RED, Style
from utina.cli.world import RealValues, constructor_over, world
from utina.fold.constitution import Constitution
from utina.fold.question import Committed
from utina.fold.triple import Position
from utina.substrate import FACADE, NAMES

__all__ = ["Console", "main", "run"]

#: What ``--at`` is called when a command was not given one.
LATEST = "the end of the record"

_EPILOG = """\
positions
  inception, d1 ... d9, board-seated -- the beats of docs/demo-script.md, so a
  narrator types something memorable rather than a digest.

identifiers
  --said and --on take the name the record commits an act under (seat-the-board),
  any unambiguous prefix of an identifier, or the whole thing. The 12-character
  prefix the screens print is a valid handle.

colour
  On when the output is a terminal. NO_COLOR turns it off, FORCE_COLOR turns it on
  through a pipe. No screen ever carries a meaning in colour alone.

examples
  utina law --at inception
  utina eval hire-vp-sales --at d3
  utina eval --said seat-the-board --at d4
  utina replay --at board-seated
  utina enact endorse --as acme:nina --on approve-budget-retabled
"""


def _no_pause() -> None:
    """The pause a non-interactive console takes between demo beats."""


def _wait_for_a_keypress() -> None:  # pragma: no cover - stdin belongs to the narrator
    input()


@dataclass(frozen=True)
class Console:
    """Where output goes, whether it takes colour, and how it waits."""

    out: TextIO
    err: TextIO
    color: bool = False
    pause: Callable[[], None] = dataclass_field(default=_no_pause)

    @classmethod
    def over(
        cls, out: TextIO, err: TextIO, *, environ: Mapping[str, str]
    ) -> Console:
        """A console over real streams, with colour decided by the stream itself."""
        return cls(
            out=out,
            err=err,
            color=_takes_colour(out, environ),
            pause=_wait_for_a_keypress,
        )

    @property
    def style(self) -> Style:
        return Style(self.color)


def _takes_colour(stream: TextIO, environ: Mapping[str, str]) -> bool:
    """NO_COLOR beats FORCE_COLOR beats the stream, which is the usual precedence."""
    if environ.get("NO_COLOR"):
        return False
    if environ.get("FORCE_COLOR"):
        return True
    return stream.isatty()


class _Parser(argparse.ArgumentParser):
    """An argparse parser that writes where it is told and raises what it must."""

    def __init__(self, *args: object, out: TextIO, **kwargs: object) -> None:
        self._out = out
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

    def _print_message(self, message: str, file: object = None) -> None:
        self._out.write(message)

    def error(self, message: str) -> None:  # type: ignore[override]
        raise COMMAND_MALFORMED(detail=message, usage=self.format_usage().strip())


def build_parser(console: Console) -> _Parser:
    """The whole command surface, as a person would discover it."""
    parser = _Parser(
        prog="utina",
        out=console.out,
        description=(
            "Compute a governed domain's law from its committed logs, and evaluate "
            "decisions against it."
        ),
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    backend = _Parser(add_help=False, out=console.out)
    backend.add_argument(
        "--substrate", choices=NAMES, default=FACADE, metavar="NAME",
        help="which substrate writes the record (default: %(default)s)",
    )
    backend.add_argument(
        "--store", type=Path, default=None, metavar="DIR",
        help="where a keripy key log is kept, for another KERI tool to read",
    )

    commands = parser.add_subparsers(dest="command", metavar="COMMAND")

    law = commands.add_parser(
        "law", out=console.out, parents=[backend],
        help="the law in force at a position",
    )
    law.add_argument("--at", required=True, metavar="POSITION")

    evaluate = commands.add_parser(
        "eval", out=console.out, parents=[backend],
        help="appraise a proposal or a committed act",
    )
    evaluate.add_argument("act", nargs="?", metavar="ACT-CLASS")
    evaluate.add_argument("--said", metavar="TOKEN")
    evaluate.add_argument("--at", required=True, metavar="POSITION")

    log = commands.add_parser(
        "log", out=console.out, parents=[backend],
        help="the committed events in canonical order",
    )
    log.add_argument("--at", metavar="POSITION")

    replay = commands.add_parser(
        "replay", out=console.out, parents=[backend],
        help="refold the log and print the canonical digest",
    )
    replay.add_argument("--at", required=True, metavar="POSITION")
    replay.add_argument("--seed", type=int, default=7, metavar="N")

    enact = commands.add_parser(
        "enact", out=console.out, parents=[backend],
        help="commit a signed endorsement or declination",
    )
    enact.add_argument("disposition", choices=("endorse", "decline"))
    enact.add_argument("--as", dest="actor", required=True, metavar="AID")
    enact.add_argument("--on", dest="subject", required=True, metavar="TOKEN")

    demo = commands.add_parser(
        "demo", out=console.out, parents=[backend],
        help="walk the ten beats of docs/demo-script.md",
    )
    demo.add_argument("--no-pause", dest="no_pause", action="store_true")
    demo.add_argument("--beat", metavar="ID")

    return parser


# --- the commands -------------------------------------------------------------


def _world(args: argparse.Namespace) -> AbstractContextManager[Acme]:
    """Acme, built by whichever substrate the command line asked for."""
    return world(args.substrate, store=args.store)


def _actor(record: Acme, name: str) -> str:
    """The identifier a party is addressed by, from the alias a person typed.

    Under the facade they are the same string. Under keripy the alias is a name
    and the identifier is a prefix (this.i @crrtzf), and a narrator is not going
    to type a prefix. Anything the record does not know as an alias goes through
    untouched, so an identifier still works — and an identifier nobody incepted
    is refused by the substrate rather than guessed at here.
    """
    return record.aids.get(name, name)


def _position(record: Acme, label: str | None) -> tuple[str, Position]:
    """The coordinate a command was pointed at, and what to call it on screen."""
    if label is None:
        return LATEST, record.events[-1].position
    return label, record.at(label)


def law_command(args: argparse.Namespace, console: Console) -> int:
    with _world(args) as record:
        label, position = _position(record, args.at)
        law = Constitution.at(record.corpus, position)
        console.out.write(law_screen(law, label, position, console.style))
    return 0


def eval_command(args: argparse.Namespace, console: Console) -> int:
    with _world(args) as record:
        question = question_from(record.saids, record.events, args.act, args.said)
        label, position = _position(record, args.at)
        appraisal = appraise(record.corpus, question, at=position, label=label)
        console.out.write(eval_screen(appraisal, console.style))
    return 0


def log_command(args: argparse.Namespace, console: Console) -> int:
    with _world(args) as record:
        label, position = _position(record, args.at)
        console.out.write(
            log_screen(record.corpus.upto(position), label, position, console.style)
        )
    return 0


def replay_command(args: argparse.Namespace, console: Console) -> int:
    with _world(args) as record:
        label, position = _position(record, args.at)
        straight = Constitution.at(record.corpus, position)
        shuffled = Constitution.at(record.permuted_corpus(seed=args.seed), position)
        console.out.write(
            replay_screen(straight, shuffled, label, position, args.seed, console.style)
        )
    return 0


def enact_command(args: argparse.Namespace, console: Console) -> int:
    """The constructor's verb: a party acts, and the act lands on the record.

    Nothing here judges. The verb commits signed bytes, and the screen then asks the
    fold what the record says about the subject now — which is the whole demonstration
    that a constructor cannot act except by producing the evidence of its act.
    """
    with _world(args) as record:
        subject = resolve_subject(record.saids, record.events, args.subject)
        _, end = _position(record, None)
        before = appraise(record.corpus, Committed(subject), at=end, label=LATEST)

        constructor = constructor_over(record)
        verb = constructor.endorse if args.disposition == "endorse" else constructor.decline
        event = verb(_actor(record, args.actor), subject)

        corpus = RealValues().corpus(constructor.emitted)
        after = appraise(
            corpus, Committed(subject), at=event.position, label="after this act"
        )
        console.out.write(enact_screen(event, before, after, console.style))
    return 0


def demo_command(args: argparse.Namespace, console: Console) -> int:
    from utina.cli.demo import walk

    return walk(
        console,
        beat=args.beat,
        pause=not args.no_pause,
        substrate=args.substrate,
        store=args.store,
    )


COMMANDS: Mapping[str, Callable[[argparse.Namespace, Console], int]] = {
    "law": law_command,
    "eval": eval_command,
    "log": log_command,
    "replay": replay_command,
    "enact": enact_command,
    "demo": demo_command,
}


# --- the entry point ----------------------------------------------------------


def render_error(error: BakoboError, style: Style) -> str:
    """An error as complete sentences, with its code and its retryability."""
    lines = [
        f"{style.banner('ERROR', RED)}  {error.code}",
        f"  {error.title}",
    ]
    if error.detail:
        lines.append(f"  {error.detail}")
    lines.append(
        "  Retrying will not help: this condition is permanent."
        if not error.retryable
        else "  Retrying may help: this condition is transient."
    )
    if error.hint:
        lines.append(f"  {error.hint}")
    return "\n".join(lines) + "\n"


def run(argv: Sequence[str], console: Console) -> int:
    """One command. 0 if it answered, 2 if it could not."""
    parser = build_parser(console)
    try:
        args = parser.parse_args(list(argv))
        if args.command is None:
            parser.print_help()
            return 0
        return COMMANDS[args.command](args, console)
    except SystemExit:
        # argparse exits only to print --help, and only ever with status 0: the one
        # path that would exit non-zero is error(), which raises instead.
        return 0
    except BakoboError as error:
        console.err.write(render_error(error, console.style))
        return 2


def main(argv: Sequence[str] | None = None) -> int:
    """The console script. ``utina --help`` starts here."""
    console = Console.over(sys.stdout, sys.stderr, environ=os.environ)
    return run(sys.argv[1:] if argv is None else argv, console)
