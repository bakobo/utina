"""What a built governed domain is: committed events, and three ways to address them.

This was ``utina.acme.Acme``, and moving it is the whole of ``this.i`` @s34hkwkv. While
there was one fixture, "the record" and "Acme's record" were one thing in the type
system, so a second domain could only exist by returning a value of a class named after
the first — which is the hardcoding ``--domain`` exists to remove, one plane above the
place a reader would look for it.

A record knows what it is called in both of the registers a command needs: :attr:`name`
is what ``--domain`` takes and what a display cast is looked up by, and :attr:`display`
is what a screen calls the domain. Neither is committed and neither reaches the fold.

The acceptance oracles never index the log. They ask for a position by the name the demo
script gives that beat, and for an event by the name of the act it commits, which is what
lets an oracle read as the table it mirrors. A domain with no such table is addressed by
sequence number instead (@qtm5ntkg), which every domain accepts.
"""

from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass

from utina.substrate import AID, SAID, Corpus, Event, FoldValues, Position, Substrate

from .errors import LABEL_UNKNOWN, LABELS_ABSENT, NAME_UNKNOWN, POSITION_OUT_OF_RANGE

__all__ = ["SEQ_DIGITS", "Record", "is_sequence"]

#: The longest a ``--at`` sequence number may be before it is out of range on its face.
#: A record of 10^18 events does not exist, and the bound keeps an arbitrarily long digit
#: string from reaching :func:`int` at all — size, then shape, then meaning, which is
#: ``AGENTS.md``'s order and not an optimization.
SEQ_DIGITS = 18


def is_sequence(label: str) -> bool:
    """Whether ``label`` is a sequence number rather than a name for one.

    ASCII digits only. :meth:`str.isdigit` is true of Arabic-Indic and other decimal
    forms that :func:`int` also accepts, and a coordinate that resolved from one of
    those would be a position nobody could have read off a screen.

    Shared with the display plane rather than reimplemented there, because the
    meanwhile card's closing note says that the coordinates it names are a demo's and
    not the record's — which is false of a coordinate somebody typed as a number, and
    two predicates drifting apart is how it would become false without anybody noticing.
    """
    return label.isascii() and label.isdigit()


@dataclass(frozen=True)
class Record:
    """One governed domain's committed record, built once and read many times."""

    name: str
    """What ``--domain`` takes to select this record, and what a display cast is keyed
    by: ``acme``, ``bank``. Lower case, because it is typed."""
    display: str
    """What a screen calls this domain: ``Acme``. Not committed, and not an alias — it
    is the domain's own name as a person says it, which no substrate knows."""

    gaid: AID
    """The governed domain's own identifier, as inception returned it. A field rather
    than a lookup through :attr:`aids`, because the alias it was incepted under is each
    fixture's own vocabulary and a shared record may not know one fixture's constant."""

    events: tuple[Event, ...]
    corpus: Corpus
    labels: Mapping[str, int]
    saids: Mapping[str, SAID]
    aids: Mapping[str, AID]
    substrate: Substrate
    values: FoldValues
    kel: tuple[Mapping[str, object], ...] = ()
    """The gAID's key log, which says where each event was committed. The corpus
    derives its order and membership from it (this.i @wsxwkwgv)."""
    registry: SAID | None = None
    """The domain's credential registry, if the story opened one. Held because a
    registry-bound credential's state is asked per registry, and a caller that
    had to rediscover the identifier would be guessing at which log answers."""

    @property
    def last(self) -> int:
        """The sequence number of the last committed event.

        Every record has one: a domain is founded by an inception, and a record with no
        events is a record no fixture can build.
        """
        return int(self.events[-1].position.seq)

    def at(self, label: str) -> Position:
        """The appraisal coordinate ``label`` names: a beat's name, or a sequence number.

        Labels first, so no existing label can change meaning by looking like a number —
        none of them does, and none can become numeric without this refusing to build.
        Then a sequence number, in every domain rather than only in one with no labels,
        because the same argument meaning two things according to a fixture's table is
        exactly the property ``--domain`` exists to stop mattering (this.i @qtm5ntkg).
        """
        if label in self.labels:
            return self.values.position(self.labels[label])
        if is_sequence(label):
            if len(label) > SEQ_DIGITS or int(label) > self.last:
                raise POSITION_OUT_OF_RANGE(
                    domain=self.display, seq=label, last=self.last
                )
            return self.values.position(int(label))
        if not self.labels:
            raise LABELS_ABSENT(domain=self.display, label=label, last=self.last)
        raise LABEL_UNKNOWN(
            domain=self.display, label=label, known=", ".join(sorted(self.labels))
        )

    def aid(self, alias: str) -> AID:
        """The identifier ``alias`` names.

        Every caller that used to write ``"acme:marta"`` asks through here. Under
        the facade the answer is the alias itself; under keripy it is a prefix
        nobody could have written down beforehand (this.i @crrtzf), and a caller
        holding the alias would be addressing a party who does not exist.
        """
        if alias not in self.aids:
            raise NAME_UNKNOWN(
                domain=self.display, name=alias, known=", ".join(sorted(self.aids))
            )
        return self.aids[alias]

    def said(self, name: str) -> SAID:
        """The identifier of the committed event ``name`` names."""
        if name not in self.saids:
            raise NAME_UNKNOWN(
                domain=self.display, name=name, known=", ".join(sorted(self.saids))
            )
        return self.saids[name]

    def permuted_events(self, seed: int) -> tuple[Event, ...]:
        """The same committed events, in a different arrival order.

        Deterministic in ``seed``, so the replay beat is reproducible rather
        than merely likely.
        """
        shuffled = list(self.events)
        random.Random(seed).shuffle(shuffled)
        return tuple(shuffled)

    def permuted_corpus(self, *, seed: int) -> Corpus:
        """The corpus loaded from a permuted arrival order.

        Beat D10, and the binding at custos-4.2.md:3101: a stream presented in
        permuted arrival order SHALL fold to a byte-identical Constitution. The
        permutation is real; the sameness has to come from the fold deriving its
        order from committed bytes, which is the property under test.
        """
        return self.values.corpus(self.permuted_events(seed), kel=self.kel, gaid=self.gaid)
