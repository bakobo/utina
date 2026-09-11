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

from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol

from utina.substrate import ISSUED, REVOKED

SAID = str
"""A self-addressing digest of committed bytes."""

__all__ = [
    "ISSUANCE_KIND",
    "REGISTRY_FIELD",
    "REVOCATION_KIND",
    "SUBJECT_FIELD",
    "CommittedEvent",
    "registry_of",
    "state_over",
    "stood_at",
]


class CommittedEvent(Protocol):
    """The read-only view of a committed event this module needs.

    Declared here rather than imported from ``utina.fold.slots``, which declares
    the same shape for the same reason (``this.i`` @yenp2x): the slot predicate
    now asks *this* module whether a cited credential stood, so an import the
    other way would close a cycle. Two four-line protocols over one structural
    shape is the cheaper of the two prices.
    """

    @property
    def said(self) -> str: ...

    @property
    def kind(self) -> str: ...

    @property
    def body(self) -> Mapping[str, object]: ...


def _acdc(event: CommittedEvent) -> Mapping[str, object]:
    """The credential an event embeds, or an empty mapping — never an error."""
    embedded = event.body.get("acdc")
    return embedded if isinstance(embedded, Mapping) else {}

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
        if event.kind == ISSUANCE_KIND and _acdc(event).get("d") == said:
            state = ISSUED
        elif event.kind == REVOCATION_KIND and event.body.get(SUBJECT_FIELD) == said:
            state = REVOKED
    return state


def registry_of(events: Iterable[CommittedEvent], said: SAID) -> SAID | None:
    """The registry a committed issuance of ``said`` names, or ``None``.

    Read out of the issuance rather than taken from a caller, because the
    registry a credential is revocable through is a fact the credential's own
    issuance committed. A credential this record never issued has no registry
    here, which is the same fail-closed answer as one issued somewhere else.
    """
    for event in events:
        if event.kind == ISSUANCE_KIND and _acdc(event).get("d") == said:
            registry = event.body.get(REGISTRY_FIELD)
            return registry if isinstance(registry, str) else None
    return None


def stood_at(asof: Sequence[CommittedEvent], said: SAID) -> bool:
    """Whether ``said`` stood in its own registry over the record ``asof``.

    ``asof`` is the record *as of a coordinate* — the committed events up to and
    including the one whose standing is in question — and that is the whole
    point of this function's shape. Custos names registry state as one of the
    four things a slot judgment asks (``:1958-1962``), and issue #82's fourth
    rule fixes which coordinate it asks about: "a prospective revocation
    falsifies nothing — the credential *did stand at p*, and revocation changes
    its state going forward". So a citation is judged at the coordinate of the
    act that made it, never at the position the question is asked from.

    That is what lets the same question be re-asked after a revocation and come
    back with the same answer, while a *new* act citing the same credential
    fails: the first cited a credential that stood when it was cited, and the
    second does not. Neither is a special case here; both are this one rule
    applied at two coordinates.
    """
    registry = registry_of(asof, said)
    return registry is not None and state_over(asof, registry, said) == ISSUED
