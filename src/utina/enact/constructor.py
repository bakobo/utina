"""Producing committed governance events, and never judging one.

Custos section 1.3: a constructor cannot act except by producing the evidence
of its act. So every verb here ends in a signed event on the record, and the
verbs are the whole vocabulary — there is no way through this object to record
that a party decided something without producing the bytes in which they
decided it.

That closure is what makes the demo's centerpiece true rather than asserted.
``endorse`` and ``decline`` are two names on one emitter, differing in a single
committed field, so a declination is exactly as much of an act as an
endorsement and an untouched slot is not an act at all (this.i @7szbfw).
"""

from __future__ import annotations

from collections.abc import Mapping

from utina.substrate import AID, SAID, Event, FoldValues, Substrate

from .errors import (
    DOMAIN_INCEPTED,
    DOMAIN_UNINCEPTED,
    SIGNATURE_UNVERIFIABLE,
    SUBJECT_UNKNOWN,
)

#: The registry operation an endorsement commits. ``docs/interfaces.md`` makes
#: every endorsement an MxN group counts carry ``act`` of ``"issue"``, and the
#: fold's slot predicate reads exactly that field: an endorsement without it is
#: not refused, it is silently PENDING, so the field is the seam and not a
#: decoration. This domain commits no revocation operator — a party who changes
#: their mind declines, which is another issuance.
ISSUANCE = "issue"


class Constructor:
    """The writing plane for one governed domain."""

    def __init__(self, substrate: Substrate, gaid: AID, *, values: FoldValues) -> None:
        self.substrate = substrate
        self.gaid = gaid
        self._values = values
        self._emitted: list[Event] = []
        self._saids: set[SAID] = set()
        self._anchored: dict[SAID, Event] = {}
        self._founded = False

    @property
    def emitted(self) -> tuple[Event, ...]:
        """Every event this constructor committed, in the order it committed them."""
        return tuple(self._emitted)

    # -- the verbs ------------------------------------------------------------

    def incept_domain(self, founding_law: Mapping[str, object]) -> Event:
        """Bring the domain into being under a founding law."""
        if self._founded:
            raise DOMAIN_INCEPTED(gaid=self.gaid)
        self.substrate.incept(self.gaid)
        event = self._emit(
            "inception", {"t": "icp", "i": self.gaid, "law": founding_law}, self.gaid
        )
        self._founded = True
        return event

    def enact_amendment(self, law: Mapping[str, object]) -> Event:
        """Commit a successor law, anchored in an establishment event.

        custos-4.2.md:2085-2087 designates an enactment amending law as a class
        that SHALL anchor in an establishment event, so the enactment is
        committed and then a rotation seals it. The rotation is the substrate's
        and never enters the corpus (this.i @jdie6v); the binding it creates is
        answerable through :meth:`anchoring_event`.
        """
        self._require_founded()
        event = self._emit("enactment", {"t": "enact", "i": self.gaid, "law": law}, self.gaid)
        self._anchored[event.said] = self.substrate.rotate(self.gaid, event.said)
        return event

    def propose(self, act: str) -> Event:
        """Commit an act for appraisal."""
        self._require_founded()
        return self._emit("act", {"t": "act", "i": self.gaid, "act": act}, self.gaid)

    def endorse(self, aid: AID, subject: SAID) -> Event:
        """Commit ``aid``'s signed yes to ``subject``."""
        return self._dispose(aid, subject, "endorse")

    def decline(self, aid: AID, subject: SAID) -> Event:
        """Commit ``aid``'s signed no to ``subject``.

        A declination is a signed, attributable, committed act. Its weight
        contributes nothing to unity and its slot is spent, but that is the
        fold's reading of these bytes, not something decided here.
        """
        return self._dispose(aid, subject, "decline")

    def anchoring_event(self, said: SAID) -> Event | None:
        """The establishment event that sealed ``said``, if one did."""
        return self._anchored.get(said)

    # -- internals ------------------------------------------------------------

    def _require_founded(self) -> None:
        if not self._founded:
            raise DOMAIN_UNINCEPTED(gaid=self.gaid)

    def _dispose(self, aid: AID, subject: SAID, disposition: str) -> Event:
        self._require_founded()
        if subject not in self._saids:
            raise SUBJECT_UNKNOWN(aid=aid, subject=subject)
        return self._emit(
            "endorsement",
            {"t": "end", "i": aid, "act": ISSUANCE, "disp": disposition, "said": subject},
            aid,
        )

    def _emit(self, kind: str, body: Mapping[str, object], signer: AID) -> Event:
        """Seal, sign, check, and only then commit.

        The order is the point. The coordinate goes into the bytes before the
        identifier is computed, so the fold's canonical order is derivable from
        committed bytes alone (S2). The identifier goes in before the signature,
        so the signature commits to it. And the signature is verified before the
        event is recorded, because an event whose own signature does not stand
        up confers no authority and must not reach the record.
        """
        seq = len(self._emitted)
        sealed = {**body, "s": seq}
        said = self.substrate.said(sealed)
        sealed = {**sealed, "d": said}
        signature = self.substrate.sign(signer, sealed)
        if not self.substrate.verify(signer, sealed, signature):
            raise SIGNATURE_UNVERIFIABLE(kind=kind, aid=signer)
        event = self._values.event(
            said=said,
            kind=kind,
            position=self._values.position(seq),
            body={**sealed, "sig": signature},
        )
        self._emitted.append(event)
        self._saids.add(said)
        return event
