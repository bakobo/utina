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
