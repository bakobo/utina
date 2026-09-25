# utina — Intent Tree (this.i)
#
# Source of truth for utina's design intentions and the decisions that follow from them,
# per the Bakobo intent-first methodology (../dev/methodology.md). Code and docs/ are DERIVED
# artifacts. Record each consequential decision here, in its own commit, BEFORE the code
# commit it justifies.
#
# Node ids are opaque base32 [a-z2-7], stable across renames. NEVER parse them, never make
# them semantic.

Make Custos's replayable governance useful to a real organization = goal:
  id: rk4mzq
  why: >
    Custos specifies governed domains whose law is committed and whose judgment is computed,
    and promises that any stranger holding the logs recomputes the same Constitution. Nothing
    has ever shown an organization actually governed that way. utina exists to close that gap:
    a company's operating agreement expressed as committed law, and its decisions answered —
    confirmed, denied, or not-yet — with a ground a stranger can check. Chose "useful engine"
    over the falsification posture of its sibling thesmo (bakobo/thesmo), which deliberately
    optimizes for a defect register and accepts being slow to production. That posture is
    right for thesmo and wrong here: an engine that will not resolve an ambiguity cannot be
    demonstrated. Tradeoff accepted: utina's readings are NOT independent evidence about the
    specification, and it must never be cited as a second implementation confirming thesmo.
  children:
    Express Acme's thresholds domain-natively, in the dossier's shape = decision:
      id: ta7vle
      why: >
        Custos section 9 carries exactly one BCP-14 keyword: the composition rule MUST be
        committed, and MAY be expressed in the ACDC edge grammar as the dossier specification
        profiles it. Expressing it as real ACDC edge groups makes the dossier specification an
        external semantics, which axiom 4 then requires be pinned by committed digest with
        anything unpinned refused. Chose a domain-native committed clause predicate whose
        STRUCTURE is isomorphic to the dossier's threshold operators — same operator/slot/weight
        shape, same unity threshold, same three dispositions, same disp and act field names —
        over both a bespoke shape and real ACDC edges. Rejected a bespoke shape because the
        long-term destination is genuine ACDC edge groups and a different shape would make that
        a rewrite. Rejected real ACDC edges now because the semantics pin and the refusal
        machinery it obliges are not needed to show the value and would not fit the schedule.
        Tradeoff accepted: utina is NOT dossier-conformant today, and must not claim to be.
    The fold computes the slot predicate itself; the substrate cannot = constraint:
      id: mw6dxh
      why: >
        Custos withdrew the claim that KERI's threshold algebra transfers to the evidence tier:
        the two constructions are analogous, never one algebra, because the predicate deciding
        what enters the sum is a fold question and not the substrate's. keripy's Tholder is a
        key-state threshold over verified signature indices and cannot answer whether a slot is
        Endorsed — that needs the referenced endorsement's issuer, disposition, subject SAID and
        revocation status. Driving constraint: wiring a substrate threshold evaluator to an edge
        group discharges the arithmetic and none of the slot dispositions. So threshold
        arithmetic and the slot predicate are separate modules, and the arithmetic is the
        trivial one.
      children:
        Weights are exact rationals; a float weight is refused, never converted = decision:
          id: qpqo3z
          why: >
            Unity has to be exactly decidable, and B2 puts three slots at 1/3 on the demo's
            critical path: in binary floating point 1/3 + 1/3 + 1/3 is not 1, so the retained
            amendment bar would be satisfied or not according to rounding. Chose
            fractions.Fraction throughout, and refused a float at construction rather than
            converting it. Rejected accepting a float and coercing it, because the coercion is
            where the lie enters — Fraction(0.1) is not 1/10, and a law that reads 1/10 in its
            committed bytes would compute as 3602879701896397/36028797018963968 with nobody the
            wiser. Refusing makes the wrong type a loud error at the law's boundary.

        A slot weight is strictly positive = decision:
          id: anoz6j
          why: >
            The dossier specification bounds only the SUM ("at least unity", dossier-spec-body.md:353)
            and says nothing about an individual weight. Chose to refuse w <= 0 at construction.
            A negative weight makes an endorsement subtract, so an endorser could defeat a
            decision by endorsing it — an anti-endorsement, which is a security property nobody
            wrote down and nobody wants. A zero weight puts an endorser in the requirement space
            who can never discharge anything, so the finding names a cure that does not cure.
            Rejected permitting both and letting the arithmetic speak, because arithmetic that
            happens to work is not a rule anyone can rely on. Logged as Q21 in custos-questions.md.

        A group is non-empty and slots one endorser at most once = decision:
          id: mfkox5
          why: >
            MxN contains "exactly N slots, one per candidate endorser"
            (dossier-spec-body.md:371), so two slots naming one endorser is outside the shape we
            claim isomorphism with, and it makes the disposition map ambiguous — one AID, two
            weights, no rule for which. An empty group is refused because it can never reach
            unity and would discharge as a pending finding whose requirement set is empty, which
            the codomain forbids (interfaces.md: requirement is non-empty). Rejected permitting
            an empty group as a lawful "nobody may do this", because the domain expresses that by
            not writing a clause, and the fold then refuses under axiom 3 instead of inventing a
            finding.

        An endorser the group does not slot contributes nothing, and does not raise = decision:
          id: 3smud6
          why: >
            satisfied_by and reachable ignore names that match no slot. Chose silence over a
            raise because both are read paths the CLI runs to DISPLAY a verdict, and a display
            path that throws turns a governance answer into a stack trace. The security property
            that matters is preserved and directly tested: an unslotted endorser can never add
            weight, so an endorsement from the wrong AID cannot help. Rejected raising on an
            unknown endorser, which would have caught a caller's typo at the cost of making the
            two most-called methods partial.

        Reachable weight is endorsed plus still-pending; a declined slot is spent = decision:
          id: dnsovg
          why: >
            reachable() asks whether unity is still attainable, which is the endorsed weight plus
            every weight that could still arrive. A declination is an authenticated act by the
            one party who could have filled that slot, so its weight is gone — that is what makes
            D3 defeat and D6 merely pending under the same signed refusal. Rejected treating a
            declination as recoverable (an endorser who might change their mind), because the
            dossier makes a declination an attributable act rather than a mood, and a
            reachability that assumes people will reverse themselves can never report unreachable
            at all.

        The predicate matches endorsements by issuer and subject, not by pointer = decision:
          id: 2pfkyg
          why: >
            In the dossier the slot POINTS at its endorsement through the `n` field
            (dossier-spec-body.md:358) and the expected endorser is the issuer of the ACDC the
            slot references. utina's committed evidence is a flat event log with no edge block, so
            there is no pointer to follow: the fold instead searches committed evidence for an
            endorsement whose issuer is the slot's endorser and whose subject SAID is the
            decision's. Rejected carrying a pointer in the law, because the law is written before
            the endorsements exist and would then have to be amended to be endorsed. The
            divergence this creates is logged as Q19 in custos-questions.md.

        A declination is decisive: conflicting acts resolve to declined = decision:
          id: tdsrgi
          why: >
            Where one endorser has committed both an endorsement and a declination naming the same
            subject, the slot is DECLINED whatever the committed order. Chose the reading that
            never grants authority: an endorser who has signed a refusal has spent the slot, and
            the later endorsement is at best a second act the law did not authorize them to take.
            Rejected last-committed-wins, which is the more natural "they changed their mind"
            reading and which we may be wrong to reject — it is logged as Q20, DIVERGENT, and the
            pin is fail-closed rather than confident.

        The endorsement's field names are the dossier's, as module literals = decision:
          id: pj3xhi
          why: >
            An endorsement event's body carries `i` (issuer), `disp`, `act` and `said`, matching
            the dossier's own names so that swapping the encoding for real ACDC edge groups is a
            substrate change and not a rewrite (@ta7vle). Rejected friendlier names like
            `endorser` and `subject`, which would read better in Python and would silently break
            the isomorphism claim the demo makes out loud. They are module-scope literals rather
            than inline strings, so the seam with utina.enact is one line to reconcile.

        The fold checks attribution; only the substrate checks signatures = decision:
          id: yrkrqj
          why: >
            "Signed by exactly the expected endorser" is enforced in the fold as: this event is of
            kind endorsement, it is in the committed evidence, and its issuer field is the slot's
            endorser. The cryptography is not re-run here, because axiom 2 closes the fold's inputs
            at committed values and a fold that verified signatures would need a KERI library the
            purity test forbids. Rejected carrying a signature into the event body for the fold to
            check, which would have looked more rigorous while actually being weaker — a signature
            the fold cannot verify is decoration.

        Provisional AID/SAID aliases and a structural event protocol = decision:
          id: yenp2x
          why: >
            group.py declares AID and SAID as local aliases for str, and slots.py accepts any
            object with said, kind and body via a structural Protocol rather than importing
            utina.fold.corpus.Event. Chose this because the corpus was being written by another
            agent at the same moment and an import of a module that does not exist yet cannot be
            driven red-to-green. Rejected defining an Event of our own, which the contract forbids;
            the protocol is a read-only VIEW of the contract's Event and the real one satisfies it
            unchanged. Both should collapse to the shared definitions at integration.

        Error codes sit under e.input and e.rule; there is no e.law branch = decision:
          id: cd5dnc
          why: >
            docs/interfaces.md reserves `e.law.clause-unknown.f`, which bakobo.errors refuses at
            import: `law` is not one of the ten first descriptors, and the taxonomy says adding one
            is a change to the standard rather than to a registry. A malformed committed law is
            material we were handed, so it sorts under e.input; the closest standing descriptor for
            a norm we enforce is e.rule. Rejected minting `law`, which would not have imported, and
            rejected e.state, which describes the condition of the target rather than the shape of
            what arrived. One code in the edition of docs/interfaces.md this commission read could
            not be declared as written — `e.law.clause-unknown.f` names a descriptor outside the
            closed set — and the corrected contract spells it `e.rule.clause-unknown.f`, which
            integration adopted. `e.input.malformed.f` was recorded here as illegal for want of a
            sub-descriptor; that reading was wrong, `malformed` is the sub-descriptor and the code
            imports, which is why the codomain commission declares and uses it. Ours are
            `e.input.format.slot-weight.f`, `e.input.range.slot-weight.f`,
            `e.input.missing.group-slots.f` and `e.input.multi.slot-endorser.f`; slots.py declares
            none at all, because everything it cannot verify is PENDING rather than an error.

    The ground is a constructor precondition, never a validated annotation = decision:
      id: ppnadi
      why: >
        Custos makes the ground a component of the finding's type — "a value that does not carry
        its ground is not a member of this type, whatever else it may be" (custos-4.2.md:1504-1507).
        Chose enforcement inside `__post_init__` of every value, raising `e.state.ground-missing.f`,
        over the obvious alternative of optional fields plus a `finding.validate()` a caller is
        expected to run. The alternative was rejected because it makes a groundless finding a value
        that exists for a while: it can be returned, logged, compared and serialized before anyone
        validates it, and the Ground Axiom's whole content is that such a thing is not a member of
        the type. Tradeoff accepted: construction can raise, so every call site that builds a
        finding from untrusted material must be prepared for an error rather than a sentinel.

    Refusal lives in its own module and is not a Finding = decision:
      id: zztcbs
      why: >
        "Refusal is not a fifth finding value — it is the evaluator declining to answer an
        ill-posed question, recorded as an operational fact" (custos-4.2.md:1898-1900; the same
        separation at :229-231). Chose a separate module with no inheritance relationship to
        `Finding`, plus a test that asserts the non-relationship in both directions, over the two
        alternatives: a fifth codomain member (forbidden outright) and an exception. The exception
        reading is lawful — nothing commits a refusal's form (see U3 in the requirements audit) —
        but it was rejected because an exception cannot be recorded as the operational *fact* the
        text calls it, and because the demo needs a refusal to be a value the CLI can print beside
        a finding. Tradeoff accepted: `evaluate` returns a union, so every caller must discriminate.

    A finding carries clause-level ground only; the triple travels with the caller = decision:
      id: t4snir
      why: >
        thesmo's m1-alpha reading made the appraisal triple a field of every finding, on the
        strength of "every finding retains its position, its defeated clause, its verification
        grain, and its committed law head". In 4.2 that sentence sits at :2782-2783, inside §15's
        federation SHALL about *conviction records*, and binds a federated GARD's convictions
        rather than the codomain at large. Chose the contract's payloads — clause set,
        endorsements and bundle identity for affirmed; citation for defeated; typed requirement
        set for pending; proof for self-convicted — over carrying the triple in every value.
        Rejected carrying it because it would duplicate in every finding what the caller already
        holds as the argument it passed, and because a federation-scoped SHALL is not a general
        one. Tradeoff accepted: a finding handed on alone does not name the law head it was
        computed under, so the record that transports one must carry the triple beside it.

    Evidence reaches the triple through a structural protocol, not an import = decision:
      id: e3qd53
      why: >
        `EvidenceBundle` holds committed events, and the corpus module defines `Event` with a
        `position` typed by this module's `Position` — so a direct import would be a cycle, and a
        `TYPE_CHECKING` import would still make one module's type-check depend on a module built
        by a different agent. Chose a `runtime_checkable` `CommittedEvent` protocol naming the four
        attributes the bundle actually reads, which `utina.fold.corpus.Event` satisfies
        structurally, over both the import and the untyped `tuple[object, ...]`. Rejected the
        untyped form because it moves the check to runtime with no name for what is expected.
        Tradeoff accepted: a structural check is by attribute presence, so a different class with
        those four attributes is admitted; the corpus is the only producer, so nothing else does.

    The byte-canonical encoder is length-prefixed, and it lives in triple.py = decision:
      id: asuj6q
      why: >
        The replay obligation needs one encoding whose field split cannot be forged — `2:ab1:c`
        is not `3:abc` — so that byte equality is a sound test of value equality, and
        custos-4.2.md:3101's permuted-arrival obligation is checkable at all. Chose thesmo
        m1-beta's length-prefixed `encode_fields`, placed on the closed input type where every
        other module can reach it, over canonical JSON and over CBOR. Rejected canonical JSON
        because its determinism rests on a key-ordering convention no one here commits, and CBOR
        because it drags a dependency into a package whose purity is a fitness function. Tradeoff
        accepted: these bytes are utina's own choice and are not a wire format; nothing outside
        this repo can read them, which is exactly what Custos leaves open (§17's semantic-equality
        grade, not byte identity, for findings).

    A requirement element defaults its kind and species rather than demanding them = decision:
      id: 7wysgy
      why: >
        Custos rules that "a pending finding SHALL carry the species of each of its requirement
        elements" (custos-4.2.md:1585-1586) and orders the set on four fields including species
        (:1647-1651), while the interface contract's element is two fields, endorser and clause.
        Chose to carry `kind` and `species` as fields with defaults — `"endorsement"` and
        `absent` — over both dropping them (which would break a keyword-force SHALL) and making
        them required (which would break the contract's declared constructor and every sibling
        that builds one). The defaults are the only values Acme's demo can produce: every pending
        element there is a missing endorsement cured by the arrival of the missing evidence, which
        is `absent` by :1575-1576. Tradeoff accepted: an engine growing a second cure path must
        pass the species explicitly, and nothing forces it to.

    The defeater class is a defaulted field on the citation = decision:
      id: jaabkd
      why: >
        A defeated finding SHALL carry its defeater class as well as its citation
        (custos-4.2.md:1641-1646), and the class is the first component of canonical selection
        (:1766-1779), so it cannot be dropped. The contract's `Citation` names three fields and
        none of them is the class. Chose a fourth field defaulting to `authority` — the reading
        pinned in custos-questions.md Q6 for a threshold defeated by a signed declination —
        over a required field, which would break every sibling call site the contract entitles to
        omit it, and over deriving the class from the presence of a declination, which would
        silently misclassify a cryptographic or a superseding defeat as an authority one.
        Tradeoff accepted: a caller that does not think about the class gets `authority`, and
        `authority` is wrong for three of the four defeat kinds; the field is documented at the
        point of default and the pin is logged as a divergence.

    A requirement set is one element per deduplication key, ordered by that key = decision:
      id: fdhqffc3
      why: >
        The element grew two fields past the four the order is ruled over — schema (Q17) and the
        ground that closed a cure path (@waihlx27) — and the dedup key sees all six, because
        custos-4.2.md:1652-1656 says it "sees every field the element carries". Two elements
        differing only in schema or ground therefore survive deduplication as two, and share one
        four-field sort key. Until this decision the two halves disagreed about them: the builder
        kept both and sorted by the four-field key, so their relative order was whatever order
        they arrived in, and Pending then rejected them as duplicates because its uniqueness
        check ran over the four-field key. Found by an outside review of the codomain on
        2026-09-24; unreachable today, because a clause slots each endorser once under one schema.
        Chose to order by the full dedup key and to check uniqueness over it, so the six-field
        key breaks ties the four-field order leaves open. The four-field order is a prefix of it,
        so every set whose sort keys are already distinct — every set utina produces today — is
        byte-identical before and after. Rejected refusing two elements with one sort key,
        because the text says they are different elements and a refusal would make a pending
        finding unconstructible on a record that is merely unusual. Rejected dropping schema and
        ground from the dedup key, back to four fields, because that would merge two elements that
        tell a party different things. Tradeoff accepted: the tie-break is utina's reading,
        not the text's, since :1650-1651 rules the order over exactly four fields. Logged as an
        amendment to Q17.

    Derive the canonical order from the coordinate and the identifier alone = decision:
      id: qv7m3d
      why: >
        Custos fixes the fold's consumption order at 3091-3101 as anchoring order first, then
        intra-anchor order as the anchoring event's seal list states. The second component is
        unavailable to us: a Position carries a sequence number alone, so by the time an event
        reaches the fold the seal-list index has been flattened away. Chose wall 6's default
        tiebreak — lexicographic over the self-addressing identifier (2905-2915) — over widening
        the Position type to carry a seal index. Rejected widening because Position is the
        triple's, fixed by the contract, and 1222-1227 defines a position as (identifier,
        sequence number) with no third component, so the widening would put the engine at odds
        with the position definition to satisfy the order rule. Tradeoff accepted: two events
        sealed into one rotation may be consumed in an order a seal-index engine would reverse.
        Logged as Q11 and DIVERGENT.

    Hold the canonical order at construction, and offer no other = decision:
      id: hs2c6f
      why: >
        3097-3099 says an implementation whose fold result depends on arrival, storage or any
        ambient sequence does not conform. Chose to sort in Corpus.load and expose no accessor
        that returns events as they arrived, over sorting lazily at each read. Rejected lazy
        sorting because it leaves an unordered sequence reachable inside the object, and the
        cheapest way to keep an ambient order out of a fold is to have nowhere to read one from.

    Refuse a SAID collision rather than convict it = decision:
      id: b4xk9w
      why: >
        Two committed events under one identifier collide at one canonical key, so nothing
        committed separates them. Chose to raise e.state.order-ambient.f over returning a
        duplicity self-conviction under wall 7 (2916-2922). Rejected the conviction because the
        obstacle observable at the corpus layer is the absent order, not the contradictory pair,
        and a self-conviction owes a proof package naming that pair, which the order walk has no
        standing to build. Logged as Q13 and DIVERGENT.

    Fold a re-presented event once = decision:
      id: n8pz5t
      why: >
        3087-3089 makes the self-addressing identifier the identity and the coordinate merely a
        location. Chose idempotent dedupe by SAID over treating a repeat presentation as a wall 7
        competitor. Rejected the competitor reading because it convicts a domain for the ordinary
        operational fact of receiving the same event down two paths. Matches thesmo m2-gamma's
        @jax6b7.

    Amendment replaces the edition; it does not add clauses = decision:
      id: wg3jr6
      why: >
        Custos never says whether an amendment is a delta or a restatement. Chose whole-edition
        replacement — an enactment commits the complete clause set in force after it — over
        gamma's additive reading, in which an amendment appends clauses to the law in force.
        Rejected the additive reading because Acme's A1 and B1 both govern ordinary acts, so
        under it both are in force after the amendment and governing() has two answers where the
        contract allows one. 3001-3003 is edition-shaped in exactly this way: a ratified
        document's clauses are the law for every position at and after effectuation, which
        describes replacement rather than accumulation. Tradeoff accepted: a domain cannot amend
        one clause without restating the rest. Logged as Q14 and DIVERGENT.

    Genesis is constructed, not judged; every later enactment is judged = decision:
      id: c5tqn2
      why: >
        Succession says law never applies to itself at a coordinate, only to its successor at the
        next (2270-2272), which taken alone would leave the founding law not in force at its own
        coordinate and the domain ungoverned at inception. Chose to treat the inception event's
        law as in force at and after its own coordinate, and every later enactment as in force
        strictly after its own, over a uniform strictly-before rule. Rejected the uniform rule
        because it makes the base case vacuous; 2272-2274 names genesis "constructed rather than
        judged" and that is the exemption doing the work. Logged as Q15.

    Order clause sub-blocks by clause SAID, and confess the digest = decision:
      id: j9vd4k
      why: >
        1475-1487 requires the clause-set head to be an aggregate commitment over per-clause
        sub-blocks and confesses in the same breath that the aggregate's digest function and
        concatenation order are semantics the document owes. Chose lexicographic order over the
        clause SAID, per wall 6's default, and SHA-256 over the sub-block bytes as the digest.
        Rejected Blake3/qb64, which would be the KERI-native choice, because utina.fold imports
        no KERI library and blake3 is on the forbidden list the purity test enforces. Tradeoff
        accepted: our law head is not the law head a KERI-native engine computes from the same
        clauses, which is exactly the openness 1478-1481 confesses.

    Name the unknown-clause error e.rule.clause-unknown.f = decision:
      id: f6mb8y
      why: >
        The edition of docs/interfaces.md this commission built against reserved
        e.law.clause-unknown.f, which is not a legal Bakobo error code: law is not one of the ten
        first descriptors and the validator rejects it at import time. Chose e.state as the
        repair. The contract has since been corrected to e.rule.clause-unknown.f, which is legal
        and which the contract rationalizes in the same breath — governance rules live under
        rule, and a clause id is the identity of a governance rule — so the repair is spent and
        integration adopted the contract's spelling. Rejected keeping e.state, which would have
        left two spellings of one condition alive in a repo whose codes are globally unique;
        rejected e.input, because a clause id that is not in force here is well-formed and may
        be in force at another position, so the obstacle is never the caller's bytes.

    Refuse a self-contradictory edition rather than order it = decision:
      id: d2wq7h
      why: >
        Two clauses in one edition governing one act kind, or one clause id committed twice,
        leaves governing() and clause() with two answers where the contract allows one. Chose to
        raise e.state.clause-ambiguous.f when the edition is folded, over picking the first match
        in canonical order. Rejected picking because the canonical order is ours by wall 6 default
        rather than the domain's by commitment, so first-match would let OUR tiebreak decide whose
        authority rules an act — which is precisely the uncommitted composition seam 1874-1876
        says an evaluator refuses rather than legislates.

    Mint e.input.malformed.law.f under the contract's reserved branch = decision:
      id: k3ynf8
      why: >
        Committed bytes that will not read as law need an error, and the contract reserves
        e.input.malformed.f for "committed bytes will not parse as the event they claim to be" —
        but that code belongs to the substrate agent's surface, not this one. Chose a deeper
        sub-descriptor under the same branch over sharing the reserved literal across two modules.
        Rejected sharing because two module-scope declarations of one code invite them to drift in
        title and detail; the deeper code still prefix-matches e.input.malformed for any caller who
        wants the whole branch.

    The writer plane constructs fold values through an injected factory = decision:
      id: tvaq2s
      why: >
        The contract has enact return `utina.fold.Event` and Acme produce a
        `utina.fold.Corpus`, so the obvious build is a direct import of the fold
        from the writing plane. Rejected. Custos section 1.3 separates the two
        verbs and says no object performs both; an import edge from enact to fold
        makes the constructor's plane unloadable without the judge's plane, which
        is the coupling the separation exists to forbid. Chose to parameterize
        enact and acme over a small `FoldValues` protocol — position, event,
        corpus — supplied at the composition root. The value types stay the fold's
        and are never redefined here; only their construction is injected.
        Consequences accepted, both real: the demo's composition root must do the
        wiring, and `src/utina` therefore ships no code that imports `utina.fold`,
        so a caller who forgets the wiring gets a type error rather than a default.
        Consequence gained, and it is why the decision was affordable: this
        commission's code is exercised and fully covered while the fold is still
        being built by three sibling commissions, instead of sitting untested
        behind an import that does not resolve yet.

    A facade signature names the key state it was made under = decision:
      id: h7l67i
      why: >
        Rotation advances Acme's gAID key state mid-log, and every signature made
        before it must still verify afterward or replay dies at the first
        amendment. Rejected verifying against the current key alone, which
        falsifies every earlier endorsement the moment the board is seated.
        Rejected verifying against any key in the identifier's history, which
        accepts a signature no key state ever authorized and is exactly the
        fail-open this repo forbids. Chose to carry the key index in the signature
        itself — `0B<index>.<mac>` — so verification resolves one key, the one
        claimed, and a signature is checkable against the key state it names rather
        than against whichever key happens to be live. Tradeoff accepted: the
        facade's signature is a keyed Blake2b MAC, so it is unforgeable only to a
        party who does not hold the deterministic seed, and it is not a signature
        in the public-key sense at all. That is honest for a fixture whose whole
        purpose is byte-reproducible replay with no cryptographic dependency, and
        the keripy commission replaces it without the fold noticing.

    Endorsement and declination are one code path = decision:
      id: 7szbfw
      why: >
        The demo turns on an asymmetry: an endorsement and a declination are both
        signed committed events, and an unsigned slot is not a decision by anybody.
        Rejected giving declination its own construction path, because two paths
        drift and the cheap drift is the dangerous one — a declination that is
        somehow lighter-weight than an endorsement re-introduces the silent no the
        demo exists to refute. `endorse` and `decline` are two names on one private
        emitter differing in a single committed field, `disp`. There is no API on
        the constructor by which a party can be recorded as declining without a
        signed event, and no API by which a slot can be marked absent at all.

    Rotations are substrate-side and never enter the corpus = decision:
      id: jdie6v
      why: >
        Custos :2085-2087 requires an enactment amending law to anchor in an
        establishment event, and the reading that puts the anchoring itself in the
        GEL is lawful — see Q25 in `docs/custos-questions.md`, where the two
        readings are set out and the divergence named. Chose to keep the rotation
        in the substrate: the contract's `Event.kind` enumeration has no member for
        an anchoring, the fold consumes governance events rather than key events,
        and the enactment is what a clause is predicated on. The facade records the
        enactment-SAID-to-rotation-SAID binding so the anchor is checkable, and a
        test asserts Acme's amendment is anchored, so :2087 is honored in a form a
        reader can verify rather than asserted in a comment. Confessed cost, filed
        as the divergence in Q25: a fold that never sees the anchoring cannot
        condition on anchor grade, so the promise-versus-physics distinction
        :2090 insists on is invisible to the machinery that judges.

    Acme commits two budget acts, not one = decision:
      id: w5yqab
      why: >
        Beat D5 needs Nina endorsed and Dev untouched; beat D6 needs Dev declined
        and Nina untouched. Slot dispositions only advance as the log grows, so one
        committed act cannot present Nina both ways at two positions, and the
        obvious single-act corpus is unbuildable rather than merely inelegant.
        Chose two committed `approve-budget` acts, the second superseding the first
        as the live proposal, which is also what an organization actually does when
        a motion is re-tabled after a director objects. This forces a reading of
        Custos that Q26 records and that we could not settle from the text: a
        prospective question naming an act kind binds to the latest committed act
        of that kind at or before the position. Under the aggregating reading D6
        is affirmed and the demo's centerpiece collapses, which is why Q26 is the
        entry in the register we most want answered.

    An event's SAID is computed over normalized bytes = decision:
      id: ff4jzv
      why: >
        Custos :3085 says the digest ranges over the event's complete canonical
        bytes, and the contract's `Event` has no slot for a signature, so utina
        carries signatures inside the committed body. Taken literally that is
        circular: signing changes the bytes that define the identifier the
        signature commits to. Chose one normalization, applied in one place, before
        every digest — the identifier field `d` is replaced by a placeholder of the
        encoded digest's length as :3083 requires, and any `sig` field is dropped —
        so the SAID of a signed event equals the SAID of the same event unsigned.
        Rejected computing the SAID before signing and never recomputing, which
        works but leaves no way for a stranger holding only the final bytes to
        check the identifier. The carve-out for signatures is inferred from
        :3087-3088, where receipts and attachments address the event's bytes and
        are therefore not among them; Q27 records that inference as a reading rather
        than letting it pass as obvious.

    Acme's committed law mirrors the contract's own field names = decision:
      id: 5ujoa2
      why: >
        The law payload is the seam between this commission, which writes it, and
        the fold commission, which parses it — and the contract specifies the
        parsed dataclasses without specifying the committed encoding, so the two
        sides could agree perfectly with the contract and still not interoperate.
        Chose the encoding that is a field-for-field image of the contract's own
        types: a clause carries `id`, `governs` and `group`; a group carries
        `operator` and `slots`; a slot carries `endorser` and `weight`. Rejected a
        bespoke or abbreviated encoding, which would save bytes nobody is counting
        and require the fold commission to learn a vocabulary. Weights are
        committed as exact rational strings — `"1/2"`, never `0.5` — because
        @ta7vle already decided unity must be decidable, and a float in the
        committed bytes would make it not.

    A facade identifier is its alias = decision:
      id: d2nlhb
      why: >
        Real AIDs are digests of key state, and the facade could imitate that.
        Rejected: the oracle reads `acme:marta` in its assertions, an identifier a
        human recognizes is worth more than a fake prefix in a fixture nobody
        verifies cryptographically, and imitating the shape without the substance
        invites a reader to trust it. `incept` therefore returns the alias it was
        given, after registering the deterministic key state behind it. The
        discipline that keeps this from becoming a trap is that callers use the
        returned value rather than assuming it: the keripy backend will return a
        real prefix from the same call, and any caller that hardcoded the alias
        breaks there rather than here.

    The reading of an unreachable threshold is one constant, not a shape = decision:
      id: dozrtx
      why: >
        Custos leaves open what an evaluator returns when a threshold can no longer reach
        unity, and the two readings are the demo's whole centerpiece (Q1, and the slot
        commission's correction at Q16). Chose to ship Defeated and to isolate the choice
        behind one module-level constant, utina.fold.evaluate.UNREACHABLE_YIELDS, with one
        named function behind it and both branches implemented and tested. Defeated is what
        docs/demo-script.md and the acceptance oracle require, and it is the reading in which
        beat D3 says what the beat is for. Rejected hard-coding it, because custos-4.2.md:1966
        leans the other way in the drafting authority's own words and the maintainer has not
        finally ruled; rejected making it a runtime option, because a governance engine whose
        codomain depends on configuration cannot claim replay — two verifiers holding the same
        bytes would answer differently. Tradeoff accepted: the flip is a source change and a
        release, which is the right friction for a change of this kind. Under the other
        reading the requirement set names the SPENT slots as expired/abandoned rather than the
        unfilled ones, because :1966's own prescription is the empty set in the two-slot case
        and the Ground Axiom refuses that value (Q8).

    A committed act is judged at its own coordinate; a proposal, at the position = decision:
      id: xq5t7m
      why: >
        evaluate() must pick a coordinate before it can pick a Constitution, and the two
        question constructors need different ones. Chose: a Committed question is judged under
        the law in force at the subject act's own coordinate, which is what makes the past
        recomputable (beat D9) and an amendment answerable under the law it replaces (beat D4);
        a Proposal is judged under the law in force at the appraisal position, because it asks
        whether an act may be performed now. Rejected judging a proposal at its bound act's
        coordinate, which would freeze an outstanding decision under superseded law and make a
        domain unable to re-ask a question under its new law without re-tabling. Custos settles
        the first half four times over and never reaches the second; logged as Q29, DIVERGENT.

    A prospective question binds to the latest tabling and never aggregates = decision:
      id: 4kv2np
      why: >
        A Proposal names an act class, and Acme tables approve-budget twice, so the fold must
        choose which committed act the question is about. Ratified the substrate commission's
        pin (Q26): the latest committed act of that class at or before the position. Rejected
        aggregating every endorsement of the act class, which is the reading that destroys the
        demo without looking broken — beat D6 would inherit Nina's endorsement of the tabling
        it replaced, come back affirmed, and the D3-against-D6 contrast the whole demo argues
        would silently become a beat about a decision that passed. The counterfactual is
        computed in tests/test_seam.py rather than asserted, because a hazard this quiet earns
        a test that demonstrates it rather than a comment that claims it.

    The writing plane keeps its protocol seam now that the fold exists = decision:
      id: mt6wbz
      why: >
        Integration ratified @tvaq2s rather than collapsing it. The obvious move on merging was
        to delete FoldValues and have enact and acme import utina.fold directly, since the fold
        now exists. Rejected: Custos section 1.3 separates the constructor's plane from the
        judge's, an import edge would make the writing plane unloadable without the judging
        plane, and the demo asserts that separation on stage. What integration owed was proof
        rather than removal — tests/test_seam.py checks that the real fold types satisfy the
        protocol and that no module of the writing plane imports utina.fold at all, by AST
        inspection rather than by grep, so a lazy import inside a function body cannot pass.

    keripy enters as a substrate-only dependency, quarantined by fitness function = decision:
      id: 343xvm
      why: >
        The demo's claim is that the fold cannot tell which substrate it is on, and a claim of
        that shape decays the moment a KERI import is convenient somewhere else. Chose to admit
        keri, keria, hio, lmdb and blake3 into exactly one place — src/utina/substrate/keri*.py —
        and to widen tests/test_fold_purity.py from the fold alone to every plane above the
        substrate: utina.fold, utina.enact, utina.acme and utina.cli. Rejected trusting review,
        because the boundary that matters is the one nobody is looking at during a deadline.
        Rejected admitting keripy into utina.cli so the composition root could name a Habery:
        the CLI selects a substrate by name and the substrate package constructs it, which keeps
        the CLI's import graph free of KERI and makes --substrate facade a real fallback rather
        than a flag over an already-loaded dependency. Pinned by commit rather than by version,
        because keripy 2.0.0-dev6 is a moving target and a demo that cannot be rebuilt from its
        manifest is not replayable.

    utina.coia is standalone and stdlib-only, so the move out stays cheap = decision:
      id: 6b3ntq
      why: >
        COIA (~/code/me/coia, whose coia.py is the normative oracle) is implemented here because
        the demo needed human-readable party names, and tick ~6s25 holds the open question of
        whether it belongs in heti as shared machinery instead. A module built to be moved and a
        module built in place differ, so the shape was chosen for the move: utina.coia imports
        nothing from utina, takes who, role and scope as arguments rather than reaching into the
        Acme record for them, and is tested against the spec's own published examples as
        hardcoded vectors, so the tests travel with the code rather than staying behind. A
        fitness test asserts the no-utina-imports property by AST inspection, because it is the
        property that would rot first and silently.
        Chose the standard library over the third-party `regex` package that the oracle uses for
        its \p{...} classes, implementing the same Unicode property tests with unicodedata
        categories and explicit code-point sets for the two binary properties (Dash and
        Quotation_Mark). Rejected adding `regex` as a runtime dependency: this repo carries
        exactly two by decision, a display-only convenience is the worst possible reason to make
        it three, and a module intended to be liftable into another repo is more liftable with no
        dependencies at all. Tradeoff accepted: the property sets are enumerated in source rather
        than resolved from the Unicode database, so a future Unicode revision could add a dash
        this module does not know about. A dev-only script cross-checks every vector against the
        oracle in an ephemeral environment; it is deliberately outside CI, because it depends on
        a path outside this repo.

    The keripy substrate imposes one key order, and it is the same order three times = decision:
      id: fy5lwj
      why: >
        keripy's Saider.saidify digests a mapping in INSERTION order; substrate/canonical.py
        sorts. Two conventions meeting inside one substrate would look exactly like a signature
        bug and nothing else — the SAID would be computed over one byte image and the signature
        over another, and the failure would surface at verify() as a false, with no error and no
        clue. So the order is decided once: the identifier field first, every remaining field in
        sorted order, the signature excluded. One helper produces the mapping and said(), sign()
        and verify() all call it; no method serializes a body it did not build. Rejected relying
        on the constructor's insertion order, which happens to be stable today and is a
        byte-level tripwire. Rejected reusing canonical_bytes() for the digest, because the point
        of the keripy substrate is that a stranger with keripy and nothing of ours recomputes the
        SAID; that requires KERI's own Blake3 SAID over KERI's own JSON.

    Determinism is pinned by salt, by inception order, and by the stretch tier = decision:
      id: 7jrbt3
      why: >
        KERI key events carry no timestamp — nowIso8601 appears only in key-state notices and
        peer messages — so a KEL is byte-reproducible once its key material is. Three things fix
        the key material and all three are explicit: a literal salt, the order in which habs are
        made (keripy derives each key from the salt plus a sequentially assigned pidx), and the
        temp flag, because temp=True stretches at a weak tier and temp=False at Argon2's, which
        yields DIFFERENT identifiers from the same salt. Chose temp=True for tests, where the
        whole suite then costs milliseconds, and a real on-disk store for the CLI, where an
        independent KERI tool has to be able to open what we wrote. Tradeoff accepted and stated
        rather than discovered: the demo's AIDs under --substrate keripy are not the AIDs the
        test suite computes, because the tier differs. The salt is a demo fixture in the source,
        which is correct for a fixture and would be a key-management failure in production.

    An endorsement stays a plain signed body anchored in a KEL, not an ACDC in a TEL = decision:
      id: 65buz7
      superseded_in_part_by: 7db5c4
      note: >
        The half of this decision that kept an endorsement a plain signed body is withdrawn
        by @7db5c4: an endorsement is now a real ACDC. The half that kept the TEL out
        stands — the credential is registry-less, which @7db5c4 shows is conformant
        evidence, and tick 56js holds the revocation question this deferred.
      why: >
        The dossier alignment makes real ACDC issuance the honest long-term encoding of an
        endorsement, and this is knowingly not that. Measured, the ACDC path on 2.0.0-dev6 costs
        a registry pinned to v1 inside a v2 KEL (v2 defaults raise SerializeError on vcp), a
        three-step anchor dance through the transaction-event verifier before issue() will run at
        all, a resolvable schema, and two more nondeterminism knobs. None of it is needed by any
        of the ten beats — revocation is out of scope by construction, since a party who changes
        their mind declines. Chose signed bodies whose field names were already chosen so the
        move is a re-encoding rather than a rename. Logged as its own question in
        docs/custos-questions.md so the gap is on the record rather than in a commit message.

    rotate returns an identifier, and the anchor binding is protocol = decision:
      id: ygjwyw
      why: >
        rotate() returned a fold Event whose Position was minted from the substrate's own key-log
        sequence number. A KEL sequence number and a corpus position are different ordering
        spaces, and putting one inside the other's type invites a comparison that would be
        meaningless and silent — a latent defect in the facade before keripy made it obvious.
        Narrowed rotate to -> SAID, and promoted the facade's anchor_of into the protocol as
        anchoring_event(said) -> SAID | None, which is where it belonged: rotations stay out of
        the corpus (@jdie6v), so the binding beat D4 asserts is answerable there or nowhere.
        Under keripy anchoring_event is a real seal lookup over the KEL, so the protocol gained a
        method that costs the implementation nothing and the demo everything.

    An alias is not an identifier, so the composition root incepts first = decision:
      id: crrtzf
      why: >
        Constructor.__init__ took a gAID and incept_domain then incepted it, which is coherent
        only while the substrate returns its argument. A keripy prefix is a digest of the
        inception event and cannot be known before makeHab returns. Chose to have the composition
        root incept every party in a fixed order and hand the Constructor a real identifier, and
        to have Acme's committed law built from the identifiers inception returned rather than
        from the alias constants. Rejected letting incept_domain assign self.gaid, which leaves
        __init__ advertising a value that is a lie until a later call. The consequence reaches the
        acceptance oracle, which addressed the founders by the literal "acme:marta": it now asks
        the record for the identifier that alias names. That is not a weakened case — the oracle
        was asserting a facade artifact, and now asserts what it meant.

    A signature carries the establishment event it was made under = decision:
      id: zk27gz
      why: >
        Resolving a verifier's keys from CURRENT key state means a rotation silently invalidates
        every signature made before it, turning an ENDORSED slot into PENDING with no error —
        and Acme's gAID rotates at beat D4, mid-record. The protocol says a substrate signature
        is an opaque string, so the fix fits inside it: the string carries the SAID of the
        establishment event whose keys signed, and verify resolves THAT event's key state out of
        the KEL rather than the current one. This is the coordinate half of what keripy's own
        trans-idx-sig-group carries, in the one field the seam gives us. The fold never looks
        inside the string; no signature above the substrate changes shape.

    The facade stays the default, and the flag is the switch = decision:
      id: dxs27r
      why: >
        --substrate keripy is opt-in and --substrate facade is what runs when nobody passes
        anything. A demo runs tomorrow morning; the fallback from a keripy fault has to be a
        flag a narrator can type, not a git operation performed under an audience. The keripy
        path is proved by the conformance suite and by the acceptance oracle running twice, so
        the default is a matter of blast radius rather than of confidence.

    Show the ground on every screen that shows a verdict = constraint:
      id: cl1grd
      why: >
        Custos's Ground Axiom (custos-4.2.md:1502-1507) makes the ground a component of what a
        finding IS: "a value that does not carry its ground is not a member of this type, whatever
        else it may be." A renderer that prints DEFEATED and stops has therefore not abbreviated
        the finding, it has displayed something that is not one. Chose to make the ground
        structurally unskippable — the finding renderer emits the verdict line and the ground block
        from one function, and there is no code path that produces one without the other. Rejected
        a `--terse` flag that would print the verdict alone, which is exactly the screen the axiom
        forbids and exactly the screen a hurried narrator would reach for. Tradeoff accepted: the
        smallest eval screen is about fifteen lines, and a demo of many evaluations scrolls.

    Show the arithmetic, not just its conclusion = decision:
      id: clarth
      why: >
        The audience is being asked to believe that a governance answer is checkable rather than
        oracular. The claim is only visible if the slots, their weights, their dispositions and the
        sum against unity are all on the screen: "DEFEATED under clause A1" is still an assertion,
        while "1/2 endorsed, 1/2 spent, 1/2 reachable, unity 1" is a calculation the audience can
        do in their heads and catch us getting wrong. Chose to render both sums — endorsed and
        still-reachable — because the demo's centerpiece (D3 against D6) turns entirely on the
        second one, and a screen showing only the endorsed sum makes D3 and D6 look identical at
        1/2 and the differing verdicts look arbitrary. Rejected showing only the outstanding slots,
        which is what the Pending finding itself carries: it answers "who else must act" and not
        "why is this dead."

    The CLI derives the slot table itself, and a test forbids it from disagreeing = decision:
      id: clxchk
      why: >
        `evaluate()` returns a Finding, and a Finding carries its ground but not the slot table:
        Affirmed names the endorsements that reached unity, Defeated names the one declination it
        cites, Pending names only the outstanding slots. None of them carries every slot with its
        weight and disposition, which is what @clarth requires on the screen. So the CLI recomputes
        it, from the same committed values, with `utina.fold.slots.classify` over the clause the
        Constitution supplies. That introduces a second path to a governance-relevant fact, and a
        second path can diverge silently — the exact failure mode this repo warns about at the
        enact/slots seam. Chose to close it with a cross-check test that walks every beat and
        asserts the derived table implies the fold's verdict: satisfied iff Affirmed, unreachable
        iff Defeated, otherwise Pending, and the clause the CLI renders is the clause the finding
        cites. Rejected calling `utina.fold.evaluate`'s private helpers, which would remove the
        divergence but make the CLI a client of another package's internals. Rejected inferring the
        clause from the finding instead of from `Constitution.governing`, which would be
        self-consistent by construction and would therefore prove nothing.

    Refusal is rendered in a different shape, not a fifth verdict colour = decision:
      id: clrfsl
      why: >
        A refusal is an operational fact and not a member of the codomain (custos-4.2.md:1896-1902,
        and `utina.fold.refusal`). A screen that renders it as a fifth verdict banner in a fifth
        colour teaches the audience the opposite of what the engine implements, and D8 exists
        precisely to teach that distinction. Chose three carried differences rather than one: the
        banner reads REFUSED — NOT EVALUABLE and says in words that it is not a verdict; the slot
        table and the sums are absent entirely, because with no governing clause there is no
        arithmetic to show; and in their place the screen lists what the law in force DOES govern,
        so the absence is visible rather than asserted. Rejected relying on colour, which fails on
        a projector, in a pipe, and for a colour-blind viewer.

    Colour is decided by the stream, never by a flag = decision:
      id: clcolr
      why: >
        Chose `isatty()` plus the NO_COLOR and FORCE_COLOR conventions over a `--color` option.
        Every flag on the base parser is a branch that has to be covered and a token the narrator
        can fumble on stage, and the three cases that matter — projector terminal, piped to a file,
        captured in a test — are all decided correctly without one. Colour never carries meaning on
        its own: every verdict is a word first and a colour second, so `NO_COLOR=1` loses nothing
        but emphasis. Tradeoff accepted: a narrator who wants colour through a pager needs
        `FORCE_COLOR=1`, which is documented in the epilog rather than discoverable in `--help`'s
        option list.

    Each stream decides its own color = decision:
      id: ig3tc5om
      why: >
        @clcolr said "decided by the stream" and the code decided it once, from stdout, for both
        streams: `Console.over` sets a single `color` flag from `_takes_colour(out, environ)` and
        `render_error` writes to `err` under it. So a terminal run with stderr redirected wrote
        escape sequences into the file, and a run with stdout redirected printed a colorless error
        to a terminal — the second harmless, the first a corrupted artifact. Reproduced on main
        before the fix (tick 3ebe). Chose to carry a Style per stream and have a renderer take the
        one belonging to the stream it writes to, which is what "decided by the stream" already
        meant. Rejected painting stderr from stdout's capability on the argument that the two are
        usually the same terminal: they are, right up to the one case that produces a bad file, and
        a rule that is right by coincidence cannot be tested. This narrows @clcolr rather than
        reversing it — the isatty/NO_COLOR/FORCE_COLOR precedence is unchanged and now runs twice.

    Color values come from the 256-palette, never from the sixteen theme slots = decision:
      id: qi3inaua
      why: >
        The first implementation painted with SGR 30-37 (`31` red, `32` green, `33` yellow). Those
        indices are the user's terminal theme and every terminal remaps them, so the verdict colors
        were whatever the machine in the room happened to be configured for — under a light or
        solarized profile, a yellow that is olive and a green that is grey. Chose the 256-color
        indices 16-255, which are fixed by the xterm cube and render identically everywhere, and
        chose an explicit gray index for scaffolding in place of SGR 2, which terminals implement
        least consistently of all and which some ignore. Two rungs only, `256` and `none`. Rejected
        a 16-color rung, because every slot in it is the thing being escaped. Rejected truecolor,
        which is not available on the terminal this is demoed from — both facts measured 2026-08-15
        and recorded in entviz's docs/terminal-pill.md §2, whose palette is pinned for this reason.
        Tradeoff accepted, and it is a real one: the only terminal detected as incapable is
        `TERM=dumb`, which announces itself. A terminal that lacks 256-color support without saying
        so gets escape sequences it cannot render, and there is no fix that is not a capability
        query — which would have to work over ssh, inside a pipe and inside a test, and does not.
        The failure is at least legible: a reader sees an escape sequence rather than a color that
        means something other than what the palette says.

    One meaning per color, and the meaning is the health state rather than the screen element = decision:
      id: w6bpgbwi
      why: >
        The request was for color that shows healthy governance against governance blockage, and
        the obvious reading — paint the verdicts — is wrong in a way that would teach the audience
        the opposite of what the engine computes. A defeat is healthy governance: a signed no
        correctly spending a slot is the arithmetic working, and D3 exists to show that. Pending is
        not a blockage, and demo 2's kernel 2 turns on one pending act whose cure path is open
        against another whose is shut. Custos's own permitted-transition table (custos-4.2.md:1662-
        1673) says the same thing structurally: pending is the only verdict with an edge to a normal
        outcome, affirmed and defeated are settled, self-convicted is absorbing — so liveness is
        orthogonal to whether the answer was yes. Blockage in utina is three predicates the fold
        already computes and the screens printed flat: reachability (`Group.reachable`), curability
        (`RequirementElement.species`) and integrity (self-conviction, and a declared disturbance
        set that differs from the computed one). Chose to give each color one meaning and paint it
        wherever that meaning appears, so that green in the disposition column, green on the sums
        row and a green banner are the same claim at three altitudes. Consequences that look like
        taste and are not: `revoked` on the registry screen is amber and not red, because beat 16's
        whole argument is that a revocation is ordinary and bounded, and red would put a malfunction
        into the one beat built to show there is none; "unity not reached" is amber while "unity
        unreachable" is red, so red appears exactly when the path is dead. Rejected a color per
        screen element, which is what a renderer grown one screen at a time produces by default.

    The columns' three colors are lightness-spaced, and the palette assumes a dark background = decision:
      id: b3nr4mq3
      why: >
        `endorsed`, `declined` and `pending` are the only colors that ever sit in one column beside
        each other, so they are the only ones whose separation cannot rely on being alone on the
        screen. Red and green is also the classic confusion, and the demo's centerpiece is exactly
        endorsed against declined in front of a room that will contain a deuteranope. Chose indices
        whose Oklab lightnesses run 0.628 / 0.762 / 0.887 — adjacent gaps of 0.134 and 0.125, level
        with the entviz palette's own worst adjacent gap, which was picked for this property — so
        the column reads dark / mid / light and survives color deficiency, a projector's crushed
        gamut, and a greyscale photograph of the screen. That monotone spacing is the property to
        protect if an index is ever swapped; hue alone is not the guarantee. The two banner-only
        colors are exempt, because a refusal screen has no table at all (@clrfsl) and a
        self-convicted banner sits over a table that is all green (beat 22), so what matters there
        is hue distance from green rather than lightness. Chose a dark background and said so:
        searched the plausible hue families and no red/green/amber triple in the 256 palette clears
        3:1 against black AND against white, so a palette that serves both does not exist. On a
        light terminal amber 220 is 1.4:1 and the sums row is unreadable. The previous SGR scheme
        assumed dark too; this only makes the assumption legible enough to be argued with.

    Demo 2's transcripts and cue card are tracked, generated, and pinned = decision:
      id: gizauc3r
      why: >
        The three transcripts and the lectern cue card were first written to `.ignored/`, on the
        reasoning that a demo artifact is a working file with the lifespan of one demo. Daniel
        rejected that and he is right: the repo already had this arrangement for one screen —
        `docs/render-candidates.md` holds rendered output, `tests/test_cli.py` pins it, and
        @4tcsbw72 names re-rendering it as a consequence of moving the record — so a transcript in
        `docs/` is an established, tested pattern here rather than an invention. Chose to extend it
        from one screen to the whole of demo 2: `tools/render-demo-2.py` renders the three parts
        through `utina.cli.run`, so a tracked transcript cannot be a screen the command could not
        produce, and builds the cue card from the driver's own OPENER, KERNELS, LEAVE_BEHIND and
        CUT_ORDER, so the card cannot name a beat the driver does not have. A test re-renders all
        four and asserts the files match, with `--check` for a maintainer and for CI.
        What tracking buys, and it is the argument rather than tidiness: a transcript in the tree
        turns "did that render change?" from a question somebody has to think to ask into a diff in
        a pull request. This session paid the price of not having it — proving the colour work left
        plain output unchanged took building a throwaway worktree at the previous commit, which a
        tracked transcript would have made a one-command check, permanently.
        Two costs accepted rather than hidden. The opener runs under keripy, so its prefixes are
        pinned to a keripy version and repinning keripy (tick 4z5c) will move every one of them;
        the test says so in its failure message, because a pinned artifact whose churn is
        unexplained is worse than none. And every render change now shows as a diff in four files,
        which is the informative churn being paid for rather than a side effect.
        The width on the card is measured from the transcripts rather than chosen, and that caught
        two things on the test's first run. The card claimed 88 — `render.WRAP` — while beat 14's
        echoed command was 89, because a command line cannot be wrapped and the prose width
        therefore does not bound the screen. And the error renderer wrapped nothing at all, so the
        same beat's refusal detail was a single 529-column line: `render_error` now wraps to the
        margin every other paragraph uses. Left alone deliberately: the SELF-CONVICTED banner
        overflows its ten-column field and pushes that one headline to 92, and widening the field
        would move the headline on every eval screen to fix one.

    An identifier is never painted = constraint:
      id: pumwsfto
      why: >
        Color on a SAID, a law head or a party identifier is noise on the hardest thing on the
        screen, and worse than noise: it suggests a distinction a reader could act on, when the
        only safe act is to compare the value whole (@clcoia, @clhndl). A reader who believes two
        green identifiers are the same pair has been misled by the renderer. So identifiers,
        aliases, weights and fractions stay unpainted, and what carries the judgment is the note
        beside them. Rejected painting a party by role, which would put the display plane in the
        business of asserting standing (@cldspl).

    Identifiers are abbreviated to a prefix that is also a valid handle = decision:
      id: clhndl
      why: >
        A SAID is 44 characters and a law head is 64, and three of them on one line push past the
        100-column budget the projector allows. Chose to render a 12-character prefix followed by
        an ellipsis in every table, and to make `--said` and `--on` accept a prefix, so what the
        screen prints is what the narrator can type back. Rejected a `--full` flag (a branch, and a
        flag nobody remembers on stage) and rejected a middle-elision like `E1rff...RWxY`, which is
        unambiguous to a reader and useless as input. The one place the full identifier appears is
        the subject line of an eval screen, where it fits and where a viewer copying it has a
        reason to.
      superseded_in_part_by: clcoia
      note: >
        The half of this decision that renders a PARTY as a truncated prefix is withdrawn by
        @clcoia: it is a security antipattern, not merely a terse rendering. The half that makes
        `--said` and `--on` accept a prefix stands, and @clwhoi extends it — a prefix remains a
        good thing to type and is no longer a good thing to print.

    `utina enact` continues the record in memory, and does not persist = decision:
      id: clphmr
      why: >
        Acme's log is rebuilt deterministically from `utina.acme.build` on every invocation, so an
        act committed by one process is gone by the next. Chose to make the verb honest within its
        own invocation rather than to add a state file: the screen shows the committed event —
        identifier, coordinate, body fields, signature, and the fact that the substrate verified it
        before it was recorded — and then shows the subject's finding before and after the act, so
        the audience sees a constructor acting onto the record and the record answering differently
        because of it. Rejected persisting the log to disk, which would make replay depend on the
        filesystem and would let a fumbled rehearsal leave state that changes what Friday's demo
        prints. Tradeoff accepted: the effect does not outlive the process, and the screen says so
        in one line rather than implying otherwise by silence.

    `utina enact` adopts an existing record through attributes `utina.enact` does not expose = deviation:
      id: cladpt
      discharged_by: jzozfn
      note: >
        The tick this deviation filed (7h6j) is closed: `utina.enact` now offers the public
        `Constructor.resume` this node asked for, the adapter is deleted, and the invariants
        its pin asserted became tests of the public API. See @jzozfn.
      why: >
        `Constructor` has no public way to resume a record it did not itself write: `_emit` takes
        its coordinate from `len(self._emitted)`, `_dispose` checks `self._saids`, and every verb
        checks `self._founded`. The CLI needs all three set from Acme's committed log. Chose to set
        them in one small documented adapter, because the alternative is to re-implement `_emit` in
        the CLI, and that would duplicate the committed byte layout — the field order, the
        coordinate-before-identifier rule, the signature-verified-before-recorded rule — across a
        seam that fails silently when the two copies drift. Reaching into another package's
        internals is the smaller and the louder of the two wrongs. Filed as a tick against
        `utina.enact` for a public `Constructor.resume(events)`; a test pins the adapter's
        invariants so the deviation cannot rot unnoticed.

    The demo driver computes nothing = constraint:
      id: cldemo
      why: >
        `utina demo` is a table of beats, each holding the argv of a command a person could type,
        and a loop that echoes the command and dispatches it through the same entry point the shell
        reaches. Driving constraint: if the driver can produce a screen the query CLI cannot, then
        what the audience is watching on Friday is a slideshow with a governance engine somewhere
        behind it, and the demo's own claim — that these are real answers to real questions — is
        the first thing it fails to demonstrate. Rejected letting the driver format even the beat's
        expected verdict, which would have made a beat that regressed still look right.

    A party is shown by a COIA alias, never by a truncated identifier = decision:
      id: clcoia
      why: >
        Every screen named its parties with a 12-character prefix and an ellipsis — `acme:marta`
        under the facade, `EPFtMUsnh_BZ...` under keripy. Both are wrong, and not for the same
        reason. The facade form is a coincidence: an identifier that happens to read like a name
        because the facade returns its argument, which teaches an audience that identifiers are
        legible and makes the keripy screen look like a regression. The keripy form is the real
        fault. A truncated prefix beside a name invites a reader to decide that two identifiers are
        the same by comparing what they can see, and it cannot support that decision:
        `~/code/me/papers/amp-diff.md` section 4.3.8 treats a prefix as an ENTROPY channel —
        faithful, but unable to amplify a difference — so an attacker who wants to match the twelve
        characters on the screen grinds twelve characters, which is cheap.
        `~/code/me/entviz-js/packages/react/docs/pill-design.md` section 2.1 draws the line this
        repo now holds: recognition is not verification, the collapsed form affords locate, expand
        and copy, and NO equality decision may be made from it. Section 3.3 rejects the short
        head-and-tail teaser by name, and is careful that the objection is to the SHORT inline
        teaser and not to a full value.
        Chose COIA aliases (`~/code/me/coia/README.md`) as what the screens name a party by, in
        every position where an identifier used to appear: the slot column, the defeat subcode and
        citation, the pending requirement, the log gloss and the enact line. Rejected keeping the
        prefix alongside the alias, which is the antipattern with a label attached and is strictly
        worse than either alone — it supplies exactly the twelve characters an eye will compare.
        Rejected showing the full 44-character identifier in the slot column, which is safe but
        does not fit, and which spends the audience's attention on the one thing they cannot check.
        Tradeoff accepted: an alias is creator-local, so the screens now show something that is
        meaningful to Acme and to nobody else. That is what @cldspl is about.
      children:
        An alias is display-only, and a fitness function enforces it = constraint:
          id: cldspl
          why: >
            COIA is explicit that an alias is a private nickname: it delivers Zooko's human-meaningful
            corner "only for the person who creates it", it "is not a commitment to meaning" for anyone
            else, it "can evolve without warning to suit its creator's fancy", and parsing someone
            else's alias for strong meaning is named in the spec as a dangerous antipattern. An alias
            therefore carries no security claim and must never acquire one by accident. Driving
            constraint: an alias must never enter committed bytes, must never be an input to the fold,
            and must never affect a finding. Chose to make that structural rather than careful — the
            alias table lives in `utina.cli`, the display plane, and is built at the CLI's composition
            root from the identifiers inception returned, so `utina.fold`, `utina.enact` and
            `utina.acme` cannot see it at all. `tests/test_purity.py` gains a second quarantine of the
            same shape as the KERI one and by AST inspection for the same reason: a lazy import inside
            a function body is exactly how this boundary would erode. `utina.cli` is the one exempt
            plane, because it is the plane whose entire job is display. Rejected hanging the alias off
            the `Acme` record in `utina.acme`, which is the obvious home and which would put a
            display-only string one attribute away from the code that writes committed bytes.

        Acme's demo identifiers carry COIA flag 9 = decision:
          id: clflg9
          amended_by: 67t6q43c
          note: >
            The reasoning holds and the digit does not. This node was written against COIA 1.x,
            where flag 9 meant a test environment; the cutover to 2.0 (@67t6q43c) makes 9 mean
            COMPROMISED and moves test to 6. Everything below about WHY Acme carries a test flag,
            and why neither 0 nor the unflagged form would do, survives unchanged.
          why: >
            COIA's flag 9 means the aliased identifier belongs to an experimental, test or demo
            environment with no real-world consequences to reputation, governance or cost, and must not
            be used where consequential production side effects are intended. That is a literal
            description of Acme: the log is rebuilt from committed bytes on every invocation, the
            keripy salt is a fixture in the source, and no decision on any screen binds anybody. Chose
            to carry the flag rather than to omit it, so that the aliases the audience reads are the
            aliases the spec would actually produce here, and so the screens say out loud that this is
            a demo instead of leaving a viewer to infer it from the company being fictional. Rejected
            flag 0 (unverified), which would be false: every party was incepted by this process, so
            there is no MITM to warn about. Rejected the unflagged form, which is the one COIA reserves
            for identifiers that are verified, public and usable in production, and which is the single
            most misleading thing these screens could claim.

        The short alias in columns, the full alias where there is room = decision:
          id: clscop
          why: >
            Truncating an alias is safe and truncating an identifier is not, and the asymmetry is the
            whole of @clcoia: an alias makes no security claim, so shortening it costs nothing that was
            ever there. Within Acme's own screens the scope is constant — everything on them is at
            Acme — so COIA's empty-scope form is not an abbreviation of the alias but a legitimate
            alias in its own right, and `9-marta-as-founder` is eighteen characters, which is the slot
            column's existing budget. Chose the short form in the arithmetic table and the law screen's
            slot list, and the full scoped form wherever the line has room for it: `utina whois`, the
            law screen's header, and the ground block. Chose to state the constant scope once, in the
            law screen header, so the short form is disclosed rather than merely convenient. Rejected
            the full form everywhere, which overflows the law screen's slot line at 106 columns.
            Rejected a per-screen truncation of the full form, which would put an ellipsis back on the
            screen and blur the one distinction this commission exists to teach.

        `utina whois` is the one place a full identifier appears = decision:
          id: clwhoi
          why: >
            Removing the prefix from the screens removes the only way an audience could see an
            identifier at all, and sometimes seeing one is the point — a viewer who wants to check
            Acme's log against another KERI tool needs the real prefix. Chose an explicit command over
            a flag or a wider column: `utina whois <alias-or-prefix>` prints the alias, the full
            untruncated identifier, and the substrate that produced it. This is the pill's expand
            affordance (pill-design section 2.1): verification routes through a deliberate act, never
            through a glance at a table. The query is normalized before lookup exactly as COIA's
            Comparing section requires, so a narrator may type `Marta as Founder at Acme` or
            `9-marta-as-founder` or a raw prefix and reach the same party. Rejected a `--full` flag on
            every command, which is a branch on every screen and a token to fumble on stage; rejected
            printing the identifier in a footer, which is a table by another name.

        Rejected for now: a fingerprint tag beside the alias = decision:
          id: clnotg
          why: >
            A five-character Crockford base32 tag over a domain-separated digest of the identifier is
            the right long-term answer to the question an alias cannot answer — whether two aliases
            that read alike label the same bytes — and it is the rejection test amp-diff argues for: a
            discrete channel, injective on its input, in an alphabet with no confusable glyphs.
            Rejected for this commission on schedule grounds and stated here rather than left implicit.
            Nobody verifies an identifier during the demo; the tag would be a channel nobody reads.
            Adding one the night before means a new column budget on the widest screen, which is the
            law screen, and a wrapped line at nine in the morning. Revisit when a screen exists whose
            job is comparison; `utina whois` is where it would land first.

        Rejected for now: extending the no-truncation rule to event SAIDs and digests = decision:
          id: clsaid
          why: >
            @clcoia removes the truncated PARTY identifier. The screens still print a truncated event
            SAID, law head, clause digest, evidence bundle and signature — `932f0ab892df...` — and the
            same amp-diff argument reaches them: a reader comparing two law heads by their first twelve
            characters is making the equality decision section 2.1 forbids. Rejected acting on it now,
            for two reasons that are about this change rather than about the argument. COIA aliases
            exist for ACTORS and the spec says so — a hash is "passive and stuck in a single, static
            role" and the conventions "make less sense" for it — so there is no alias to put in a
            digest's place, and the replacement would have to be invented: a committed name where the
            record has one, a coordinate where it does not. That is a redesign of the log screen's
            columns rather than a substitution into them, and the brief for this commission asks that
            everything else keep working exactly as it does now. Note the mitigation already present:
            the replay screen does not ask a viewer to compare its two heads by eye, it prints the
            machine's own verdict on the comparison (`IDENTICAL`), which is the correct pattern and the
            one a later commission should extend. Revisit as its own commission, with the log screen's
            layout in scope.

            RULED 2026-08-13 by the maintainer, and the ruling narrows the scope rather than merely
            deferring it: party identifiers are where the risk concentrates, because the attack the
            truncation enables is a man in the middle — a reader satisfied by a matching prefix accepts
            a substituted party. An event SAID, law head or clause digest carries less, because no
            reader forms a belief about WHO someone is from one. So the no-truncation rule is a rule
            about actors, and the remaining truncations are a legibility question rather than a
            security one. That does not make them free — the replay screen's pattern of printing the
            machine's verdict instead of inviting the eye stays the right one to extend — but it does
            mean a later commission may weigh layout against them honestly, which it could not do while
            the argument was framed as security.

    Exit status reports whether the command answered, not what it answered = decision:
      id: clexit
      why: >
        Chose 0 for any command that produced a screen, including a defeated finding and a refusal,
        and 2 for an error. A defeated finding is a correct and complete answer, and a shell that
        treats it as a failure would make `utina eval ... && echo ok` mean something the engine
        never said. Rejected mapping the four verdicts onto four exit codes, which invites exactly
        that confusion and would make `utina demo` exit non-zero on the beats it is proudest of.

    The constructor resumes a committed record through a public classmethod = decision:
      id: jzozfn
      why: >
        @cladpt reached into Constructor privates from the CLI's composition root because
        `utina.enact` offered no public way to continue a record it did not write. That
        deviation is discharged: `Constructor.resume(substrate, gaid, values=..., events=...)`
        is an alternate constructor on the writing plane. Chose a classmethod over a mutator on
        a fresh instance so that resuming a constructor that has already emitted is
        unrepresentable rather than checked — no state to police, and no error code for a
        misuse that cannot be typed. Founding is derived from the events themselves, an
        inception among them, rather than taken as a flag, so a caller cannot assert a founding
        the record does not carry. Positions must run contiguously from zero, refused with
        e.input.format.resume-record.f, because `_emit` takes its next coordinate from the
        record's length, and continuing over a gapped or permuted record would put every later
        event at a coordinate the committed bytes contradict — silently, which is the one
        failure shape this repo always refuses. Rejected verifying signatures at resume: the
        events are the caller's own committed log, and judging evidence is the fold's job under
        Custos section 1.3 — a constructor that re-checked proofs would be judging, and a check
        it cannot actually perform is decoration. The CLI's adapter `constructor_over` is
        deleted, and the invariants its pin asserted move to tests/test_enact.py as tests of
        the public API.

    An endorsement is a real ACDC — registry-less, schema-pinned, anchored = decision:
      id: 7db5c4
      why: >
        Tick 2coc, ruled narrow 2026-08-15: the evidence becomes real ACDCs while the law's
        composition rule stays domain-native (tick 5psg holds the wide half). The dossier
        spec's own Endorsed predicate is "a signed Endorsement ACDC with disp endorse and act
        appropriate to the operation, issued by the expected endorser and anchored in that
        endorser's KEL" (dossier-spec-body.md:223, restated :359) — revocation status is not a
        term in it, and the normative endorsement schema (SAID
        EAfn0gRMUnp6d1hyE5qJCN86kBFBp80JwMdm0BqiC1B0, named at :367 as the single schema all
        four operators use) has no registry field. So a registry-less credential is conformant
        evidence rather than a shortcut, and the costs @65buz7 measured — the v1 registry
        pinned inside a v2 KEL, the three-step anchor dance, the registry nonce — belonged to
        the TEL, not to the credential. Tick 56js holds whether revocation ever enters the
        vocabulary; the dossier-shaped door is an RMxN/RMxQ revocation OPERATOR in the law,
        not a registry on the credential. Chose the v1 ilkless shape via
        keri.vc.proving.credential(version=Vrsn_1_0, no status): its committed fields
        {v, d, i, s, a} are exactly the schema's required set, where v2's acm adds a t field
        the schema never names and most-compact SAID machinery that buys nothing here. The
        one nondeterminism left was the wall-clock dt keripy injects into the attributes
        block when the caller supplies none (proving.py:68, verified live on the pinned
        build): the substrate supplies a fixed fixture timestamp, the same posture as the
        pinned salt (@7jrbt3). Confessed reading: the schema's a.said is "typically the
        dossier's SAID" and utina's subject is a committed act event — the schema and the
        predicate are satisfied either way, and this note is where that reading is on the
        record. docs/custos-questions.md Q32 carries the settlement: the middle reading, a
        real credential with no registry operation.

    The governance event embeds the credential; the corpus discipline is unchanged = decision:
      id: vi4t4i
      why: >
        The event body seals its coordinate under the key s (Q24), and an ACDC's s is its
        schema — one key, two meanings — so the endorsement event cannot simply BE the
        credential. Nor should it: _emit's discipline (coordinate before identifier,
        identifier before signature, signature verified before recording) presumes utina's
        event shape, while an ACDC has its own identity discipline — a SAID over KERI's bytes
        — and its own signature, indexed and attached, in the substrate's existing
        est-coordinate format. Chose {t: "end", i, acdc: <sad>, acdc_sig: <signature>}: the
        event is sealed, signed and verified exactly as every other kind, and the credential
        inside stands alone — its own SAID, its own signature over its own canonical bytes,
        its own KEL anchor sealed by an interaction event, which is what the dossier predicate
        requires and what anchoring_event() already finds unchanged. Two signatures by one
        party accepted and distinguished: the event's covers the coordinate and the embedding
        (the corpus's replay claim), the credential's is what a stranger with KERI tooling and
        the key log verifies with nothing of ours. That is not the body-borne signature
        @yrkrqj rejected — the fold still never reads acdc_sig; it rides for the stranger,
        and the predicate stays attribution over substrate-vouched evidence. The substrate
        gains one protocol method, issue_acdc(issuer, schema, attributes) -> (sad, signature)
        — construct, sign, verify fail-closed, anchor — because credential construction needs
        the KERI library the planes above may not import; the facade mirrors it
        deterministically and does not fake a sized KERI version string (@d2nlhb's honesty).
        The fold's predicate reads issuer and schema from the embedded credential and
        disposition, act and subject from its attributes block, and gains one conjunct — the
        credential's s equals the pinned schema SAID, the one-schema form of the dossier's
        "names the schema that endorsement MUST satisfy" (:356) — with anything malformed
        still reading PENDING, never an error.

    An enactment takes force where it is affirmed, not where it is committed = decision:
      id: xhtvuxnc
      why: >
        R4 in docs/custos-proposals.md, and the correctness bug tick 4pmw held. Constitution.at
        keyed an edition's force on its enactment being COMMITTED and never consulted an
        endorsement, so in the demo record the board law was in force one event before the
        amendment enacting it reached unity, and a unilaterally committed — or actively defeated
        — enactment changed the law just the same. Custos implies the opposite without stating
        it: 214-215 makes a ratification an enactment, an enactment judged under the
        Constitution it amends, and that judgment "a finding like any other", and 1796-1800 has
        defeat annihilate upward — voiding "what was built on it", which an edition is, though
        the passage's own examples stop at the enactment rather than at the law it leaves. But
        207, read alone, says the fold "reads the successor law the enactment left", which is
        what was built. Chose: an edition takes force at and
        after its EFFECTUATION COORDINATE — the first coordinate at which the enactment's own
        lawfulness reaches unity, under the clause governing its act class in the law in force
        at its own coordinate — and an enactment never affirmed, or defeated, never takes force
        at all. Rejected force-on-commitment, the shipped bug. Rejected the coordinate strictly
        AFTER unity, because 3001-3003 binds a ratified document's clauses "for every position
        at and after the effectuation coordinate", and effectuation is where the enactment
        carried, not the event after it; under the strict reading the coordinate that seats the
        board is one the board's own law does not govern. Deliberately NOT decided: which
        edition governs where two enactments amend one predecessor and their effectuation
        coordinates interleave. 3038-3050 rules that case, where Custos governs its own
        succession by "the same discipline this standard imposes on every governed corpus"
        (2992-2994) — a successor cites its predecessor's bytes, eligibility is
        latest-unsuperseded, and "where two enactments claim the same predecessor, the GEL's
        committed order rules: the earlier lawful enactment is the succession, and the later
        travels as evidence" — but utina's enactment events cite no predecessor at all, so
        neither the eligibility test nor the fork rule is expressible over the bytes utina
        commits. The walk therefore keeps the shipped engine's own resolution, which is the last
        law event in canonical order among those in force, and that is an artifact of the walk
        rather than a reading: every record utina builds has a linear succession, in which the
        two rules cannot disagree. Widening the enactment to carry its predecessor is the
        prerequisite for deciding it, and it is not this tick's. Tradeoff accepted: the law fold
        is no longer a walk over law events alone. It consults the slot predicate, so
        constitution.py imports slots.py, and finding a first crossing re-classifies the slots
        at every candidate coordinate — quadratic in the record's length, taken over duplicating
        the precedence rules that make a declination decisive. This also builds the derived
        primitive docs/custos-proposals.md:244-251 says R1, R2 and R3 all need: the coordinate
        at which an act stops being in flight. Logged as Q33 and filed as
        Nicholas-Keystate/custos#96, whose second half is the predecessor citation (tick 5edf).

    A retraction reaches its act only while the act is still in flight = decision:
      id: nuxitore
      why: >
        Tick 5wu5 and R1 in docs/custos-proposals.md. The slot predicate filtered a retracted
        act out of `standing` unconditionally, so a slot fell back to PENDING at unlimited
        distance and a settled affirmation came apart: measured on the demo corpus, the bank
        account is affirmed at d9, and appending one retraction eighteen events after the act
        settled returns the same question to pending, naming its cure as the arrival of evidence
        that had already arrived. 1698-1712 forbids that edge by name — affirmed -> pending,
        "evidence does not un-arrive" — and 1730-1745 permits a successor to reverse a terminal
        value only where its grown bundle carries evidence falsifying a ground the prior finding
        cites, "never on added contrary weight alone". Chose: a retraction is honored only where
        it was committed while its act was still in flight, in flight meaning unity is neither
        reached nor unreachable, decided by one forward walk in canonical order in which each
        retraction is judged against the record before it. Rejected the unconditional filter,
        the shipped bug. Rejected Q18's reading B, in which a retraction spends its slot,
        because that gives the withdrawal an authority nothing committed gives it and lets a
        party defeat a live act by first endorsing it. The doctrine is the ground-evaporation
        text drafted for the spec at 1740 and never applied: withdrawal is not falsification,
        it is "a fact about the giver's present will, never a fact about the artifact the prior
        finding appraised", so it is added contrary weight and reverses nothing — because a
        system in which withdrawal undercuts is one in which any party unmakes any settled
        question at any distance, unilaterally. Q18's pin therefore narrows from A to A bounded
        by settlement, and the twin doctrine repair is owed by Custos. The unreachable half of
        the gate is independent of the UNREACHABLE_YIELDS reading and does not touch that
        constant (@dozrtx): under the shipped Defeated pin the finding is terminal, and under
        section 9's pending reading its species is expired/abandoned, whose ratified cure is
        re-presentation and not the arrival of evidence — so under both readings nothing further
        can be added to that act. This is the second crossing of the same shape as the
        effectuation coordinate (@xhtvuxnc) and the two are deliberately not unified: one asks
        where unity was reached and holds positions, the other asks where the act stopped being
        reachable and lives in a module that cannot see a coordinate. Tradeoff accepted: that
        module now steps event by event in the committed order, so two events at one coordinate
        resolve by the canonical tiebreak rather than as one bundle, which is the only order
        available to it; and classification is quadratic when a retraction is present, behind an
        early return for the ordinary case where none is.

    A third founding clause, carried into edition 2 byte-identical = decision:
      id: rwo55zyw
      why: >
        Tick 6ms6. Demo 1's founding law committed {A1, A2} and its board law {B1, B2}, so every
        clause changed across the amendment and no beat could show a pending act SURVIVING one.
        Issue 82's rule 2 — an amendment elsewhere leaves the cure path open, tested by same
        clause SAID, same requirement space, same pinned lens — was unshowable, and so was its
        contrast with rule 1, which is the pair the demo now turns on. Chose a third founding
        clause A3, release of escrowed founder equity, at the founders' own weights, re-committed
        in edition 2 with unchanged bytes: a clause is its bytes and each is independently
        SAID-addressed (1483), so that is the same clause with the same identifier. Rejected a
        clause that merely resembles itself across the amendment, which would demonstrate rule
        2's stability test FAILING and read as though it passed. Rejected making amendment
        additive so that unmentioned clauses persist implicitly, which is @wg3jr6's settled
        question and would put two clauses over one act kind. The subject matter is the argument
        rather than a convenience: seating a board distributes ordinary authority and the
        authority to amend, and deliberately does not reach the founders' own escrowed equity, so
        A3 is untouched for a reason a room accepts instead of because the fixture wanted a
        control. Both editions build A3 through one function so the two sites cannot drift, and
        tests assert the identity where it is claimed — equal SAIDs and equal sub-block bytes,
        read out of the two committed law events rather than out of the builder. Consequences
        accepted: the record grows the tabled release and Marta's endorsement before the
        amendment and Dev's cure after it, so every coordinate after d3 moves and the founding
        law head changes with it; demo 1's law screens, its prologue narration and its pinned
        head fragment therefore change, while every demo-1 verdict stands unaltered, which is
        exactly what choosing a clause no other beat touches buys.

    The signed no at D3 moves from the hire to a new office-lease act = decision:
      id: 4tcsbw72
      why: >
        The demo-2 beat in which a pending act's cure path CLOSES needs an act that is still
        pending when the amendment lands: the hire, whose cited clause A1 the amendment repeals,
        leaving the amending enactment as its ground (issue 82 determination 1). Demo 1 had
        already spent that act — Dev declines the hire at D3, which is the defeat half of the
        D3-against-D6 centerpiece — so one of the two had to give. Chose the split demo 2's
        script already calls for: a new ordinary act, sign-office-lease, takes Dev's declination
        and becomes D3's subject, and the hire keeps Marta's endorsement alone and stays pending
        across the amendment. Rejected the additive alternative, keeping D3's declined hire and
        tabling the hire a second time for demo 2, which costs no test and puts two tablings of
        one act class in a log this audience reads line by line, where the only honest
        explanation is that one of them serves a different demo. D3's argument does not depend
        on which act carries the no: it is the same person's same signed declination under a
        two-slot clause, and the contrast with D6 is untouched. Daniel ruled it 2026-09-10, the
        question being whether a row of a script still in force may move; it may. Consequences:
        the D3 row of that script, the acceptance oracle's D3 cases and the demo driver's D3
        beat all name the lease; the record gains two events, so every coordinate after the
        hire's endorsement moves again; and docs/render-candidates.md is re-rendered where a
        test pins it and says plainly that its two unchosen alternates were drawn against the
        pre-split subject.

    One verb performs both halves of a cooperative delegation = decision:
      id: 2a25xudi
      why: >
        2139-2148 says a seated organ SHOULD be a delegated identifier of the gAID, so that
        delegation "dual-anchors the seat's key events (the organ signs; the delegator seals)"
        and gives the charter's delegation strata KERI's delegation semantics rather than a
        metaphor. KERI's delegation is cooperative and has exactly two halves: the delegate's
        inception names its delegator in di, and the delegator seals the delegate's inception
        event into its own key log. Neither half alone is a delegation — an unanchored dip is a
        claim, and a seal with no dip anchors nothing. Chose one verb, delegate(delegator,
        alias) -> AID, which performs both halves and returns the delegated identifier.
        Rejected two verbs, an incept-delegated followed by an approve, because that lets a
        caller produce the unanchored half and leave a record claiming a seat nobody approved;
        making the halves inseparable at the seam is the fail-closed direction. Rejected a
        delegator argument on incept, because a delegation is not an inception with a flag: it
        returns an identifier whose authority is another's, and a caller reading incept would
        not know a seal was owed. Observability needed one new query and not two: a delegated
        inception's identifier IS its own event's digest, so anchoring_event(seat) already
        returns the delegator's sealing event, exactly as it does for a credential, and only the
        di half needed asking for. delegator_of is total and answers None rather than raising,
        matching anchoring_event and verify — "this substrate cannot show that anybody delegated
        it" is the same fail-closed answer for an unknown identifier as for a self-incepted one.
        Under keripy this is makeHab(delpre=...), an event seal (i, s, d) in the delegator's
        interaction event, and processing escrows so the delegate's key state is accepted;
        measured on the pinned build, the dip carries di and its prefix equals its own said, and
        the seat signs and can take a delegated rotation afterwards. The facade records the
        delegator and seals the delegated identifier through the same interaction an issuance
        uses. Neither backend adds a corpus event: delegation lives in the key log (@jdie6v), so
        it moves no coordinate and regenerates no identifier in the record. Tradeoff accepted:
        every party's keys still come from one pinned salt in one keystore, so "Nina holds seat
        3's keys" is a story the fixture tells rather than a custody boundary it enforces.

    A real TEL holds the registry, and the fold never reads it = decision:
      id: exy3u4t7
      why: >
        1420-1422 requires a standing-conferring credential to be revocable through its
        registry, so the seat credential is registry-bound where an endorsement stays
        registry-less (@7db5c4): two credential kinds with different obligations, and the demo
        shows both. Chose a real keri.vdr registry under keripy — vcp, iss and rev events in a
        TEL, anchored by seals in Acme's KEL — over a registry-shaped field on the credential,
        because 1916-1927's doctrine is that registry state is EVIDENCE and a relying party
        that treats it as authority "has skipped the law and trusted the ledger", and a field
        nobody can revoke would make that sentence unshowable. The three sources of
        nondeterminism @65buz7 priced are all pinnable, measured on the pinned build: the
        registry nonce is a fixed qb64 seed, the vcp is built at version Vrsn_1_0 because the
        v2 defaults raise on it, and iss/rev take the same fixed dt the credentials take, since
        keripy stamps wall-clock time when the caller supplies none. With those three pinned,
        two Haberies built from the same salt produce the same registry identifier, the same
        credential identifier and the same final KEL digest. The anchor dance is four steps and
        cannot be shortened: makeRegistry builds the vcp but its own regser property reads
        through a tever that does not exist until the anchor lands, so the sequence is build,
        seal (i, s, d) from the TEL event into the controller's interaction event, anchorMsg to
        hand the TEL event its anchor, then processEscrows. A seal whose s is not the TEL
        event's own sequence number is accepted and does nothing, which is how a revocation can
        appear to succeed and leave the state at iss.
        The seam gains three verbs and one query — open_registry, a registry keyword on
        issue_acdc, revoke_acdc, registry_state — and issue_acdc takes a keyword rather than
        splitting into two verbs, so both kinds of credential are constructed, signed, verified
        and anchored by one code path and the difference between them is one argument at the
        call site. State reads as "issued" or "revoked", utina's words rather than KERI's ilks,
        because the protocol is above the seam.
        The load-bearing negative: the FOLD never calls registry_state. It cannot — the purity
        fitness function forbids the import — and it should not, because a fold that read
        registry state from a substrate would be reading an ambient condition, which is exactly
        what issue 82 rule 3 rules out when it makes registry state "a member of the evidence
        bundle rather than an ambient condition read against it". So the constructor commits the
        issuance and the revocation as governance events and the fold folds THOSE into standing;
        registry_state answers for screens and for the constructor's own fail-closed checks.
        That split is what keeps the two currents unmerged at the layer where they could quietly
        merge.

    A slot names the office that may act and the schema its evidence must satisfy = decision:
      id: z373ew7j
      why: >
        Two changes to one committed field, taken together because they are one statement about
        what a slot is, and because each alone would move every identifier in the record.
        FIRST, the law slots the SEAT rather than Nina. 2139-2148 asks for a seated organ to be
        a delegated identifier of the gAID, and slotting the officer instead of the office
        quietly says a governance power attaches to a human rather than to a post someone holds:
        a director leaving would then be a reissued credential and an amended law, where under
        the office it is a rotation on the seat and nothing else moves. Nina stays an incepted
        party with an alias and commits no act in the record — she holds the seat's keys in the
        story, and the fixture models that as the seat signing, because the substrate holds
        every party's keys anyway (@2a25xudi's tradeoff, restated where it bites).
        SECOND, a slot names the schema its evidence must satisfy. 1946-1951 describes exactly
        that — "each slot naming the schema its evidence must satisfy" — and 1435-1437 then
        SHALLs the consequence: "Requirement elements in typed requirement sets SHALL name their
        required schemas by schema identifier in the same discipline." utina satisfied neither,
        invisibly, because one endorsement schema existed and the slot predicate pinned it as an
        engine constant. A second credential kind (@exy3u4t7) ends that: a requirement for an
        endorsement must not read as dischargeable by a seat credential, and the engine could
        not say which it wanted. Chose to commit the schema in the slot and have the fold read
        it from the law, over defaulting it on the requirement element from a constant the way
        kind and species are defaulted (@7wysgy). Rejected the default because a schema the
        engine supplies is not a requirement the law made — it is an ambient input wearing a
        field's clothes, and the whole reason the element names a schema is so a reader can see
        what the LAW asked for. Tradeoff accepted: every clause's bytes change, so every
        identifier in the record moves once more, and a domain that writes a clause must now
        decide which schema each slot wants rather than inheriting the one the engine knew.

    An unvalidated edge is refused at commitment, not folded as evidence = decision:
      id: x7crwavm
      why: >
        1423-1434 requires a warranty's edge to its warrantor's seat credential to carry DI2I,
        so that "the warrantor holds the seat it claims" is checked by edge validation in the
        existing toolchain BEFORE any fold runs, and says an unseated warrantor's warranty
        "fails credential verification". It then adds the sentence the demo exists to show:
        "That check is evidence the fold consumes, never a verdict: the two currents stay
        unmerged." There are two readings of where the check's result lives. Chose refusal at
        commitment: the constructor validates the edge and declines to commit an endorsement
        whose edge does not validate, exactly as _emit already declines to commit an event
        whose own signature does not verify. Rejected committing the failure as a typed
        evidence fact the fold then reads, which is what the build plan assumed. Two reasons.
        Axiom 2 closes the fold's inputs at COMMITTED values, and a verification result
        computed at presentation time is not one — an engine that folded it would have widened
        the triple by a fourth input nobody committed. And the unseated endorsement is not
        evidence of anything: a credential whose edge does not validate confers nothing, so
        admitting it to the record would mean recording an act that never had authority in
        order to say that it did not. Under refusal, beat 14 shows a commitment that did not
        happen beside a fold answer that did not move, which is the two currents in their
        strongest form — the toolchain's current ran and stopped, and the governance current
        never heard about it. Daniel ruled it tentatively on 2026-09-11, explicitly to see
        whether it becomes uncomfortable; the discomfort to watch for is "evidence the fold
        consumes" becoming a sentence the demo cannot show, and if that bites, the failure
        becomes a committed fact and the slot predicate gains a conjunct.
        The seam grows one verb, verify_edges(sad) -> bool, total and fail-closed like verify:
        an edge naming a far node the substrate cannot resolve, an operator it does not
        implement, and a relation that does not hold are all False, because each of them means
        the same thing — no authority. keripy answers through Verifier.verifyChain, which
        returns the far node's registry state or None and requires the far node to be SAVED in
        the Reger, so a registry-bound issuance now writes the credential to the credential
        store as well as to the transaction log; the facade implements DI2I itself over the
        delegations it recorded, which is one walk up the delegator chain with a visited set.
        Both implement the semantics WebOfTrust/keripy#1564 settled rather than the ones the
        ACDC text alone compels: issuer == issuee satisfies DI2I outright because it is a
        superset of I2I, and the delegation arm admits any depth, each hop requiring the
        delegator to have ANCHORED the delegate's dip. utina's delegate verb already anchors
        (@2a25xudi), which is the half that would otherwise have looked correct everywhere
        except under a real validator.

    A requirement element names the event that closed its cure path = decision:
      id: waihlx27
      why: >
        Issue 82's first two rules, ruled 2026-08-27, are one test read twice: a pending
        finding's requirement space is reachable at a later position only if the clause it
        declared at birth is still the clause in force. Chose to ask it as one comparison —
        the clause SAID at the act's own coordinate against the clause governing that act class
        at the appraisal position — and to carry the amending enactment as the element's GROUND
        where they differ. Rejected a fifth pending species, per determination 1's own
        preference: expired/abandoned already means "cured by re-presentation", and the
        amendment is a committed ground where the species' original eviction receipt is not.
        Rejected putting the ground on the Pending finding rather than on the element, because
        the species is per-element and an element that says "no longer curable" without saying
        what did it is an assertion. The field defaults to empty and stays empty for every cure
        that is just the arrival of missing evidence: an absent slot needs no citation.
        The test is two-thirds of the three Custos describes. Same clause SAID carries same
        requirement space here, because a clause IS its bytes and an edition refuses to rule one
        act class twice, so equal identifiers mean equal slots, weights and schemas by
        construction. The third part, the same pinned lens, is the semantics declaration Acme's
        law does not carry yet (tick 2uhi) — and the asymmetry is safe in the direction that
        matters: a lens that moved could only make a STABLE answer unstable, never an unstable
        one stable, so what the missing third costs is a beat and never a wrong closure.
        Only the pending branch consults it. A finding that reached a terminal value stands at
        its coordinate forever and re-asking it returns the same answer under the law in force
        then, which is the utility claim the demo closes on; rule 1 reaches acts still in flight
        and nothing else. And a proposal can never close, because it is judged under the law at
        the position it is asked from, so the two clauses are the same clause by construction.
        Constitution gains one field for this: the identifier of the law event whose edition it
        is. A finding that says a cure path closed has to name what closed it, and the fold had
        no way to say which enactment that was — it computed the edition and forgot where it
        came from.

    An amendment that declares nothing has declared the empty set = decision:
      id: bvzzaquc
      superseded_by: ow6dzro4
      note: >
        Withdrawn entire on 2026-09-23. The declaration duty this node works out the details of
        is removed by @ow6dzro4, so the two choices below — silence as an empty claim, and
        conviction at the carrying coordinate — decide the shape of a mechanism that no longer
        exists. Kept because it records what was built and why, and because the second choice's
        reasoning about effectuation survives in @xhtvuxnc, which the removal does not touch.
      why: >
        Issue 82's determination 5 makes an amending enactment declare the pending questions
        its change disturbs, has the fold compute the true set from the same committed bytes,
        and convicts the declaration on a mismatch. Two choices fell out of building it.
        FIRST, an enactment carrying no declaration is read as claiming that nothing is
        disturbed, rather than as having made no claim. Chose that over treating silence as
        no testimony, because the alternative guts the mechanism: an amender who could omit the
        field would evade conviction by saying nothing, and the whole point of the declaration
        is that it is a claim a stranger can falsify. The constructor therefore commits the
        field always, including empty. Acme's board-seating amendment now declares the hire
        truthfully, and the demo-1 suite caught its absence the moment the rule landed — D4
        went self-convicted, which is the mechanism working on the first record it met.
        SECOND, the conviction arrives at the coordinate the amendment CARRIES, not at the one
        it is committed at. Nothing is disturbed until an edition takes force, so an enactment
        short of its threshold is simply pending and one that never carries disturbs nothing
        ever (@xhtvuxnc). Measured on a synthetic record: pending, pending, self-convicted, at
        the three coordinates from commitment to unity. Demo 2's beat 22 reads "declared
        affirmed", which is the amender's claim and not the fold's answer; the fold's answer is
        beat 23's, and under-declaring it was never affirmed at any coordinate.
        The value is self-convicted rather than defeated, which is the pinned reading of an
        open question (docs/demo-2-script.md "Open readings", tick 7xe6): the enactment commits
        two things that cannot both be true of one set of bytes, which is 1499-1530's "two
        voices where its constitution demands one". Defeated would say a committed requirement
        was violated, and no clause of Acme's commits one about declarations.
        The proof package is a SHA-256 over both sets in canonical order — rendered sorted
        rather than as declared, because a set is a set and a package that moved with the
        declaration's ORDER would make one falsehood two different proofs. The pair field is
        left empty: the two contradicting commitments are in one event, so there are not two
        identifiers to name, and the ruled payload is the package alone anyway (1659-1660).

    A certification is one GEL event, because only the domain can write one = decision:
      id: qk3kcds6
      why: >
        The build plan called for two committed events per certified act — the sponsor's dossier
        and the domain's admission. That was wrong and the reason is @2e2dncfe's own: only the
        gAID's controller can anchor into the gAID's KEL (`:1114-1120`), so nothing a sponsor
        does can put anything in a domain's log, and there is no such thing as a sponsor's GEL
        event. Chose one event, signed by the domain, carrying the sponsor's dossier ACDC inside
        it with the sponsor's own signature — exactly the shape an endorsement already uses
        (@vi4t4i), so a stranger verifies the tally with KERI tooling and the key log alone.
        Two acts and one event, and the asymmetry is the content rather than an encoding
        convenience: the sponsor's act is real, attributable and signed, and it is not
        consequential until somebody with authority over the log admits it. That is the whole
        claim of @2e2dncfe restated at the level of bytes.
        What the domain checks before admitting is the FLOOR and is deliberately narrow: that
        the weights the dossier cites reach unity. Rejected having the constructor recompute
        which dispositions the clause counts, because that is the fold's question and
        `utina.enact` may not ask it — `tests/test_purity.py` enforces the boundary. So the
        caller supplies what it is claiming and the domain checks the claim, which is also the
        honest division of labour: the sponsor did the legwork and owns what they counted.

    A certification is checked against the whole record, not against its own edges = decision:
      id: epztz4wd
      why: >
        Daniel ruled this on 2026-09-24. Edges prove presence and never absence, so a check
        confined to what a certification cites catches only a sponsor claiming a threshold they
        did not reach — which the constructor already refuses at commitment (@qk3kcds6), making
        that check nearly redundant. The interesting failure is a sponsor who cites AROUND a
        disposition the domain has already admitted: in this model a declination SPENDS a slot
        rather than merely failing to fill it, so omitting one changes the answer and leaves no
        trace in the certification itself. Checking against the record catches it.
        This is what makes the false-certification beat worth showing, and it is also why tick
        4uus matters more than it looked: a certification can only be checked against what the
        domain admitted, so admission discipline is load-bearing for certification's integrity
        rather than a tidy-up.
        Its limit is named rather than left to be discovered, and it is structural: a
        disposition the domain NEVER admitted is invisible to this and to everything else in the
        record, because only the domain can write to its own log. Suppression is not preventable
        — it is evidenceable by a party holding their own log, which is KERI's posture for
        duplicity applied one tier up. Custos has the shape for that at `:2518-2530` and scopes
        it to key state; the governance-tier case has no committed form. Filed as Q36.

    A false certification convicts the question it was supposed to authorize = decision:
      id: 7shpbven
      why: >
        M4's fold half, following @qk3kcds6 and @epztz4wd. A certification is proof rather than
        assertion, so one the record does not support has contradicted itself on bytes its own
        sponsor signed and its own domain admitted — "two voices where its constitution demands
        one" (`:1527-1533`). The finding is self-convicted, carrying a proof package any reader
        recomputes from committed bytes alone.
        TWO INDEPENDENT CONTRADICTIONS, checked in a fixed order because a certification can
        carry both and two verifiers must name the same one. First the certification against
        ITSELF: its cited edges sum to less than unity while it claims a met threshold. Second
        the certification against THE RECORD: the clause's own arithmetic over every disposition
        the domain admitted at or before the certification's coordinate does not reach unity.
        The first is nearly redundant because `enact` refuses to emit one (@qk3kcds6) and is kept
        because the fold may not assume its own constructor wrote the log it is reading — a
        corpus arrives from a substrate, and `Corpus.load` trusts what it is handed (tick 6ofh).
        The second is the one @epztz4wd ruled and the one the beat is worth showing.
        THE CHECK CANNOT LIVE IN THE AFFIRMED ARM, which is the discovery this milestone turned
        on rather than a detail of layout. The dispatch reached the certification path only under
        `satisfied(held)`, so a certification of an act the record DEFEATS returned defeated and
        never looked at the certification at all — and an act the record defeats is exactly the
        case a sponsor citing around a declination produces, since a declination spends its slot.
        The check therefore runs before the threshold dispatch, over every committed
        certification of the subject, whatever the arithmetic says.
        THE PROOF PAIR IS DERIVED, never chosen. Where the record carries a declination that the
        certification did not cite — bearing on the subject, in a slot the governing clause
        counts, committed at or before the certification — the pair is the certification and the
        lexicographic minimum such declination, in the discipline `:1766-1770` applies to
        defeated citations: two verifiers holding the same bundle emit the same finding down to
        the byte. Where there is no omitted declination the contradiction is internal and the
        package alone names it, which is the shape `Proof.pair` was already built to allow.
        THE ORDER AGAINST TAINT SPLITS THE TWO ARMS, and the split is the answer rather than a
        compromise. Taint's SUBJECT arm goes first: a bearing conviction is key-tier, decided by
        KERI's superseding-recovery calculus rather than by anything Acme committed (@yrkrqj's
        consequence, argued at the duplicity node), and a party convicted of speaking with two
        voices poisons every artifact they touched including a certification, so naming the
        duplicity pair is the more informative proof. The false certification goes second.
        Taint's CITED arm goes LAST, because what it returns is pending with a cure — an act
        owned by the party whose conflict it is — and no act by anybody cures a record that
        contradicts itself. Offering that cure path would tell the reader the wrong thing to go
        and do.
        This reverses the first draft of this node, which put all of taint first and recorded
        the cure-path objection as an unexercised rebuttal. The session in bakobo:10 read that
        rebuttal and pointed out it was not a rebuttal but the argument — by Q38's own reasoning,
        a conviction outranks a pending whatever tier it came from, and the SUBJECT/CITED split
        is what lets both claims hold at once. Their own fix landed alongside it: `_tainted`
        returned on the FIRST convicted party it met, so an earlier cited taint hid a later
        subject conviction (@zmlvpkhl). Recorded here because the first draft is on the record
        and a reader of it should know it was argued down rather than drifted from.
        WHAT THIS DOES NOT BUILD. `enact` still refuses to construct an unsupported
        certification, so a false one enters only from a hand-built log or a foreign corpus. The
        fixture beat that shows one (M10) needs a deliberate escape hatch in the constructor, and
        it is not added here: a builder that can emit a false certification by accident is worse
        than one that cannot emit one at all.

    An edition takes force where its enactment was certified, not where its votes reached unity = decision:
      id: pv7a6dhc
      why: >
        Forced by @2e2dncfe meeting @xhtvuxnc, and found while scoping M6 rather than designed.
        An enactment is an act — "a ratification is an enactment, an enactment is judged under
        the Constitution it amends, and the judgment is a finding like any other" (`:214-215`) —
        and an act in a domain whose law requires certification is PENDING until the domain
        admits one. So an edition that took force on a threshold alone would bind the whole
        domain on a judgment the fold itself reports as not yet authorized. The law fold and the
        evaluator would be saying different things about the same event.
        `constitution._effectuation` keyed on `clause.group.satisfied()` alone, which was correct
        while no domain required certification and silently wrong the moment one did. It now
        advances only at a candidate coordinate where the threshold is met AND a certification
        of the enactment has been admitted at or before it.
        A FALSE certification does not effectuate either, for the same reason and one step
        further: a certification the record refutes convicts the enactment (@7shpbven), and an
        edition binding on a self-convicted enactment would be worse than one binding on a
        pending one. The check is the same predicate the evaluator runs, called from here rather
        than reimplemented.
        WHERE THE SCHEMA COMES FROM is the law in force at the enactment's OWN coordinate — the
        law it amends, which is the law that judges it — and never the successor it commits. An
        amendment that introduced a certification requirement would otherwise have to satisfy the
        requirement it was itself introducing. The clause-over-law precedence is `schema_for`,
        moved out of `evaluate` into `fold/certification.py` so that the law fold and the
        evaluator cannot drift on the question of whether this domain certifies at all; it takes
        the clause and the law's default rather than a Constitution, because `constitution`
        imports `certification` and the reverse would be a cycle.
        NO ARTIFACT MOVES TODAY. Acme's law requires no certification until M6 commits one, so
        every existing effectuation coordinate is unchanged and this lands as a fold change with
        synthetic coverage only. That is deliberate sequencing rather than luck: the rule has to
        be in place before the fixture can carry a certified amendment at all.

    A slot is addressed by the seat it is, never by the party currently in it = decision:
      id: qjjlkrxt
      why: >
        A REPAIR, and the defect is worth stating before the fix because it says what @ftjpdph5
        left unfinished. A filled office slot contributed no weight. `Group._where` looked each
        slot's disposition up under `slot.endorser`, which is the empty string on a slot that
        seats an office, while `slots.classify` resolved the office to its holder and keyed the
        mapping by the HOLDER's AID — so the lookup never matched and every office slot read
        PENDING in `satisfied`, `reachable` and `outstanding` however the record actually stood.
        The office machinery was arithmetically inert from the day it landed.
        M2's criterion did not catch it, and that is the lesson rather than the bug. It tested
        that a slot naming an office is FILLED by a qualifying endorsement and unfilled when none
        does — a claim about `classify` — and never once asked what the group made of the
        result. A criterion that stops at the predicate and never reaches the arithmetic can pass
        over a feature that does nothing, which is exactly what happened; it took M6 putting an
        office slot into Acme's real law for anything to notice.
        THE FIX IS THAT A SLOT HAS AN IDENTITY DISTINCT FROM ITS OCCUPANT. `Slot.key` is the
        office where it seats one and the endorser otherwise, and every disposition mapping is
        keyed by it. `SlotDisposition` carries that key beside the `endorser` it reports, because
        the two are genuinely different questions and collapsing them is what caused this: the
        key is which seat this is, stable across a change of director, and the endorser is who is
        in it right now, which is what a screen must show — a filled seat renders as
        `nina-board-seat-3` and a vacant one under the office's own name.
        Rejected keying the mapping by the office name and letting the display derive it,
        because a vacant office and a filled one would then be indistinguishable to a caller
        holding only the mapping, and `outstanding` would name a seat without saying it is empty.
        Rejected passing the classified sequence to `satisfied` instead of a mapping: it is the
        better shape and it is a wider change than a repair should make, since `satisfied_by`,
        the constitution's effectuation walk and two render paths all consume the mapping form.
        Filed as tick-worthy rather than done here.

    An office slot counts who held the seat when they acted, never who holds it now = decision:
      id: djyj2bc2
      why: >
        The second defect the office-slot model produced, found the same way as @qjjlkrxt —
        by putting an office slot into Acme's real law and watching Act III die. Revoking a
        seating retroactively UN-COUNTED every endorsement that seat had ever made.
        `_classify_slot` resolved an office through `_holder`, which asks who holds it at the
        QUESTION's position, and when nobody did it returned pending at once without ever
        looking at whether the seat's committed endorsement had stood when it was made.
        Measured on Acme before the fix: at d5 the office resolves to the seat and the budget's
        seat slot is endorsed; at b16 and b17, with the credential revoked, the same slot reads
        pending and the endorsement is gone.
        THAT IS THE ONE THING CUSTOS FORBIDS BY NAME. "What was affirmed above stands at its
        coordinate forever" (`:1805`), and "the reversal is a new fact, not a rewrite"
        (`:1741`). It also destroys the demo's answer to the 4.1 KERI panel's sharpest
        objection: beats 18 and 19 exist to show that a prospective revocation falsifies
        nothing, because the credential DID stand at the position it was cited from, and under
        the broken reading the revocation reached backwards and unmade the finding.
        THE RULE is the one issue #82's rule 4 already states for a cited credential, applied
        one level out to the seat itself: an office slot counts an endorsement whose issuer held
        the office at the ENDORSEMENT's own coordinate. So the walk resolves the holder per
        candidate event against the bundle up to that event, rather than once against the whole
        bundle. This is the same shape as `_qualified`, which is the point — "did it stand when
        it was cited" is one question the fold should not answer twice differently.
        WHO-HOLDS-IT-NOW SURVIVES, in the one place it is right. Where no committed act counts,
        the slot reports whoever holds the office at the question's position, or the office's own
        name where nobody does — which is beat 17 exactly: a NEW question over a bundle the
        revocation is already in, pending under the seat's own name. So the revocation still
        bites forward and no longer bites backward, which is the whole distinction between a
        revocation and a duplicity taint that the bearing machinery keeps separate elsewhere.
        NOT WIDENED: `seating_is_ambiguous` still asks at the question's position, so an office
        contested only in the past is not caught and `_holder` takes the first of two. That gap
        predates this and is left where it was rather than half-closed here.

    The meanwhile card is a COMMAND, and it shortens the run = decision:
      id: eelnh6dn
      why: >
        M9. Between two marked beats the record commits events the room never sees, and
        the narrator was covering them in speech — which is the expensive medium. Daniel
        corrected an earlier reading of this milestone that had it LENGTHENING the live
        run: the room reads a screen faster than it hears a sentence, so putting the span
        on screen buys narration time back rather than spending it.
        IT IS A CLI COMMAND AND NOT A CARD THE DRIVER PRINTS, which is forced rather than
        chosen. `utina.cli.demo2` computes nothing (@cldemo, and `test_the_demo_driver
        computes_nothing` enforces it): a beat is a title, a narration and an argv, and
        the walk dispatches through the same entry point a shell reaches. A card the
        driver assembled from the corpus would make the driver a second reader of the
        record, and the demo's own claim is that every screen is one a person could have
        produced by typing. So `utina meanwhile --from <label> --to <label>` is the
        screen, and the driver emits its argv between beats like any other command.
        WHAT IT SAYS, and the third part is the one that is not obvious. The count and
        the events, so nothing between beats is hidden. The certifications among them
        named as such, because after M6 every affirmation rests on one and a room that
        never saw them would think an endorsement authorized something. And that the
        position labels are OURS: `d1` and `b17` are this demo's names for coordinates
        and are committed nowhere — the record has sequence numbers. Saying so on the
        screen is cheaper than saying it once in narration and hoping it is remembered,
        and it is the same disclosure the alias header already makes about party names.
        THE SPAN COMES OFF THE BEATS' OWN ARGV rather than from a second field naming it.
        A `--at` duplicated into a `Beat.at` would be two literals that can disagree, and
        the failure mode is a meanwhile card describing a span the beat is not asked at.
        Beats with no `--at` — beat 14's enact, which is a refusal — carry the previous
        beat's coordinate forward, because no coordinate is where the question is asked.

    The sequence diagram is COLLAPSED, and it is generated rather than drawn = decision:
      id: y7ytqzyj
      why: >
        M11. A reader who was not in the room gets the transcripts and the script, and
        neither shows the SHAPE of the thing — who spoke to whom, in what order, across
        four acts. A sequence diagram does that in one screen. Mermaid because GitHub
        renders it inline, so the artifact is readable where the repo is read and needs
        no toolchain to view.
        COLLAPSED, EXPLICITLY NOT 49 MESSAGES. One participant per party, one message per
        MARKED beat, and the events between beats as notes. The full-fidelity version was
        considered and rejected: at one message per committed event it is 49 arrows, which
        is unreadable on a projector, unreadable in a PR, and says less than the log
        already says in a table. The value of a diagram is exactly the compression — a
        reader who wants every event has `utina log`, and a reader who wants the shape
        has this. A diagram that tried to be both would serve neither.
        GENERATED BY `tools/render-demo-2.py` AND PINNED, on the reasoning that already
        governs the other four artifacts: a hand-drawn diagram is a second account of the
        record that drifts silently, and the last thing this demo needs is a picture that
        disagrees with the transcripts. Generated from `demo2`'s own KERNELS and the
        record's labels, so it cannot name a beat the driver does not have or a
        coordinate the record does not carry.
        PARTIES ARE ALIASED, never identified, for the reason every screen is (@clcoia):
        a diagram is read at a glance and a glance is exactly when a truncated identifier
        does its damage. The domain is a participant like any other, because after M6 it
        is the one that certifies and the diagram's most surprising message is the one
        that goes to it and comes back.

    The false certification is an INFLATED weight, and it needs no escape hatch = decision:
      id: t3kuqli6
      why: >
        M10, and it turned out smaller than @7shpbven predicted. That node said the beat
        would need "a deliberate escape hatch in the constructor", because `enact.certify`
        refuses a tally whose edges fall short. It does not need one: the constructor's
        check is that the CITED WEIGHTS sum to unity, and a sponsor who cites one
        endorsement at 1/1 instead of the 1/2 its slot commits passes that check exactly.
        The dossier is well-formed, the domain admits it, and the record refutes it. So
        the builder stays incapable of emitting a tally it knows to be short, which is
        the property worth keeping (a builder that can lie by accident is worse than one
        that cannot lie at all), and the beat is committed by an honest verb.
        THAT IS ALSO THE BETTER STORY. The domain's admission check is the floor — edges
        sum to unity — and the domain does not re-fold its own record before admitting.
        The beat is therefore not "somebody bypassed a check" but "the check that exists
        is not the check that matters", and the fold is what makes the sponsor
        accountable afterwards. Marta, sponsoring, cites her own endorsement at full
        weight and omits Dev's signed no; any reader who folds the record convicts her on
        her own signature, which is @epztz4wd's whole argument on screen.
        WHERE IT SITS, and every part of this is forced. It is the LAST act in the record,
        after the duplicity observation, so no existing coordinate moves and beat 22's
        dependence on that observation being last is untouched. It is a second tabling of
        the founders' equity act, under clause A3, because A3 is the one clause neither
        amendment moves: under the LOWERED B1 every slot is worth unity on its own, so a
        single endorsement would make the certification SOUND and there would be no lie
        to show. And it involves seat 3 nowhere, because a convicted cited party fires
        the taint succession instead and the beat would show beat 20's screen twice.
        DEV'S DECLINATION IS WHAT POPULATES THE PROOF PAIR. Without it the contradiction
        is internal and the package stands alone; with it the finding names both halves,
        which is the screen worth having — a reader sees the certification and the
        declination it was written around, side by side.
        IT IS NOT IN `CUT_ORDER`. The cut list is what to drop when the clock runs out,
        and this beat restores the fourth verdict that removing the declaration duty took
        off the demo (@ow6dzro4). Cutting it costs a quarter of the codomain.

    A law that names a schema is held to it, and a gloss that cannot read a kind says so = decision:
      id: 45pjebk4
      why: >
        Five findings from the review round on PR #9, all five valid, and two of them
        correctness rather than tidiness. Recorded together because they share one shape:
        a check or a claim that was written and then not actually applied.
        THE FAIL-OPEN IS THE ONE THAT MATTERED. `certifying` located a certification by
        kind and subject and never compared the credential's schema against the one the
        law names — so a tally issued against ANY schema discharged the requirement, was
        accepted as sound by the falsity check, and could effectuate an enactment. This
        module's own docstring cites `:1946-1951` for why a slot commits its schema — "a
        requirement that could not say which evidence it wanted would be satisfiable by
        the wrong one" — and then the certification field was read and not checked. The
        schema is now a required argument at every call site rather than an optional one,
        because a default would have let the next caller reintroduce exactly this.
        A WRONG-SCHEMA EVENT IS NOT A LATE CERTIFICATION. "The first rather than the
        last" is a rule about two tallies this law would accept; an event against another
        schema is not a certification under this law at all, so it is skipped and a later
        valid one still discharges. A check that stopped at the first kind-and-subject
        match would have let a wrong-schema event SHADOW a valid one by arriving first,
        which is a second fail-open wearing the first one's clothes.
        THE SEAT COLLISION IS @qjjlkrxt ONE LAYER UP, and it is the same lesson twice in
        one PR. `Group.__post_init__` deduplicated slots by `endorser`; every office slot
        names the empty string, so a law with two distinct offices — or one office beside
        a directly-entitled party — was refused as a duplicate before it could be folded.
        Acme has a single office, so nothing exercised it, and M7's second domain would
        have met it immediately. The error is renamed to say seat rather than endorser,
        because the message a reader gets is part of the fix.
        A GLOSS THAT GUESSES IS WORSE THAN ONE THAT SAYS NOTHING. The log screen's
        fall-through rendered any unreadable kind through the disposition path. An earlier
        pass at this guarded on an EMPTY attributes block, which caught the certification
        and the duplicity observation and missed the issuance — an issuance has a
        non-empty block — so `acme-governed-domain,6 declines None` shipped in the tracked
        transcripts six times over. Now every kind is named explicitly and the
        fall-through is the em dash. The near-miss is the point: a fix aimed at the
        symptom rather than the branch left two thirds of the bug on screen.
        THE ISSUANCE ROW DOES NOT REPEAT THE OFFICE, though the row is about an office
        being filled. A COIA alias already carries its holder's role, so
        `nina-board-seat-3,6` names the seat in the same breath as the person; naming it
        again pushed the row to 105 columns against the projector's 96 for no information.
        TWO HARD-CODED COUNTS were stale on the day they were written — a docstring saying
        forty-nine over a record of fifty-three, and "the live thirteen ... the four
        leave-behind beats" written into a GENERATED artifact that beat 26 contradicted
        immediately. Both are derived now. Committing a literal count inside the generator
        is the worst available place for one: the generate-and-pin arrangement exists
        precisely so a stale number cannot survive a rebuild, and this one was upstream of
        the mechanism that would have caught it.
        THE FIX DIFF WAS REVIEWED BY A NON-CLAUDE SEAT before it was committed, and that
        paid: `ds` accepted four of the five fixes and found the wrong-schema test asserted
        something weaker than the finding it was meant to pin — it committed one bad
        certification and asserted pending, which passes against an implementation that
        merely ignores the bad event, there being nothing else to find. The shadowing case
        above is that criticism. It also observed that "first" depends on an ordering this
        function does not itself enforce; it holds because `Corpus` enforces it, and the
        docstring now says which.

    The law creates a seat; a credential fills it = decision:
      id: ftjpdph5
      why: >
        Daniel, 2026-09-23: "We have to change the law to create a board seat. We don't change
        the law to fill the seat." A slot may therefore commit an OFFICE and no AID at all, and
        the fold resolves who fills it by asking the record for a standing credential of the
        slot's qualification seating somebody there. Creating the seat is an amendment, filling
        it is an issuance, vacating it is a revocation, and only the first touches the law —
        which is what stops a change of director from being a constitutional matter.
        This is smaller than it sounds because `Qualification` was already most of the way
        there: its own docstring said a slot carrying one "names an office, whose holder acts
        because a credential says so". What it did NOT do was let the law stop naming the
        office's AID, so personnel and law were still welded together. The office label itself
        already existed too, as `SEAT_OFFICE` in Acme's law, described there as "a label for a
        reader; nothing computes over it". Now it does.
        THE OFFICE IS IN THE CLAUSE'S CANONICAL BYTES, for the reason the slot schema is: a slot
        that seated a different office is a different slot, and a head that could not tell them
        apart would let an amendment move authority from one seat to another in silence. The
        parts are appended only where a slot seats one, so every existing law head is unchanged.
        A SLOT NAMING BOTH A PARTY AND AN OFFICE IS REFUSED rather than reconciled. It would be
        saying who fills a seat that a credential is supposed to fill, and guessing which half
        was meant is exactly what the fold does not do.
        TWO HOLDERS OF ONE OFFICE IS A REFUSAL, not an adjudication. MxN commits "exactly N
        slots, one per candidate endorser", so two standing seatings break the operator
        structurally; nothing committed says which supersedes, and a fold that picked one would
        invent the rule it exists to apply. The refusal names where the defect is fixable — in
        the registry, by revoking one. Daniel corrected an earlier and over-general version of
        this rule that would have applied to every office: a body whose membership is open-ended
        and whose count moves is not this defect, it is the dossier's MxQ operator, which utina
        does not implement (tick 5psg). Two credentials naming the SAME holder are one holder,
        so reissuing a seating to a sitting director is not a contested seat.
        A VACANT OFFICE IS PENDING UNDER ITS OWN NAME. "board-seat-3, pending" tells a reader
        what to go and do; an empty endorser column does not. Beat 17's screen has been claiming
        exactly this since the revocation landed, and now it is true by construction rather than
        by an AID whose qualification happens to be gone.

    A decision is consequential when it is certified, not when its votes are cast = decision:
      id: 2e2dncfe
      why: >
        Daniel's, 2026-09-23, and the argument is an analogy that holds all the way down: an
        election is not consequential when votes are cast, nor when a pollster guesses at them,
        but when they are officially tabulated and certified. The fold was treating the existence
        of endorsement ACDCs as the result. It was reading the polls.
        WHAT THIS MILESTONE BUILDS is the fold's half only: where a law requires a certification
        and none has been admitted for a subject whose threshold is met, the finding is pending
        with a requirement element of kind `certification`, and the act is authorized when the
        domain admits one. The element names the party that committed the subject, because
        admitting a tally is the domain's act and nobody else's — a sponsor may assemble a
        certification and cannot make it consequential.
        A DOMAIN SAYS WHETHER IT WANTS ONE, by naming the schema its certifications must satisfy,
        exactly as a slot names the endorsement schema its evidence must satisfy (1946-1951). A
        law naming none requires none. THE CLAUSE DECIDES AND THE LAW IS THE DEFAULT — Daniel's
        refinement the same day: how much ceremony a decision needs is a fact about the KIND of
        decision, and minuting a board resolution and approving a routine purchase are not the
        same act wearing different clothes. A clause may be silent and inherit, pin its own
        schema, or commit `false` and say its acts stand on their arithmetic. What it says is in
        its canonical bytes, for the reason the slot schema is: a head that could not tell an
        exempt clause from a silent one would let an amendment exempt the acts it cared about
        without moving the law head. The absent case emits nothing, so no existing head moves.
        Two fail-closed readings fall out. An unreadable certification field INHERITS rather than
        exempts, because a malformed field must not be a way out of a requirement. And loosening
        is safe despite being the obvious abuse — a clause exempting the most consequential acts
        cannot be smuggled in, since an enactment is judged under the law it replaces, so
        committing that exemption is itself an act the predecessor governs and certifies. Chose that over making certification unconditional, and
        the reason is not migration convenience: whether decisions in a domain need certifying is
        a governance question, and Custos already delegates this kind of committed form to the
        domain — :1924 does it for expiry semantics. It also lets Acme keep working while the
        rest of the mechanism lands, and lets a later beat show a domain that has adopted it
        beside one that has not.
        NOTHING IS COINED. The dossier specification already has this machinery: joint issuance
        defines a finalization event, an `fi` field naming the AID whose KEL carries it, and a
        finalizer who "observes the threshold to be met" and anchors the threshold-satisfying
        proofs where a verifier can find them (dossier-spec-body.md:377-379). There it is
        advisory — an aid to verifiers who would rather not walk the edge graph. The change is to
        make it constitutive, which is a smaller and better-founded amendment than a new concept.
        WHAT IS DEFERRED, and named so it is not mistaken for settled. Whether a certification's
        edges actually support its claim, and what the domain must check before admitting one,
        are M3 and M4. The certifier is not merely asserting — the dossier carries an edge per
        counted disposition, so a verifier recomputes the threshold and a certification claiming
        more than its edges support contradicts itself on bytes its own signer committed — but
        none of that is enforced yet. Also open (Q-YHJA): whether the fold checks a certification
        against its cited edges alone or against the whole GEL. Edges prove presence and never
        absence, so a certifier citing around an admitted declination is invisible to the first
        and caught by the second.
        A COST TAKEN KNOWINGLY: the first certification of a subject wins, not the last. A
        coordinate that moved when a later event arrived would make the moment of authorization a
        function of when the question was asked, which is the property this whole change exists
        to fix.

    An amendment declares nothing, because the declaration changed no outcome = decision:
      id: ow6dzro4
      why: >
        Daniel ruled this on 2026-09-23, and the ruling is one sentence: an obligation that
        changes no outcome is not one governance should impose. The `disturbs` field, the
        mismatch check, and the self-conviction it produced are all removed. What stays is the
        substantive rule — a clause change ends the acts pending under that clause, and the fold
        computes which — which never depended on the declaration and is keyed on the discharge
        species instead (@f3pmxu3x).
        Three things grounded the ruling, and the first is the one that decided it. The declared
        set was read in exactly two places: the mismatch check, and the screen that drew it. It
        gated nothing. The law changed identically whether the field was accurate, wrong or
        absent, so the field existed for no purpose except to create something that could be
        false. The argument for it — the computation is the check and the declaration is the
        claim — is an argument for manufacturing a catchable lie, and that is not a governance
        requirement.
        SECOND, the analogy it rested on does not hold. KERI duplicity is one signer contradicting
        themselves, both halves inside their own knowledge and control. Here the fold computes the
        true set at EFFECTUATION (@xhtvuxnc) while the amender declares at commitment, and any
        party may table an act in the window between. Demonstrated on a built record rather than
        argued: two runs whose only difference is a bare act tabled by somebody else, nobody
        endorsing it, with the amender's own committed events byte-identical across both —
        affirmed in one, self-convicted in the other. An honest amender cannot always discharge
        the duty, which is disqualifying for a duty whose breach was a conviction.
        THIRD, none of it is ratified. "Disturb" appears nowhere in custos-4.2.md; the mechanism
        comes from issue 82's determination 5 and from docs/custos-proposals.md R3, and the demo
        presented it as conformance. Rejected keeping it behind narration that called it a
        proposal, because the beat's whole force was that a stranger can compute the lie, and a
        stranger computing it against an unratified rule proves nothing about Custos.
        Consequences taken knowingly. Beat 22 was the only beat of the thirteen that produced a
        self-convicted verdict, so the demo loses one of the four values unless it is shown
        another way — and it can be, on the ratified route (:1527, :1659, and the affirmed to
        self-convicted edge at :1672): a duplicity observed at the party who COMMITTED the
        subject act convicts the act, and Acme tables every ordinary act itself. Verified before
        the cut, not after. The disturbance screen survives with its declared column removed,
        which turns it from an accusation into a report of what an amendment ended.

    COIA is vendored from upstream at 2.0, not reimplemented = decision:
      id: 67t6q43c
      why: >
        utina carried its own 493-line COIA 1.x implementation with a 463-line hand-written test
        of it. Daniel ruled the cutover on 2026-09-23. Chose to VENDOR the upstream reference
        implementation byte for byte — coia.py and its tables.json from the spec repo, plus that
        repo's normative vector file — rather than port our own forward. The vectors are the
        argument: their own header says they were authored from the specification's prose and not
        from any implementation's output, six implementations in six languages are held to them,
        and a local variant would be the seventh that nobody checks. A test asserts byte-identity
        with the upstream checkout and skips where that checkout is absent, so a contributor
        without it still runs the 139 vectors that travel with this repo.
        THE BUG THIS FOUND, and no test of ours could have: every alias on every screen carried
        flag 9. Under 1.x that meant a test environment. Under 2.0 it means "compromised —
        positive evidence that the wrong party controls it", so the demo was announcing that
        every party in it had been captured. Our tests agreed with our implementation and both
        were wrong together. CHANGES.md names this as the one flag that inverts across the
        boundary rather than merely being lost. The test flag in 2.0 is 6.
        Three consequences taken with it, because the aliases had to be reminted anyway.
        The SEAT is Nina's — the alias moves from acme-as-board-seat-3 to nina-board-seat-3-acme
        — on the reading that "the organ's AID" at custos-4.2.md:2145 means an AID its holder owns
        in that capacity, which is Provenant's own role-dedicated-AID model. No spec amendment is
        needed and the record finally names an accountable human: duplicity at that AID is Nina's
        rather than an abstraction's. QUINN becomes Acme's CFO, because beat 14 refuses him and a
        refusal only teaches where the refused party had a plausible claim — a stranger turned
        away surprises nobody, a CFO who cannot approve the budget makes a room ask why, and the
        answer is that he prepares it and the board approves it. And Nina's separate personal AID
        is DELETED: it committed nothing, it existed only because the seat used to be Acme's, and
        the facets of her life this record has no business with are not this record's to model.
        Costs accepted. The vendored module is exempt from mypy's strict mode and from two ruff
        rules, because correcting somebody else's reference implementation is the failure being
        avoided; the typed boundary is crossed at one wrapper. It is omitted from the coverage
        gate for the same reason — its oracle is the vector file, not this repo's branch counter.
        The slot column widens from 18 to 20, since nina-board-seat-3,6 is nineteen.

    Authority comes from a revocable credential, never from the delegation relationship = decision:
      id: cglayqvw
      why: >
        Daniel ruled this on 2026-09-11, against the position I had reached, and the argument is
        his: a delegator and a delegate standing in a relationship whose ilk is delegation proves
        that a RELATIONSHIP exists and confers no authority whatever. A president may delegate an
        identifier for greeting schoolchildren and another for negotiating arms-reduction
        treaties, and KERI cannot tell them apart — both are a dip naming a delegator and an
        interaction event sealing it. The conferral of authority is a separate artifact, and in
        Bakobo's stack that artifact is the GCD (bakobo/schema), an ACDC expressing a delegate's
        authorizations, constraints and duties. So a seat does not hold governance power because
        it is delegated from the gAID; it holds it because a credential says which power it
        inherited, and that credential is revocable.
        Three things fall out, and the first two correct what I had built toward.
        FIRST, tick 3un3 is settled and its beat-15 slot rule is dead in both of its forms. I had
        proposed that an endorsement fills a slot if it CITES a qualification whose issuee is the
        slotted endorser; Daniel's objection was that naming a SAID in an edge is a claim anybody
        can make. I then proposed keying on the KERI delegation, committed as a governance event.
        Rejected: the relationship confers nothing, so a fold reading it would be reading a fact
        that does not bear on authority at all — a subtler error than the citation one and harder
        to see. The predicate keys on a standing GCD whose issuer is the slotted endorser and
        whose issuee is the acting AID, found by SEARCHING the record rather than by following a
        citation the acting party wrote. Nothing the endorser says about itself enters.
        Also rejected, and worth recording because it was the previous session's lean: an IPEX
        presentation transcript anchored in the record, with a pre-committed nonce converting
        "the nonce was novel" into "the challenge's coordinate precedes the grant's". It works,
        and it answers a question nobody here is asking — a presentation proves the presenter
        controlled signing keys at the presentation's coordinate, which the endorsement's own
        signature already proves at its own. And @2a25xudi's accepted tradeoff is fatal to it as
        a DEMO: every party's keys come from one salt in one keystore, so a live presentation
        here is the keystore proving something to itself. Recorded as the destination for real
        custody, built now for nothing.
        SECOND, revocability is now uniform and the KERI side's inability to un-delegate stops
        mattering. Measured on the pinned keripy: only dip and drt carry a delegator
        (core/eventing.py:2819-2827, whose else branch reads "not delegable event icp, rot, ixn"),
        so a delegate's interaction events need no approval ever and utina anchors a credential in
        an interaction event; a drt needs the delegate's own signature as well as the delegator's
        seal (:3224-3226), so a delegator holding none of the delegate's keys cannot rotate it to
        null; superseding recovery rule B (:3175-3199) lets a delegator choose between competing
        delegated rotations but not author one; and there is no un-delegation concept in the
        library at all. The relationship is permanent — di is written only into a dip
        (:676-677), a drt takes its delegator from kever state (:2825), and the prefix is a digest
        over the dip including di. All of which is harmless once authority lives in the
        credential, because a frozen delegate holding a revoked GCD is signing events no fold
        counts. Revocation state answers the whole question, through the machinery U2.1 and U2.2
        already built: stood_at, at the citing coordinate.
        THIRD, what the fold may gate on. presentsAs is NOT it, and this corrects a claim I made
        to Daniel: gcd.schema.json:113 says "presenting-as without this granted capability is
        impersonation", but index.md:78 says "the facet is descriptive; only constraints gates the
        authorization decision", rule 1 says "nothing outside constraints constrains", and
        schema/this.i's facet node says the facet is "descriptive accountability a verifier MAY
        ignore for the authorization decision". The rules win over the field description, the
        contradiction is filed as bakobo/schema#3, and presentsAs becomes a display fact for the
        seat screen. Gating on the credential's own i and a.i is stronger anyway — identity rather
        than metadata.
        Version is gcd-2.0.1, EAqOeo_YMHDEMZ-dIJTYd72nsoUS-C1RdXtOdfAj7ZxR, and it is forced
        rather than preferred. The current GCD is 3.1.x, which requires rd and the ACDC v2
        envelope with v2 most-compact SAIDs; keripy's credential path builds only the v1 envelope
        (vc/proving.py:19-50), the acm ilk reaches no further than core/serdering.py, and
        @exy3u4t7 already measured that keripy's v2 defaults raise. index.md calls 2.0.1 "the same
        semantic content on the v1 envelope", so this is a published GCD with a real SAID and not
        a lookalike. When keripy grows v2, the pin moves and the record churns again.
        Constraint scope: Acme's GCDs carry acts and nothing else. GCD's rule 1 makes an
        unrecognized key inside constraints fail-closed — "a verifier that does not recognize it
        MUST assume that constraint is unmet and MUST deny" — which is the slot predicate's own
        posture (fold/slots.py:33-37) arriving from the other direction, so the rule and the
        engine already agree and the predicate denies on any constraint key it does not implement.
        utina implements acts, the effect x state-kind grid, because it is string parsing over
        committed bytes with no KERI and no clock in it. Rejected implementing validFrom and
        validUntil, which need a clock: a wall clock is exactly the ambient input axiom 2 forbids,
        and judging them against the citing event's own committed dt is arguable but unruled, so
        Acme's GCDs carry neither field and the question does not arise here.
        FOURTH, learned from the toolchain during the build rather than reasoned to in advance,
        and recorded here because it changes who may revoke what: A CONFERRING PARTY NEEDS A
        REGISTRY OF ITS OWN. The seat's grant to Nina's device was first issued into Acme's
        governance registry, and under keripy it stayed in escrow and read as unissued — a
        transaction event log takes its authorization from a seal in the CONTROLLER's key log,
        and the seat is not Acme. The facade, which keys state on a pair rather than on an
        anchor, accepted it and said nothing, so this is a case of the real substrate catching
        what the fixture could not. The governance argument is better than the mechanical one
        and is the reason this is the shape rather than a workaround: revocation authority
        follows the registry's controller, so a grant the seat kept in Acme's registry would be
        one the seat itself could never take back, which is the whole property the adoption
        exists to secure. So open_registry takes a controller, revoke takes one, and the
        constructor holds a registry per party instead of one for the domain. Acme still
        revokes the seat credential it issued (beat 16) and the seat revokes the device grant it
        issued, which is the same rule applied twice rather than a hierarchy.
        Tradeoffs accepted, all three real. Every identifier in the record moves again, on the
        artifact carrying beats 8, 12, 16, 17 and 19, sixteen days from the demo. utina takes a
        cross-repo dependency on bakobo/schema's published SAID, which is a thing that can move
        under it. And utina evaluates a small fraction of GCD's constraint surface, which is
        honest only because the fold denies the rest rather than ignoring it — an engine that
        carried a GCD and silently skipped its constraints would be the "looks like verification
        and is not" failure this whole line of reasoning exists to avoid.

    A slot names what its endorser must hold, not only what its evidence must be = decision:
      id: y76zc4bz
      why: >
        Recorded AFTER the code commit it justifies (d12ddb8), which inverts this repo's own
        discipline. Saying so rather than back-dating it: the decision was Daniel's, made in
        conversation on 2026-09-11, and the node is late because the build ran straight from his
        ruling into the change. The ordering rule exists so that a decision is reasoned about
        before it is implemented, and here it was — in chat, on tick 652c — but the artifact
        that is meant to be the source of truth trailed the code, and that is worth one sentence
        of honesty in the tree rather than a tidy history.
        THE DEFECT. Measured on the record after beat 16 revoked the seat credential: the seat
        endorsing while CITING the revoked credential was committed and not counted, and the
        seat endorsing while citing NOTHING filled its slot and the finding was affirmed. So
        revoking the credential custos-4.2.md:1420-1425 calls standing-conferring conferred no
        standing the fold checked. _fills short-circuited when the actor was the slot's own
        endorser, and an act citing nothing was qualified trivially, so the only check on an
        office's standing was one the office opted into by volunteering a citation. Beat 17's
        "seat 3 unfilled" was true only because the record happened to have the seat not acting,
        and a viewer asking "what if it endorses anyway?" would have got affirmed. Act III would
        have been theatre.
        THE CHOICE. A slot gains a second committed term, the credential its ENDORSER must be
        standing on, distinct from the schema its EVIDENCE must satisfy (@z373ew7j committed the
        first; this is the second and they are easy to collapse). Absent for Marta and Dev, whom
        the law entitles directly. Present for board seat 3, which is an office and whose holder
        acts because a credential says so. Section 9 delegates exactly this to the domain —
        "which schemas, issued by which registries, confer which powers" (1924) — so this is
        committed law the fold reads rather than an engine rule, which is the same argument
        @z373ew7j made for the evidence schema.
        Rejected leaving it, which was my own lean for the schedule: the credential is called
        standing-conferring in the ratified text and a credential that confers no standing is a
        prop. Rejected inferring it from delegation — the seat is a delegated AID and the
        founders are not — because key events are out of the corpus (@jdie6v) and because a
        delegation relationship confers nothing anyway (@cglayqvw), which is the error this
        whole line of work exists to stop repeating.
        The ISSUER is committed alongside the schema, and this is the half that would be easy to
        drop. A schema alone lets anybody confer the power: a stranger issues a credential of the
        right shape naming the office as issuee, into a registry of their own, and seats
        themselves in somebody else's Constitution. The issuer is named rather than the registry
        because a registry's identifier does not exist when the law requiring it is written —
        Acme opens its governance registry after the amendment that seats the board — and the
        fold resolves the registry out of the issuance itself.
        TWO THINGS THE BUILD FORCED, neither foreseen, both kept because they are true.
        FIRST, A REVOKED CREDENTIAL CANNOT BE REISSUED. Act IV needs the seat voting, so the
        office had to be re-seated; the obvious re-seating produced bytes identical to the
        revoked credential, which means it WAS that credential, and keripy refused the duplicate
        iss by name. That is the correct answer and the facade would have accepted it silently —
        the second time in this build that the real substrate caught what the fixture could not.
        A fresh appointment is a fresh credential, so the seam takes ACDC's salty nonce, pinned
        like the salt and the registry nonce (@7jrbt3, @exy3u4t7) because a generated one would
        put wall-clock randomness into committed bytes and end the replay claim.
        SECOND, _disturbed_by was counting acts that were ALREADY closed. "In flight" means the
        cure path was still open, not merely that the act was pending. Without that, every later
        amendment inherits every earlier amendment's disturbances, the declared set grows without
        bound down the chain, and an amender is convicted for failing to declare a question
        somebody else's amendment already killed. Acme's own record showed it: the hire has been
        expired/abandoned since the board-seating amendment and the second amendment disturbs it
        not at all. This is a correctness fix to U3.3 and it would have been invisible until a
        third amendment existed.
        Tradeoffs accepted. Every clause's bytes move, so every identifier in the record moves
        for the third time this build, and the committed d3 rendering and the CLI's pins were
        regenerated with it; demo 1's nine verdicts are unchanged, which is the gate that
        matters. Acme's record gains a re-seating beat the demo-2 script does not have, and it
        is the honest consequence of making a revocation bite: an office whose credential is
        gone is not an office until one is issued again. And beat 23's computed disturbance set
        has three members where the script expected two, because demo 1's retabled budget is
        pending under B1 as well — the lie is larger than the script anticipated rather than
        different in kind.

    Duplicity at a cited third party taints the voice, and does not convict the question = decision:
      id: f3pmxu3x
      why: >
        Beat 20 re-asks beat 12's question over a bundle carrying duplicity at board seat 3's
        signing position. docs/demo-2-script.md expects SELF-CONVICTED and says duplicity "does
        reach back". Daniel ruled on 2026-09-15, after the four governing spans were read back
        to him, that the value is PENDING with species unresolved-conflict, reaching forward.
        The fixture does not move; the expected value does.
        WHY THE SCRIPT'S READING IS REASONABLE, recorded because it nearly went the other way.
        The transition table at 1672 permits the edge in as many words — affirmed to
        self-convicted, "a contradictory pair bearing on the question enters the bundle" — and
        1706 says affirmed and defeated are final "except for one event: the arrival of a
        contradictory pair bearing on the same question, which moves either to self-convicted".
        Read alone, those two sentences settle it for the script.
        WHY THEY DO NOT. Both turn on BEARING, and the paragraph immediately after the table
        defines it and then routes it: "The convict's role dispatches the edge: a convicted
        subject fires the edge into self-convicted; a convicted cited third party fires the taint
        succession of the duplicity section — the finding's voice is poisoned, not the question"
        (1689-1694). So the table row is the SUBJECT case, and a document that states an edge
        before it states the edge's condition is a document that will be misread in exactly this
        direction. Beat 12's subject is the budget act, committed by the gAID (propose emits
        under self.gaid); seat 3's endorsement is the affirmation's GROUND. Third party, so the
        role dispatches to taint. The succession rule closes the loop: a successor may reverse a
        terminal value only on evidence falsifying a cited ground, "an undercut, computable
        through the bearing rule" (1734-1740), so the undercut inherits the same dispatch.
        WHAT TAINT YIELDS (1805-1813): "what was affirmed above stands at its coordinate forever.
        The taint's consequence is a succession: at the next position the fold returns pending
        with the taint as its typed requirement, species unresolved-conflict — no missing bytes
        cure a taint, no log growth cures it; only a committed act owned by the party whose
        conflict it is."
        THE BEAT LOSES NOTHING, which is what made the ruling cheap. What beats 18, 19 and 20 are
        built on is that re-asking after a revocation gives the SAME answer and re-asking after
        duplicity gives a DIFFERENT one. Under taint the re-ask returns pending/unresolved-conflict
        where beat 19 returned affirmed, so the answer still moves; "does reach back" was loose for
        "the same question now answers differently". And even the script's own reading would not
        have rewritten beat 12, because 1741 says "the prior finding stands at its coordinate, and
        the reversal is a new fact, not a rewrite". Only the verdict word changes. The demo gains
        the one pending species it otherwise never exercises — beats 3, 5, 10 and 17 are all
        absent and beat 9 is expired/abandoned — and gains the sharpest sentence in the section
        with it.
        Rejected moving the duplicity to the gAID's signing position, which would make
        self-convicted correct: it means Acme signing two conflicting budget acts, which is a
        different story, it discards the third-party distinction entirely, and Act IV already
        shows a self-conviction on an amendment's own bytes.
        THE CONVICTION IS KEY-TIER AND THE FOLD CANNOT RUN IT, which decides the shape of the
        machinery rather than being an aside. 1680-1683: a conviction is conviction-grade at the
        registry and governance tiers "only within frames that committed the violated predicate —
        no committed predicate, no conviction, and the pair is ordinary evidence to consume".
        Acme's law commits no predicate about signing duplicity, so the conviction can only be
        key-tier under KERI's superseding-recovery calculus, and no plane above the substrate may
        import a KERI library (@yrkrqj). So the record carries a committed event recording that
        duplicity WAS OBSERVED, and the fold consumes that as evidence rather than computing the
        conviction itself. That is the same posture the fold already takes toward signatures —
        a committed event is one the substrate verified (fold/slots.py) — and it is stated here
        rather than discovered, because "the fold reads that a conviction happened" is a weaker
        claim than "the fold convicts" and the demo must not blur them.
        The bearing machinery is its own module and shares no code path with revocation. Issue
        82's determination 4 asks specifically that an implementation "make the two unmistakable
        in the bearing machinery", and the two are genuinely different: a revocation moves what a
        registry says about a credential and reaches no finding backwards or forwards, while a
        taint poisons a party's voice from the observation onward and cannot be cured by evidence
        at all. Sharing a path would make that a coincidence of layout rather than a property.
        One repair rides along. _closed() tested whether a requirement element carried any
        ground, which was written when the only closed cure path was an amendment's. A taint also
        names a ground, so the test now keys on the species that actually means it,
        expired/abandoned. Equivalent today and correct once a second kind of ground exists —
        without it a tainted act would read as newly disturbed by whatever amendment came next.

    A convicted subject is convicted even while its slots are still open = decision:
      id: zmlvpkhl
      why: >
        When a subject is convicted by a bearing pair at or before the position and some slot of
        the governing clause has no disposition, the fold returns self-convicted, not pending.
        This was already the behaviour — the bearing walk runs after the requirement space is
        built and before any verdict is chosen — but it was the product of where one call sat,
        not a recorded reading, and an outside comparison found a second engine returning
        pending on the same case, both citing custos-4.2.md:1753-1762. Recorded as Q38.
        Chose conviction-wins. The transition table's condition for pending to self-convicted
        (1664-1671) is the pair entering the bundle; under pending-wins the pair enters and
        nothing moves until the last missing endorsement arrives, which the table does not name.
        A pending finding names its cure (1575), and here the cure it would name is false: the
        missing endorsements arriving does not bring the question to a lawful value, and no
        missing bytes cure a conviction. And pending-wins lets a subject's own contradiction
        stay hidden for as long as any other party withholds a vote.
        Rejected pending-wins, whose textual case is real: 1753-1762 says no finding is terminal
        while any enumerated check is unexamined. utina reads a slot the fold looked at and found
        empty as examined, and a check whose evidence has not arrived as a different thing from
        one nobody looked at. Tradeoff accepted: on any record where a subject contradicts
        itself mid-vote, a conforming engine holding the other reading returns a different value.
        THE SAME REASONING REACHES THE TAINT ARM, found while checking this node against M4's
        second conviction. The bearing walk returned on the first convicted party it met, so an
        earlier taint at a cited endorser hid a later conviction of the subject, and the fold
        returned pending with a taint's cure — an owned act of the tainted party — on a question
        that act cannot rescue. And a second tainted endorser went unnamed, so the pending told a
        reader one act would suffice when two were owed. Chose to walk every observation at or
        before the position: any subject conviction wins, and otherwise the pending names every
        taint, in canonical order. Neither case occurs on a record utina builds today.

    The GEL is sealed into the gAID's key log, and the fold derives its order from the seals = decision:
      id: wsxwkwgv
      why: >
        custos-4.2.md:1114-1120 seals every GEL event into the gAID's KEL "by the same anchoring
        discipline KERI's registry layer uses for TELs", and 3091-3101 derives the fold's order
        from that anchoring: KEL order first, then the seal list. Until now only enactments were
        anchored, order came from a sequence number the writer committed (Q24), and the seal
        index had been flattened away (Q11). Tick 4uus.
        Chose the TEL discipline literally. Each GEL event is sealed with an EVENT seal
        {i: the GEL's identifier, s: the event's GEL sequence number, d: its SAID} — the
        shape a TEL event's anchor takes — into an interaction event, or a rotation for an
        enactment (2085-2087). The event body keeps its own s, as a TEL event does, so Position
        is still the GEL sequence number and no coordinate moves. The gAID's key events travel
        beside the GEL events as evidence, and Corpus.anchored checks the two against each
        other: the seals naming the GEL run 0..n-1 in KEL-then-seal-list order, every seal has
        a presented event, every presented event has a seal, each event's s is its seal's, and
        an enactment sealed in an interaction event is refused (3232). Every failure refuses the
        stream, because 3178-3181 makes membership fail loud and names "a membership rule
        yielding a proper subset of the GEL without a refusal" a must-reject.
        Rejected putting the key events into the corpus as GEL members, which keeps Q25's pin:
        a rotation is evidence of where a governance event was committed, not a governance
        event. Rejected a digest seal {d} per event, which is what enactments used, because a
        digest seal cannot say which log the sealed thing belongs to, so a fold could not tell
        a GEL event's seal from a credential's and could never detect an omitted event. The
        event seal's i is what makes membership decidable.
        This supersedes @qv7m3d's order (coordinate then SAID) wherever key events are
        presented, and the part of @jdie6v that kept the fold from seeing any anchoring.
        Corpus.load stays as the hand-positioned door that fold unit tests use; everything the
        constructor writes goes through Corpus.anchored. Tradeoff accepted: the fold reads key
        events it cannot verify, the same trust it already extends to signatures (@f3pmxu3x);
        verifying them belongs to an ingestion path in the substrate plane (tick 6ofh).

    The founding law designates its GEL by an identifier computed before the gAID exists = decision:
      id: ryh5orta
      why: >
        3151-3153: "a domain's founding law SHALL commit the identifier of the governance
        registry it designates as its GEL, at inception grade, sealed by the genesis knot". And
        1085: "the gAID SHALL NOT appear in C or in any body C cites". Read together those are a
        cycle for any registry whose identifier digests its controller, which a KERI registry's
        does: the registry names the gAID, the founding law names the registry, and the gAID is a
        digest over the inception that seals the founding law.
        Chose to break it with the sentinel the text already provides (1076-1078). The GEL's
        identifier is the digest of a registry-inception body {t: gel, ii: <the sentinel>, u:
        <nonce>}, which names the controller only through the sentinel, so it is computable
        before the gAID exists and the founding law can commit it outright. The sentinel
        resolves to whichever prefix's inception seals the founding law, as 1078 says.
        Rejected the construction another engine uses, where the gAID's first rotation seals
        both the founding law and a registry inception naming the gAID: it is lawful, but the
        designation then lives in a rotation rather than in the founding law, which is not what
        3151 says. Rejected deriving the identifier from (gAID, nonce) at verification, which
        makes the founding law commit a nonce and not an identifier. Tradeoff accepted: the GEL
        identifier is not a keripy registry — no Tever exists for it and a KERI tool resolves
        none — because utina's GEL events are its own governance ilks, not registry forms (track
        two, 3119-3127). Logged as a Q: the text does not say how 1085 and 3151 coexist.

    A born-governed domain's inception seals its founding law = decision:
      id: 4b2mmhbf
      why: >
        1073-1084: a born-governed GARD's genesis is (K0, C), and "K0 SHALL seal C's
        self-addressing identifier among its anchoring seals", so the founding law is inside the
        bytes the gAID digests. utina incepted the gAID bare and put the founding law in an
        unanchored event, which is not even the adopted construction 1088-1092 allows at a lesser
        grade, since that one anchors the law later.
        Chose Constructor.found, which takes the founding law, commits the GEL designation into
        it, gives it its SAID, incepts the gAID with a digest seal of that SAID, and then emits
        the GEL's inception event. incept_domain stays as the adopted construction — a gAID
        incepted bare, the law sealed by an interaction afterwards — because 1088 makes it
        lawful and every test that builds a record by hand relies on it. The fold reports which
        grade a record is at, refuses a founding law no key event seals, and refuses a
        born-governed founding law that contains the gAID. Supersedes @crrtzf's rule that the
        composition root incepts every party: the gAID is now incepted by the verb that founds
        it, because only that verb knows the founding law's SAID. Tradeoff accepted: under the
        facade an identifier is its alias rather than a digest of its inception, so there
        "inside the bytes the identity digests" is simulated. The facade says so; keripy makes it
        true.

    An enactment claims a predecessor, and the earliest lawful claimant is the succession = decision:
      id: fougolzt
      why: >
        custos-4.2.md:3043-3050: "Eligibility is latest-unsuperseded: an enactment is a lawful
        succession only under the Constitution in force at its own coordinate, and a
        ratification whose cited predecessor was already superseded at that coordinate confers
        nothing, however well signed. Where two enactments claim the same predecessor, the GEL's
        committed order rules: the earlier lawful enactment is the succession, and the later
        travels as evidence." utina's enactments cited nothing, so the law fold resolved a fork
        to the last edition in canonical order, which it confessed was an artifact (tick 5edf).
        Chose three rules. An enactment may cite its predecessor in "prior", the identifier of
        the law event whose edition it amends; the constructor commits one when the domain
        supplies it, and Acme's amendments do. An enactment that cites a predecessor which is
        not the edition in force at its own coordinate confers nothing. An enactment that cites
        none claims the edition in force at its own coordinate, because §18 never obliges the
        field (Q33) and a rule that refused every uncited enactment would be a reading the text
        does not make. Then the law in force at a position is a chain from the founding law:
        from each edition, the succession is the earliest enactment in GEL order that claims it,
        is eligible, and has taken force by that position.
        The consequence worth stating, because it is where affirmation-keyed force (Q33,
        @xhtvuxnc) meets the fork rule: if two enactments claim one predecessor and the later
        is affirmed first, the later is in force until the earlier is affirmed, and from then
        the earlier is. Each position is computed from its own bundle and nothing earlier is
        rewritten — the reversal is a new fact (1741-1742) — but the law does move twice. The
        alternative, holding the later enactment out of force while an earlier claimant might
        still be affirmed, makes a position's law depend on events that have not happened.
        Rejected sealing a predecessor lens into the anchoring rotation, which another engine
        does: the enactment's own SAID already digests its "prior", and the rotation seals that
        SAID, so a second seal would commit the same fact twice. The succession record 3040-3042
        asks for — predecessor, ratifying enactment, effectuation coordinate — is offered as
        Constitution.succession, derived from the GEL alone.

    A record utina did not write is rebuilt, never trusted = decision:
      id: k6agmgtn
      why: >
        utina could fold only what its own constructor wrote, in the same process, so it could
        not serve as an oracle against any other engine's output — the largest limit an outside
        comparison found (tick 6ofh). Custos's replay promise is that "any stranger holding the
        logs" recomputes the same findings (29-34), and the stranger is the case utina could not
        be.
        Chose a serialized record — the gAID, the key logs of every party who signs, and the GEL
        events with their signatures — and an ingestion path that admits it only by rebuilding
        it in a fresh substrate. Each key log is replayed through the substrate's own verifier,
        so key state is computed rather than read; each GEL event's identifier is re-derived from
        its bytes; each event's signature, and each embedded credential's, is verified against
        the key state its signer's replayed log establishes; and only then does fold/gel.py
        derive order and membership from the gAID's replayed log. Any failure refuses the
        record. The ingesting substrate never signs, incepts or rotates anything of its own.
        Rejected folding the serialized events directly, which is what Corpus.load would do:
        it trusts every identifier and signature it is handed, which is the posture this
        decision exists to end for foreign records. Rejected a reader that imports keripy
        outside the substrate, because tests/test_purity.py forbids it and the substrate is
        where key state already lives. Tradeoff accepted: under the facade "replaying a key
        log" means re-deriving every event's identifier and its key names from the fixed
        seed, which catches tampering and nothing about custody; under keripy it is real.

    A record that presents anything the fold does not examine is refused = decision:
      id: gnviwwjc
      why: >
        Axiom 4's membership face turned inward (tick 4jcx): a fold that silently skips what it
        does not understand has answered "I folded what I understood" to a caller who asked
        "what does this record say". The ingestion path therefore refuses a record carrying a
        field it does not read, an event of a kind no fold module reads, or a key log belonging
        to nobody who signs, delegates or founds. Chose refusal over a warning, because a
        warning is a proper subset of the record folded without a refusal, which 3178-3181
        names a must-reject for membership and which is the same failure one level up.
        Scoped to the ingestion door: the hand-positioned door fold unit tests use, and the
        anchored door the constructor's own records take, admit only what the constructor
        writes, and the kinds it writes are exactly the kinds the fold reads.

    A refusal names the seal kind its ground is missing under = decision:
      id: kr7j7d7l
      why: >
        custos-4.2.md:3016-3028 makes cross-implementation equality semantic full-payload
        equality, including "refusal grounds with the seal kind named per the seal ladder's
        three-kind discipline wherever refusal fires", and 2049-2056 makes that discipline the
        naming rule wherever the document requires a refusal to name its ground: "a digest
        mismatch, a coordinate mismatch, and a clause violation are three different refusals".
        utina's Refusal named its ground in prose and no kind, so two engines agreeing on every
        refusal were unequal under the predicate (Q9, tick 6d5k).
        Chose a required field naming one of the three kinds (1242-1250), assigned by what the
        missing thing is a commitment to. Covenant, for the three refusals where the committed
        law runs out: no clause governs the act class, the committed event names no act class a
        clause could govern, and an office has two standing holders the clause gives one share.
        Event, where the question names an event nothing committed at or before the position
        bears — a coordinate that does not resolve. Digest, for both semantics refusals, since
        axiom 4 pins an external semantics by digest and what is missing is either the digest or
        an implementation of the bytes it names.
        Rejected a default, because a refusal that forgot its kind would then carry a
        plausible one. Rejected deriving the kind from the prose, which is the ambiguity the
        field exists to remove. Tradeoff accepted: the assignment is utina's reading, and the
        second of the covenant cases — an event whose kind carries no act class — could be read
        as an event-seal mismatch instead; that is recorded in Q9.
