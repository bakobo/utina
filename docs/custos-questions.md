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
| Q4 | what does affirmed carry | — | Q4 |
| Q5 | how does species order in the canonical total order | DIVERGENT | QC1 |
| Q6 | which defeater class does a declination produce | DIVERGENT | QC2 |
| Q7 | an empty subcode is the minimum, yet orders last | DIVERGENT | QC3 |
| Q8 | may a pending carry an empty requirement set | DIVERGENT | QC4 |
| Q9 | the refusal record has no committed form | convergent | QC5 |
| Q10 | "citing-clause bytes" has no stated flattening | convergent here | QC6 |
| Q11 | intra-anchor order with no seal index | DIVERGENT | QL1 |
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
| Q24 | canonical order with no KEL to derive it from | convergent | S2 (substrate) |
| Q25 | is the anchoring establishment event in the GEL | DIVERGENT | S3 (substrate) |
| Q26 | what a prospective question binds to | DIVERGENT | S4 (substrate) |
| Q27 | are signatures in the bytes the SAID digests | convergent | S5 (substrate) |
| Q28 | may a requirement element omit its species | DIVERGENT | S6 (substrate) |
| Q29 | which law judges a prospective question | DIVERGENT | new at integration |
| Q30 | what act class does an enactment perform | DIVERGENT | new at integration |
| Q31 | what is a threshold defeat's subcode | DIVERGENT | new at integration |

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

## Q9 — The refusal record has no committed form *(convergent; deliberately open)*

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

**Ask Custos:** is the retraction of an endorsement a governed act with a
committed form, or is it outside the composed-evidence rule entirely?

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

*Further underdetermination found by the requirements audit, not all of which
utina has had to decide yet, is in
`../../thesmo-demo/audit-spec-requirements.md` §2 (U1–U13). Entries move here as
the build actually hits them.*
