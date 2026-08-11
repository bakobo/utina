# Intent — the law fold

*Decisions taken while building `utina.fold.corpus`, `clause` and
`constitution`, in `this.i` node format so the orchestrator can fold them into
the tree. Not the source of truth; `this.i` is. This file is a staging area.*

```
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
    Logged as QL1 and DIVERGENT.

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
    standing to build. Logged as QL3 and DIVERGENT.

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
    one clause without restating the rest. Logged as QL4 and DIVERGENT.

Genesis is constructed, not judged; every later enactment is judged = decision:
  id: c5tqn2
  why: >
    Succession says law never applies to itself at a coordinate, only to its successor at the
    next (2270-2272), which taken alone would leave the founding law not in force at its own
    coordinate and the domain ungoverned at inception. Chose to treat the inception event's
    law as in force at and after its own coordinate, and every later enactment as in force
    strictly after its own, over a uniform strictly-before rule. Rejected the uniform rule
    because it makes the base case vacuous; 2272-2274 names genesis "constructed rather than
    judged" and that is the exemption doing the work. Logged as QL5.

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
```
