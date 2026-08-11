"""The two protocols the writing plane is written against.

``Substrate`` is the KERI-facing seam. The demo runs the pure-Python facade in
this package; keripy arrives later as a second implementation of exactly this
protocol, which is what makes it a drop-in rather than a rewrite. Nothing above
this seam may reach past it for a digest.

``FoldValues`` is the other seam, and it exists because of Custos section 1.3:
the constructor's plane and the judge's plane are separate, and no object
performs both. The writing plane produces the fold's value types without
importing the fold, by being handed their constructors at the composition root
(this.i @tvaq2s). The values are opaque here — constructed, carried, never
inspected — which is why they are typed ``Any`` rather than imported for the
sake of an annotation the writing plane would then be entitled to read.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

#: An identifier. ``"acme:marta"`` under the facade; a real prefix under keripy.
AID = str

#: A self-addressing digest of committed bytes.
SAID = str

#: ``utina.fold.triple.Position`` — an appraisal coordinate.
Position = Any

#: ``utina.fold.corpus.Event`` — one committed governance event.
Event = Any

#: ``utina.fold.corpus.Corpus`` — committed evidence in canonical order.
Corpus = Any


class Substrate(Protocol):
    """Digests, signatures, identifiers and key state."""

    def said(self, body: Mapping[str, object]) -> SAID:
        """The self-addressing identifier of ``body``.

        Computed over the body's canonical bytes with the identifier field held
        at a placeholder of the identifier's own length, and with any signature
        removed. So this is idempotent over a sealed, signed event: the SAID of
        a signed event equals the SAID of the same event before it was signed
        (this.i @ff4jzv; S5 in ``docs/questions-substrate.md``).
        """
        ...

    def sign(self, aid: AID, body: Mapping[str, object]) -> str:
        """Sign ``body`` as ``aid``, under that identifier's current key state."""
        ...

    def verify(self, aid: AID, body: Mapping[str, object], signature: str) -> bool:
        """Whether ``signature`` is ``aid``'s over ``body``.

        Fail closed and total: anything unverifiable — an unknown identifier, a
        malformed signature, a key state that never existed — is ``False``, and
        never an exception a caller might be tempted to treat as a maybe.
        """
        ...

    def incept(self, alias: str) -> AID:
        """Bring an identifier into being, and return the identifier to use."""
        ...

    def rotate(self, aid: AID, anchor: SAID) -> Event:
        """Rotate ``aid``, sealing ``anchor`` into the establishment event.

        This exists because Custos binds law-amending enactments to anchor in
        an establishment event (custos-4.2.md:2085-2087): Acme's board-seating
        amendment rides a rotation.
        """
        ...


class FoldValues(Protocol):
    """Constructors for the three fold value types the writing plane produces."""

    def position(self, seq: int) -> Position:
        """An appraisal coordinate at committed sequence ``seq``."""
        ...

    def event(
        self,
        *,
        said: SAID,
        kind: str,
        position: Position,
        body: Mapping[str, object],
    ) -> Event:
        """One committed event."""
        ...

    def corpus(self, events: Sequence[Event]) -> Corpus:
        """Committed evidence, which the fold will put in canonical order."""
        ...
