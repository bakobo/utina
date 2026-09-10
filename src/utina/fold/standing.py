"""Registry state, folded from committed evidence and never read from anywhere.

Custos §9 is emphatic about what registry state is and is not. "Registry state
is evidence. Standing is judgment. The committed covenant set is the function
between them" (``custos-4.2.md:1916``), and "a relying party that treats
registry state as authority has skipped the law and trusted the ledger"
(``:1927``). Issue #82's third rule turns that into an implementation
obligation: registry state is "a member of the evidence bundle rather than an
ambient condition read against it", so a revocation is a new registry span,
hence a new bundle, hence a new finding at a new position.

**That is why this module exists and why it is in the fold.** The substrate can
answer what a registry says — it holds the transaction log — but a fold that
asked it would be consulting an ambient condition, and could not do so anyway,
because no plane above the substrate may import a KERI library. So the
constructor commits an issuance and a revocation as governance events, and this
folds *those*: same inputs as every other question the fold answers, same
canonical order, same replay claim (``this.i`` @exy3u4t7).

The events are the credential-registry pair, not the credential alone. One
credential could in principle be issued in two registries, and the question a
caller has is always "does this stand *here*" — the law names the registry a
standing-conferring credential must come from, so a state read that ignored the
registry would answer a question nobody asked.
"""

from __future__ import annotations

from collections.abc import Iterable

from utina.fold.slots import CommittedEvent, credential
from utina.substrate import ISSUED, REVOKED

__all__ = [
    "ISSUANCE_KIND",
    "REGISTRY_FIELD",
    "REVOCATION_KIND",
    "SUBJECT_FIELD",
    "state_over",
]

ISSUANCE_KIND = "issuance"
"""The event kind that commits a registry-bound credential's issuance. It embeds
the credential, as an endorsement event does (``this.i`` @vi4t4i)."""

REVOCATION_KIND = "revocation"
"""The event kind that commits a revocation. It names the credential rather than
embedding it: the credential has not changed, and a second copy of it would be a
second set of bytes claiming to be the same artifact."""

REGISTRY_FIELD = "ri"
"""Where both kinds name the registry the state belongs to — ACDC's own field
name for it, so the committed event and the credential inside agree."""

SUBJECT_FIELD = "said"
"""Where a revocation names the credential it revokes."""


def state_over(
    events: Iterable[CommittedEvent], registry: str, said: str
) -> str | None:
    """Whether ``said`` stands in ``registry`` over ``events``.

    :data:`~utina.substrate.ISSUED`, :data:`~utina.substrate.REVOKED`, or
    ``None`` where nothing committed issues that credential in that registry — a
    credential nobody issued and a credential issued somewhere else are the same
    answer here, and both mean "no standing to read".

    The walk takes the last transition rather than the first, which is the one
    place this differs from the fold's other crossings. Registry state is not a
    threshold being reached: it is a state machine whose committed transitions
    are the events, and a revocation *is* the later fact. What does not move is
    the finding that cited the credential while it stood — that stands at its
    own coordinate, because the bundle it was appraised over does not contain
    this revocation. Prospective revocation falsifies nothing, and the reason it
    reaches no earlier finding is the position, never a special case here.

    Malformed evidence contributes nothing rather than raising. A revocation
    naming no credential, an issuance embedding no credential, a registry field
    that is not a string: each is an event the fold cannot read as a transition,
    and an unreadable transition leaves the state where it was. That is the same
    fail-closed posture the slot predicate takes, for the same reason — a fold
    that raised on a stranger's bytes would let anybody stop it.
    """
    state: str | None = None
    for event in events:
        if event.body.get(REGISTRY_FIELD) != registry:
            continue
        if event.kind == ISSUANCE_KIND and credential(event).get("d") == said:
            state = ISSUED
        elif event.kind == REVOCATION_KIND and event.body.get(SUBJECT_FIELD) == said:
            state = REVOKED
    return state
