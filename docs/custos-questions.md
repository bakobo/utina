# Questions against Custos

*A running register of places where building utina required guessing what the
specification means. Every entry here is a candidate bug against Custos.*

This file is append-only during a build. **Anyone implementing utina who has to
guess adds an entry before the code that depends on the guess.** A guess made
silently is the one thing this register cannot recover.

Entries follow thesmo's register shape, because the Custos author already reads
that shape: the span, each lawful reading with the lines permitting it, the one
we pinned, and — the part that matters — whether the readings **produce
different results on some input**. `DIVERGENT` means two conforming engines can
disagree on committed bytes. `convergent` means the text is loose but every
lawful reading computes the same thing; logged anyway, because a logged
non-ambiguity costs almost nothing.

Line references are into `custos-4.2.md` unless stated.

Note on standing: utina is **not** a blind implementation. Its readings are not
independent evidence about the document the way thesmo's are — utina's
implementers may read anything. An entry here says "we could not tell what was
meant," which is a weaker and more practical claim than thesmo's, and it should
be filed as such.

**Provenance.** utina was built by four commissions working in parallel, each
keeping its own register, folded into this one at integration. Every entry is
preserved; the numbering is now a single `Q` series, and each entry that came
from a commission register says which id it carried there, so a citation made
before the fold can still be followed. The per-commission files are gone.

| Q | Question | Mark | Was |
|---|---|---|---|
| Q1 | an unreachable group: defeated or pending | DIVERGENT | Q1 |
| Q2 | threshold language: whose semantics | pinned | Q2 |
| Q3 | is an amendment judged at its own coordinate | — | Q3 |
| Q4 | what does affirmed carry | DIVERGENT | Q4 |
| Q5 | how does species order in the canonical total order | DIVERGENT | QC1 |
| Q6 | which defeater class does a declination produce | DIVERGENT | QC2 |
| Q7 | an empty subcode is the minimum, yet orders last | DIVERGENT | QC3 |
| Q8 | may a pending carry an empty requirement set | DIVERGENT | QC4 |
| Q9 | the refusal record has no committed form | convergent decision, DIVERGENT record | QC5 |
| Q10 | "citing-clause bytes" has no stated flattening | convergent here | QC6 |
| Q11 | intra-anchor order with no seal index | DIVERGENT; A since 2026-09-24 | QL1 |
| Q12 | re-presenting one committed event | convergent | QL2 |
| Q13 | re-presentation against collision | DIVERGENT | QL3 |
| Q14 | is an amendment an edition or a delta | DIVERGENT | QL4 |
| Q15 | is the founding law in force at its own coordinate | convergent | QL5 |
| Q16 | §9:1966 says pending where Q1 pinned defeated | DIVERGENT | S1 (slots) |
| Q17 | a requirement element's fields, enumerated twice | DIVERGENT | S2 (slots) |
| Q18 | how is an endorsement retracted | DIVERGENT | S3 (slots) |
| Q19 | which endorsement fills a slot: pointer or match | DIVERGENT | S4 (slots) |
| Q20 | one endorser, two contradictory acts | DIVERGENT | S5 (slots) |
| Q21 | is a slot's weight bounded | DIVERGENT | S6 (slots) |
| Q22 | law whose slots cannot sum to unity | DIVERGENT | S7 (slots) |
| Q23 | which field carries the SAID, under what digest | DIVERGENT | S1 (substrate) |
| Q24 | canonical order with no KEL to derive it from | retired 2026-09-24 | S2 (substrate) |
| Q25 | is the anchoring establishment event in the GEL | DIVERGENT | S3 (substrate) |
| Q26 | what a prospective question binds to | DIVERGENT | S4 (substrate) |
| Q27 | are signatures in the bytes the SAID digests | convergent | S5 (substrate) |
| Q28 | may a requirement element omit its species | DIVERGENT | S6 (substrate) |
| Q29 | which law judges a prospective question | DIVERGENT | new at integration |
| Q30 | what act class does an enactment perform | DIVERGENT | new at integration |
| Q31 | what is a threshold defeat's subcode | DIVERGENT | new at integration |
| Q32 | must an endorsement be an ACDC issuance in a registry | DIVERGENT | new at the keripy substrate |
| Q33 | at which coordinate does an affirmed enactment take force | DIVERGENT | new at demo 2 |
| Q34 | is a decision consequential when cast or when certified | DIVERGENT | new 2026-09-23 |
| Q35 | what does an amendment owe about the acts it ends | gap | new 2026-09-23 |
| Q36 | how is a suppressed act evidenced when the domain omits it | gap | new 2026-09-23 |
| Q37 | may a clause slot seat an office rather than name a party | DIVERGENT | new 2026-09-24 |
| Q38 | a subject convicted while slots are open: pending or self-convicted | DIVERGENT | new 2026-09-24 |
| Q45 | a founding law designating a registry that names the gAID it may not name | gap | new 2026-09-24 |

---

## Q1 — Does a declination make a finding `defeated`, or leave it `pending`? **DIVERGENT**

**Where it bit:** the demo's centerpiece. Acme's clause A1 has two slots at
`w=1/2`. Marta endorses; Dev signs a declination. The endorsed weight is 1/2
either way, but no further endorsement can arrive from a slot that is spent, so
unity is now unreachable.

Custos §8 gives four values and their grounds, and the dossier specification
gives the three slot dispositions. This register's first edition said neither
says what an evaluator returns when a threshold is *unreachable* rather than
merely *unmet*. **That was wrong, and the correction cuts against the pin:** §9
`:1966–1971` says outright that "an unsatisfied operator group is not a defect
and not a defeat: it discharges as a pending finding whose typed requirement set
enumerates exactly the unfilled slots". The slot commission found it and filed it
as its own S1, which is Q16 here; the reading analysis lives there and is not
repeated.

The two readings:

- **Reading A — `pending`.** The requirement space is not discharged; the typed
  requirement is the outstanding slot. `:1966` states it flatly, "unsatisfied" is
  unqualified, and nothing in the codomain speaks of reachability.
- **Reading B — `defeated`.** The question can no longer be affirmed under this
  clause, and the declination is a committed citation that says so. Leaving it
  `pending` names a requirement that can never be discharged, which makes the
  typed requirement a lie. `:1966` is written in the vocabulary of cure ("the
  cure path for insufficient composed evidence is readable off the finding
  itself", `:1969–1971`), and a spent slot has no cure; §8.3 `:1668` makes
  `pending → defeated` a permitted edge conditioned on the requirement set
  discharging by defeat, which is what a committed declination does.

**Pinned: B, and B is what shipped.** `utina.fold.evaluate.UNREACHABLE_YIELDS`
is `Defeated`. Three things decided it, and only the third is an argument about
the text:

1. `docs/demo-script.md` and `tests/test_acceptance_oracle.py` both require it.
   The oracle is the binding statement of the contract, and D3 is the beat where
   a two-slot decision with a signed no against it is dead — a verdict of "not
   yet" would say something the beat is not for.
2. `:1966` carries **no BCP-14 keyword**, so it binds nothing. It is the drafting
   authority's plain intent and not a requirement, which is exactly the class of
   sentence this register exists to surface.
3. Reading A has a hole. "Exactly the unfilled slots" is the **empty set** in the
   two-slot case, because a declined slot is a *filled* slot — and Q8 pins that a
   pending finding may not carry an empty requirement set, since the Ground Axiom
   makes the cure path part of what a pending *is*. So the sentence's own
   prescription is unconstructible on the case it most obviously covers.

**Reading A is implemented anyway, and it is one line away.** Flipping
`UNREACHABLE_YIELDS` to `Pending` selects a branch that returns a pending finding
whose requirement set names the **spent** slots, marked undischargeable —
`PendingSpecies.EXPIRED_ABANDONED`, whose cure is re-presentation. That repairs
the hole in `:1966` in the only way we can see: it honours "not a defeat", it
satisfies the Ground Axiom, and it still tells a reader that nothing they do to
*this* decision will move it. It is not what `:1966` says, because `:1966` says
the unfilled slots and this names the filled ones. The maintainer has not finally
ruled and may flip it.

**Divergence:** engines disagree on every decision where an endorser declines and
the remaining slots cannot reach unity. Under A the finding is pending forever;
under B it is defeated with the declination cited.

**Ask Custos:** should the finding codomain distinguish *unmet* from
*unreachable*? If `:1966` is meant to cover both, it needs to say what the typed
requirement set holds when every unsatisfied slot is filled — the set it
prescribes is empty, and §8's own Ground Axiom refuses that value.

---

## Q2 — Threshold language: whose semantics? *(pinned, see `this.i` @ta7vle)*

§9 carries one BCP-14 keyword in its length (`:1945`): the composition rule MUST
be committed, and MAY be expressed in the ACDC edge grammar as the dossier
specification profiles it. Expressing it that way makes the dossier spec an
external semantics, which axiom 4 (`:290`) then requires be pinned by committed
digest, with anything unpinned refused.

Pinned: a domain-native committed clause predicate, structurally isomorphic to
the dossier's threshold operators. Not a defect in Custos — it is Custos working
as intended, leaving the choice to the domain — but logged because the cost of
the permitted option is not stated where the option is offered, and an
implementer will meet the axiom-4 obligation only after choosing.

---

---

## Q3 — Is an amendment judged at its own coordinate under the law it replaces?

**Where it bit:** demo beat D4. Both founders enact the amendment seating the
board. It must clear clause A2 (unanimity), not the B2 it installs. Custos says
an amendment is judged under the law in force, and that the fold reads the
successor law the enactment left — but the position at which the enactment is
*itself* appraised is the thing under change.

See U10 in `../../thesmo-demo/audit-spec-requirements.md` for the full reading
analysis. Pinned: the enactment is appraised under the law in force immediately
*before* its own coordinate. Logged because getting this backwards is silent —
the demo would still pass, since both founders also satisfy B2's founder slots.

---

---

## Q4 — What does `affirmed` carry?

§8's required-payload enumeration presents itself as complete and does not list
`affirmed`, while the Ground Axiom makes the ground a component of the type.
thesmo's `m1-alpha` reading found the same thing and pinned the payload; a 4.2
seed repairs it. Recorded here because utina's `Affirmed` carries the evidence
bundle identity and the clause set, and a reader comparing utina against the
ratified enumeration will find a field the enumeration does not require.

**Amended 2026-09-24: DIVERGENT.** The conformance predicate at `:3016-3028` is
semantic full-payload equality, "grounds in canonical order" among its terms, so the
affirmed payload is compared even though no clause rules it. A second lawful reading
carries the evidence reference and the law applied — the pair the appraisal triple
already names — where utina carries clause ids, endorsement identifiers and a bundle
identifier. Two engines agreeing on every verdict are then unequal on every affirmed
finding. **Ask Custos:** rule the affirmed payload, since §17 compares it.

---

## Q5 — How does `species` order inside the canonical four-field total order? **DIVERGENT**

*Was QC1 in the codomain commission's register.*

**Where it bit:** the sort key of every `Pending` finding's requirement set.

The order is ruled: a pending finding SHALL carry its typed requirement set
"in the canonical four-field total order — subject, then kind, then
citing-clause bytes, then species" (`:1650-1651`), and the deduplication key
"sees every field the element carries: elements differing only in species do not
merge" (`:1652-1656`). So two elements can differ in species alone and must then
be ordered by species — and the document never says how a species compares to a
species.

- **Reading A — the enumeration order the document itself states.** "The species
  are absent, window-open, unresolved-conflict, and expired/abandoned"
  (`:1560-1561`), restated as cure paths in the same order at `:1575-1585`. The
  ranking is the document's own, exactly as the defeater classes are "enumerated
  and ranked, in this order" (`:1771-1772`).
- **Reading B — lexicographic over the species name's bytes.** The neighbouring
  component in the same sentence is "citing-clause **bytes**" (`:1651`), so the
  sentence is already comparing byte-wise, and a reader is entitled to carry that
  through to the last component rather than import a ranking stated 90 lines
  earlier for a different purpose.

**Pinned: A.** `PendingSpecies` carries an explicit rank in the document's order,
and the sort key uses the rank. Reading B is defensible.

**Divergence:** any pending finding holding two elements that differ only in
species. A orders `window-open` (rank 1) before `expired/abandoned` (rank 3); B
orders `expired/abandoned` before `window-open` because `e` < `w`. The findings
are then unequal under §17's semantic full-payload equality, which is the
determinism obligation at `:1631-1634`.

**Ask Custos:** state the species collation the way the defeater classes state
theirs — "ranked, in this order" — or say that species compares as bytes.

---

---

## Q6 — Which defeater class does a signed declination produce? **DIVERGENT**

*Was QC2 in the codomain commission's register.*

**Where it bit:** the demo's centerpiece. Q1 already pins *that* an unreachable
threshold is `defeated`; this is the next question, which Q1 does not reach. A defeated finding SHALL carry its defeater class (`:1641-1646`), and the
classes are closed at four: **crypto** "a cryptographic verification failed"
(`:1772-1773`), **authority** "the actor lacked the invoked power"
(`:1773-1774`), **merit** "the content violates a committed clause"
(`:1774-1775`), **superseded** "a later lawful act displaced the subject"
(`:1775-1776`). A slot holder's signed declination that puts unity out of reach
is none of these on its face.

- **Reading A — `authority`.** The invoked power is the clause's composition
  rule, and the proposer never held it alone; the declination is the committed
  proof that the power was not conferred. Permitted by `:1773-1774`.
- **Reading B — `merit`.** The clause is a committed clause, the act fails its
  unity test, and failing a committed clause's own test is what merit names.
  Permitted by `:1774-1775`.

**Pinned: A.** A threshold is a statement about who may act, so a threshold that
cannot be reached is a power that was not conferred. `Citation.defeater_class`
defaults to `authority` for exactly this case.

**Divergence:** every declination-defeated finding. The class is a payload field,
so the two engines' findings differ directly; worse, the class *rank* is the
first component of canonical selection (`:1766-1770`), so where a question has
both this defeat and another, A and B cite different clauses.

**Ask Custos:** name the class for a composition rule that cannot reach unity, or
say the class is the domain's to assign in the clause.

---

---

## Q7 — An empty subcode is the lexicographic minimum, yet "orders last" **DIVERGENT**

*Was QC3 in the codomain commission's register.*

**Where it bit:** `select_defeat`, the canonical-selection helper.

One sentence rules the selection: the finding "SHALL cite the lexicographic
minimum of (defeater-class rank, citation identifier, subcode)" (`:1766-1770`).
Fourteen lines later: "where the clause defines none, the subcode is empty and
orders last" (`:1776-1779`). The empty string is the *minimum* of any set of
strings under lexicographic comparison, so the two sentences select opposite
defeats whenever they both apply.

- **Reading A — the special case wins.** `:1778-1779` is the more specific
  statement and would be dead text under B, and a reading that makes ruled text
  dead is the one to drop.
- **Reading B — the tuple comparison wins.** `:1767-1769` is the sentence that
  says SHALL about the selection itself, and "orders last" can be read as loose
  prose about where empties sit in a *displayed* list.

**Pinned: A.** An empty subcode sorts after every non-empty one, implemented as a
presence flag ahead of the subcode in the sort key.

**Divergence:** two defeats sharing a defeater class and a citation identifier
where one carries a subcode and the other does not. A cites the one with the
subcode; B cites the one without. Both are single, deterministic engines, and
they disagree on committed bytes.

**Ask Custos:** rewrite the selection sentence so the empty subcode's position is
inside it, e.g. "(defeater-class rank, citation identifier, subcode presence,
subcode)".

---

---

## Q8 — May a `pending` finding carry an empty requirement set? **DIVERGENT**

*Was QC4 in the codomain commission's register.*

**Where it bit:** the constructor of `Pending`.

`pending`'s ground is "the typed requirement set — each element naming its
requirement kind, its subject, and the clauses that make it required"
(`:1522-1526`), and the payload rule says a pending finding "SHALL carry its
typed requirement set: deduplicated elements" (`:1647-1649`). Neither says the
set is non-empty, and a clause committing no slots yields an empty one.

- **Reading A — empty is not a member.** The Ground Axiom excludes "a value that
  does not carry its ground" (`:1504-1507`), and a pending finding whose set is
  empty names nothing that would discharge it, which is the one thing `pending`
  is defined to do: "the finding names what is missing" (`:1522-1523`).
- **Reading B — empty is lawful.** Nothing states a cardinality, and the
  terminality discipline at `:1754-1764` says an evaluator returns pending
  whenever an enumerated check is unexamined, without conditioning on the set
  being non-empty.

**Pinned: A.** Constructing a `Pending` with an empty requirement set raises
`e.state.ground-missing.f`.

**Divergence:** a question governed by a clause whose committed slot list is
empty. Under B the engine returns `pending(∅)` and the reader is told a decision
is outstanding with no way to discharge it; under A the engine fails closed.
Both are conforming readings of the same committed triple.

**Ask Custos:** say whether the typed requirement set is non-empty by
construction, and — if it is — what an evaluator returns for a question whose
committed requirement space is empty. U4 in the requirements audit argues that
such a question is malformed rather than satisfiable, which would make a refusal
the answer; that inference is ours, not the document's.

---

---

## Q9 — The refusal record has no committed form *(convergent decision; DIVERGENT record)*

*Was QC5 in the codomain commission's register.*

**Where it bit:** the shape of `utina.fold.refusal.Refusal`.

Custos requires a refusal to name its ground (`:277-278`) and says what a refusal
*is* (`:1898-1900`), but §16 holds the record's form expressly open. So a value
had to be invented: `Refusal { missing, detail }`, carrying no self-addressing
identifier and never committed to the GEL.

- **Reading A — a typed value outside the codomain, with a named ground.**
  Permitted by `:1883-1894` and by the naming rule at `:2047-2055`.
- **Reading B — an exception with a message.** Permitted because no clause
  commits a form at all.

**Pinned: A**, because `:1899-1900` calls a refusal a fact "recorded as an
operational fact" and you cannot record what you threw.

**Convergent:** both readings refuse the same invocations on the same committed
inputs, and Custos owes byte-equality only for the *decision* to refuse
(`:31-34`), not for the record. Logged because the reading is ours and a reader
comparing utina to the document will find a type the document does not describe.
See U3 in `../../thesmo-demo/audit-spec-requirements.md`.

**Amended 2026-09-24: the convergence above holds for the decision and not for the
record.** The conformance predicate at `:3016-3028` compares "refusal grounds with the
seal kind named per the seal ladder's three-kind discipline wherever refusal fires",
and `:2049-2056` makes that discipline the naming rule wherever the document requires
a refusal to name its ground. utina's `Refusal` names its ground in prose (`missing`)
and names no seal kind, and neither reading above carries one. So two engines refusing
the same invocation are unequal under the predicate unless both name a seal kind, and
the form the predicate compares is one §16 declines to give. Three conditions another
engine might return as refusals are raised errors here instead: a SAID collision
(`fold/corpus.py`), a contradictory edition (`fold/constitution.py`) and an unreadable
law (`fold/clause.py`). **Ask Custos:** §17 compares a refusal record that §16 leaves
formless; one of the two has to move.

---

---

## Q10 — "Citing-clause bytes" has no stated flattening *(convergent here; DIVERGENT for anyone else)*

*Was QC6 in the codomain commission's register.*

**Where it bit:** `RequirementElement.sort_key`, and it bit softly because the
interface contract gives each element one clause rather than a list.

The canonical order compares "citing-clause **bytes**" (`:1650-1651`) and the
element carries "the list of citing clauses" (`:1648-1649`). A list has to be
flattened to bytes before it can be compared as bytes, and the document nowhere
says how — no separator, no length prefix, no ordering within the list.

- **Reading A — join the clause identifiers with a separator below every
  character an identifier can carry**, so the flattening is injective. thesmo's
  `m1-alpha` pinned `\x00`.
- **Reading B — compare the lists element-wise**, which needs the list's own
  order pinned first, and the document does not pin that either.

**Not pinned, because utina does not reach it:** each of our requirement elements
cites exactly one clause, so its bytes are that clause's bytes and every lawful
reading agrees. An engine whose elements cite two clauses would face a genuine
divergence — `["A1","B2"]` and `["A1B","2"]` flatten identically under a
separator-free join — and two conforming engines would order their requirement
sets differently.

**Ask Custos:** state the flattening, or drop "bytes" and compare the clause list
lexicographically as a sequence of identifiers.

---

## Q11 — Intra-anchor order, where the consumed model carries no seal index **DIVERGENT**

*Was QL1 in the law-fold commission's register.*

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

**Amended 2026-09-24: reading A, for every corpus the constructor writes.** Each
GEL event is now sealed into the gAID's key log with an event seal naming the GEL,
the event's GEL sequence number and its identifier, and `fold/gel.py` requires those
sequence numbers to count up in key-log order and then seal-list order (`this.i`
@wsxwkwgv). So the seal index survives into the fold, and a position is still one
number — the GEL sequence number, which the seal list fixes. That also suggests an
answer to the Ask: a position of `(the GEL's identifier, its sequence number)` is an
`(identifier, sn)` pair in 1222-1227's sense, and carries 3095's intra-anchor order
without a third component, exactly as a TEL event's does. Reading B still governs
hand-positioned corpora, which fold unit tests build and nothing a user runs does.

---

---

## Q12 — Is re-presenting the same committed event an error, or a no-op? **convergent**

*Was QL2 in the law-fold commission's register.*

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

---

## Q13 — What separates a re-presentation from a collision? **DIVERGENT**

*Was QL3 in the law-fold commission's register.*

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

---

---

## Q14 — Is an amendment a restatement of the law, or a delta on it? **DIVERGENT**

*Was QL4 in the law-fold commission's register.*

**Span:** `custos-4.2.md:2266-2272` (amendments "judged under the Constitution in
force before them"); 3001-3003 (a ratified document's clauses "are the GARD's law
for every position at and after the effectuation coordinate"); 1199-1203 (a
clause is "the committed unit of law").

**Where it bit:** `Constitution.at`, deciding what the clause set becomes when an
enactment is consumed.

Custos says an amendment is judged under prior law, and it says the successor's
clauses become the law from effectuation onward. It never says what happens to
the *predecessor's* clauses. Two readings:

- **Reading A — the enactment commits the complete clause set in force after
  it,** replacing the prior edition wholesale. Permitted by 3001-3003, which is
  edition-shaped: it speaks of "this document's clauses" becoming "the GARD's
  law", not of clauses being added to a pool. Section 17's whole succession
  apparatus — predecessor digest, ratifying enactment, effectuation coordinate
  (3039-3042) — is the machinery of editions superseding editions.
- **Reading B — the enactment adds clauses to the law in force.** Permitted by
  the absence of any repeal language; Custos supplies no committed way to say
  "clause A1 is repealed", and thesmo `m2-gamma` reads it this way explicitly,
  confessing in its own module docstring that "it does not repeal."

**Pinned: A.** Under B, Acme's A1 and B1 both govern ordinary acts after the
board is seated, so `governing("open-bank-account")` has two answers and the
engine must either refuse every ordinary act forever or invent a precedence rule
— and inventing one is what 1874-1876 forbids by name. A is the only reading in
which the demo's central act is evaluable at all.

**Divergence:** engines disagree on every domain that amends. Under A the law
after an amendment is exactly what the amendment committed; under B it is that
plus everything ever enacted, and every act kind governed by both a superseded
and a successor clause becomes an uncommitted precedence seam. The two engines
return different findings for the same act on the same bytes.

**Ask Custos:** does an enactment commit a whole edition or a delta? If a delta,
what is the committed form of a repeal, and what orders two in-force clauses that
govern one act class? Section 17's succession record reads as edition-shaped, but
§18's GEL event grammar never says a later enactment displaces an earlier one.

---

---

## Q15 — Is the founding law in force at its own coordinate? **convergent**

*Was QL5 in the law-fold commission's register.*

**Span:** `custos-4.2.md:2270-2274` — "law never applies to itself at a
coordinate, only to its successor at the next … The recursion's base case is
genesis, constructed rather than judged."

**Where it bit:** `Constitution.at`, choosing the interval over which law events
are consumed.

Read as a uniform rule, "law never applies to itself at a coordinate" excludes
the inception event's own law at the inception coordinate, which leaves a domain
ungoverned at its own genesis and makes the base case vacuous. The sentence that
follows rescues it: genesis is "constructed rather than judged."

- **Reading A — the rule is uniform, and law binds strictly after its own
  coordinate, genesis included.** Permitted by the bare sentence at 2270-2272.
- **Reading B — genesis is exempt.** The founding law binds at and after its own
  coordinate because it is constructed rather than judged; every later enactment
  binds strictly after its own, because it is judged. Permitted by 2272-2274 and
  by 1079-1093, where the founding law is sealed at inception and the gAID is
  defined in terms of it.

**Pinned: B**, implemented as: the inception event's clauses take force at its
own coordinate; an enactment's clauses take force strictly after its own.

**Convergent**, but only just, and only because of what the exemption is *for*.
Under A a domain has no law at its inception coordinate, so every question asked
there refuses; under B it has its founding law. That is a visible difference —
it is logged as convergent rather than divergent because Reading A makes the
inception coordinate uninhabitable by any question at all, and a reading under
which no domain can ever be governed at genesis is not a lawful reading of a
document whose section 5 constructs the identifier out of the founding law.

**Ask Custos:** confirm that "constructed rather than judged" is the intended
exemption, and that the interval is `[genesis, p]` for founding law and
`[genesis, p)` for enactments. The engine turns on this and the text states it
only by implication.

---

## Q16 — An *unreachable* group: §9 says pending, and we pinned defeated **DIVERGENT**

*Was S1 in the slot commission's register.*

**Where it bit:** every beat of the demo's centerpiece, D3 against D6.

Q1 records this pin and, in the edition this commission read, said that neither
Custos nor the dossier specification says what an unreachable threshold produces. That is not quite
right, and the correction cuts against our pin: §9 `:1966–1971` says outright that
"an unsatisfied operator group is not a defect and not a defeat: it discharges as
a pending finding whose typed requirement set enumerates exactly the unfilled
slots."

- **Reading A — `pending`, always.** `:1966` is a flat statement about operator
  groups, and it is the only sentence in the document that speaks to the
  question. "Unsatisfied" is not qualified, so an unreachable group is one kind of
  unsatisfied group and discharges pending like any other.
- **Reading B — `defeated` when unity is unreachable.** `:1966` addresses the
  ordinary case of evidence that has not arrived yet — it is written in the
  vocabulary of cure ("the cure path for insufficient composed evidence is
  readable off the finding itself", `:1969–1971`), and a spent slot has no cure.
  §8.3 `:1668` makes `pending → defeated` a permitted edge conditioned on the
  requirement set discharging by defeat, which is exactly what a committed
  declination does.

**Pinned: B**, unchanged, but with less confidence than Q1 originally recorded;
Q1 now carries this correction and the shipped reading.

**Settled at integration.** `UNREACHABLE_YIELDS` is `Defeated`, and Reading A is
implemented behind that one constant. This entry is why the switch exists. The
disagreement is not about the arithmetic; it is about whether a declination is
evidence that *discharges* a requirement element negatively or merely fails to
discharge it.

**Divergence:** every decision where a declination puts unity out of reach. Under
A the finding is pending forever, naming a requirement no act can satisfy; under B
it is defeated with the declination cited.

**Ask Custos:** does `:1966`'s "unsatisfied" mean "not yet satisfied", or does it
also cover "can no longer be satisfied"? If the former, say so at `:1966`; if the
latter, the codomain has no way to distinguish a cure path that exists from one
that does not.

---

---

## Q17 — A requirement element's fields are enumerated twice, differently **DIVERGENT**

*Was S2 in the slot commission's register.*

**Where it bit:** what `Group.outstanding()` must hand the evaluator for a pending
finding.

Two sections enumerate the payload of a typed requirement element and they do not
agree:

- §8.3 `:1647–1651`: "requirement kind, subject identifier, the list of citing
  clauses, and its discharge species, in the canonical four-field total order —
  subject, then kind, then citing-clause bytes, then species."
- §9 `:1968–1971`: "each element naming the slot's required schema, its expected
  issuer, and the citing clause."

§9's element has no requirement kind and no species; §8.2 `:1585–1586` says "a
pending finding SHALL carry the species of each of its requirement elements",
so §9's three-field element cannot be conformant on its face. §9 has a required
schema, which §8.3's four fields have nowhere to put. §9 has one citing clause
where §8.3 has a list.

- **Reading A — §9 is a projection of §8.3.** The slot's expected issuer *is* the
  subject identifier, the required schema is folded into the requirement kind, and
  the species is omitted from §9's sentence for brevity rather than by intent.
- **Reading B — §9 states the element for composed evidence and §8.3 the general
  case,** with the composed-evidence element carrying a schema field that the
  general enumeration does not know about.

**Pinned: A**, and utina's `RequirementElement` (the codomain's, not ours) carries
the endorser and the clause only — which is conformant to neither reading as
written.

**Divergence:** the dedup key at `:1652` "sees every field the element carries",
so two engines carrying different field sets deduplicate differently, and a
pending finding's requirement set differs in cardinality on the same bytes. That
is the strongest form of divergence in the codomain.

**Ask Custos:** which enumeration governs a composed-evidence requirement element,
and is the discharge species mandatory on one produced by an unfilled slot? (Its
species would presumably be **absent**, cured by the arrival of the endorsement.)

**Amended 2026-09-24.** The pin above is stale in one respect: the element now carries
six fields — endorser, clause, schema, kind, species, and the `ground` that names the
event closing its cure path (`this.i` @waihlx27) — so utina has moved toward reading B,
with schema a field of its own rather than folded into the kind. That sharpens the
divergence rather than easing it. An engine carrying the four fields of `:1647-1651`
deduplicates over four and merges two elements this engine keeps apart.

It also exposed a second, smaller question. `:1650-1651` rules the order over exactly
four fields, so two elements differing only in a field past those four are distinct
by the dedup key and tied by the order, and the text gives no way to order them. utina
breaks the tie with the remaining fields of the dedup key, schema then ground, and
checks both order and uniqueness over that one key (`this.i` @fdhqffc3). Before that
decision the builder and `Pending` disagreed about such a pair: the builder kept both
in arrival order and `Pending` refused them as duplicates. No record utina builds
reaches the case. **Ask Custos**, in addition: where an element carries more than the
four ordered fields, what breaks a tie among them?

---

---

## Q18 — How is an endorsement retracted, and what does the slot fall back to? **DIVERGENT**

*Was S3 in the slot commission's register.*

**Where it bit:** the fourth of the four checks that gate ENDORSED. A slot is
endorsed only if the endorsement stands; nothing says how it stops standing.

In the dossier an endorsement is an ACDC, so it is revoked through its issuance
registry and §9 `:1919–1928` is emphatic that registry state is the evidence a
standing covenant computes over. utina's facade substrate has no TEL, so the
retraction has to be committed as an event, and no text says what that event looks
like or what the slot becomes.

- **Reading A — a retracted endorsement is as if never committed:** the slot
  returns to PENDING, and its weight is reachable again.
- **Reading B — retraction is itself an act that spends the slot:** the endorser
  has now acted twice, and a slot that has been endorsed and un-endorsed records
  attributable ambivalence rather than silence.
- **Reading C — an endorsement, once committed, cannot be retracted at all;**
  revocation applies to the *subject*, under a revocation operator (`RMxN`,
  dossier-spec-body.md:372), never to an endorsement.

**Pinned: A**, with the retraction committed as an event whose body carries
`revokes` naming the endorsement's SAID, from the same issuer. Chosen because it
is the reading under which a retraction grants no authority and creates no state
the law did not describe.

**Divergence:** under A a retracted declination un-spends the slot and a defeated
decision becomes pending again; under B it does not; under C the retraction is
not evidence at all. The demo commits no retraction, so the divergence is latent
here and live anywhere real.

**AMENDED 2026-09-10 — the pin narrows to A bounded by settlement** (`this.i` @nuxitore, tick `5wu5`). Reading A as pinned was not merely one guess among three; it was inconsistent with a keyword-force span nobody had connected to it. Under it a retraction is effective at unlimited distance, so a settled affirmation returns to pending — measured on the demo corpus, appending one retraction eighteen events after the bank account settled returns that question to pending and names its cure as the arrival of evidence that had already arrived. `:1698-1712` forbids that edge by name (affirmed → pending, "evidence does not un-arrive"; defeated → pending, likewise), and `:1730-1745` permits a successor finding to reverse a terminal value only where its grown bundle carries committed evidence falsifying a ground the prior finding cites, "never on added contrary weight alone". A withdrawal falsifies nothing: it is a fact about the giver's present will, not about the artifact the prior finding appraised.

So A holds while the act is still in flight — unity neither reached nor unreachable — and a retraction committed after that is inert. The divergence paragraph above stands for the live case and is wrong for the settled one: a retracted declination un-spends the slot in a three-slot group, where the act is still reachable, and does not in a two-slot group, where the declination itself ended the flight. Both halves of that gate are reading-independent: where unity is unreachable, §8's pin makes the finding terminal, and §9's competing pending reading types the requirement `expired/abandoned`, whose ratified cure is re-presentation rather than the arrival of evidence.

**Ask Custos:** is the retraction of an endorsement a governed act with a
committed form, or is it outside the composed-evidence rule entirely? And define `ground-evaporation`, which `:1701` names as load-bearing — "taint-cure and ground-evaporation are different phenomena, and neither is an edge" — and which appears nowhere else in 3,940 lines. The distinction the engine now rests on is that withdrawal is not falsification, and it is stated in the ratified text only by that one unexplained hyphenation.

---

---

## Q19 — Which endorsement fills a slot, when the evidence is flat? **DIVERGENT**

*Was S4 in the slot commission's register.*

**Where it bit:** the slot predicate's first line.

The dossier's slot *points* at its endorsement: the `n` field references the
endorsement ACDC and "the expected endorser is identified by the issuer (`i`) of
the ACDC the slot references" (dossier-spec-body.md:358). Custos cites that
grammar rather than restating it (`:1946–1951`) and adds only that the slot names
"the schema its evidence must satisfy". Neither says what fills a slot when the
committed law names an endorser but references no artifact — which is the case
for any law written before the endorsements exist.

- **Reading A — pointer.** The law commits the reference, and an endorsement that
  the slot does not point at is not in the group at all.
- **Reading B — match.** The slot names the expected endorser, and the fold finds
  the committed endorsement whose issuer is that endorser and whose subject SAID
  is the decision's.

**Pinned: B** (`this.i` @2pfkyg). Under A the law would have to be amended
before it could be endorsed, which inverts the order of every governance act.

**Divergence:** an endorsement issued by the right endorser, naming the right
subject, but not referenced by the slot. Under A it contributes nothing; under B
it reaches unity. Two conforming engines return affirmed and pending on identical
committed bytes.

**Ask Custos:** for composed evidence whose slots are committed in a domain's law
rather than in an instance dossier, is the slot–endorsement relation a reference
or a predicate?

---

---

## Q20 — One endorser, two contradictory acts on one subject **DIVERGENT**

*Was S5 in the slot commission's register.*

**Where it bit:** the slot predicate's conflict handling; not exercised by the
demo, exercised by the tests.

The dossier says a slot is in "exactly one of three dispositions"
(dossier-spec-body.md:358) and never says what makes it exactly one when the
endorser has committed both an endorsement and a declination naming the same
subject. Custos's own machinery for contradiction is the duplicity ladder (§8.4),
but that is about conviction-grade contradictory pairs at the key and registry
tiers, not about an endorser exercising the same power twice.

- **Reading A — the declination wins,** whatever the order. The slot is spent by an
  authenticated refusal and nothing un-spends it.
- **Reading B — the last committed act wins.** Committed order is the domain's
  own total order, and people revise decisions.
- **Reading C — the pair is a contradiction** and the finding is self-convicted, or
  the pending species *unresolved-conflict* (`:1560`), cured "by an owned act of the
  party whose conflict it is" (`:1583–1584`) — which fits this case suspiciously well.

**Pinned: A**, fail-closed. Reading C is the most textually attractive and we
did not take it because it makes an ordinary governance mistake escalate to the
duplicity machinery.

**Divergence:** any subject carrying both acts from one endorser; A and B disagree
on the verdict whenever the endorsement is the later act.

**Ask Custos:** is an endorser's contradictory pair on one subject an
unresolved-conflict pending species, or is it the domain's own law to resolve?

---

---

## Q21 — Is a slot's weight bounded? **DIVERGENT**

*Was S6 in the slot commission's register.*

**Where it bit:** `Slot` construction.

Custos delegates the weight to the dossier's grammar; the dossier bounds only the
sum — "satisfied when the weights of the slots that hold valid endorsements sum to
at least unity" (dossier-spec-body.md:353) — and gives examples only of positive
fractions.

- **Reading A — unbounded rationals.** Nothing forbids `w=0` or `w<0`.
- **Reading B — strictly positive.** A weight is a share of authority, and the
  language of "how much each is worth" (dossier-spec-body.md:353) presupposes it.

**Pinned: B**; a non-positive weight is refused at construction
(`this.i` @anoz6j).

**Divergence:** committed law carrying a negative weight. Under A an endorsement
*reduces* the sum, so an endorser defeats a decision by endorsing it and a
declination becomes the pro-decision act — a governance inversion reachable from
one character of committed law. Under B the law is refused. This is the entry with
the worst consequence-per-word ratio in the file.

**Ask Custos:** should §9 bound an individual slot weight, or say explicitly that
bounding it is the domain's business?

---

---

## Q22 — Law whose slots cannot sum to unity **DIVERGENT**

*Was S7 in the slot commission's register.*

**Where it bit:** `Group.reachable` on a group with no declinations in it at all.

A group whose slot weights total less than 1 can never be satisfied. Custos's
composed-evidence rule (`:1942–1971`) does not say whether such a rule is
committable.

- **Reading A — the law is malformed** and its commitment is refused, per the
  refusal clause the section invokes at `:1952–1956` ("refusal fires where
  composition is uncommitted"), read as covering composition that is committed but
  inoperative.
- **Reading B — the law is well-formed and permanently unreachable.** The fold
  does not legislate; a domain may commit a power nobody holds, and the finding
  says so.

**Pinned: B.** Reading A would have the fold rule on the wisdom of committed law,
which axiom 3 forbids more clearly than `:1952` permits.

**Divergence:** a refusal under A, a finding under B, on the same bytes — and the
two are not the same kind of object, so this divergence is not even
comparable within the codomain.

**Ask Custos:** is an inoperative composition rule a refusal, or a finding?

---

*Standing, as this register's preamble says: utina's implementers may read anything,
so these are not independent readings the way thesmo's are. Each says "we could
not tell what was meant", which is weaker than "a blind implementer read it the
other way" — but Q1, Q17 and Q21 would each have bitten a blind implementer too.*

---

## Q23 — What field carries a GEL event's self-addressing identifier, and under what digest? **DIVERGENT**

*Was S1 in the substrate commission's register.*

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

---

## Q24 — How does a fold derive canonical order when the log has no KEL to derive it from? **convergent**

*Was S2 in the substrate commission's register.*

**Span:** `:3091`–`:3101`, canonical order — "KEL anchoring order first,
intra-anchor order as the anchoring event's seal list states, and no tiebreak
that consults anything uncommitted". Read against the spine paragraph at
`:3071`–`:3079`.

**Where it bit:** demo beat D10, and the corpus every other beat reads. The
rule is stated as a derivation from two committed sources, both of which live
in the KEL. utina's facade has no KEL: rotations exist (Q25), but the endorsements,
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

**Amended 2026-09-24: retired in favour of B for every corpus the constructor
writes.** Every GEL event is anchored now, and `fold/gel.py` derives the order from
the key log and refuses a corpus whose committed coordinates disagree with it
(`this.i` @wsxwkwgv). The committed `s` stays in each event, as a TEL event's does,
and is now checked against its seal rather than trusted. The equality this entry
called a property of how utina builds the log is enforced rather than assumed.

---

---

## Q25 — Is the establishment event that anchors an enactment itself a member of the GEL? **DIVERGENT**

*Was S3 in the substrate commission's register.*

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

**Amended 2026-09-24.** The pin stands — no key event is a GEL member — but its
cost is gone. The gAID's key events now travel beside the GEL as evidence, the fold
reads the seal that anchors each GEL event, and an enactment anchored in an
interaction rather than an establishment event is refused (`fold/gel.py`,
`this.i` @wsxwkwgv). So the fold does see anchor grade, which was the
uncomfortable half. What it still cannot do is verify a key event's signatures;
that belongs in the substrate plane, on an ingestion path (tick `6ofh`).

---

---

## Q26 — What is a prospective question bound to when several committed acts share an act kind? **DIVERGENT**

*Was S4 in the substrate commission's register.*

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

**Settled at integration, and tested.** `_latest_act` implements Reading A, and
`tests/test_seam.py` proves on Acme's own log both that the fold binds to the
latest tabling and — computed rather than asserted — that pooling across both
tablings really does satisfy clause B1 and affirm D6. The divergence this entry
claims is therefore not hypothetical: it is one line of engine away.

**Ask Custos:** does the finding codomain admit a question that names an act
class rather than a committed act, and if so what evidence is in scope? This is
the entry in this file we most want answered.

---

---

## Q27 — Are signatures part of the bytes an event's SAID digests? **convergent**

*Was S5 in the substrate commission's register.*

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

---

## Q28 — May a pending finding's requirement elements omit their discharge species? **DIVERGENT** *(fold surface, found here)*

*Was S6 in the substrate commission's register.*

**Span:** `:1585` — "A pending finding SHALL carry the species of each of its
requirement elements" — against the four species enumerated at `:1560`–`:1562`
(absent, window-open, unresolved-conflict, expired/abandoned).

**Where it bit:** not in this commission's own code. It was found while reading
§8 to answer Q26, and it is recorded here because the register is the only place
it will not be lost. `docs/interfaces.md` types `RequirementElement` with an
endorser and a clause and no species field, and the acceptance oracle's D2 and
D6 cases assert only over `element.endorser`. An engine built to that contract
returns pending findings that `:1585` says SHALL carry something they do not.

**Answered at integration.** `RequirementElement` carries `kind` and `species`,
and `evaluate()` populates both rather than leaning on their defaults: an
untouched slot is `absent`, and a spent slot under Q1's other reading is
`expired/abandoned`. The contract was updated to match.

Not pinned by the commission that raised it — `utina.fold` was another
commission's surface, and the choice was theirs. Flagged as DIVERGENT because a verifier consuming a
pending finding cannot compute the cure path `:1575`–`:1585` promises it, which
is a difference in what the finding means and not only in what it holds.

**Ask Custos:** nothing. **Ask the fold commission:** whether the contract's
`RequirementElement` is a deliberate deviation with a `this.i` node behind it,
or an omission. Every Acme requirement element is species **absent** — cured by
the arrival of the missing endorsement — so the fixture can supply the species
the day the type grows one.

---

## Q29 — Which law judges a prospective question? **DIVERGENT**

*New at integration, where `evaluate()` first had to choose.*

**Span:** `:2266–2272` (an amendment is "judged under the Constitution in force
before" it; "law never applies to itself at a coordinate, only to its successor
at the next"); `:3001–3003` (a ratified document's clauses bind "every position
at and after the effectuation coordinate"); `:1620–1624`, the requirement space
committed ex ante.

**Where it bit:** `utina.fold.evaluate`, which must pick a coordinate before it
can pick a Constitution. Q3 and Q15 settle it for a *committed* act: the act is
judged under the law in force at its own coordinate, which is what makes the past
recomputable and an amendment answerable under the law it replaces. Neither
reaches a `Proposal`, which names an act class rather than a committed act, and
whose subject — under Q26's pin — is the latest committed act of that class.

- **Reading A — the law in force at the appraisal position.** A proposal asks
  whether an act *may* be performed, which is a question about now. `:3001–3003`
  makes the current edition the law "for every position at and after"
  effectuation, and the position the question is asked at is the position it is
  asked at.
- **Reading B — the law in force at the coordinate of the act it binds to.** The
  proposal resolves to a committed act, and treating that act differently
  depending on whether the question names it or its class is a distinction the
  document never draws.

**Pinned: A.** Under B a proposal about an act tabled before an amendment would
be judged under the superseded law forever, so a domain could never re-ask a
question under its new law without re-tabling the act — and re-tabling is exactly
what Q26's pin already requires for a fresh vote, which would make B's answer
unreachable in practice as well as wrong in principle.

**Divergence:** any proposal about an act class whose live tabling predates an
amendment that changed the clause governing it. Under A the new clause rules;
under B the old one does. Acme's demo does not reach it — every re-tabling
follows its amendment — so this is latent here and live in any domain that amends
while a decision is outstanding.

**Ask Custos:** is a prospective question judged at the appraisal position, or at
its subject's coordinate? §17's succession machinery is written for committed
acts and says nothing about a question asked about a class.

---

## Q30 — What class of act does an enactment perform? **DIVERGENT**

*New at integration, where beat D4 refused instead of affirming.*

**Span:** `:2085–2087`, the designated act classes — "charter, revocation of a
seat, enactment amending law, and the succession acts of section 17" — read
against §9's composition rule, which governs acts *by class*, and `:1199–1203`,
where a clause is the committed unit of law that rules them.

**Where it bit:** beat D4, the amendment that seats Acme's board. It must clear
clause A2, and A2 governs the act class `amend-operating-agreement`. Custos
designates "enactment amending law" as a class in its own §10 sense, but a
domain's clause governs act classes the *domain* names, and nothing in the event
grammar says an enactment carries the domain's name for what it is doing.

- **Reading A — the class is Custos's designation.** An enactment is an
  "enactment amending law" and a clause governing amendments governs it by that
  designation. The domain never names it, because the document already has.
- **Reading B — the class is the domain's, committed in the enactment.** A clause
  governs act kinds the domain committed (`:1199–1203`), Acme's phrase is
  `amend-operating-agreement`, and no fold can map the document's designation
  onto a domain's vocabulary without legislating the mapping.

**Pinned: B.** `Constructor.enact_amendment` takes the act class from the caller
and commits it; an enactment that names none is refused rather than judged under
a guessed class. Reading A would require the fold to know that Acme's
`amend-operating-agreement` is the local spelling of Custos's "enactment amending
law", which is precisely the uncommitted seam `:1874–1876` says an evaluator
refuses rather than legislates.

**Divergence:** every domain whose amendment clause is named anything but the
document's own designation. Under A the fold finds the clause; under B a domain
that omits the class gets a refusal where A gets a finding — and worse, two
engines can find *different* clauses for one enactment if the domain happens to
govern both spellings.

**Ask Custos:** does a designated-class act carry the domain's name for its class
in committed bytes, or is a clause expected to govern the designation §10 gives?

---

## Q31 — What is a threshold defeat's subcode? **DIVERGENT**

*New at integration, where `Citation.subcode` had to be populated rather than
defaulted.*

**Span:** `:1776–1779` — the subcode is "the defeat's discriminator within its
citation, assigned by the cited clause's own committed enumeration", and "where
the clause defines none, the subcode is empty and orders last". Read against the
canonical selection at `:1766–1770`, where the subcode is the third component.

**Where it bit:** `_citation` in `utina.fold.evaluate`, building the ground of a
defeat where more than one slot declined. Acme's clauses commit no field called
an enumeration of defeats, so the literal reading gives every declination-defeat
an empty subcode, and the canonical selection between two of them then turns on
nothing.

- **Reading A — empty.** The clause defines no enumeration of defeat
  discriminators, so `:1778–1779`'s explicit fallback applies and the subcode is
  empty.
- **Reading B — the declining endorser.** A clause's committed slot list *is* an
  enumeration the clause owns, and the discriminator between two defeats of one
  clause is which slot spent itself. The subcode is then assigned by the cited
  clause's own committed enumeration, exactly as the sentence requires.

**Pinned: B.** Under A the selection sentence is vacuous for the only defeat this
engine can currently reach: two declinations under one clause produce two
citations with identical selection keys, and "two verifiers holding the same
bundle SHALL emit the same defeated finding down to the byte" (`:1766–1770`)
survives only because our tie-break falls through to committed order — which is
the kind of accident that stops being deterministic the moment anything upstream
reorders. Under B the key is total and derived from committed law.

**Divergence:** any question defeated by two or more declinations under one
clause. Under A the engines agree only by accident of iteration order; under B
they cite the lexicographically first declining endorser. The cited declination
is a payload field, so the findings differ directly.

**Ask Custos:** is a clause's slot list an "own committed enumeration" for the
purpose of `:1776–1779`, or does the subcode require a clause to commit a defeat
enumeration explicitly — and if the latter, what makes canonical selection total
for a clause that commits none?


---

## Q32 — Must an endorsement be an ACDC issuance in a registry? **DIVERGENT**

*Found building the keripy substrate. Logged before the code that depends on the
guess, and the guess is knowingly the cheaper of the two readings.*

**Span:** §9's single BCP-14 keyword — the composition rule MUST be committed,
and MAY be expressed in the ACDC edge grammar as the dossier specification
profiles it — read against the endorsement's own committed shape, where a slot
is discharged by an act carrying `act` of `"issue"` and a `disp`.

**Where it bit:** `utina.substrate.keripy`, and `utina.enact.Constructor._dispose`
above it. `"issue"` is the name of a registry operation. If it *means* one, then
an endorsement is an ACDC issued into a transaction event log and the substrate
owes a registry, a schema and a TEL; if it is only a committed field naming what
class of act the endorsement performs, then a signed body carrying that field is
a conforming endorsement and no registry exists at all.

- **Reading A — a committed field.** `act` is one more field in a signed body,
  chosen to name the operation an ACDC encoding would perform, so that the move
  to ACDCs is a re-encoding rather than a rename. Nothing in §9 requires a
  registry, and the only MAY in the section is permissive about the *edge
  grammar*, not mandatory about issuance.
- **Reading B — a registry operation.** An act of the class `issue` is the ACDC
  issuance it is named after. The endorsement is a credential, its authority is
  the issuer's, and its revocability is the registry's — which is why `disp` and
  `act` are separate fields in the first place.

**Pinned: A.** Measured against keripy 2.0.0-dev6, B costs a registry pinned to
v1 inside a v2 KEL (the v2 defaults raise `SerializeError` on `vcp`), a
three-step anchor dance through the transaction-event verifier before `issue()`
will run at all, a resolvable schema, and two further sources of
nondeterminism — a random registry nonce and a wall-clock `dt` on every
credential. None of it is reached by any beat of `docs/demo-script.md`:
revocation is out of scope by construction, since a party who changes their mind
declines, which is another issuance.

**This is the honest long-term shape and we are knowingly not building it
tonight.** The dossier alignment (this.i @ta7vle) makes real ACDC edge groups the
destination, and real issuance is what an edge group would carry. `docs/interfaces.md`
already chose the field names so the swap is a re-encoding, and this entry exists
so the gap is on the record rather than in a commit message. this.i @65buz7.

**Divergence:** everything about the committed bytes of an endorsement, and
therefore its SAID. Under A an endorsement is a body in the corpus; under B it is
a credential whose issuance is a TEL event anchored in the issuer's KEL, and the
corpus holds — something else, which Custos does not say either. Two conforming
engines do not merely disagree on a verdict here; they disagree about what the
evidence *is*.

**SETTLED 2026-08-15, by a ruling that lands between the readings** (this.i
@7db5c4, @vi4t4i; tick 2coc). An endorsement is now a real ACDC — the v1 ilkless
shape, the dossier's single normative schema, a fixed fixture `dt`, signed over
its own bytes and sealed into the issuer's KEL by an interaction event — and
there is still no registry, because the dossier's own Endorsed predicate
(dossier-spec-body.md:223) is signed + `disp` + `act` + expected issuer +
anchored, with revocation not a term in it and no registry field in the
normative schema. So B was right that the endorsement is a credential and wrong
that a credential needs a TEL; A's cost argument survives only for the registry
half it originally priced. What the corpus holds is answered by embedding: the
governance event carries the credential in its body and keeps the corpus's own
sealing discipline, so the fold's inputs stay closed at committed values.
Revocation remains open as tick 56js, and the dossier-shaped door is an
RMxN/RMxQ revocation operator in the law rather than a registry on the
credential. The composition-rule half of §9's MAY stays domain-native; tick
5psg holds the wide commission.

**Ask Custos:** does an endorsement's `act` of `"issue"` denote an ACDC issuance
in a credential registry, or is it a committed classification of the act with no
registry implied? If the former, what is the committed form the fold folds — the
credential, the TEL event, or the anchoring KEL event — and how does an evaluator
with no network resolve the schema that issuance requires?

---

## Q33 — At which coordinate does an affirmed enactment take force? **DIVERGENT**

*New at demo 2. The companion to Q3, which settles which law judges an enactment and says nothing about when the edition it commits begins to bind.*

**Span:** `:207` ("the fold never writes, it reads the successor law the enactment left"); `:214-215` (a ratification is an enactment, an enactment is judged under the Constitution it amends, "and the judgment is a finding like any other"); `:1796-1800` (defeat annihilates upward, voiding "what was built on it"); `:3001-3003` (a ratified document's clauses "are the GARD's law for every position at and after the effectuation coordinate, and SHALL bind no position before it"). The phrase "effectuation coordinate" appears at `:3001-3002` and `:3041` and is nowhere defined; `:2999` names effectuation as the third step of an operational ceremony whose "circumstances remain outside the ratified bytes".

**Where it bit:** `Constitution.at`. utina keyed force on the enactment being *committed*, which is one of the three readings below and the weakest of them.

- **Reading A — the enactment's own coordinate.** Permitted by `:207` read alone: the enactment "left" a successor law, and the fold reads it. Under this reading an enactment that nobody endorsed, or that was defeated, changes the law exactly as an affirmed one does — the law fold never consults an endorsement at all, so an unendorsed unilateral commitment is a lawful amendment.
- **Reading B — the coordinate at which the enactment is first affirmed.** Permitted by `:214-215` with `:3001-3003`: the enactment is judged like any other act, so what it commits binds from where its judgment carried, which is where the effectuation coordinate falls.
- **Reading C — the coordinate after the one at which it is first affirmed.** Permitted by reading the succession rule at `:2270-2272` ("law never applies to itself at a coordinate, only to its successor at the next") as ranging over the affirmation rather than over the commitment.

**Pinned: B.** A defeats itself against `:214-215`: a judgment "like any other" whose value changes nothing about whether the law changes is not a judgment. `:1796-1800` points the same way, though it is an extension rather than a ruling on this case — defeat voids "what was built on" a defeated finding, and its examples run up to the enactment and stop short of the edition the enactment leaves. Between B and C, `:3001-3003` binds "at and after the effectuation coordinate", and the coordinate at which an enactment carried is the coordinate at which it took effect — under C the coordinate that seats a board is a coordinate the board's own law does not yet govern, which is a distinction nothing committed marks. `this.i` @xhtvuxnc.

**Divergence.** Between A and B, every position between an enactment and its affirmation, and every record in which an enactment is unendorsed or defeated: two conforming engines return findings under different editions on identical bytes, and one of them lets any single party amend the law alone. Between B and C, exactly one coordinate — the affirming one — which is enough for two engines to disagree about a beat asked there.

**What B does not settle, and what utina cannot express.** Once force is keyed to affirmation, an enactment's commitment order and its effectuation order can disagree: commit two amendments to one predecessor, affirm the second before the first, and two editions become in force at coordinates whose order is the reverse of their events'. `:3038-3050` rules that case, in the clause where Custos governs its own succession and calls it "the same discipline this standard imposes on every governed corpus, applied to itself" (`:2992-2994`) — the successor cites its predecessor's bytes, eligibility is latest-unsuperseded, and "where two enactments claim the same predecessor, the GEL's committed order rules: the earlier lawful enactment is the succession, and the later travels as evidence — of error or of duplicity." utina cannot apply either half: its enactment events carry a law body and no predecessor citation, so nothing committed says which predecessor an enactment claims, and "already superseded at that coordinate" has no committed term to test. The law fold keeps its walk in canonical order and therefore resolves such a fork to the last law event in force, which is an artifact of the walk and not a reading of the text. Every record utina builds has a linear succession, where the two rules cannot disagree.

**Ask Custos** — filed as [`Nicholas-Keystate/custos#96`](https://github.com/Nicholas-Keystate/custos/issues/96), both halves. Define the effectuation coordinate. Does an enactment's edition bind from the coordinate at which the enactment reaches unity, and does an enactment that is defeated or never affirmed confer nothing? This is R4 in `docs/custos-proposals.md`, where it is stated as a requirement rather than a reading; one sentence at the succession rule closes both. Second, and consequent: §17's succession record and fork rule presume a committed predecessor citation on every enactment, and §18's GEL event grammar never obliges one. Either §18 owes the field, or §17 owes the rule that applies without it.

**Amended 2026-09-24: utina now applies both halves** (`this.i` @fougolzt). An enactment may cite its predecessor in `prior`, and Acme's two amendments do. One citing anything other than the edition in force at its own coordinate confers nothing. One citing nothing claims that edition, which is utina's answer to the "or" above: §17's rule applies to the claim whether the claim is cited or implicit. The law in force is then a chain from the founding law, and from each edition the succession is the earliest claimant in GEL order that has taken force. The last-in-canonical-order artifact is gone. `Constitution.succession` derives the record 3039-3042 asks for. The case this entry warned about now has a stated answer, and it is worth reading because it is where affirmation-keyed force meets the fork rule. If two enactments claim one predecessor and the later is affirmed first, the later is in force until the earlier is affirmed, and the earlier is in force from then on. Each position is computed from its own bundle and nothing is rewritten, but the law moves twice. Under Reading A this cannot arise, since force would key on commitment. **Ask Custos**, in addition: is "the earlier lawful enactment" earlier by commitment or by effectuation, and may the law in force move back from a later claimant to an earlier one?

## Q34 — Is a decision consequential when its votes are cast, or when the tally is certified? **DIVERGENT**

*New 2026-09-23, from Daniel. The question the fold had never asked, because it had always answered it one way without noticing there was a choice.*

**Span:** `:1502-1507` (the Ground Axiom: a finding carries what it rests on); `:1622` ("decidable and affirmation reachable"); the four findings at `:1527`; and — the load-bearing absence — nothing anywhere that names a moment at which an act becomes authorized. `dossier-spec-body.md:377-379` is the nearest committed machinery: a joint issuance MAY advertise a **finalization event** through its `fi` field, and a **finalizer** who "observes the threshold to be met" anchors the threshold-satisfying proofs in that AID's KEL, which "a verifier SHOULD use as the definitive proof of issuance."

**Where it bit:** `evaluate`. utina affirmed an act the moment its slot weights summed to unity, with no event marking that they had.

- **Reading A — cast.** The threshold is a property of the evidence bundle, so an act is authorized at the first coordinate where the weights reach unity, whether or not anybody has noticed. This is what utina did and what the four findings read most naturally as.
- **Reading B — certified.** A threshold being met and an act being authorized are different facts, and the second needs a committed act to exist. The dossier's finalization event is that act, promoted from advisory to constitutive.

**Pinned: B**, and it is a change to Custos rather than a reading of it. The argument is Daniel's and it is an analogy that survives pushing: an election is not consequential when votes are cast, nor when a pollster guesses at them, but when they are officially tabulated and certified. Reading A makes the moment of authorization a fact nobody commits, computable only by whoever happens to hold the whole bundle — and by Custos's own observation premise at `:2969-2975`, "completeness of view is never a committed property of any enumerable party." So under A the moment an act became lawful is a function of who is asking and what they have seen, which is precisely the property replayability is supposed to remove. `this.i` @2e2dncfe.

**How utina implements it.** A sponsor gathers the dispositions, issues a dossier ACDC whose edges cite each one with its weight, and the domain verifies that dossier and admits it to the GEL with an event of its own. The certifier is therefore not merely asserting: a verifier walks the edges, recomputes the sum, and a certification claiming more than its edges support contradicts itself on bytes its own sponsor signed. A domain says whether it wants this by naming the schema its certifications must satisfy, exactly as a slot names the endorsement schema its evidence must satisfy (`:1946-1951`); a law naming none requires none, and the clause may override the law's default in either direction.

**Divergence.** Total, on every record. Under A an act with unity reached is affirmed; under B it is pending with a requirement of kind `certification`, at every coordinate until one is admitted. Two conforming engines return different values on identical bytes for every decision in any domain that adopted this.

**Ask Custos.** Should a governance act become consequential only on a committed certification, and if so should the dossier's finalization event be raised from SHOULD-use-as-proof to constitutive for governance acts? Note the smaller shape of the request: the machinery, the roles and the field already exist in the dossier specification and need no invention — what is missing is the sentence making them load-bearing. See also Q36, which is what certification does *not* fix.

---

## Q35 — What does an amendment owe about the acts it ends? **gap**

*New 2026-09-23. This entry replaces a pinned reading that has been withdrawn, and the withdrawal is the interesting part.*

**Span:** `:2649` (an act lawful under the law then in force "remains lawful in the record even after the law that authorized it is superseded" — the retrospective half, which is settled); `:1730-1733` (the monotonicity guarantee is scoped "**at a fixed law head**, never over wall time", so the document knows the across-head case is different and declines to say how); `:1775` (`superseded` is a defeater class, but defined as "a later lawful act displaced the subject" — a competing *act*, not a changed *rule*). The word "disturb" appears **nowhere** in `custos-4.2.md`.

**Where it bit:** utina implemented a declared disturbance set — an amending enactment naming the pending acts it claimed to end, with the fold computing the true set and returning **self-convicted** on a mismatch. That came from issue #82's fifth determination and from `docs/custos-proposals.md` R3, neither of which is ratified, and the demo presented it as conformance.

**Withdrawn 2026-09-23**, by Daniel, on one sentence: an obligation that changes no outcome is not one governance should impose. The declared set was read in exactly two places — the mismatch check and the screen that drew it — and gated nothing. The law changed identically whether it was accurate, wrong or absent, so the field existed only to create something that could be false. It could not always be discharged honestly either: the fold computes the true set at effectuation (Q33) while the declaration is made at commitment, and any party may table an act in the window between, so an honest amender can be convicted for a third party's later act. Demonstrated on a built record rather than argued. `this.i` @ow6dzro4.

**What utina does now.** The substantive rule stands — an act in flight before an enactment took force, whose cure path is closed after, is ended by it, and only where *that act's own clause* moved, which is the specificity that stops an amendment being a way to kill anything inconvenient. The fold computes which, the `disturbance` screen reports them, and nobody is charged with anything.

**Ask Custos.** Two things, and the first is the gap. What becomes of a pending act when the clause governing it is amended, and what becomes of endorsements given under the predecessor? `:1730-1733` says the across-head case is different and stops. This is R3 in `docs/custos-proposals.md`. Second, and only if the first is answered: does an amender owe any *declaration* about the acts it ends — and if the answer is yes, note that the duty must be dischargeable at the coordinate it is made, which the effectuation/commitment gap currently prevents.

---

## Q36 — How is an act evidenced when the domain's own log omits it? **gap**

*New 2026-09-23. Found while working out what certification (Q34) does and does not buy.*

**Span:** `:1114-1120` (GEL events "are sealed into the gAID's KEL by the same anchoring discipline KERI's registry layer uses for TELs"); `:2969-2975` (the observation premise: "completeness of view is never a committed property of any enumerable party… the total view is a join no single party holds"); `:2518-2530` (the **watcher discrepancy report** and the key-state-notice comparison package — two committed object forms by which a watcher evidences that observed key state for an identifier diverges from another observed state, "so the divergence is recomputable from the package rather than believed from the report").

**Where it bit:** working out whether a certifier could suppress a declination. They can, and so can the domain, and no mechanism in the document reaches it.

**The shape of it.** Only the gAID's controller can anchor into the gAID's KEL, so nothing an external party does can put anything in a domain's log. A GEL therefore records what the domain *accepted*, never what the world *did* — which is not a defect to engineer away, it is what a log is, and a company's minute book has the same property. Certification does not fix it: checking a certification against the whole GEL catches a sponsor citing around a disposition the domain already admitted, and nothing catches one the domain never admitted.

**The remedy that exists is asymmetric and is KERI's own posture.** An excluded party's act lives in *their* log, signed and permanent, whether the domain likes it or not. So suppression is not preventable — it is evidenceable by anyone holding both logs, exactly as duplicity is evidenced rather than prevented.

**The gap.** `:2518-2530` is the right machinery and the wrong scope. The watcher discrepancy report is defined over **key state** divergence. There is no committed object form for "this party committed an act bearing on a governed question, and the domain's governance log does not contain it."

**Ask Custos.** Does the cross-frame discipline's evidence production extend to governance-tier omission, and if so what is the committed form? The discrepancy report is the pattern to copy rather than a new invention. Worth noting for whoever files it: the 2025 US electoral-certification dispute is the same shape — the attack was on the certifying step rather than on the votes, and the check that held was that the states held their own records, so the divergence was computable by anyone who cared to look.

---

## Q37 — May a clause slot seat an office rather than name a party? **DIVERGENT**

*New 2026-09-24, from Daniel: "We have to change the law to create a board seat. We don't change the law to fill the seat."*

**Span:** `:2139-2148` — "Seated organs SHOULD be delegated identifiers of the gAID… The seat grant itself takes credential form where the objects section types it: **a seat credential naming the organ's AID as issuee**, issued under the domain's registry"; `:1924` (§9 delegates to the Constitution which schemas, issued by which registries, confer which powers); `:1946-1951` (each slot names the schema its evidence must satisfy).

**Where it bit:** utina's clause slots named an AID, always. Seating an office therefore meant slotting the office's AID, so appointing or removing a director was an amendment to the committed law.

- **Reading A — a slot names an AID.** The literal reading of every slot example. Who may act is committed law, and changing who holds a seat is changing the law.
- **Reading B — a slot may seat an office, and a credential says who fills it.** `:2145` names the seat credential's issuee, and `:1924` delegates to the Constitution what confers a power — so a slot can commit the *qualification* and leave the holder to the record.

**Pinned: B.** Creating a seat is an amendment, filling it is an issuance, vacating it is a revocation, and only the first touches the law. Under A, personnel is constitutional: a company amends its operating agreement to replace a director, which is not how any real governance works and not something the text requires. `this.i` @ftjpdph5.

**A second reading, settled the same day, that B depends on.** "The organ's AID" at `:2145` is an AID **its holder owns**, dedicated to that capacity — the role-dedicated-AID model, one AID per person-and-role pair. Under the alternative reading, where the organ's AID belongs to the domain, a record can contain no accountable human at all: utina's did, and Nina appeared in zero committed events while duplicity attached to an abstraction of Acme's. The ratified text does not distinguish the two readings and both are lawful, which is the divergence.

**Divergence.** Two conforming engines given one committed law disagree about who may fill a slot, and about whether a change of officeholder requires an amendment. Under A a revocation cannot empty a slot without the law moving; under B it does, at the next coordinate.

**Two consequences utina pins, which the text does not.** An office two parties hold at once is **refused** rather than adjudicated: `MxN` commits "exactly N slots, one per candidate endorser" (`dossier-spec-body.md:369`), two standing seatings break that structurally, and nothing says which supersedes. An office held by many *by design*, whose count moves, is not that defect — it is the dossier's `MxQ`, an open-ended set of qualified endorsers, which utina does not implement (tick `5psg`). And a vacant office is **pending under its own name** rather than under nobody's.

**Ask Custos.** May a clause slot commit an office and no identifier, with the holder resolved from standing credentials? If so, `:2145`'s "the organ's AID" wants a sentence saying whose AID that is — the holder's, dedicated to the capacity — because the alternative reading produces records in which no human is accountable for anything.

## Q38 — A subject convicted while slots are still open: pending or self-convicted? **DIVERGENT**

*New 2026-09-24, from an outside comparison of two engines' codomains. Neither this register nor `this.i` had recorded the choice, because utina made it by where it put one call.*

**Span:** `:1664-1671` (the transition table: pending → self-convicted when "a bearing contradictory pair, or new governed-status evidence … enters the bundle"); `:1753-1762` ("no finding is terminal while any enumerated check in the question's committed requirement space is unexamined. An evaluator holding a bundle that leaves any enumerated check unexamined returns pending with that check as its typed requirement"); `:1563` and `:1575` (pending species "describe cure paths", and each species "names its cure").

**Where it bit:** `evaluate`, at a question whose subject is convicted by a bearing pair at or before the position while some slot of the governing clause has no disposition. `_tainted` runs after the requirement space is built and before any verdict is chosen (`src/utina/fold/evaluate.py:194-196`), so its answer wins over every other.

- **Reading A — conviction wins.** A bearing conviction is itself one of the enumerated checks, and once it has been examined and fires, the finding is self-convicted whatever else is outstanding. The transition table's condition for pending → self-convicted is the pair *entering the bundle*, not the requirement set discharging.
- **Reading B — pending wins.** An open slot is an unexamined check, and `:1753-1762` says no finding is terminal while one exists, so the evaluator returns pending naming the open slots and consults convictions only once every requirement has discharged.

Both readings cite `:1753-1762`, and the text supports each. They part on what "unexamined" means: whether a slot the evaluator looked at and found empty has been examined (A) or has not, because its evidence has not yet arrived (B).

**Pinned: A.** Three reasons. First, under B the table's pending → self-convicted edge does not fire when its stated condition occurs: the pair enters the bundle and the finding stays pending, and it moves to self-convicted only later, when the last missing endorsement arrives — an event the table does not name as the edge's condition. Second, a pending finding's requirement names a cure (`:1575`), and under B the cure it names is false. The arrival of the missing endorsements does not bring the question to a lawful value; it brings it to self-convicted, and no missing bytes cure a conviction. Third, B makes the conviction's visibility depend on how many other parties have acted, so a subject whose question is still collecting endorsements is shielded from its own contradiction for as long as someone withholds. `this.i` @zmlvpkhl; pinned by `tests/test_evaluate.py::test_a_convicted_subject_is_convicted_while_its_slots_are_still_open`.

**What A does not change.** The third-party arm is the same dispatch. A convicted *cited* party taints the voice rather than convicting the question (`this.i` @f3pmxu3x), and the taint returns pending with species unresolved-conflict, so under either reading a taint yields pending; the readings differ only in which requirement elements that pending carries. utina's carries every taint and nothing else, and a subject conviction anywhere in the walk beats every taint.

**Divergence.** On every record where a subject is convicted before its question's requirement set has discharged, two conforming engines return self-convicted and pending on identical bytes. The case is reachable in any domain where a party can contradict itself while a vote is still open.

**A sibling, recorded here because it is the same missing rule.** Reading B, applied consistently, also puts pending ahead of defeat when a question has several requirements and one is defeated while another is open, which `:1760-1762` supports in as many words ("never defeated either"). utina never reaches that case because a question is governed by one clause and one group, and within a group a declination that forecloses unity defeats whatever slots remain (Q1, Q16). An engine composing several requirements per question does reach it.

**Ask Custos.** The transition table says which edges are lawful and not which value wins where several are supportable at one position. State a precedence among the four values, or define "unexamined" so that it settles one: does a slot whose evidence has not arrived count as an unexamined check?

## Q45 — How can a founding law designate a registry that names the gAID, when the founding law may not name the gAID? **gap**

*New 2026-09-24, found building the genesis knot. Q39–Q44 are left for the certification work in flight.*

**Span:** `:1073-1087` (a born-governed genesis is `(K0, C)`; K0 seals C; "the gAID SHALL NOT appear in C or in any body C cites, transitively"; C "refers to the domain's authority only through a reserved sentinel resolved at verification"); `:3151-3153` ("a domain's founding law SHALL commit the identifier of the governance registry it designates as its GEL, at inception grade, sealed by the genesis knot").

**Where it bit:** `Constructor.found`. A KERI registry's identifier is a digest over its inception, which names its controller, so the registry's identifier depends on the gAID. The gAID depends on K0, K0 on C, and 3151 puts the registry's identifier in C. Read literally, the two sentences cannot both hold for a KERI registry.

- **Reading A — the designation lives in the knot, not in C.** The gAID's first rotation seals both the founding law and a registry inception naming the gAID. Lawful, and it is how another engine builds its knot, but the identifier is then committed by a rotation and not by the founding law.
- **Reading B — the sentinel reaches the registry.** The GEL's identifier digests a registry inception that names its controller through the sentinel rather than as the gAID. C can then commit it outright, and the sentinel resolves to whichever prefix's inception seals C.
- **Reading C — C commits the inputs, and the verifier derives the identifier.** C commits a nonce, and the identifier is recomputed from `(gAID, nonce)` at verification. C then commits no identifier at all.

**Pinned: B** (`this.i` @ryh5orta). It is the only reading under which C itself commits an identifier, as 3151 says, without naming the gAID, as 1085 forbids. The sentinel's value is ours to choose, because the text reserves one without giving it: utina uses `#gAID`, which is outside the qb64 alphabet. The cost is that utina's GEL identifier is not a KERI registry, and no KERI tool resolves a TEL for it. That is consistent with utina speaking its own governance ilks (track two, `:3119-3127`), and it would not be available to a track-one domain whose GEL events are registry forms.

**Divergence:** the designation's committed location and the GEL identifier's bytes. Under A a verifier finds the designation in the first rotation, and under B and C in the founding law. Two engines therefore disagree about whether a record with an empty rotation seal list is designated.

**Ask Custos:** does 1085's exclusion extend to the designated registry's identifier? If it does, which cut breaks the cycle: the knot (A), the sentinel (B) or derivation (C)? And what is the sentinel's reserved value? Two engines choosing different sentinels produce different founding-law bytes from one intent.

---

*Further underdetermination found by the requirements audit, not all of which
utina has had to decide yet, is in
`../../thesmo-demo/audit-spec-requirements.md` §2 (U1–U13). Entries move here as
the build actually hits them.*
