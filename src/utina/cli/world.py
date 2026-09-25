"""The record every command reads, which domain built it, and the fold types it is over.

Each fixture is parameterized over a ``FoldValues`` protocol so the writing plane never
imports the fold (this.i @tvaq2s). The CLI is the composition root that hands it the real
constructors, which is the same job ``tests/conftest.py`` does for the acceptance oracle.

:data:`DOMAINS` is the whole of ``--domain``: a name to the function that builds that
domain's record. Adding a third is an entry here and a cast in ``utina.cli.aliases``, and
nothing else — which is the property the flag exists to demonstrate (this.i @s34hkwkv).

The record is rebuilt on every invocation rather than persisted. It is deterministic in
its own committed bytes, so two invocations produce the same log down to the identifier;
what does not survive is an act committed by ``utina enact``, which is a property this.i
@clphmr chose deliberately and which the enact screen states in words.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path

from utina import acme, bank
from utina.domain import Record
from utina.fold.corpus import Corpus, Event
from utina.fold.gel import anchored
from utina.fold.triple import Position
from utina.substrate import FACADE, substrate_named

__all__ = ["DEFAULT_DOMAIN", "DOMAINS", "RealValues", "world"]

#: Every governed domain a command can be pointed at, by the name ``--domain`` takes.
#: Acme is first because it is the demo's, and a mapping preserves insertion order, so
#: the help text lists it first without anybody sorting for that.
DOMAINS: Mapping[str, Callable[..., Record]] = {
    acme.DOMAIN: acme.build,
    bank.DOMAIN: bank.build,
}

#: What ``--domain`` means when nobody says. Acme, because every beat of both demo
#: scripts is Acme's and a default that moved would make the demo depend on a flag.
DEFAULT_DOMAIN = acme.DOMAIN


class RealValues:
    """A ``utina.substrate.FoldValues`` over ``utina.fold``'s own value types."""

    def position(self, seq: int) -> Position:
        return Position(seq=seq)

    def event(
        self, *, said: str, kind: str, position: Position, body: Mapping[str, object]
    ) -> Event:
        return Event(said=said, kind=kind, position=position, body=body)

    def corpus(
        self,
        events: Sequence[Event],
        *,
        kel: Sequence[Mapping[str, object]] | None = None,
        gaid: str | None = None,
    ) -> Corpus:
        if kel is None:
            return Corpus.load(events)
        return anchored(events, kel, gaid=str(gaid))


@contextmanager
def world(
    substrate: str = FACADE,
    *,
    store: Path | None = None,
    domain: str = DEFAULT_DOMAIN,
) -> Iterator[Record]:
    """One domain's law and committed log, folded over the real types.

    A context manager because one of the backends holds a keystore and two LMDB
    environments and has to close them, and because a command that asked the
    fold a question after the key log was shut would get PENDING for an answer
    rather than an error. The facade opens and closes nothing; the ``with`` is
    written once here so no command has to know which it got.

    ``substrate`` defaults to the facade by decision (this.i @dxs27r): a demo
    runs in the morning, and the fallback from a keripy fault has to be a flag
    somebody can type rather than a git operation performed in front of an
    audience.

    ``domain`` defaults to Acme for the same kind of reason: both demo scripts are
    Acme's, and a default that could move would make the demo depend on a flag nobody
    types. The builder is resolved before a substrate is opened, so a name that is not
    one of :data:`DOMAINS` fails with nothing to close — though the CLI offers these
    names as argparse choices and refuses an unknown one a layer earlier.
    """
    builder = DOMAINS[domain]
    with substrate_named(substrate, store=store) as backend:
        yield builder(values=RealValues(), substrate=backend)
