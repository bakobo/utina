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
from types import TracebackType
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
        (this.i @ff4jzv; Q27 in ``docs/custos-questions.md``).

        The substrate owns canonicalization outright, because it owns the
        digest. A caller may not rely on mapping insertion order reaching, or
        not reaching, the bytes — implementations disagree about that, and an
        implementation that let two conventions meet would produce a signature
        failure wearing a digest's clothes (this.i @fy5lwj).
        """
        ...

    def sign(self, aid: AID, body: Mapping[str, object]) -> str:
        """Sign ``body`` as ``aid``, under that identifier's current key state.

        The returned string is opaque above this seam. An implementation whose
        key state moves is expected to pack the coordinate it signed under into
        it, so that :meth:`verify` keeps answering the same way after a
        rotation (this.i @zk27gz).
        """
        ...

    def verify(self, aid: AID, body: Mapping[str, object], signature: str) -> bool:
        """Whether ``signature`` is ``aid``'s over ``body``.

        Fail closed and total: anything unverifiable — an unknown identifier, a
        malformed signature, a key state that never existed — is ``False``, and
        never an exception a caller might be tempted to treat as a maybe. A real
        KERI library raises on malformed CESR and on an unknown prefix, so a
        conforming implementation over one wraps rather than propagates.
        """
        ...

    def incept(self, alias: str) -> AID:
        """Bring an identifier into being, and return the identifier to use.

        The alias is a name for the caller's convenience and the return value is
        the identifier. They are the same string under the facade and different
        under keripy, where a prefix is a digest of the inception event and
        cannot be known before this call returns; a caller that hardcodes the
        alias breaks there rather than here (this.i @crrtzf).
        """
        ...

    def rotate(self, aid: AID, anchor: SAID) -> SAID:
        """Rotate ``aid``, sealing ``anchor`` into the establishment event.

        Returns that establishment event's identifier. This exists because
        Custos binds law-amending enactments to anchor in an establishment event
        (custos-4.2.md:2085-2087): Acme's board-seating amendment rides a
        rotation.

        It returns an identifier rather than a committed ``Event`` because the
        rotation's own sequence number lives in the key log's ordering space,
        which must never be compared with a corpus position (this.i @ygjwyw).
        """
        ...

    def anchoring_event(self, said: SAID) -> SAID | None:
        """The establishment event that sealed ``said``, if one did.

        Rotations stay out of the corpus the fold folds (this.i @jdie6v), so the
        binding an anchored enactment claims is answerable here or nowhere.
        """
        ...


class OpenSubstrate(Substrate, Protocol):
    """A substrate that also has a lifecycle, which is every concrete one.

    ``Substrate`` is the six governance answers and nothing else: that is what
    the writing plane is written against, and it should not have to know that
    one backend owns a keystore and two LMDB environments. Opening and closing
    is a construction contract, so it is named here rather than folded into the
    protocol above — the composition root writes one ``with`` and every backend
    honours it, including the facade, which has nothing to close.
    """

    def __enter__(self) -> Substrate:
        """The substrate, ready to answer."""
        ...

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Release whatever was held, whether or not the block succeeded."""
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
