# Questions against Custos — the law fold

*Guesses made while building `utina.fold.corpus`, `clause` and `constitution`.
Companion to `docs/custos-questions.md`, which holds the register for the engine
as a whole; this file is the law-fold agent's contribution to it and folds into
it at integration.*

Same shape as its companion: the span with line numbers into `custos-4.2.md`,
each lawful reading with the lines permitting it, the reading we pinned, and
whether two conforming engines **diverge** on some input. `DIVERGENT` means they
can disagree on committed bytes. `convergent` means the text is loose but every
lawful reading computes the same thing.

Line references are into `custos-4.2.md` unless stated.

---

## QL1 — Intra-anchor order, where the consumed model carries no seal index **DIVERGENT**

**Span:** `custos-4.2.md:3091-3101`, the canonical-order site rule. Related to
U9 in `thesmo-demo/audit-spec-requirements.md:370-381`.

**Where it bit:** `Corpus.load`, the only place the order is decided.

Custos fixes the order as "KEL anchoring order first, intra-anchor order as the
anchoring event's seal list states, and no tiebreak that consults anything
uncommitted" (3094-3097). The first clause we can honour exactly: a position
carries a sequence number and we sort on it. The second we cannot, because the
committed value a `Position` carries in this engine is a sequence number alone
(`docs/interfaces.md`, the `triple` section) — the anchoring event's *seal list
index* is not among the fold's three closed inputs by the time the fold sees an
event. Two GEL events anchored in one KEL event therefore reach us with their
seal-list order already flattened away.

- **Reading A — recover the seal index and order by `(sn, index)`.** Permitted,
  and plainly the literal reading of 3095. It requires the position type to
  carry the index, i.e. a coordinate of `(identifier, sn, seal-index)`. But
  1222-1227 defines a position as `(identifier, sequence number)` with no third
  component, so the literal reading of 3095 needs a coordinate the position
  definition does not supply.
- **Reading B — fall through to wall 6's default and order by SAID.** Wall 6
  (2905-2915) says "the canonical order is total — lexicographic over the
  encoded self-addressing identifiers at the site unless the site's clause
  commits a different derivable order." Where the seal index has not survived
  into the consumed model, the site's clause has committed no derivable order,
  so the wall's default governs.

**Pinned: B.** It is derivable from committed bytes, total, and explicitly
blessed by the wall that 3091 says this paragraph descends from. Reading A is
the better reading of 3095 in isolation and we may be wrong; it is unavailable
without widening the position type, which the contract fixes elsewhere.

**Divergence:** engines disagree wherever two GEL events share one anchoring
coordinate and their seal-list order differs from their SAID order. Under A the
earlier-sealed event is consumed first; under B the lexicographically smaller
SAID is. It is invisible in Acme's demo, where no two events share a coordinate,
and it bites the moment a domain seals two enactments into one rotation — which
is a natural thing to do, since 2085-2088 pushes every law-amending enactment
into an establishment event and a domain amending two clauses at once has every
reason to seal both into the same one.

**Ask Custos:** does a position carry the intra-anchor index, or is 3095's
"intra-anchor order as the anchoring event's seal list states" meant to be
discharged before the fold, by whatever assembles the bundle? If the latter,
1222-1227's two-component position and 3095's seal-list order need reconciling —
they cannot both be the whole story.

---

## QL2 — Is re-presenting the same committed event an error, or a no-op? **convergent**

**Span:** `custos-4.2.md:3087-3089` — "a coordinate tuple is a location, never
an identity"; wall 7 at 2916-2922 — "Competitors at one coordinate entering the
bundle convict as duplicity."

**Where it bit:** `Corpus.load`, which must decide what a repeated event means.

Wall 7 speaks to *competitors* — two different events at one coordinate. It does
not say what the same event presented twice means. Two readings: the second
presentation is a competitor and convicts, or a said is an identity so the second
presentation is the same object arriving again and folds once.

**Pinned: fold once.** 3087-3089 makes the self-addressing identifier the
identity and the coordinate merely a location, so two spans with one SAID are one
event by construction, not two competitors. This is also thesmo `m2-gamma`'s
reading, pinned there as `@jax6b7`.

**Convergent:** every lawful reading computes the same Constitution, because
folding an identical event twice is idempotent over a clause set either way. It
is logged because the *error* behaviour differs — an engine reading wall 7
broadly would convict a stream that this one accepts — and a conformance vector
would catch that even though no Constitution differs.

---

## QL3 — What separates a re-presentation from a collision? **DIVERGENT**

**Span:** `custos-4.2.md:3097-3099` — "An implementation whose fold result
depends on arrival order, storage order, or any ambient sequence does not
conform"; 3081-3087, the self-addressing identity requirement.

**Where it bit:** `Corpus.load`'s `e.state.order-ambient.f` branch — the one
place this engine refuses a stream outright rather than folding it.

Two events bearing one SAID but differing in their other committed fields cannot
both be right: under 3081-3087 the identifier ranges over the event's complete
canonical bytes, so differing bytes with one identifier means at least one
identifier does not re-derive. Custos says what a non-saidive event is — "not a
GEL event of this standard" (3086-3087) — but not what the *fold* does when it
meets one.

- **Reading A — refuse the stream.** The two events collide at one canonical key,
  so nothing derivable from committed bytes separates them, and consulting the
  order they arrived in is what 3097-3099 forbids by name. Also gamma's reading
  of a neighbouring case (`@jve6ne`: an anchored event whose identifier does not
  re-derive refuses the stream rather than dropping out of it).
- **Reading B — convict as duplicity under wall 7 (2916-2922).** They are
  competitors in the plainest sense, and wall 7 says competitors convict.

**Pinned: A**, and this engine raises `e.state.order-ambient.f`. The obstacle we
can actually observe at this layer is that no committed order separates them; the
duplicity finding of Reading B belongs to a tier that can name the contradictory
pair as a proof package, which the corpus walk cannot.

**Divergence:** engines disagree on every stream carrying a SAID collision. Under
A the stream is refused and no Constitution exists; under B a self-conviction is
returned and the domain is tainted. Those are very different outcomes for the
same bytes — one is an operational fact, the other a finding that propagates.

**Ask Custos:** when a fold meets two spans bearing one self-addressing
identifier and different bytes, is that a refusal (no derivable order) or a
duplicity conviction (competitors at a coordinate)? Wall 6 and wall 7 both reach
it and they discharge differently.
