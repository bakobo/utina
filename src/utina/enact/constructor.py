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
from fractions import Fraction

from utina.substrate import (
    AID,
    CERTIFICATION_SCHEMA,
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
    CERTIFICATION_UNSUPPORTED,
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

#: Where a founding law names the log it designates as its GEL, and the reserved
#: sentinel a GEL identifier names its controller through. The fold reads the
#: first under the same literal (``fold/gel.py``); neither plane imports the other.
#: The sentinel's value is ours: ``custos-4.2.md:1076-1078`` reserves "a sentinel
#: resolved at verification" without giving one, and ``#`` is outside the qb64
#: alphabet, so no identifier can ever be mistaken for it (this.i @ryh5orta).
GEL_FIELD = "gel"
GEL_SENTINEL = "#gAID"

#: The nonce a domain's GEL identifier is derived with, unless a domain supplies
#: its own. Two domains sharing it and a founding text are still distinguished by
#: their inceptions (``custos-4.2.md:1083-1084``), and a GEL's seals are only ever
#: read out of its own gAID's key log.
GEL_NONCE = "utina-gel"

#: The name of the edge an endorser's qualification rides on. The dossier
#: specification's own label for a qualification-proof edge
#: (``dossier-spec-body.md``'s endorsement schema, ``e.qp``), which is exactly
#: what a seat credential is: proof the endorser may act on this subject.
QUALIFICATION_EDGE = "qp"


def gel_identifier(substrate: Substrate, nonce: str = GEL_NONCE) -> SAID:
    """The identifier of a GEL whose controller is not yet known.

    The digest of a registry inception naming its controller only through the
    sentinel, so it can be computed before the gAID exists and committed in the
    founding law the gAID's inception seals — which is how 3151's designation and
    1085's exclusion coexist (this.i @ryh5orta).
    """
    return substrate.said({"t": "gel", "ii": GEL_SENTINEL, "u": nonce})


class Constructor:
    """The writing plane for one governed domain."""

    def __init__(
        self,
        substrate: Substrate,
        gaid: AID,
        *,
        values: FoldValues,
        gel: SAID | None = None,
    ) -> None:
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
        self.gel = gel_identifier(substrate) if gel is None else gel
        """The identifier of the log this domain's founding law designates as its GEL."""
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
        constructor = cls(substrate, gaid, values=values, gel=cls._designated(events))
        constructor._emitted = list(events)
        constructor._saids = {event.said for event in events}
        constructor._founded = any(event.kind == "inception" for event in events)
        return constructor

    @staticmethod
    def _designated(events: Sequence[Event]) -> SAID | None:
        """The GEL a resumed record's founding law designates, if it has one."""
        for event in events:
            law = event.body.get("law") if event.kind == "inception" else None
            if isinstance(law, Mapping) and isinstance(law.get(GEL_FIELD), str):
                return str(law[GEL_FIELD])
        return None

    @property
    def key_events(self) -> tuple[Mapping[str, object], ...]:
        """The gAID's key log, which says where every GEL event was committed.

        Asked of the substrate rather than kept here, for the reason
        :meth:`anchoring_event` gives. This is what the fold derives the GEL's
        order and membership from (``fold/gel.py``, this.i @wsxwkwgv).
        """
        return self.substrate.key_events(self.gaid)

    # -- the verbs ------------------------------------------------------------

    @classmethod
    def found(
        cls,
        substrate: Substrate,
        alias: str,
        founding_law: Mapping[str, object],
        *,
        values: FoldValues,
        nonce: str = GEL_NONCE,
    ) -> Constructor:
        """Bring a born-governed domain into being: the genesis knot, then its GEL.

        ``custos-4.2.md:1073-1084``: the founding law is computed first, its
        authors pre-existing the domain; the gAID's inception seals the law's
        identifier, so the law lies inside the bytes the identity digests; and
        the GEL opens with the event committing that law. The designation goes
        into the law before its identifier is taken, because 3151 wants it "at
        inception grade, sealed by the genesis knot" (this.i @4b2mmhbf).

        The gAID is incepted here and not by the composition root, because only
        this verb knows the founding law's identifier.
        """
        gel = gel_identifier(substrate, nonce)
        law = cls._designating(substrate, founding_law, gel)
        gaid = substrate.incept(alias, seals=(str(law["d"]),))
        constructor = cls(substrate, gaid, values=values, gel=gel)
        constructor._emit_founding(law)
        return constructor

    def incept_domain(self, founding_law: Mapping[str, object]) -> Event:
        """Bring an adopted domain into being: a gAID incepted bare, its law later.

        Lawful at the lesser grade ``custos-4.2.md:1088-1092`` confesses — the
        identity ranges over keys alone — and :meth:`found` is the construction
        that is not. Both designate the GEL in the founding law.
        """
        if self._founded:
            raise DOMAIN_INCEPTED(gaid=self.gaid)
        return self._emit_founding(self._designating(self.substrate, founding_law, self.gel))

    @staticmethod
    def _designating(
        substrate: Substrate, founding_law: Mapping[str, object], gel: SAID
    ) -> dict[str, object]:
        """``founding_law`` naming the GEL it designates, and carrying its own identifier."""
        law = {**founding_law, GEL_FIELD: gel}
        return {**law, "d": substrate.said(law)}

    def _emit_founding(self, law: Mapping[str, object]) -> Event:
        event = self._emit("inception", {"t": "icp", "i": self.gaid, "law": law}, self.gaid)
        self._founded = True
        return event

    def enact_amendment(
        self, law: Mapping[str, object], *, act: str | None = None
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

        **An amendment declares nothing about what it ends** (this.i @ow6dzro4).
        It used to commit a ``disturbs`` field naming the pending questions its
        change would kill, and the fold convicted it where that list differed
        from the one it computed. The field gated nothing — the law changed the
        same way whether it was right, wrong or absent — so it existed only to
        create something that could be false. The fold still computes what an
        amendment ended, and the ``disturbance`` screen still prints it; nobody
        is charged with getting it wrong.
        """
        self._require_founded()
        body: dict[str, object] = {"t": "enact", "i": self.gaid, "law": law}
        if act is not None:
            body["act"] = act
        return self._emit("enactment", body, self.gaid, establishment=True)

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
        nonce: str | None = None,
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

        ``nonce`` is needed only when the same party is conferred the same
        authority twice — re-seating an office after its credential was revoked.
        Without it the two grants are byte-identical and therefore one
        credential, which a transaction log correctly refuses to issue again.
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
            nonce=nonce,
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

    def observe_duplicity(self, party: AID, pair: Sequence[SAID]) -> Event:
        """Commit that ``party`` was observed signing two contradictory things.

        **This records an observation; it does not convict.** A conviction is
        conviction-grade at the governance tier "only within frames that
        committed the violated predicate — no committed predicate, no conviction,
        and the pair is ordinary evidence to consume" (``custos-4.2.md:1680-1683``),
        and Acme's law commits no predicate about signing duplicity. So the only
        tier that can convict here is the key tier, under KERI's
        superseding-recovery calculus, which no plane above the substrate may run
        (``this.i`` @yrkrqj). The domain commits what it observed, and the fold
        consumes that as evidence — the same posture it already takes toward a
        signature it cannot re-check (``this.i`` @f3pmxu3x).

        The domain signs, because observing is an act and an act is somebody's.
        The pair is committed in canonical order rather than as observed, for the
        reason the disturbance proof package is: a set is a set, and a record that
        moved with the order of observation would make one duplicity two facts.

        What this deliberately does NOT do is touch a registry. A revocation and
        an undercut are different mechanisms and issue #82's determination 4 asks
        that they be unmistakable in the bearing machinery; sharing a verb would
        make the separation a matter of layout.
        """
        self._require_founded()
        return self._emit(
            "duplicity",
            {"t": "dup", "i": self.gaid, "party": party, "pair": tuple(sorted(pair))},
            self.gaid,
        )

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

    def certify(
        self,
        subject: SAID,
        *,
        sponsor: AID,
        counted: Sequence[tuple[SAID, Fraction]],
    ) -> Event:
        """Admit a sponsor's tally, which is what makes ``subject`` consequential.

        **Two acts and one committed event, and the asymmetry is the point.** The
        sponsor assembles a dossier ACDC citing each disposition they counted and
        signs it with their own key; the domain verifies it and admits it to the GEL
        with an event of its own. Only the second is a GEL event, because only the
        gAID's controller can anchor into the gAID's KEL — nothing a sponsor does can
        put anything in a domain's log, which is why admission is necessarily the
        domain's act (``this.i`` @ftjpdph5's sibling, @2e2dncfe). So the sponsor's
        dossier travels INSIDE the domain's event, carrying its own signature, the
        way an endorsement's credential already does (@vi4t4i).

        **The domain checks before it admits**, and what it checks here is the floor:
        that the weights the dossier cites sum to unity. A certification is not an
        assertion that a threshold was met, it is the proof — a verifier walks the
        edges and recomputes — so one claiming more than its edges support would
        contradict itself on bytes its own sponsor signed, and the domain declines to
        put that in its log.

        ``counted`` is supplied by the caller rather than computed here, and that is
        the plane boundary rather than laziness: which dispositions a clause counts
        and what each is worth is the fold's question, and this module may not ask it
        (``tests/test_purity.py``).
        """
        self._require_founded()
        if subject not in self._saids:
            raise SUBJECT_UNKNOWN(aid=sponsor, subject=subject)
        reached = sum((weight for _, weight in counted), Fraction(0))
        if reached < 1:
            raise CERTIFICATION_UNSUPPORTED(
                sponsor=sponsor,
                subject=subject,
                reached=f"{reached.numerator}/{reached.denominator}",
            )
        sad, signature = self.substrate.issue_acdc(
            sponsor,
            CERTIFICATION_SCHEMA,
            {"said": subject, "act": ISSUANCE},
            edges=self._tally_edges(counted),
        )
        return self._emit(
            "certification",
            {
                "t": "cert",
                "i": self.gaid,
                "certifies": subject,
                "acdc": sad,
                "acdc_sig": signature,
            },
            self.gaid,
        )

    @staticmethod
    def _tally_edges(counted: Sequence[tuple[SAID, Fraction]]) -> dict[str, object]:
        """One edge per counted disposition, weighted, under the threshold operator.

        The shape is the dossier specification's joint issuance: an edge group whose
        ``o`` field carries the operator and whose member edges are the slots, each
        with its weight in ``w`` (``dossier-spec-body.md:351``). Weights commit as
        exact rational strings, which is the form the committed law already uses.
        """
        members: dict[str, object] = {EDGE_OPERATOR_FIELD: "MxN"}
        for index, (said, weight) in enumerate(counted):
            members[f"e{index}"] = {
                EDGE_NODE_FIELD: said,
                SCHEMA_FIELD: ENDORSEMENT_SCHEMA,
                "w": f"{weight.numerator}/{weight.denominator}",
            }
        return {"endorsements": members}

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

    def _emit(
        self,
        kind: str,
        body: Mapping[str, object],
        signer: AID,
        *,
        establishment: bool = False,
    ) -> Event:
        """Seal, sign, check, commit, and anchor.

        The order is the point. The GEL sequence number goes into the bytes
        before the identifier is computed, as a TEL event's does. The identifier
        goes in before the signature, so the signature commits to it. The
        signature is verified before the event is recorded, because an event
        whose own signature does not stand up confers no authority and must not
        reach the record. And then the gAID seals it into its key log with an
        event seal naming the GEL, its sequence number and its identifier — in a
        rotation for an enactment (2085-2087), an interaction otherwise — which
        is where the fold reads its order and membership from (this.i @wsxwkwgv).
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
        self.substrate.seal(
            self.gaid,
            ({"i": self.gel, "s": format(seq, "x"), "d": said},),
            establishment=establishment,
        )
        # Recorded only once the key log has it: an event nothing sealed is not a
        # GEL event, and the fold would refuse a record that carried one.
        self._emitted.append(event)
        self._saids.add(said)
        return event
