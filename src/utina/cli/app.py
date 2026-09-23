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
import textwrap
from collections.abc import Callable, Mapping, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path
from typing import TextIO

from bakobo.errors import BakoboError  # type: ignore[import-untyped]

from utina.acme import Acme
from utina.cli.aliases import Aliases, aliases_over
from utina.cli.appraisal import (
    appraise,
    held_by,
    question_from,
    registry_holdings,
    resolve_credential,
    resolve_subject,
)
from utina.cli.demo2 import PARTS
from utina.cli.errors import ALIAS_UNKNOWN, COMMAND_MALFORMED
from utina.cli.render import (
    MARGIN,
    WRAP,
    brief_screen,
    disturbance_screen,
    enact_screen,
    eval_screen,
    law_screen,
    log_screen,
    registry_screen,
    replay_screen,
    seat_screen,
    whois_screen,
)
from utina.cli.style import SPENT, Style
from utina.cli.world import RealValues, world
from utina.enact import Constructor
from utina.fold.constitution import Constitution
from utina.fold.evaluate import disturbed_by
from utina.fold.question import Committed
from utina.fold.triple import Position
from utina.substrate import FACADE, NAMES

__all__ = ["Console", "main", "run"]

#: What ``--at`` is called when a command was not given one.
LATEST = "the end of the record"

_EPILOG = """\
positions
  inception, d1 ... d9, board-seated -- the beats of docs/demo-script.md, so a
  narrator types something memorable rather than a digest. b5 and b11 are beats
  of docs/demo-2-script.md, whose numbering is its own.

identifiers
  --said and --on take the name the record commits an act under (seat-the-board),
  any unambiguous prefix of an identifier, or the whole thing.

parties
  Screens name a party by a COIA alias -- marta-founder,6 -- and never by a
  piece of its identifier, because a prefix is not a safe way to decide that two
  identifiers are the same. The trailing ,6 is COIA's test flag: throwaway, demo,
  no real-world consequence. Inside these
  screens the scope is always Acme, so the columns drop it. To see the identifier
  behind an alias, ask for it: utina whois marta-founder,6.

color
  On when the output is a terminal, and decided per stream, so a redirected stderr
  stays plain. NO_COLOR turns it off, FORCE_COLOR turns it on through a pipe,
  TERM=dumb turns it off. Six colors, each meaning one thing everywhere it appears:
  green reached, red spent, amber awaiting, magenta convicted, blue not evaluable,
  grey scaffolding. No screen ever carries a meaning in color alone.

examples
  utina law --at inception
  utina eval sign-office-lease --at d3
  utina eval --said seat-the-board --at d4
  utina replay --at board-seated
  utina whois marta-founder,6
  utina enact endorse --as acme:seat3 --on approve-budget-retabled
"""


def _no_pause() -> None:
    """The pause a non-interactive console takes between demo beats."""


def _wait_for_a_keypress() -> None:  # pragma: no cover - stdin belongs to the narrator
    input()


@dataclass(frozen=True)
class Console:
    """Where output goes, whether each stream takes color, and how it waits.

    ``err_color`` defaults to ``None``, meaning "whatever ``color`` says", so a caller
    that knows both streams are the same place — every test that constructs one by hand —
    says it once. :meth:`over` asks each real stream separately, which is the whole point
    of tick 3ebe (this.i @ig3tc5om).
    """

    out: TextIO
    err: TextIO
    color: bool = False
    err_color: bool | None = None
    pause: Callable[[], None] = dataclass_field(default=_no_pause)

    @classmethod
    def over(
        cls, out: TextIO, err: TextIO, *, environ: Mapping[str, str]
    ) -> Console:
        """A console over real streams, with color decided by each stream itself."""
        return cls(
            out=out,
            err=err,
            color=_takes_color(out, environ),
            err_color=_takes_color(err, environ),
            pause=_wait_for_a_keypress,
        )

    @property
    def style(self) -> Style:
        """The style for ``out``, which is where every screen goes."""
        return Style(self.color)

    @property
    def err_style(self) -> Style:
        """The style for ``err``, which is where an error goes.

        Deciding this from ``out`` is what put escape sequences into a redirected stderr:
        the two streams are usually the same terminal, right up to the one case that
        writes a corrupted file, and a rule that is right by coincidence cannot be
        tested (this.i @ig3tc5om).
        """
        return Style(self.color if self.err_color is None else self.err_color)


def _takes_color(stream: TextIO, environ: Mapping[str, str]) -> bool:
    """NO_COLOR beats FORCE_COLOR beats TERM beats the stream, which is the precedence.

    ``TERM=dumb`` is the one terminal that announces it cannot render this, and it is
    checked below FORCE_COLOR so that an explicit request still wins. A terminal that
    lacks 256-color support without saying so is not detected, and that is accepted
    rather than solved: there is no capability query that works over ssh and inside a
    test, the ladder has only the two rungs (this.i @qi3inaua), and the failure is
    legible — a reader sees an escape sequence rather than a wrong color.
    """
    if environ.get("NO_COLOR"):
        return False
    if environ.get("FORCE_COLOR"):
        return True
    if environ.get("TERM") == "dumb":
        return False
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
    evaluate.add_argument("--brief", action="store_true", help="the same answer in 8-10 lines")

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

    whois = commands.add_parser(
        "whois", out=console.out, parents=[backend],
        help="the full identifier behind an alias",
    )
    whois.add_argument("party", metavar="ALIAS-OR-PREFIX")

    enact = commands.add_parser(
        "enact", out=console.out, parents=[backend],
        help="commit a signed endorsement or declination",
    )
    enact.add_argument("disposition", choices=("endorse", "decline"))
    enact.add_argument("--as", dest="actor", required=True, metavar="AID")
    enact.add_argument("--on", dest="subject", required=True, metavar="TOKEN")
    enact.add_argument("--citing", dest="citing", metavar="TOKEN")

    seat = commands.add_parser(
        "seat", out=console.out, parents=[backend],
        help="one office, with KERI's binding and ACDC's side by side",
    )
    seat.add_argument("seat", metavar="OFFICE")
    seat.add_argument("--at", metavar="POSITION")

    registry = commands.add_parser(
        "registry", out=console.out, parents=[backend],
        help="what a credential registry says, folded at a position",
    )
    registry.add_argument("--registry", metavar="SAID")
    registry.add_argument("--at", metavar="POSITION")

    disturbance_parser = commands.add_parser(
        "disturbance", out=console.out, parents=[backend],
        help="which acts in flight an amendment ended",
    )
    disturbance_parser.add_argument("amendment", metavar="TOKEN")
    disturbance_parser.add_argument("--at", metavar="POSITION")

    demo = commands.add_parser(
        "demo", out=console.out, parents=[backend],
        help="walk the ten beats of docs/demo-script.md",
    )
    demo.add_argument("--no-pause", dest="no_pause", action="store_true")
    demo.add_argument("--beat", metavar="ID")

    demo2 = commands.add_parser(
        "demo2", out=console.out, parents=[backend],
        help="walk docs/demo-2-script.md: the opener, the live thirteen, or all of it",
    )
    demo2.add_argument("--part", choices=PARTS, default="live")
    demo2.add_argument("--no-pause", dest="no_pause", action="store_true")
    demo2.add_argument("--beat", metavar="ID")

    return parser


# --- the commands -------------------------------------------------------------


def _world(args: argparse.Namespace) -> AbstractContextManager[Acme]:
    """Acme, built by whichever substrate the command line asked for."""
    return world(args.substrate, store=args.store)


def _aliases(record: Acme) -> Aliases:
    """The display names for this record's parties.

    The composition root's half of this.i @clcoia. Built here, in the CLI, from the
    identifiers inception returned — which is why an alias cannot reach the fold, the
    constructor or the committed bytes, and why both substrates render identically.
    """
    return aliases_over(record.aids)


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
        console.out.write(
            law_screen(law, label, position, _aliases(record), console.style)
        )
    return 0


def eval_command(args: argparse.Namespace, console: Console) -> int:
    with _world(args) as record:
        question = question_from(record.saids, record.events, args.act, args.said)
        label, position = _position(record, args.at)
        appraisal = appraise(record.corpus, question, at=position, label=label)
        draw = brief_screen if args.brief else eval_screen
        console.out.write(draw(appraisal, _aliases(record), console.style))
    return 0


def log_command(args: argparse.Namespace, console: Console) -> int:
    with _world(args) as record:
        label, position = _position(record, args.at)
        console.out.write(
            log_screen(
                record.corpus.upto(position),
                label,
                position,
                _aliases(record),
                console.style,
            )
        )
    return 0


def whois_command(args: argparse.Namespace, console: Console) -> int:
    """The one place a party's full identifier appears (this.i @clwhoi).

    Removing the prefix from every screen removes the only way an audience could see an
    identifier at all, and sometimes seeing one is the point. So it is an explicit act
    rather than a glance: this is the pill's expand affordance, where verification is
    allowed to happen because the reader asked for it.
    """
    with _world(args) as record:
        aliases = _aliases(record)
        identifier = aliases.resolve(args.party)
        if identifier is None:
            raise ALIAS_UNKNOWN(query=args.party, count=len(aliases.every_alias()))
        console.out.write(
            whois_screen(identifier, aliases, args.substrate, console.style)
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


def seat_command(args: argparse.Namespace, console: Console) -> int:
    """One office, with KERI's binding and ACDC's shown side by side.

    The delegation half is asked of the substrate, because key events are not in
    the corpus the fold folds (``this.i`` @jdie6v) and are answerable there or
    nowhere. The credential half is folded from committed events, because
    registry state is a member of the evidence bundle and a screen that read it
    off a transaction log would be showing the fold something it may not use.
    That split is the seam, on one screen, which is the beat.
    """
    with _world(args) as record:
        label, position = _position(record, args.at)
        seat = _actor(record, args.seat)
        upto = record.corpus.upto(position)
        delegation = {
            "delegator": record.substrate.delegator_of(seat),
            "seal": record.substrate.anchoring_event(seat),
        }
        credential = held_by(upto, seat)
        console.out.write(
            seat_screen(
                seat, label, position, delegation, credential,
                _aliases(record), console.style,
            )
        )
    return 0


def registry_command(args: argparse.Namespace, console: Console) -> int:
    """What a registry says about everything in it, folded at one coordinate."""
    with _world(args) as record:
        label, position = _position(record, args.at)
        upto = record.corpus.upto(position)
        registry = record.registry if args.registry is None else args.registry
        console.out.write(
            registry_screen(
                str(registry), record.gaid, label, position,
                registry_holdings(upto, str(registry)), _aliases(record), console.style,
            )
        )
    return 0


def disturbance_command(args: argparse.Namespace, console: Console) -> int:
    """Beat 23: which acts that were in flight this amendment ended.

    The computed side is asked of the evaluator's own function rather than
    recomputed here, because a screen that reimplemented it could disagree with
    the finding printed beside it — and the whole beat is that two readers of one
    record compute one answer.

    A token naming nothing committed renders two empty columns rather than
    raising. A question about bytes nobody committed is ill-posed, and the honest
    screen is the one showing that the record has nothing to say — the same
    posture :func:`resolve_subject` takes one layer up.
    """
    with _world(args) as record:
        label, position = _position(record, args.at)
        said = resolve_subject(record.saids, record.events, args.amendment)
        amendment = record.corpus.event(said)
        computed = (
            () if amendment is None else disturbed_by(record.corpus, amendment, position)
        )
        console.out.write(
            disturbance_screen(
                said,
                label,
                position,
                computed,
                {value: key for key, value in record.saids.items()},
                console.style,
            )
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

        constructor = Constructor.resume(
            record.substrate, record.gaid, values=record.values, events=record.events
        )
        verb = constructor.endorse if args.disposition == "endorse" else constructor.decline
        event = verb(
            _actor(record, args.actor),
            subject,
            qualification=resolve_credential(record.saids, record.events, args.citing),
        )

        corpus = RealValues().corpus(constructor.emitted)
        after = appraise(
            corpus, Committed(subject), at=event.position, label="after this act"
        )
        anchor = record.substrate.anchoring_event(str(event.body["acdc"]["d"]))
        console.out.write(
            enact_screen(
                event, before, after, _aliases(record), console.style, anchor=anchor
            )
        )
    return 0


def demo2_command(args: argparse.Namespace, console: Console) -> int:
    from utina.cli.demo2 import walk2

    return walk2(
        console,
        part=args.part,
        beat=args.beat,
        pause=not args.no_pause,
        substrate=args.substrate,
        store=args.store,
    )


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
    "whois": whois_command,
    "enact": enact_command,
    "seat": seat_command,
    "registry": registry_command,
    "disturbance": disturbance_command,
    "demo": demo_command,
    "demo2": demo2_command,
}


# --- the entry point ----------------------------------------------------------


def render_error(error: BakoboError, style: Style) -> str:
    """An error as complete sentences, with its code and its retryability.

    Wrapped to the same width and margin as every other paragraph the CLI prints. It
    was not, and the error whose detail runs longest is the one demo 2 plays live —
    beat 14, whose whole content is the toolchain refusing an unqualified endorsement.
    That detail is 400-odd characters, and unwrapped it reached the projector as one
    line the terminal broke wherever it happened to run out, unindented and aligned
    with nothing, at the moment the demo wants to show the tool working correctly.
    """
    lines = [f"{style.banner('ERROR', SPENT)}  {error.code}", *_sentences(error.title)]
    if error.detail:
        lines.extend(_sentences(error.detail))
    lines.extend(
        _sentences(
            "Retrying will not help: this condition is permanent."
            if not error.retryable
            else "Retrying may help: this condition is transient."
        )
    )
    if error.hint:
        lines.extend(_sentences(error.hint))
    return "\n".join(lines) + "\n"


def _sentences(text: str) -> list[str]:
    """One block of an error, wrapped into the margin every screen uses."""
    return textwrap.wrap(
        text, width=WRAP, initial_indent=MARGIN, subsequent_indent=MARGIN
    )


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
        console.err.write(render_error(error, console.err_style))
        return 2


def main(argv: Sequence[str] | None = None) -> int:
    """The console script. ``utina --help`` starts here."""
    console = Console.over(sys.stdout, sys.stderr, environ=os.environ)
    return run(sys.argv[1:] if argv is None else argv, console)
