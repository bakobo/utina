# Intent — the codomain commission

*Nodes for `this.i`, written here because four agents cannot edit one file
concurrently. The orchestrator folds these into the tree at integration; ids are
already minted and stable, so folding is a move, not a rewrite. Parent for all of
them is the goal node @rk4mzq.*

---

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
    pinned in questions-codomain.md QC2 for a threshold defeated by a signed declination —
    over a required field, which would break every sibling call site the contract entitles to
    omit it, and over deriving the class from the presence of a declination, which would
    silently misclassify a cryptographic or a superseding defeat as an authority one.
    Tradeoff accepted: a caller that does not think about the class gets `authority`, and
    `authority` is wrong for three of the four defeat kinds; the field is documented at the
    point of default and the pin is logged as a divergence.
