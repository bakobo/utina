"""Who certified an act, which is when it becomes consequential.

Votes being cast is not a result. An election is consequential when it is officially
tabulated and certified, and governance is the same: a decision is authorized when the
domain records that its threshold was met, not at the moment the last endorsement
happens to exist somewhere. Daniel ruled this on 2026-09-23 and ``this.i`` @2e2dncfe
carries the argument; what follows is only the part the fold needs.

**What a certification is.** A sponsor gathers the dispositions, issues a dossier ACDC
whose edges cite each one, and the domain verifies that dossier and admits it to the
GEL with an event of its own. The dossier is the proof and the admission is the act —
which is why the certifier is not merely asserting. A verifier walks the edges,
recomputes the threshold, and a certification that claims more than its edges support
contradicts itself on bytes its own signer committed.

This is the dossier specification's own machinery rather than a new invention. Joint
issuance already defines a **finalization event**, the ``fi`` field naming the AID whose
KEL carries it, and a **finalizer** who "observes the threshold to be met" and anchors
the threshold-satisfying proofs where a verifier can find them
(``schemas/dossier-spec-body.md:377-379``). There it is advisory, an aid to verifiers
who would rather not walk the graph. Here it is constitutive.

**A domain says whether it requires one**, by naming the schema its certifications must
satisfy, exactly as a slot names the endorsement schema its evidence must satisfy
(``custos-4.2.md:1946-1951``). A law that names none requires none, and its acts are
authorized by their arithmetic alone. That is not a migration convenience: whether
decisions in a domain need certifying is a governance question, and Custos delegates
this kind of committed form to the domain elsewhere for the same reason — ``:1924``
does it for expiry semantics.

**What this module does not decide.** Whether a certification's edges actually support
its claim, and what the domain must check before admitting one, are the next milestone's
(M3 and M4 of the build plan). Here the fold answers one question: does a certification
for this subject exist at or before this coordinate.
"""

from __future__ import annotations

from collections.abc import Mapping

from utina.fold.corpus import Corpus, Event
from utina.fold.triple import SAID, Position

__all__ = [
    "CERTIFICATION_KIND",
    "CERTIFIES_FIELD",
    "REQUIRES_FIELD",
    "certifying",
    "required_by",
]

CERTIFICATION_KIND = "certification"
"""The committed event kind by which a domain admits a sponsor's tally to its GEL."""

CERTIFIES_FIELD = "certifies"
"""Where a certification names the subject whose threshold it reports as met."""

REQUIRES_FIELD = "certification"
"""Where a law names the schema its certifications must satisfy, or names none."""


def required_by(law: Mapping[str, object]) -> SAID | None:
    """The certification schema this law requires, or ``None`` where it requires none.

    Read fail-closed in the same shape as the semantics block: a field whose value is
    not a usable identifier is read as naming nothing rather than guessed at, because a
    requirement the fold cannot read is not one it can hold anybody to.
    """
    named = law.get(REQUIRES_FIELD)
    return named if isinstance(named, str) and named else None


def certifying(corpus: Corpus, said: SAID, upto: Position) -> Event | None:
    """The committed certification of ``said`` at or before ``upto``, if there is one.

    The first rather than the last. A second certification of one subject is not a
    correction — the first one already made the act consequential, and a coordinate
    that moved when a later event arrived would make the moment of authorization a
    function of when the question was asked.
    """
    for event in corpus.upto(upto):
        if event.kind != CERTIFICATION_KIND:
            continue
        if event.body.get(CERTIFIES_FIELD) == said:
            return event
    return None
