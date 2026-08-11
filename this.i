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
