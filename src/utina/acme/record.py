"""What a built Acme is: committed events, and two ways to address them.

The acceptance oracle never indexes the log. It asks for a position by the name
the demo script gives that beat, and for an event by the name of the act it
commits, which is what lets the oracle read as the table it mirrors.
"""

from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass

from utina.substrate import AID, SAID, Corpus, Event, FoldValues, Position, Substrate

from .errors import LABEL_UNKNOWN, NAME_UNKNOWN
from .law import GAID


@dataclass(frozen=True)
class Acme:
    """Acme's committed record, built once and read many times."""

    events: tuple[Event, ...]
    corpus: Corpus
    labels: Mapping[str, int]
    saids: Mapping[str, SAID]
    aids: Mapping[str, AID]
    substrate: Substrate
    values: FoldValues

    def at(self, label: str) -> Position:
        """The appraisal coordinate of the beat ``label`` names."""
        if label not in self.labels:
            raise LABEL_UNKNOWN(label=label, known=", ".join(sorted(self.labels)))
        return self.values.position(self.labels[label])

    @property
    def gaid(self) -> AID:
        """The governed domain's identifier, as inception returned it."""
        return self.aids[GAID]

    def aid(self, alias: str) -> AID:
        """The identifier ``alias`` names.

        Every caller that used to write ``"acme:marta"`` asks through here. Under
        the facade the answer is the alias itself; under keripy it is a prefix
        nobody could have written down beforehand (this.i @crrtzf), and a caller
        holding the alias would be addressing a party who does not exist.
        """
        if alias not in self.aids:
            raise NAME_UNKNOWN(name=alias, known=", ".join(sorted(self.aids)))
        return self.aids[alias]

    def said(self, name: str) -> SAID:
        """The identifier of the committed event ``name`` names."""
        if name not in self.saids:
            raise NAME_UNKNOWN(name=name, known=", ".join(sorted(self.saids)))
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
        return self.values.corpus(self.permuted_events(seed))
