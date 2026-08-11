# Intent — the substrate, enact and Acme commission

*Decisions taken while building `utina.substrate`, `utina.enact`, `utina.acme`
and the acceptance oracle's `acme` fixture. Written in `this.i` node format so
they can be grafted into the intent tree under the existing goal @rk4mzq once
the parallel commissions merge; kept in `docs/` meanwhile because `this.i` is
outside this commission's owned files and four agents amending one tree
concurrently would collide.*

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
    GEL is lawful — see S3 in `docs/questions-substrate.md`, where the two
    readings are set out and the divergence named. Chose to keep the rotation
    in the substrate: the contract's `Event.kind` enumeration has no member for
    an anchoring, the fold consumes governance events rather than key events,
    and the enactment is what a clause is predicated on. The facade records the
    enactment-SAID-to-rotation-SAID binding so the anchor is checkable, and a
    test asserts Acme's amendment is anchored, so :2087 is honored in a form a
    reader can verify rather than asserted in a comment. Confessed cost, filed
    as the divergence in S3: a fold that never sees the anchoring cannot
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
    Custos that S4 records and that we could not settle from the text: a
    prospective question naming an act kind binds to the latest committed act
    of that kind at or before the position. Under the aggregating reading D6
    is affirmed and the demo's centerpiece collapses, which is why S4 is the
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
    are therefore not among them; S5 records that inference as a reading rather
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
