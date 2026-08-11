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

---

## Q1 — Does a declination make a finding `defeated`, or leave it `pending`? **DIVERGENT**

**Where it bit:** the demo's centerpiece. Acme's clause A1 has two slots at
`w=1/2`. Marta endorses; Dev signs a declination. The endorsed weight is 1/2
either way, but no further endorsement can arrive from a slot that is spent, so
unity is now unreachable.

Custos §8 gives four values and their grounds, and the dossier specification
gives the three slot dispositions, but neither says what an evaluator returns
when a threshold is *unreachable* rather than merely *unmet*. The two readings:

- **Reading A — `pending`.** The requirement space is not discharged; the
  typed requirement is the outstanding slot. Nothing in the codomain speaks of
  reachability, and `pending` is defined by what has not yet been shown.
- **Reading B — `defeated`.** The question can no longer be affirmed under this
  clause, and the declination is a committed citation that says so. Leaving it
  `pending` names a requirement that can never be discharged, which makes the
  typed requirement a lie.

**Pinned: B.** A `pending` whose requirement is undischargeable misinforms the
reader, and §8's full-discharge discipline treats a bundle that cannot grow the
missing evidence as one that has settled. Reading A is defensible and we may be
wrong.

**Divergence:** engines disagree on every decision where an endorser declines
and the remaining slots cannot reach unity. Under A the finding is `pending`
forever; under B it is `defeated` with the declination cited.

**Ask Custos:** should the finding codomain distinguish *unmet* from
*unreachable*, or is that a domain-law question the fold must not decide?

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

## Q4 — What does `affirmed` carry?

§8's required-payload enumeration presents itself as complete and does not list
`affirmed`, while the Ground Axiom makes the ground a component of the type.
thesmo's `m1-alpha` reading found the same thing and pinned the payload; a 4.2
seed repairs it. Recorded here because utina's `Affirmed` carries the evidence
bundle identity and the clause set, and a reader comparing utina against the
ratified enumeration will find a field the enumeration does not require.

---

*Further underdetermination found by the requirements audit, not all of which
utina has had to decide yet, is in
`../../thesmo-demo/audit-spec-requirements.md` §2 (U1–U13). Entries move here as
the build actually hits them.*
