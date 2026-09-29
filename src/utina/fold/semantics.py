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
from dataclasses import dataclass

from utina.fold.refusal import Refusal, SealKind

__all__ = [
    "CONSUMED",
    "DOSSIER",
    "DOSSIER_KEY",
    "EXCLUDED",
    "IMPLEMENTED",
    "KERI",
    "KERI_KEY",
    "KERI_SPEC_KEY",
    "RECOGNIZED",
    "RECOVERY_KEY",
    "RECOVERY_RULES",
    "SEMANTICS_FIELD",
    "Dependency",
    "declared",
    "dependency",
    "dependency_refusal_for",
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
            seal_kind=SealKind.DIGEST,
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
            seal_kind=SealKind.DIGEST,
            missing=f"an implementation of the semantics this law pins, {pinned[:16]}...",
            detail=(
                "The law pins a revision of the dossier specification this engine does not "
                "implement, so its clauses are expressed in terms this fold cannot read. "
                "That is a refusal and not a finding: the evidence is not short, the lens "
                "is one the fold does not have."
            ),
        )
    return None


# --- the functional-dependency declaration -----------------------------------------
#
# custos-4.2.md:2850-2858: a Constitution SHALL commit the revision digests of every
# external specification whose semantics its fold consumes, naming the predicate set
# consumed — KERI's superseding-recovery calculus rule by rule, each consumed or
# expressly excluded, never in silence. The fold runs none of those rules, since no
# plane above the substrate may; it consumes them because a duplicity observation
# convicts only under the key tier's committed rules, and these are those rules
# (this.i @ehrgtmuj, tick 3uv4).

KERI_KEY = "keri"
"""Where the semantics block carries the KERI dependency."""

KERI_SPEC_KEY = "spec"
"""The digest of the KERI specification revision, inside the dependency."""

RECOVERY_KEY = "recovery"
"""The disposition of each superseding-recovery rule, inside the dependency."""

KERI = "10df5b8ca9395ce8d4270a84fb7338124b0bd8c80dfc27b65601418b3c4533c4"
"""SHA-256 over the KERI specification's body, as vendored at
``schemas/keri-spec-body.md`` and recomputed by ``tests/test_schemas.py``.

The document is ``spec/spec-body.md`` from ``trustoverip/kswg-keri-specification`` at
``71cb54ebb445dd9d8cb33cd29a5f50894fafc569`` (2026-07-28), the revision the Custos
engagement companion pins. The whole-file digest stands where the recovery rules
live, which :2857-2859 confesses as pin granularity rather than design."""

RECOVERY_RULES = ("A0", "A1", "A2", "B1", "B2", "B3", "C", "C1")
"""The superseding-recovery rules the pinned revision names, in its own order.

Every labelled item of the section except the headings ``A.`` and ``B.``, whose
content their numbered members carry. ``C`` is a rule in its own right, the recursion
through delegators, and ``C1`` is its terminal case; ``tests/test_schemas.py`` checks
the set against the vendored text in both directions."""

CONSUMED = "consumed"
EXCLUDED = "excluded"


@dataclass(frozen=True)
class Dependency:
    """What a law commits about KERI: which revision, and each recovery rule's fate.

    ``recovery`` is a sorted tuple of pairs rather than a mapping so the value is
    hashable and two declarations compare equal exactly when they say the same thing.
    """

    spec: str
    recovery: tuple[tuple[str, str], ...]


IMPLEMENTED = Dependency(KERI, tuple(sorted((rule, CONSUMED) for rule in RECOVERY_RULES)))
"""The one declaration this engine implements. Closed like :data:`RECOGNIZED`, and
for the same reason: an exclusion the engine cannot honour is refused, not assumed."""


def dependency(law: Mapping[str, object]) -> Dependency | None:
    """The KERI dependency a law body declares, or ``None`` where it declares none
    this fold can read. Read fail-closed, like every other committed value."""
    block = law.get(SEMANTICS_FIELD)
    if not isinstance(block, Mapping):
        return None
    keri = block.get(KERI_KEY)
    if not isinstance(keri, Mapping):
        return None
    spec = keri.get(KERI_SPEC_KEY)
    recovery = keri.get(RECOVERY_KEY)
    if not (isinstance(spec, str) and spec and isinstance(recovery, Mapping)):
        return None
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in recovery.items()):
        return None
    return Dependency(spec, tuple(sorted(recovery.items())))


def dependency_refusal_for(declared: Dependency | None) -> Refusal | None:
    """The refusal a law's KERI dependency earns, or ``None`` where it is applicable.

    Four failures, each refused in its own words, because they are four different
    mistakes: saying nothing, pinning a revision this engine does not carry, leaving a
    rule in silence, and declaring dispositions this engine does not implement.
    """
    if declared is None:
        return Refusal(
            seal_kind=SealKind.DIGEST,
            missing=(
                "a functional-dependency declaration naming KERI's revision by digest and "
                "the fate of each superseding-recovery rule"
            ),
            detail=(
                "Custos requires a Constitution to commit the revision of every external "
                "specification its fold consumes, and this law says nothing about KERI. A "
                "duplicity observation convicts only under the key tier's committed rules, "
                "so without the declaration there is no committed rule for it to convict under."
            ),
        )
    if declared.spec != KERI:
        return Refusal(
            seal_kind=SealKind.DIGEST,
            missing=(
                f"an implementation of the KERI revision this law pins, {declared.spec[:16]}..."
            ),
            detail=(
                "The law pins a revision of the KERI specification this engine does not carry, "
                "so the recovery rules it names are rules this fold has not read."
            ),
        )
    named = {rule for rule, _ in declared.recovery}
    silent = [rule for rule in RECOVERY_RULES if rule not in named]
    if silent:
        return Refusal(
            seal_kind=SealKind.DIGEST,
            missing=f"a disposition for superseding-recovery rules {', '.join(silent)}",
            detail=(
                "Each rule the fold's semantics depend on is to be consumed or expressly "
                "excluded, never passed over in silence, and this law is silent on some."
            ),
        )
    if declared != IMPLEMENTED:
        return Refusal(
            seal_kind=SealKind.DIGEST,
            missing="an implementation of the recovery dispositions this law declares",
            detail=(
                "This engine consumes every superseding-recovery rule and implements no other "
                "declaration. Answering under an exclusion it cannot honour would be assuming "
                "at exactly the moment axiom 4 forbids it."
            ),
        )
    return None
