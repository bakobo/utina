# Questions against Custos — the codomain commission

*Where building the four-valued codomain, the closed triple, refusal and the two
question constructors required guessing what the specification means. Same shape
as `custos-questions.md`; the orchestrator folds these in and renumbers. Ids are
`QC*` here so a fold-in cannot collide with the `Q*` series already there.*

Line references are into `/home/daniel/code/3GR/custos/spec/custos-4.2.md`.

Q4 in `custos-questions.md` — what `affirmed` carries — is the fourth guess this
commission depends on. It is already registered, so it is not repeated here;
`Affirmed` carries the clause set, the endorsements that reached unity, and the
bundle identity, which is Q4's pin.

---

## QC1 — How does `species` order inside the canonical four-field total order? **DIVERGENT**

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

## QC2 — Which defeater class does a signed declination produce? **DIVERGENT**

**Where it bit:** the demo's centerpiece. Custos Q1 already pins *that* an
unreachable threshold is `defeated`; this is the next question, which Q1 does not
reach. A defeated finding SHALL carry its defeater class (`:1641-1646`), and the
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

## QC3 — An empty subcode is the lexicographic minimum, yet "orders last" **DIVERGENT**

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

## QC4 — May a `pending` finding carry an empty requirement set? **DIVERGENT**

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

## QC5 — The refusal record has no committed form *(convergent; deliberately open)*

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

## QC6 — "Citing-clause bytes" has no stated flattening *(convergent here; DIVERGENT for anyone else)*

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
