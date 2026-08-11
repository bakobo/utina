# Questions against Custos — the substrate, enact and Acme surfaces

*The register kept by the commission that built `utina.substrate`, `utina.enact`
and `utina.acme`. Same shape and same standing as `docs/custos-questions.md`:
the span with line numbers, every lawful reading with the lines permitting it,
the one we pinned, and whether the readings **produce different results on some
input**. `DIVERGENT` means two conforming engines can disagree on committed
bytes; `convergent` means the text is loose but every lawful reading computes
the same thing.*

Line references are into `/home/daniel/code/3GR/custos/spec/custos-4.2.md`.

These entries are weaker evidence than thesmo's, for the reason
`custos-questions.md` already states: utina's implementers may read anything,
so an entry here says "we could not tell what was meant," never "a blind reader
converged elsewhere."

A standing caveat over the whole file: the facade substrate is a **model**, not
a conformance witness. It computes SAIDs and signatures with the standard
library so the demo replays without keripy. Where a question below turns on
CESR or KERI physics, the answer utina pins binds the facade only, and the
keripy commission re-answers it against the real medium.

---

## S1 — What field carries a GEL event's self-addressing identifier, and under what digest? **DIVERGENT**

**Span:** `:3081`–`:3089`, event identity. Also the must-reject at `:3232`,
which makes "non-saidive event identity" a boundary vector.

**Where it bit:** every event `utina.enact` emits. The rule at `:3081`–`:3085`
is unambiguous about the *discipline* — the identifier field carries a
placeholder of the encoded digest's length while the digest is computed, and
the digest ranges over the event's complete canonical bytes — and silent about
the two things an implementer must choose before writing a byte: which field
holds it, and which digest fills it.

- **Reading A — the field and digest are KERI's, inherited silently.** `:3082`
  says "computed under the reading rules' pin discipline", and the reading
  rules govern a KERI/CESR document; the field is `d` and the digest is
  whatever CESR's primitive table makes the domain's, Blake3-256 by present
  practice. Nothing here needs saying because nothing here is new.
- **Reading B — the field and digest are the domain's committed law.** `:3086`
  says an event whose identifier field is not self-addressing "is not a GEL
  event of this standard", which constrains the *property* and not the
  spelling; §18's own two tracks (`:3103`–`:3127`) make the event grammar a
  committed choice, and the ilk table for track two is explicitly "committed
  data in the GEL" (`:3121`–`:3123`). A domain that commits its grammar commits
  this with it.

**Pinned: A for the field, a deliberate departure for the digest.** The field
is `d`, with a 44-character placeholder. The digest is **Blake2b-256**,
encoded as `E` followed by unpadded base64url — KERI-shaped, KERI-sized, and
not KERI's, because Blake3 is not in the standard library and the facade's
whole purpose is to run with no cryptographic dependency.

**Divergence:** total and by construction. A stranger recomputing utina's SAIDs
under CESR's Blake3 primitive gets different identifiers for identical
committed bytes. This is a confessed property of the facade, not a reading of
Custos: the digest is a substrate choice, the fold never inspects a SAID's
internals, and the keripy commission replaces the primitive without touching
`utina.fold`. It is logged as DIVERGENT rather than as an implementation note
because a reader comparing utina's vectors against a keripy engine's will find
every identifier different, and needs to know that is expected.

**Ask Custos:** should §18 name the identifier field, or state explicitly that
the field name and digest primitive are committed law under the track choice?
The must-reject at `:3232` cannot be tested without knowing which field to
look at.

---

## S2 — How does a fold derive canonical order when the log has no KEL to derive it from? **convergent**

**Span:** `:3091`–`:3101`, canonical order — "KEL anchoring order first,
intra-anchor order as the anchoring event's seal list states, and no tiebreak
that consults anything uncommitted". Read against the spine paragraph at
`:3071`–`:3079`.

**Where it bit:** demo beat D10, and the corpus every other beat reads. The
rule is stated as a derivation from two committed sources, both of which live
in the KEL. utina's facade has no KEL: rotations exist (S3), but the endorsements,
declinations and act events are not individually anchored, so neither source is
available for most of the log.

- **Reading A — commit the coordinate in the event.** Each event carries its
  own sequence number in its committed body, and the fold orders by it. This
  satisfies the rule's actual requirement, which `:3096`–`:3097` states
  negatively: "no tiebreak that consults anything uncommitted". A sequence
  inside the digested bytes is committed, so ordering by it consults nothing
  ambient.
- **Reading B — anchor everything, and derive order the way the text
  describes.** `:3094`–`:3096` names two sources and no third. A log whose order
  comes from anywhere else is not deriving order the way this paragraph says to,
  however committed the substitute is. Under this reading every GEL event is
  anchored, and the anchoring event's seal list is the only order there is.

**Pinned: A.** Every event `utina.enact` emits carries `s`, its coordinate, in
the bytes the SAID digests, and `Event.position` is that same number. Reading B
is the shape the keripy commission should build, and this pin is a facade
convenience that reading B would subsume.

**Convergent** for this corpus: both readings order utina's log identically,
because A's committed sequence is assigned in exactly the order B's anchorings
would occur. Logged because the equality is a property of how utina builds the
log and not of the readings, and an implementer who assumes it generally will
be wrong the first time two events share an anchor.

**Ask Custos:** is a committed per-event coordinate a lawful order source, or
does `:3094` close the list at two?

---

## S3 — Is the establishment event that anchors an enactment itself a member of the GEL? **DIVERGENT**

**Span:** `:2085`–`:2087` — "Designated act classes — charter, revocation of a
seat, enactment amending law, and the succession acts of section 17 — SHALL
anchor in establishment events". Read against the spine at `:3071`–`:3079` and
the must-reject at `:3232`–`:3233`, "designated-class act anchored in an
interaction event".

**Where it bit:** demo beat D4, and the shape of `Substrate.rotate`. Acme's
board-seating amendment is an enactment amending law, so it must anchor in an
establishment event. The question is what the fold then sees: does
`Corpus.upto` return the rotation alongside the enactment, or only the
enactment?

- **Reading A — the rotation is a KEL event, and the GEL holds the enactment.**
  §10 is a section about seals, and a seal is "carried in" an establishment
  event (`:2081`); carriage is the KEL's. The GEL entry is the enactment, and
  the anchor is a fact about it that a verifier checks by resolving the seal in
  the KEL. The fold consumes governance events, not key events.
- **Reading B — the anchoring is itself the GEL event.** `:3072`–`:3074` says
  "the only utterances a gAID makes unilaterally into its own GEL are
  anchorings: commitments of acts to coordinates", which reads the anchoring as
  a GEL member and the anchored act as the evidence it carries. Under this
  reading a fold that never sees the anchoring has not read its own log.

**Pinned: A.** `Substrate.rotate` returns an event of kind `rotation`, the
facade records the enactment-SAID-to-rotation-SAID binding, and no rotation is
ever loaded into the corpus the fold folds. The contract's `Event.kind`
enumeration — `inception`, `enactment`, `endorsement`, `act` — is read as
evidence for A, since it has no member for an anchoring.

**Divergence:** what `Corpus.upto` returns, on every log containing a
designated-class act. Under B a clause predicated on establishment events is
computable by the fold; under A the fold cannot see the anchor grade at all,
and the difference between promise and physics that `:2090` insists on is
invisible to the very machinery that judges. That is the uncomfortable half of
this pin, and the reason it is filed DIVERGENT rather than as a modeling note.

**Ask Custos:** does the fold consume the anchoring establishment events, and
if not, how does a clause condition on anchor grade?

---

## S4 — What is a prospective question bound to when several committed acts share an act kind? **DIVERGENT**

**Span:** `:1503`–`:1526`, the finding codomain, which speaks throughout of "the
proposition" without saying what identifies one. Read against `:3087`–`:3089`,
"a coordinate tuple is a location, never an identity".

**Where it bit:** demo beats D5 and D6, the second half of the centerpiece.
Both ask about `approve-budget` under the seated board. D5 must find Marta and
Nina endorsing and Dev untouched; D6 must find Marta endorsing, Dev declining
and **Nina untouched**. Slot dispositions only ever advance, so one committed
act event cannot present Nina as endorsed at D5 and pending at D6. The two
beats are two committed acts of the same kind, and the question
`Proposal("approve-budget")` names the kind.

- **Reading A — the latest act of that kind at or before the position.** A
  prospective question is asked about the live proposal, and the live proposal
  is the most recent one committed. Endorsements name their subject's SAID
  (`:3087`–`:3088` makes the SAID the identity), so gathering them against the
  latest act is unambiguous once the act is chosen.
- **Reading B — every act of that kind, aggregated.** The question named a
  kind, so the evidence is every committed endorsement bearing on that kind.
  Nothing in §8 licenses discarding committed evidence, and `:1516` says
  affirmed means "the proposition holds over the committed evidence" — all of
  it.
- **Reading C — the question is ill-posed and the fold refuses.** A kind is not
  an identity (`:3088`), so a question that names only a kind has not named a
  proposition, and §18's bootstrap refusal shape (`:3143`–`:3149`) is the
  template: name the underivable commitment and refuse.

**Pinned: A.**

**Divergence:** decisive, and it is the demo's centerpiece. Under B, Nina's
endorsement of the first budget act counts toward the second, D6 reaches unity
and is **affirmed** rather than pending — the D3-against-D6 contrast collapses
and with it the argument the whole demo makes. Under C, D5 and D6 both refuse.
Three lawful readings, three different verdicts, on one set of committed bytes.

**Ask Custos:** does the finding codomain admit a question that names an act
class rather than a committed act, and if so what evidence is in scope? This is
the entry in this file we most want answered.

---

## S5 — Are signatures part of the bytes an event's SAID digests? **convergent**

**Span:** `:3081`–`:3089`. `:3085` says the digest "ranges over the event's
complete canonical bytes"; `:3087`–`:3088` says "receipts and attachments
addressing a GEL event address these bytes".

**Where it bit:** the contract's `Event` has four fields — `said`, `kind`,
`position`, `body` — and no slot for a signature, so utina carries each
signature inside `body`. If the SAID digested it, no event could be both signed
and self-addressing.

- **Reading A — signatures are attachments and are excluded.** `:3087`–`:3088`
  distinguishes attachments from "these bytes" they address, which is only
  coherent if an attachment is not itself among them. This is KERI's own
  construction.
- **Reading B — "complete canonical bytes" means complete.** The phrase admits
  no carve-out on its face.

**Pinned: A.** `Substrate.said` normalizes before digesting — the `d` field
becomes the placeholder and any `sig` field is removed — so the SAID of a
signed event equals the SAID of the same event unsigned, and the signature
commits to the SAID rather than the reverse.

**Convergent**, since B is not constructible: an event under B has no
self-addressing identifier once signed, which `:3086` says makes it not a GEL
event. Logged because the carve-out is inferred from a sentence about receipts
rather than stated, and an implementer reading `:3085` alone will build B and
discover the circularity only at the digest.

---

## S6 — May a pending finding's requirement elements omit their discharge species? **DIVERGENT** *(fold surface, found here)*

**Span:** `:1585` — "A pending finding SHALL carry the species of each of its
requirement elements" — against the four species enumerated at `:1560`–`:1562`
(absent, window-open, unresolved-conflict, expired/abandoned).

**Where it bit:** not in this commission's own code. It was found while reading
§8 to answer S4, and it is recorded here because the register is the only place
it will not be lost. `docs/interfaces.md` types `RequirementElement` with an
endorser and a clause and no species field, and the acceptance oracle's D2 and
D6 cases assert only over `element.endorser`. An engine built to that contract
returns pending findings that `:1585` says SHALL carry something they do not.

Not pinned by this commission — `utina.fold` is another commission's surface,
and the choice is theirs. Flagged as DIVERGENT because a verifier consuming a
pending finding cannot compute the cure path `:1575`–`:1585` promises it, which
is a difference in what the finding means and not only in what it holds.

**Ask Custos:** nothing. **Ask the fold commission:** whether the contract's
`RequirementElement` is a deliberate deviation with a `this.i` node behind it,
or an omission. Every Acme requirement element is species **absent** — cured by
the arrival of the missing endorsement — so the fixture can supply the species
the day the type grows one.
