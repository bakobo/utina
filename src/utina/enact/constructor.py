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

from collections.abc import Mapping, Sequence

from utina.substrate import (
    AID,
    DI2I,
    EDGE_NODE_FIELD,
    EDGE_OPERATOR_FIELD,
    ENDORSEMENT_SCHEMA,
    GCD_RULES,
    GCD_SCHEMA,
    SAID,
    Event,
    FoldValues,
    Substrate,
)

from .errors import (
    CITATION_UNKNOWN,
    DOMAIN_INCEPTED,
    DOMAIN_UNINCEPTED,
    EDGE_UNVALIDATED,
    RECORD_UNRESUMABLE,
    REGISTRY_UNOPENED,
    SIGNATURE_UNVERIFIABLE,
    SUBJECT_UNKNOWN,
)

#: The registry operation an endorsement commits. ``docs/interfaces.md`` makes
#: every endorsement an MxN group counts carry ``act`` of ``"issue"``, and the
#: fold's slot predicate reads exactly that field: an endorsement without it is
#: not refused, it is silently PENDING, so the field is the seam and not a
#: decoration. This domain commits no revocation operator — a party who changes
#: their mind declines, which is another issuance — and the credentials this
#: constructor issues carry no registry, so they are structurally unrevokable;
#: whether revocation ever enters the vocabulary is deliberately open (~56js).
ISSUANCE = "issue"

#: The event kind a registry-bound issuance commits, and the field a credential
#: names its schema in. Both are read back when an endorser cites a credential as
#: their qualification, so the citation resolves out of the record.
ISSUANCE_KIND = "issuance"
SCHEMA_FIELD = "s"

#: The name of the edge an endorser's qualification rides on. The dossier
#: specification's own label for a qualification-proof edge
#: (``dossier-spec-body.md``'s endorsement schema, ``e.qp``), which is exactly
#: what a seat credential is: proof the endorser may act on this subject.
QUALIFICATION_EDGE = "qp"


class Constructor:
    """The writing plane for one governed domain."""

    def __init__(self, substrate: Substrate, gaid: AID, *, values: FoldValues) -> None:
        """Take a gAID that already exists, because under keripy it must.

        A keripy prefix is a digest of its own inception event and is unknowable
        before ``incept`` returns it, so the composition root incepts every party
        and hands this a real identifier (this.i @crrtzf). A ``Constructor``
        built over an unincepted gAID is not refused here — it fails at the first
        verb, where signing as an identifier the substrate holds no key state for
        is refused by the substrate itself.
        """
        self.substrate = substrate
        self.gaid = gaid
        self._values = values
        self._emitted: list[Event] = []
        self._saids: set[SAID] = set()
        self._founded = False
        self._registries: dict[AID, SAID] = {}

    @property
    def emitted(self) -> tuple[Event, ...]:
        """Every event this constructor committed, in the order it committed them."""
        return tuple(self._emitted)

    @classmethod
    def resume(
        cls,
        substrate: Substrate,
        gaid: AID,
        *,
        values: FoldValues,
        events: Sequence[Event],
    ) -> Constructor:
        """Continue a committed record this constructor did not write (this.i @jzozfn).

        A classmethod rather than a mutator, so a constructor that has already
        emitted cannot be resumed at all. Founding is derived from the events —
        an inception among them — never asserted by the caller, and the positions
        must run contiguously from zero, because :meth:`_emit` takes its next
        coordinate from the record's length. Signatures are not re-verified here:
        judging evidence is the fold's job, and these events are the caller's own
        committed log.
        """
        for expected, event in enumerate(events):
            if event.position.seq != expected:
                raise RECORD_UNRESUMABLE(expected=expected, found=event.position.seq)
        constructor = cls(substrate, gaid, values=values)
        constructor._emitted = list(events)
        constructor._saids = {event.said for event in events}
        constructor._founded = any(event.kind == "inception" for event in events)
        return constructor

    # -- the verbs ------------------------------------------------------------

    def incept_domain(self, founding_law: Mapping[str, object]) -> Event:
        """Bring the domain into being under a founding law."""
        if self._founded:
            raise DOMAIN_INCEPTED(gaid=self.gaid)
        event = self._emit(
            "inception", {"t": "icp", "i": self.gaid, "law": founding_law}, self.gaid
        )
        self._founded = True
        return event

    def enact_amendment(
        self,
        law: Mapping[str, object],
        *,
        act: str | None = None,
        disturbs: Sequence[SAID] = (),
    ) -> Event:
        """Commit a successor law, anchored in an establishment event.

        custos-4.2.md:2085-2087 designates an enactment amending law as a class
        that SHALL anchor in an establishment event, so the enactment is
        committed and then a rotation seals it. The rotation is the substrate's
        and never enters the corpus (this.i @jdie6v); the binding it creates is
        answerable through :meth:`anchoring_event`.

        ``act`` names the class of act this amendment performs, so that the fold
        can find the clause that governs amending the law and judge the amendment
        under the law it replaces. The domain supplies the name — "amending the
        operating agreement" is Acme's phrase, and a constructor that invented one
        would be legislating a class no clause governs. A domain that designates
        none commits none, and the fold then refuses to appraise the enactment,
        which is the honest answer rather than a guessed one.

        ``disturbs`` is the amender's declaration of which pending questions this
        change disturbs (issue #82, determination 5). It is always committed,
        including when it is empty, because an omitted declaration is read as
        claiming that nothing is disturbed — the fail-closed reading, and the
        only one under which the mechanism works at all: if silence were no
        claim, an amender could evade conviction by saying nothing, which is
        precisely what the declaration exists to make impossible.
        """
        self._require_founded()
        body: dict[str, object] = {
            "t": "enact",
            "i": self.gaid,
            "law": law,
            "disturbs": tuple(disturbs),
        }
        if act is not None:
            body["act"] = act
        event = self._emit("enactment", body, self.gaid)
        self.substrate.rotate(self.gaid, event.said)
        return event

    def open_registry(self, alias: str, *, controller: AID | None = None) -> SAID:
        """Open a credential registry for ``controller``, and hold its identifier.

        No corpus event. A registry's own inception confers nothing on anybody:
        what bears on a standing judgment is the issuance and the revocation,
        and those are committed as governance events below. The registry itself
        is substrate machinery, like a rotation, and stays out of the log the
        fold folds (this.i @jdie6v, @exy3u4t7).

        ``controller`` defaults to the domain. It exists because **a transaction
        event log accepts issuances only from the identifier that controls it** —
        the authorizing seal lands in the controller's key log, and a registry
        whose controller never sealed the issuance leaves the credential in
        escrow rather than issued. So a party conferring authority of its own
        needs a registry of its own, and that is the right shape rather than a
        workaround: revocation authority follows the registry's controller, so a
        seat's grant kept in the *domain's* registry would be a grant the seat
        itself could never take back (this.i @cglayqvw).
        """
        self._require_founded()
        holder = self.gaid if controller is None else controller
        registry = self.substrate.open_registry(holder, alias)
        self._registries[holder] = registry
        return registry

    @property
    def registry(self) -> SAID | None:
        """The domain's registry, or ``None`` before one is opened."""
        return self._registries.get(self.gaid)

    def confer(
        self,
        delegate: AID,
        *,
        role: str,
        acts: Sequence[str],
        issuer: AID | None = None,
        presents_as: AID | None = None,
    ) -> Event:
        """Confer authority on ``delegate``, as a GCD under the domain's registry.

        **This verb is where authority comes from, and the KERI delegation
        underneath it is not.** A delegator and a delegate standing in a
        relationship whose ilk is delegation proves a relationship exists and
        confers nothing — the same fact holds of an identifier delegated to greet
        visitors and one delegated to sign treaties (``this.i`` @cglayqvw). What
        a delegate may do is this credential's business, and because it is a
        credential it is revocable, where the relationship is permanent.

        It is the seat credential of ``custos-4.2.md:1420-1425`` — "a seat
        credential names the organ's AID as issuee, issued under the domain's
        registry", typed by a schema identifier and revocable through that
        registry — and it is also the grant a seat makes to a device it acts
        through. One verb, because they are one kind of statement.

        ``acts`` is the only constraint dimension committed, and that is a
        completeness claim rather than an omission: GCD's rule 1 makes an
        unrecognized key inside ``constraints`` fail-closed, so a dimension the
        fold cannot evaluate must not be written for it to ignore. ``role`` and
        ``presents_as`` land in the descriptive facet, which the published rules
        say a verifier MAY ignore for the authorization decision — the facet
        tells a reader what the relationship is, and ``constraints`` alone gates
        (bakobo/schema#3).

        ``issuer`` defaults to the domain, because seating an organ of a domain
        is that domain's own act and no stranger's attestation does it. A seat
        conferring on its own device passes itself, because that grant is the
        seat's to make and the seat's to revoke.
        """
        self._require_founded()
        conferring = self.gaid if issuer is None else issuer
        registry = self._registries.get(conferring)
        if registry is None:
            raise REGISTRY_UNOPENED(gaid=conferring, organ=delegate)
        facet: dict[str, object] = {
            "role": role,
            "relationType": "delegation",
            "exerciseMode": "act",
        }
        if presents_as is not None:
            facet["presentsAs"] = presents_as
        sad, signature = self.substrate.issue_acdc(
            conferring,
            GCD_SCHEMA,
            {"i": delegate, "facet": facet, "constraints": {"acts": list(acts)}},
            registry=registry,
            rules=GCD_RULES,
        )
        return self._emit(
            "issuance",
            {
                "t": "iss",
                "i": conferring,
                "ri": registry,
                "acdc": sad,
                "acdc_sig": signature,
            },
            conferring,
        )

    def revoke(self, credential: SAID, *, controller: AID | None = None) -> Event:
        """Revoke ``credential`` in the domain's registry, and commit that it moved.

        Two things happen and the order matters. The registry's transaction log
        takes a ``rev`` — the substrate's business, and what a KERI tool reads —
        and then the record takes a governance event saying which credential
        stopped standing in which registry. The second is what the fold folds:
        registry state is "a member of the evidence bundle rather than an ambient
        condition read against it", so it has to be *in* the record and not
        merely true of a log beside it (this.i @exy3u4t7).

        The registry's controller signs, because revocation is an act of whoever
        conferred the standing and a transaction log takes its authorization from
        the identifier that controls it. The credential itself does not
        change and is not re-embedded: it has not moved, and a second copy of it
        would be a second set of bytes claiming to be the same artifact. What
        changes is what the registry says about it from this coordinate forward.
        """
        self._require_founded()
        holder = self.gaid if controller is None else controller
        registry = self._registries.get(holder)
        if registry is None:
            raise REGISTRY_UNOPENED(gaid=holder, organ=credential)
        revocation = self.substrate.revoke_acdc(registry, credential)
        return self._emit(
            "revocation",
            {
                "t": "rev",
                "i": holder,
                "ri": registry,
                "said": credential,
                "tel": revocation,
            },
            holder,
        )

    def propose(self, act: str) -> Event:
        """Commit an act for appraisal."""
        self._require_founded()
        return self._emit("act", {"t": "act", "i": self.gaid, "act": act}, self.gaid)

    def endorse(self, aid: AID, subject: SAID, *, qualification: SAID | None = None) -> Event:
        """Commit ``aid``'s signed yes to ``subject``.

        ``qualification`` is a credential this endorser cites as what entitles
        them to act — for the demo, a seat credential. It is the *endorser's*
        claim and is never inferred here: an endorser who holds no seat can
        still cite one, which is the whole of beat 14, and a constructor that
        looked the right credential up would have made that claim unmakeable and
        the check unshowable. Citing one attaches the DI2I edge and submits it to
        edge validation before anything is committed (this.i @x7crwavm).
        """
        return self._dispose(aid, subject, "endorse", qualification)

    def decline(
        self, aid: AID, subject: SAID, *, qualification: SAID | None = None
    ) -> Event:
        """Commit ``aid``'s signed no to ``subject``.

        A declination is a signed, attributable, committed act. Its weight
        contributes nothing to unity and its slot is spent, but that is the
        fold's reading of these bytes, not something decided here. A declination
        offered as a seat's cites the seat credential exactly as an endorsement
        does, and is refused on the same terms: a "no" from an unseated party is
        no more attributable than their "yes".
        """
        return self._dispose(aid, subject, "decline", qualification)

    def anchoring_event(self, said: SAID) -> SAID | None:
        """The identifier of the establishment event that sealed ``said``.

        Asked of the substrate rather than remembered here, because the seal is
        the substrate's own record and a second copy of it in this object would
        be a cache that can disagree with the key log it claims to describe.
        """
        return self.substrate.anchoring_event(said)

    # -- internals ------------------------------------------------------------

    def _require_founded(self) -> None:
        if not self._founded:
            raise DOMAIN_UNINCEPTED(gaid=self.gaid)

    def _qualifying_edge(self, aid: AID, qualification: SAID) -> dict[str, object]:
        """The DI2I edge citing ``qualification`` as what qualifies ``aid``.

        The far node's schema comes out of the committed issuance that carries
        it, rather than from a caller or a constant: the edge's ``s`` is a claim
        about the credential it points at, and the only honest source for that
        is the credential. A citation this record does not carry is refused —
        a qualification a stranger cannot resolve from the record is not one.
        """
        cited = self._credential(qualification)
        if cited is None:
            raise CITATION_UNKNOWN(aid=aid, qualification=qualification)
        return {
            QUALIFICATION_EDGE: {
                EDGE_NODE_FIELD: qualification,
                SCHEMA_FIELD: cited.get(SCHEMA_FIELD),
                EDGE_OPERATOR_FIELD: DI2I,
            }
        }

    def _credential(self, said: SAID) -> Mapping[str, object] | None:
        """The credential a committed issuance embeds under ``said``, if any.

        Read out of the record rather than remembered in a field, so a
        constructor that resumed somebody else's record can cite what that
        record carries (this.i @jzozfn).
        """
        for event in self._emitted:
            if event.kind != ISSUANCE_KIND:
                continue
            acdc = event.body.get("acdc")
            if isinstance(acdc, Mapping) and acdc.get("d") == said:
                return acdc
        return None

    def _dispose(
        self, aid: AID, subject: SAID, disposition: str, qualification: SAID | None = None
    ) -> Event:
        """Issue the credential, then commit the event that embeds it.

        The credential is a real, registry-less ACDC — the substrate constructs,
        signs, verifies and anchors it (this.i @7db5c4) — and the event around it
        is the corpus's own sealing discipline, unchanged (this.i @vi4t4i). The
        substrate signature travels in ``acdc_sig`` for a stranger to verify with
        KERI tooling alone; the fold never reads it.
        """
        self._require_founded()
        if subject not in self._saids:
            raise SUBJECT_UNKNOWN(aid=aid, subject=subject)
        edges = None if qualification is None else self._qualifying_edge(aid, qualification)
        sad, signature = self.substrate.issue_acdc(
            aid,
            ENDORSEMENT_SCHEMA,
            {"said": subject, "act": ISSUANCE, "disp": disposition},
            edges=edges,
        )
        if edges is not None and not self.substrate.verify_edges(sad):
            raise EDGE_UNVALIDATED(aid=aid, qualification=str(qualification))
        return self._emit(
            "endorsement",
            {"t": "end", "i": aid, "acdc": sad, "acdc_sig": signature},
            aid,
        )

    def _emit(self, kind: str, body: Mapping[str, object], signer: AID) -> Event:
        """Seal, sign, check, and only then commit.

        The order is the point. The coordinate goes into the bytes before the
        identifier is computed, so the fold's canonical order is derivable from
        committed bytes alone (Q24). The identifier goes in before the signature,
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
