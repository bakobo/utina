# Questions against Custos — the slot surface

*Underdetermination found while building the slot predicate and the threshold
arithmetic. Same shape and same standing as `custos-questions.md`: the span, each
lawful reading with the lines permitting it, the reading we pinned, and whether
two conforming engines can disagree on committed bytes. Entries here are numbered
`S1…` so they can be merged into the main register without renumbering it.*

Line references are into `spec/custos-4.2.md` in the Custos repository unless
stated. `dossier-spec-body.md` references are into
`kswg-dossier-specification/spec/dossier-spec-body.md`.

Custos §9 is thin on this surface by design — it carries **one** BCP-14 keyword
in its whole length (`:1945`) and cites the dossier specification rather than
restating it. Almost everything an implementer needs to decide about slots is
therefore ours, which is why this file is longer than the surface looks.

---

## S1 — An *unreachable* group: §9 says pending, and we pinned defeated **DIVERGENT**

**Where it bit:** every beat of the demo's centerpiece, D3 against D6.

`custos-questions.md` Q1 records this pin and says neither Custos nor the dossier
specification says what an unreachable threshold produces. That is not quite
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

**Pinned: B**, unchanged, but with less confidence than Q1 records. The
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

## S2 — A requirement element's fields are enumerated twice, differently **DIVERGENT**

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

## S3 — How is an endorsement retracted, and what does the slot fall back to? **DIVERGENT**

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

## S4 — Which endorsement fills a slot, when the evidence is flat? **DIVERGENT**

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

**Pinned: B** (`intent-slots.md` @2pfkyg). Under A the law would have to be amended
before it could be endorsed, which inverts the order of every governance act.

**Divergence:** an endorsement issued by the right endorser, naming the right
subject, but not referenced by the slot. Under A it contributes nothing; under B
it reaches unity. Two conforming engines return affirmed and pending on identical
committed bytes.

**Ask Custos:** for composed evidence whose slots are committed in a domain's law
rather than in an instance dossier, is the slot–endorsement relation a reference
or a predicate?

---

## S5 — One endorser, two contradictory acts on one subject **DIVERGENT**

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

## S6 — Is a slot's weight bounded? **DIVERGENT**

**Where it bit:** `Slot` construction.

Custos delegates the weight to the dossier's grammar; the dossier bounds only the
sum — "satisfied when the weights of the slots that hold valid endorsements sum to
at least unity" (dossier-spec-body.md:353) — and gives examples only of positive
fractions.

- **Reading A — unbounded rationals.** Nothing forbids `w=0` or `w<0`.
- **Reading B — strictly positive.** A weight is a share of authority, and the
  language of "how much each is worth" (dossier-spec-body.md:353) presupposes it.

**Pinned: B**; a non-positive weight is refused at construction
(`intent-slots.md` @anoz6j).

**Divergence:** committed law carrying a negative weight. Under A an endorsement
*reduces* the sum, so an endorser defeats a decision by endorsing it and a
declination becomes the pro-decision act — a governance inversion reachable from
one character of committed law. Under B the law is refused. This is the entry with
the worst consequence-per-word ratio in the file.

**Ask Custos:** should §9 bound an individual slot weight, or say explicitly that
bounding it is the domain's business?

---

## S7 — Law whose slots cannot sum to unity **DIVERGENT**

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

*Standing, as `custos-questions.md` says: utina's implementers may read anything,
so these are not independent readings the way thesmo's are. Each says "we could
not tell what was meant", which is weaker than "a blind implementer read it the
other way" — but S1, S2 and S6 would each have bitten a blind implementer too.*
