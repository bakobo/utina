# Questions against Custos, from building the command line

*Companion to `docs/custos-questions.md`, in that file's shape and under its standing:
utina is **not** a blind implementation, so an entry here says "we could not tell what was
meant," which is a weaker and more practical claim than thesmo's. Line references are into
`custos-4.2.md`. Numbered `C1`, `C2`, … to avoid colliding with the `Q` series; fold into
it at integration.*

Most of what the CLI decided is not Custos's business. How wide a column is, whether the
verdict leads or the arithmetic does, what a screen is painted in — those are taste, and
they are recorded as this.i nodes in `docs/intent-cli.md`, not here. Two things were not
taste: the CLI made a question reachable that the fold's own register does not cover, and
building a display of a finding raised a question about what the Ground Axiom binds.

| C | Question | Mark |
|---|---|---|
| C1 | a prospective question about a class with **nothing** tabled | DIVERGENT |
| C2 | does the Ground Axiom bind a *rendering* of a finding, or only the value | convergent |

---

## C1 — What does a prospective question answer when no act of the class has been tabled at all? **DIVERGENT**

**Span:** `:225`–`:231`, the pending-versus-refusal boundary; `:1522`–`:1526`, the ground a
pending finding carries; `:1619`–`:1621`, "the law commits the question's requirement space
ex-ante."

**Where it bit:** `utina eval open-bank-account --at inception`. Clause A1 is in force and
governs the class, and no act of that class has been committed at that coordinate. The
command answers, and this is the screen:

```
  PENDING     may Acme perform an act of the class open-bank-account?

  subject     nothing of this class has been tabled at this position
  ...
  ground - what would discharge this
    acme:dev    endorsement under clause A1, absent
    acme:marta  endorsement under clause A1, absent
```

`docs/custos-questions.md` Q26 asks what a prospective question binds to when **several**
acts share a class, and pins the latest. It does not reach the case of **none**, and the
two are not the same question: Q26 chooses among subjects, and this one asks whether there
is a question at all.

- **Reading A — pending, naming the slots.** The rule exists and the evidence is short,
  which is exactly the boundary `:225`–`:228` draws: "where committed evidence runs short
  under a committed rule, its finding is pending." The law commits the requirement space
  ex-ante (`:1619`–`:1621`), so the space is computable before anything is tabled, and a
  prospective question is asked precisely to see it.
- **Reading B — refusal.** `:228`–`:231` refuses "where no committed rule makes the
  invocation evaluable at all," and there is a sense in which nothing here is evaluable:
  there is no committed regime for the judgment to be a judgment *over*. The fold already
  reads it this way for the other constructor — a `Committed` question naming bytes nobody
  committed is refused, in those words — and the two constructors are answering the same
  underlying condition differently.

**Pinned: A**, which is what `utina.fold.evaluate` already implements by handing its slot
predicate an empty subject.

**Divergence:** two conforming engines return different values — a pending finding against
an operational fact — on the same committed bytes and the same question. It is not on the
demo's critical path, because every beat asks about a class that has been tabled.

**The part we think is a defect rather than a preference.** Under Reading A the requirement
set names endorsements as the cure, and an endorsement's `said` attribute must equal the
subject's identifier (`docs/interfaces.md`, and the dossier's shape). There is no subject,
so no endorsement can be written that would discharge this finding. The Ground Axiom makes
the cure path part of what a pending *is* (`:1522`–`:1526`), and here the cure path names
an act nobody can perform yet. Either the requirement set should carry a further element —
the tabling of the act itself — or the answer should be a refusal. The screen above is what
made this visible: the subject line and the ground block contradict each other in plain
sight.

**Ask Custos:** is a prospective question about an ungrounded act class evaluable, and if
it is pending, does its typed requirement set have to name the tabling as well as the
endorsements?

---

## C2 — Does the Ground Axiom constrain a rendering of a finding, or only the value? convergent

**Span:** `:1503`–`:1512`. "A finding is a judgment over a committed regime that carries its
own ground … A value that does not carry its ground is not a member of this type, whatever
else it may be. This is the Ground Axiom applied as a typing rule."

**Where it bit:** the whole of `utina.cli.render`. Deciding whether the CLI could ever
offer a compact mode that prints `DEFEATED` and stops.

- **Reading A — the axiom is about values inside an engine.** It is stated as a typing
  rule, and a typing rule constrains what the fold may construct and return. What an
  interface then chooses to display is outside the document, which nowhere describes a
  presentation layer.
- **Reading B — the axiom reaches anything that presents itself as a finding.** The
  sentence is unusually broad — "not a member of this type, *whatever else it may be*" — and
  the justification given in the next clause is about what a reader can do: "because every
  finding carries its ground, every finding is checkable by replay." A screen that strips
  the ground has produced something that is not a finding and labelled it with a verdict,
  which is the substitution the axiom exists to forbid.

**Pinned: B**, and this.i @cl1grd makes it structural rather than a policy: the verdict line
and the ground block are emitted by one function, and there is no code path that produces
one without the other.

**Convergent**, and deliberately marked so: no computed value differs between the readings,
and no two engines disagree about any committed bytes. It is logged because the choice is
consequential for anyone building on Custos — a conformance suite that tests only returned
values would pass an engine whose only interface hides the ground — and because it costs
almost nothing to log a non-ambiguity.

**Ask Custos:** is §8.1 meant to bind conformance of an interface that displays findings, or
only of the engine that computes them? If the former, it is the one requirement in the
document that a test over return values cannot check.
