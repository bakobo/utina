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

#: The dossier specification's single endorsement schema — the one all four
#: threshold operators use, which every endorsement credential's ``s`` field
#: names (``dossier-spec-body.md:367``; the schema itself is
#: ``schemas/endorsement.json`` in the specification repo, and its ``$id`` is
#: this SAID). Declared at the substrate because both backends construct
#: credentials and both planes above read the pin (this.i @7db5c4).
ENDORSEMENT_SCHEMA = "EAfn0gRMUnp6d1hyE5qJCN86kBFBp80JwMdm0BqiC1B0"

#: Bakobo's Generalized Cooperative Delegation credential — "an ACDC expressing a
#: delegate's authorizations, constraints, and duties" — which is the artifact
#: that CONFERS authority, as against the KERI delegation relationship, which
#: confers none (``this.i`` @cglayqvw). Version 2.0.1 rather than the current
#: 3.1.x, and that is forced rather than preferred: 3.x requires the ACDC v2
#: envelope, and keripy's credential path writes only v1
#: (``keri/vc/proving.py``). The document is vendored at
#: ``schemas/gcd-2.0.1.json`` and ``tests/test_schemas.py`` recomputes this pin
#: from it, so an upstream edit is a red test rather than an untypable credential.
GCD_SCHEMA = "EAqOeo_YMHDEMZ-dIJTYd72nsoUS-C1RdXtOdfAj7ZxR"

#: The governance framework a GCD is issued under, named by its ruleset's own
#: identifier because "the act of issuing or receiving a GCD credential
#: constitutes binding acceptance of the rules". Committed in the compact form —
#: the SAID alone, which the schema's ``r`` admits — because the rules are the
#: same for every GCD utina writes and inlining them would put five disclaimers
#: into every credential's bytes. ``schemas/gcd-rules.json`` is the document.
GCD_RULES = "ENiUyBCG2MjCHa9djlgHiogd6uZHECc09ZELmQ3fEMzR"

#: Where a credential carries its edges, and the two fields an edge node carries
#: that this seam reads: the far node's identifier and the operator that
#: constrains the relation. ACDC's own field names, so a credential utina writes
#: is one the existing toolchain reads.
EDGES_FIELD = "e"
EDGE_NODE_FIELD = "n"
EDGE_OPERATOR_FIELD = "o"

#: Where a credential names the governance framework it is issued under. ACDC's
#: own field, carried in its compact form — the ruleset's identifier alone.
RULES_FIELD = "r"

#: The edge operator a seat's endorsement carries. custos-4.2.md:1425-1428
#: requires it by name: "a warranty's edge to its warrantor's seat credential
#: SHALL carry the ACDC edge operator DI2I — the citing credential's issuer must
#: be the pointed-to credential's issuee or a delegated AID thereof". A superset
#: of I2I, and the delegation arm admits any depth (WebOfTrust/keripy#1564).
DI2I = "DI2I"

#: The two states a registry-bound credential can be in, in utina's words rather
#: than KERI's ilks, because this protocol is above the seam. A credential the
#: registry never issued is in neither, and reads ``None``.
ISSUED = "issued"
REVOKED = "revoked"

#: The timestamp every credential's attributes block carries. A fixed fixture,
#: the same posture as the pinned salt (this.i @7jrbt3): keripy injects a
#: wall-clock ``dt`` when the caller supplies none, which would give the same
#: endorsement a different identifier on every run and break replay outright.
ACDC_DT = "2026-01-01T00:00:00.000000+00:00"

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

    def delegate(self, delegator: AID, alias: str) -> AID:
        """Bring an identifier into being whose authority is ``delegator``'s.

        Custos asks for a seated organ to *be* a delegated identifier of the
        governed domain, so that delegation "dual-anchors the seat's key events
        (the organ signs; the delegator seals)" and the charter's delegation
        strata carry KERI's delegation semantics rather than a metaphor
        (``custos-4.2.md:2139-2148``).

        KERI's delegation is cooperative and has two halves — the delegate's
        inception names its delegator, and the delegator seals that inception
        into its own key log — and this verb performs both, because neither
        alone is a delegation: an unanchored delegated inception is a claim, and
        a seal with no inception anchors nothing. One call, both halves, so a
        caller cannot leave the unapproved half in a record (this.i @2a25xudi).

        Returns the delegated identifier, which is the delegate's own — it
        signs for itself, and only its *authority* is another's.
        :meth:`delegator_of` answers for the first half and
        :meth:`anchoring_event`, given the returned identifier, for the second.
        """
        ...

    def delegator_of(self, aid: AID) -> AID | None:
        """The identifier that delegated ``aid``, or ``None`` where none did.

        Total, like :meth:`verify` and :meth:`anchoring_event`: an identifier
        this substrate has never seen, and one that incepted itself, are the
        same fail-closed answer — nothing committed shows anybody delegating
        it, so no delegated authority may be read off it.
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
        """The key event that sealed ``said``, if one did.

        An establishment event for an amendment's anchor, an interaction event
        for a credential's or a delegation's — the distinction belongs to what
        was being anchored and not to this question, which asks only where in a
        key log the seal is. Key events stay out of the corpus the fold folds
        (this.i @jdie6v), so a binding an anchored artifact claims is answerable
        here or nowhere.
        """
        ...

    def open_registry(self, controller: AID, alias: str) -> SAID:
        """Bring a credential registry into being under ``controller``.

        Returns the registry's identifier. Custos requires a
        standing-conferring credential to be revocable through its registry
        (``custos-4.2.md:1420-1422``), which is why the seat credential is
        registry-bound where an endorsement is not: two credential kinds with
        different obligations (this.i @7db5c4, @exy3u4t7).

        The registry's own inception is sealed into the controller's key log, so
        :meth:`anchoring_event` answers for it given the registry identifier.
        """
        ...

    def revoke_acdc(self, registry: SAID, said: SAID) -> SAID:
        """Revoke ``said`` in ``registry``, and return the revocation's identifier.

        Refused where the registry holds no standing issuance of that
        credential: a revocation of nothing would put a state change in a
        registry whose issuance is not there, and registry state is evidence a
        fold consumes rather than a note anybody may write.
        """
        ...

    def registry_state(self, registry: SAID, said: SAID) -> str | None:
        """Whether ``said`` stands in ``registry``: :data:`ISSUED`,
        :data:`REVOKED`, or ``None`` where that registry never issued it.

        **The fold must never call this.** It cannot — the purity fitness
        function forbids importing a substrate above the seam — and it should
        not: a fold reading registry state out of a substrate would be reading
        an ambient condition, where the rule is that registry state is "a member
        of the evidence bundle rather than an ambient condition read against it".
        So the constructor commits an issuance and a revocation as governance
        events, the fold folds those, and this question is for screens and for
        the constructor's own fail-closed checks (this.i @exy3u4t7).
        """
        ...

    def verify_edges(self, sad: Mapping[str, object]) -> bool:
        """Whether every edge ``sad`` carries validates under its own operator.

        This is the *other current*. Custos has "the warrantor holds the seat it
        claims" checked by edge validation in the existing toolchain before any
        fold runs, and an unseated warrantor's warranty failing credential
        verification (``custos-4.2.md:1423-1434``). That check belongs to the
        substrate and its answer is not a finding: no value this returns is one
        of the four, and the fold never calls it (this.i @x7crwavm).

        Total and fail-closed, like :meth:`verify`. An edge naming a far node
        this substrate cannot resolve, an operator it does not implement, and a
        relation that does not hold are all ``False``, because each of them means
        the same thing: no authority. A credential carrying no edges validates
        trivially — there is nothing to check and nothing being claimed.
        """
        ...

    def issue_acdc(
        self,
        issuer: AID,
        schema: SAID,
        attributes: Mapping[str, object],
        *,
        registry: SAID | None = None,
        edges: Mapping[str, object] | None = None,
        rules: SAID | None = None,
    ) -> tuple[Mapping[str, object], str]:
        """A credential: constructed, signed, verified, anchored.

        ``rules`` names the governance framework the credential is issued under,
        by the ruleset's identifier, and lands in the ACDC's ``r``. A GCD
        requires it — "the act of issuing or receiving a GCD credential
        constitutes binding acceptance of the rules" — and an endorsement, which
        is issued under no framework but Acme's own committed law, omits it.
        Only the compact form is offered: a SAID, never an inlined ruleset,
        because a framework every credential restates in full is one whose bytes
        say five times what its identifier says once.

        ``registry`` is the difference between the two kinds. Given one, the
        credential names it in committed bytes and its issuance is a registry
        event, so it can later be revoked; omitted, the credential is
        registry-less, which is what the dossier's Endorsed predicate asks for
        and all an endorsement needs. One code path builds both, so they cannot
        drift in how they are digested, signed or anchored (this.i @exy3u4t7).

        Returns the credential as a plain mapping — ``{v, d, i, s, a}``, the
        dossier schema's required shape — together with the issuer's signature
        over the credential's own canonical bytes, opaque above this seam in
        the same establishment-coordinate format ``sign`` uses. The attributes
        block gains a fixed ``dt`` (:data:`ACDC_DT`) so the same endorsement is
        the same bytes on every run, and the credential's identifier is sealed
        into the issuer's key log by an interaction event — the log advances,
        the keys do not — so :meth:`anchoring_event` answers for it. A
        credential whose signature does not verify is refused rather than
        returned (this.i @7db5c4, @vi4t4i).
        """
        ...


class OpenSubstrate(Substrate, Protocol):
    """A substrate that also has a lifecycle, which is every concrete one.

    ``Substrate`` is the governance answers and nothing else: that is what
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
