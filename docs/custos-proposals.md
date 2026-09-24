# Requirements against the current theories

*Where a governance requirement meets what Custos and utina currently say, and
what has to change in each to reconcile them. Companion to
`custos-questions.md`, and deliberately a separate file.*

## What this file is for

`custos-questions.md` holds ambiguities: a span exists, it admits more than one
lawful reading, utina had to pin one, and two conforming engines could disagree.
Every entry there starts from the text.

This file starts from the requirement. A requirement arrives from the domain
owner, and the ratified text and the shipped code are then two *theories* about
how governance ought to work, both of which may be wrong. Neither is normative
over a requirement. Their value is diagnostic: knowing where a theory already
agrees tells you the change is cheap, knowing where it conflicts tells you which
artifact has to move, and knowing where it is silent tells you nobody has thought
about it yet. An entry that concludes "already settled" has failed — the
conclusion of an entry is always a list of edits.

**Standing.** The question register carries a caveat: utina is not a blind
implementation, so its *readings* are not independent evidence about what Custos
means. That caveat does not bind this file. A requirement is not a reading, and
an entry here stands or falls on the governance argument.

Each entry names the requirement, states what utina does now and what Custos
says now, separates alignment from conflict from silence, and ends in actions
against named artifacts. Line references are into `custos-4.2.md` unless stated.

---

## R1 — An endorser may revoke, and ratification is irrevocable once threshold is reached

**The requirement.** An endorsement can be withdrawn. A withdrawal before the
threshold is reached is effective: the slot's weight goes away and the act may
fail that would otherwise have carried. A withdrawal after the threshold is
reached is inert, because reaching the threshold ratifies the act and
ratification does not unwind.

**What utina does now.** Contradicts the second half. Retraction is
unconditional and retroactive in effect. Measured against the demo corpus: the
bank account is `Affirmed` at `d9`; append one retraction at seq 21 in which Dev
revokes the endorsement he committed at seq 3 — eighteen events after the act
settled — and the same question returns `Pending`, carrying a requirement
element naming Dev's slot `absent`, "cured by the arrival of the missing
evidence." The cure it names is the arrival of evidence that already arrived.
This is `custos-questions.md` Q18's Reading A working exactly as pinned.

**What Custos says now.** Two things, and they point in opposite directions.

*Aligned:* `:1698-1707` tabulates forbidden finding transitions, including
`affirmed → pending` ("evidence does not un-arrive"). `:1708` says no backward
edge exists anywhere in the system. `:1712` names this Terminality and admits one
exception, self-conviction on a contradictory pair. On that text the requirement
and Custos want the same thing.

*In conflict:* `:1734-1741` permits a successor finding to reverse a terminal
value where its grown bundle carries committed evidence **falsifying a ground the
prior finding cites**. An affirmed finding cites its endorsements as its ground.
If a retraction counts as falsifying the endorsement it retracts, Custos permits
precisely the reversal this requirement forbids — at a new position, as a new
finding, but a reversal. Nothing in the text says whether it counts.

`:1701` gestures at the distinction the requirement needs — "taint-cure and
ground-evaporation are different phenomena, and neither is an edge" — but
`ground-evaporation` appears once, is never defined, and is never connected to
the undercut condition four paragraphs later. So the requirement is *not* settled
by Custos. It needs the distinction that `:1701` names in passing to be made
load-bearing.

**The distinction to commit.** Withdrawal is not falsification. A retraction says
"I no longer give this," which is a fact about the endorser's present will. An
undercut says "this ground was never good," which is a fact about the artifact.
Only the second is evidence about the state of affairs the prior finding
appraised, and only the second should reopen it. A system that lets withdrawal
undercut lets any party unilaterally unmake a settled ratification at any
distance, which is the failure the requirement exists to prevent.

**Actions.**

- utina: a retraction is effective only where the act has not settled. Tick
  `5wu5`.
- utina: amend Q18 in `custos-questions.md` — Reading A is not merely a guess
  among three, it is inconsistent with `:1698-1712`, and the pin moves.
- Custos: define `ground-evaporation` at `:1701` and state its relation to the
  undercut condition at `:1734-1741` — specifically, that withdrawal of a cited
  ground is not falsification of it and does not license reversal. This is the
  proposal; the rest of R1 is repair work on utina.

---

## R2 — An act may carry a clock, and lapses if the threshold is not reached in time

**The requirement.** A proposal does not stay live forever. It carries a window,
and unity reached after the window closes does not ratify. The case that makes it
concrete is the US Equal Rights Amendment: proposed in 1972 with a seven-year
ratification deadline, extended to 1982, three states short when the window
closed, and brought to the nominal threshold decades later by Nevada, Illinois
and Virginia. The claim that it thereby took effect was rejected. Note what did
*not* happen there — Article V, the governing law, never changed. The ERA is an
argument for a clock on the proposal, not for supersession, which is R3.

*(Procedural caution for anyone citing this: there was no Supreme Court merits
ruling. The deadline position came from a 2020 OLC opinion; `Illinois v.
Ferriero` was dismissed below and affirmed on standing; certiorari was denied.
Verify the posture before putting it in an upstream document.)*

**What utina does now.** Cannot express it. A committed clause carries an
operator, a set of slots and their weights, and nothing else. Acme's law has
nowhere to write a window, so no act can lapse.

**What Custos says now.** Delegates rather than legislates, and the delegation is
unfinished. `:1924` says the GARD's Constitution names which schemas, issued by
which registries, "under which expiry and supersession semantics," confer which
powers — so expiry is the domain's to commit. `:1584` types the cure:
`expired/abandoned` is a ratified pending species, "cured by re-presentation."
What is missing is any committed form: `:1924` says the Constitution carries
expiry semantics and never says what they look like on the wire.

**Alignment and gap.** The requirement and Custos agree that expiry exists and
belongs to the domain. Neither Custos nor utina supplies a place to write it.
The vocabulary for the *result* is already ratified and should be reused rather
than reinvented.

**Actions.**

- utina: add an expiry term to the clause grammar, and to Acme's committed law.
  Tick `66mh`.
- utina: a lapsed act's requirement elements take `expired/abandoned`, not
  `absent` — the species already exists and already means this.
- demo: a beat in which an act lapses. There is currently no beat that turns on
  time at all.
- Custos: `:1924` delegates expiry semantics to the Constitution but owes no
  committed form for them. Either owe one, or say explicitly that the form is the
  domain's, as the composition rule's form already is.

---

## R3 — A change to the law governing an act ends the window for that act, and only for that act

**The requirement.** An act proposed under one version of the law does not
survive unchanged into another. If the rule governing it changes, the
endorsements gathered under the old rule are spent and the act must be
re-endorsed under the new one. But this is specific, not general: amending some
other part of the law must not touch a pending act whose own rule was left alone.

**Why it is right, stated as the argument rather than the assertion.** An
endorser who signs under a clause requiring two of two signs a bargain in which
their signature is decisive. Under a clause requiring any two of three the
identical signature is dispensable. Carrying it across the amendment converts
what the endorser agreed to, with no new act of will from them. And the
specificity is not a nicety: without it, any party able to enact anything can
kill any inconvenient pending act by amending something irrelevant.

**What utina does now.** Nothing, and cannot. The only change signal available is
the law head, which is an aggregate over the whole clause set, so every amendment
changes it and clause-level granularity is unavailable at that layer. Worse, the
moment of change is itself ill-defined — see R4, which is a prerequisite for this
one.

**What Custos says now.** Settles the completed case and is silent on the
incomplete one. `:2649`: an act "lawful under the Constitution then in force
remains lawful in the record even after the law that authorized it is
superseded." That is the retrospective half, and it is why re-asking an old
question yields the old law.

For an act still in flight, the tell is `:1730-1733`. The monotonicity guarantee
— "no finding is erased, no citation un-happens, every coordinate's fact stands
forever" — is scoped "**at a fixed law head**, never over wall time." The
document knows the across-head case is different and declines to say how.
Everything this requirement asks about lives past that qualifier.

`superseded` does appear as a defeater class at `:1775`, but it is defined as "a
later lawful act displaced the subject" — a competing *act*, not a changed
*rule*. It is a different phenomenon that happens to share the word.

**The mechanism proposed.** Four parts.

1. **Trigger:** the substance of the clause governing this act changed. Compare
   operator, slots and weights between the law in force when the act was tabled
   and the law now. Not the law head, which is too coarse — it moves on every
   amendment. Not the clause identifier, because a clause renamed but otherwise
   identical presents the endorser the same bargain. Not the clause's governed-act
   list, because a clause gaining an unrelated act kind changes nothing for this
   act. Custos already requires each clause to be independently SAID-addressed
   (`:1483`), so per-clause granularity is available and ratified; the comparison
   proposed here is structural rather than over that digest, which keeps the law
   head and the byte-identical replay obligation at `:3101` untouched.
2. **Effect:** the act's endorsements are spent. The act itself survives.
3. **Cure:** re-presentation, with requirement elements typed
   `expired/abandoned` — the same ratified species R2 uses, for the same reason.
   Voiding the act instead would destroy a live matter for a reason unconnected
   to its merits.
4. **Interaction with R1:** an act that has already settled is untouched. R1's
   closure comes first; supersession can only reach an act still in flight.

**Actions.**

- utina: R4 first — the trigger has no well-defined moment until an enactment's
  force is pinned to its affirmation.
- utina: implement the structural clause comparison and the spend. Tick `6pdw`.
- demo: `founding_law` commits {A1, A2} and `board_law` commits {B1, B2}, so
  every clause changes across the amendment and there is no act whose rule
  survives. The specificity half of this requirement — the half that keeps it
  from being an attack — is unshowable until a clause is carried across
  unchanged. That is a demo-script design question, not an implementation detail.
- Custos: this is the one item here that Custos must change to accommodate. It
  should state what becomes of a pending act when the clause governing it is
  amended, and what becomes of endorsements given under the predecessor. If the
  answer is that the domain commits it — as `:1924` does for expiry — then say
  so, and say what the committed form is, because there is nowhere in a clause to
  write it today.

---

## R4 — An enactment confers its successor law only if it carries

**Status.** Not a requirement Daniel stated; surfaced while working R3, and R3
cannot be built without it. Recorded here because it is the same kind of thing.

**What utina does now.** `Constitution.at` treats an enactment as taking force
from its own coordinate onward, keyed on the event being *committed* and never on
its being affirmed. Measured: in the demo record the successor law is in force at
seq 8, one event before the amendment enacting it reaches unity at seq 9. Nothing
in that code path consults endorsements, so a unilaterally committed,
never-endorsed — or actively defeated — enactment changes the law just the same.

**What Custos says now.** Strongly implies the opposite without stating it.
`:214`: "a ratification is an enactment, an enactment is judged under the
Constitution it amends, and the judgment is a finding like any other." `:1795`:
defeat annihilates upward, voiding what was built on a defeated finding. But
`:207` — "the fold never writes, it reads the successor law the enactment left"
— read alone, describes what utina built.

**Actions.**

- utina: pin force to affirmation. Tick `4pmw`.
- Custos: state it at the succession rule. One sentence closes it, and until it
  is closed R3 has no moment to fire on.

---

## Cross-cutting: one primitive under R1, R2 and R3

All three requirements need the same derived value — the coordinate at which an
act stops being in flight. R1 needs it to know when a retraction goes inert; R2
needs it to know whether the clock beat the threshold; R3 needs it to know
whether the act was still reachable when the rule changed. It is the first
coordinate at which any of these holds: unity reached, unity unreachable, the
clock expired, the governing clause superseded.

Two cautions on building it. Custos's model is not that later events become
inert: a finding stands at its coordinate and a later finding is a *new fact at a
new position*, reversible only under the undercut condition (`:1734-1745`). And
computing a first-crossing coordinate makes the fold an ordered scan where it is
currently a set predicate — the replay obligation survives, since canonical order
derives from coordinate and identifier rather than arrival, but
`custos-questions.md` Q20's pin ("a declination is decisive whatever the
committed order") does not, and reopens.
