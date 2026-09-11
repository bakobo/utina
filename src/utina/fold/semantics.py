"""The external semantics a law is expressed in, pinned by digest — axiom 4.

``custos-4.2.md:290`` requires an external semantics to be pinned by committed
digest, and an unpinned or unrecognized one to be **refused**, never assumed at
whatever revision happens to be installed. Acme's law is expressed in the
dossier specification's terms — its operator vocabulary, its slot shape, its
three dispositions — so the dossier specification is exactly such a semantics,
and the law has to name which revision of it the clauses mean.

**Why this is in the law and not in the engine.** An engine that assumed its own
revision would answer confidently under a lens nobody committed, and would keep
answering after the lens moved underneath it. The failure is not hypothetical:
the discipline ``companions/engagement-companion.md`` exists because three of
Custos 4.1's five pinned artifacts moved *after* ratification. So the digest is
committed law, this module holds only the revisions the engine can actually
apply, and a law pinning anything else produces a refusal rather than an answer.

**Why a refusal rather than a pending finding.** Rule-presence, not
evidence-presence (``fold/refusal.py``). A law pinning a semantics this engine
does not implement has not run short of evidence — it has named a lens the fold
cannot look through, so the question is ill-posed for this engine rather than
undischarged. Axiom 3's "where committed law runs out, the fold refuses rather
than legislates" reaches this case: what has run out is law this fold can read.
"""

from __future__ import annotations

from collections.abc import Mapping

from utina.fold.refusal import Refusal

__all__ = [
    "DOSSIER",
    "DOSSIER_KEY",
    "RECOGNIZED",
    "SEMANTICS_FIELD",
    "declared",
    "refusal_for",
]

SEMANTICS_FIELD = "semantics"
"""Where a law body carries its semantics-declaration block."""

DOSSIER_KEY = "dossier"
"""The semantics Acme's composition rule is expressed in."""

DOSSIER = "08fd67445b6f1a966f5f13f3ff028d3d9a48d2ab2acb8e3147ac538cff4a489a"
"""SHA-256 over the dossier specification's body, as vendored at
``schemas/dossier-spec-body.md`` and recomputed by ``tests/test_schemas.py``.

Provenance, because a digest with none is a number: the document is
``spec/dossier-spec-body.md`` from ``trustoverip/kswg-dossier-specification`` at
``5906e8cf570099761b57761fac6cbec50325b3c1`` (2026-08-12). SHA-256 rather than
the KERI-native digest for the reason ``clause.py`` gives for the same choice —
the fold imports no KERI library, so it cannot compute one.

**The vendored copy can go stale, and that is the point rather than a defect.**
If the specification moves, this engine still implements the revision it was
written against, and Acme's law still pins that revision; a law pinning the new
one would be refused here until the engine is updated to match. That is axiom 4
working. What it does NOT do is notice the drift on its own, so re-pinning is a
deliberate act (tick 2uhi)."""

RECOGNIZED = frozenset({DOSSIER})
"""Every semantics revision this fold can actually apply. A set rather than a
single value because an engine may legitimately implement two revisions at once
during a migration; it is a *closed* set because the whole discipline is that
anything outside it is refused rather than attempted."""


def declared(law: Mapping[str, object]) -> str | None:
    """The semantics digest a law body pins, or ``None`` where it pins none.

    ``None`` is the unpinned case and it is not the same as an unrecognized one,
    though both refuse: a law that never said what its clauses mean is a
    different mistake from one that said something this engine cannot read, and
    the refusal names which it was.
    """
    block = law.get(SEMANTICS_FIELD)
    if not isinstance(block, Mapping):
        return None
    pinned = block.get(DOSSIER_KEY)
    return pinned if isinstance(pinned, str) and pinned else None


def refusal_for(pinned: str | None) -> Refusal | None:
    """The refusal a law's declaration earns, or ``None`` where it is applicable.

    Total over both failures, because an engine that refused the unpinned case
    and quietly attempted the unrecognized one would be assuming at exactly the
    moment axiom 4 forbids it.
    """
    if pinned is None:
        return Refusal(
            missing="a semantics declaration naming the dossier specification by digest",
            detail=(
                "This law's composition rule is expressed in an external semantics and the "
                "law does not say which revision of it the clauses mean. Axiom 4 requires an "
                "external semantics to be pinned by committed digest; a fold that assumed "
                "its own revision would answer under a lens nobody committed."
            ),
        )
    if pinned not in RECOGNIZED:
        return Refusal(
            missing=f"an implementation of the semantics this law pins, {pinned[:16]}...",
            detail=(
                "The law pins a revision of the dossier specification this engine does not "
                "implement, so its clauses are expressed in terms this fold cannot read. "
                "That is a refusal and not a finding: the evidence is not short, the lens "
                "is one the fold does not have."
            ),
        )
    return None
