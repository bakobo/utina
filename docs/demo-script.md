# Acme, Inc. — demo script and acceptance oracle

*Written 2026-08-11. This file is the oracle: nothing gets built that it does not call for,
and every row below is a test before it is a demo beat. It doubles as the run-of-show.*

Moves to `utina/docs/demo-script.md` when the repo exists.

## Parties

| Party | Role | AID |
|---|---|---|
| Marta Reyes | founder | `acme:marta` (facade AID; real AID after the keripy commission) |
| Dev Patel | founder | `acme:dev` |
| Nina Adeyemi | outside director, seated at E4 | `acme:nina` |
| Acme, Inc. | the governed domain (gAID) | `acme:gaid` |

## The law, expressed as weighted slot groups

Acme's committed law expresses every composition rule as an edge group: an operator, a set of
slots, each slot naming its expected endorser and carrying a weight. A group is satisfied when
the weights of its **Endorsed** slots sum to at least unity. This is the dossier
specification's threshold shape, adopted as Acme's own committed law rather than consumed as
an external semantics — see the decision note at the end.

Each slot is in exactly one disposition:

- **Pending** — no signed act from the named endorser. Contributes nothing. A pending slot and
  an absent slot are equivalent in trust terms.
- **Endorsed** — a signed endorsement from the named endorser, `disp: "endorse"`, whose `said`
  attribute equals the decision's SAID. Its weight is added.
- **Declined** — the same signed act with `disp: "decline"`. Contributes nothing to the sum,
  but records attributable dissent, and — decisively — *spends* the slot, so its weight is no
  longer reachable.

An active "no" is always a signed declination, never a silent slot.

### State 1 — from inception (clauses A1, A2)

| Clause | Governs | Slots | Effect |
|---|---|---|---|
| A1 | ordinary acts | Marta `w=1/2`, Dev `w=1/2` | both required |
| A2 | amendment of the operating agreement | Marta `w=1/2`, Dev `w=1/2` | both required |

### State 2 — after E4 seats the board (clauses B1, B2)

| Clause | Governs | Slots | Effect |
|---|---|---|---|
| B1 | ordinary acts | Marta `w=1/2`, Dev `w=1/2`, Nina `w=1/2` | any two reach unity |
| B2 | amendment of the operating agreement | Marta `w=1/3`, Dev `w=1/3`, Nina `w=1/3` | all three required |

The retained higher bar at B2 is the point: seating a board distributes ordinary authority
without distributing the authority to change the rules.

## The beats

| # | State | Question | Slots | Sum | Expected | Ground it must carry |
|---|---|---|---|---|---|---|
| D1 | 1 | Open a bank account | Marta E, Dev E | 1.0 | **affirmed** | clause A1 + both endorsement SAIDs |
| D2 | 1 | Hire a VP of Sales | Marta E, Dev P | 0.5 | **pending** | typed requirement naming Dev's slot |
| D3 | 1 | Hire a VP of Sales, after Dev declines | Marta E, Dev **D** | 0.5 | **defeated** | Dev's declination SAID + clause A1; unity unreachable |
| D4 | 1→2 | Seat the board (the amendment itself) | Marta E, Dev E under **A2** | 1.0 | **affirmed** | judged under the law it replaces; anchored in an establishment event |
| D5 | 2 | Approve the annual budget | Marta E, Nina E, Dev P | 1.0 | **affirmed** | unity reached though one party never acted |
| D6 | 2 | Approve the annual budget, after Dev declines | Marta E, Dev **D**, Nina P | 0.5 | **pending** | Nina's slot still reachable |
| D7 | 2 | Amend the operating agreement | Marta E, Dev E, Nina **D** under **B2** | 2/3 | **defeated** | the retained bar bites; unity unreachable |
| D8 | 2 | May the board declare a dividend? | — no clause governs distributions | — | **refusal** | names the missing rule; not a finding |
| D9 | — | Re-ask D1 at a position after the amendment | as D1 | 1.0 | **affirmed** | under clause A1, the law in force *then* |
| D10 | — | Refold the log with events in permuted arrival order | — | — | **byte-identical Constitution** | `custos-4.2.md:3101`, binding |

E = Endorsed, P = Pending, D = Declined.

### What each beat is for

- **D3 against D6** is the centerpiece. The same signed "no" from the same person is *defeat*
  under the founders and *pending* under the board — not because the engine treats Dev
  differently, but because with two slots a declination makes unity unreachable, and with
  three it does not. The Constitution changed; the arithmetic did the rest.
- **D2 against D5** is the secondary contrast: a decision can be affirmed while a party has
  never acted, and pending while one has. Presence is not the question; reachable weight is.
- **D8** is the beat for this audience. The engine refuses rather than legislating, and names
  what is missing. Custos's own axiom 3, shown rather than asserted.
- **D9** is the utility claim: the past is recomputable under the law in force then.
- **D10** is cheap to run and binding in the spec. One command, same bytes.

Cut order if the clock runs out: D10, then D5, then D7. **D3 and D6 are never cut.**

## Decision note — why the law is domain-native and dossier-shaped

Custos §9 carries one BCP-14 keyword in its length (`custos-4.2.md:1945`): the composition rule
MUST be committed, and MAY be expressed in the ACDC edge grammar. Expressing it as real ACDC
edge groups makes the dossier specification an external semantics, which axiom 4
(`custos-4.2.md:290`) then requires be pinned by committed digest, with anything unpinned
refused. That obligation is the long-term destination and not a Friday problem.

So the law is expressed as Acme's own committed clause predicate, in a structure isomorphic to
the dossier's threshold operators: the same operator/slot/weight shape, the same unity
threshold, the same three dispositions, the same `disp` and `act` field names, the same
endorsement-references-the-decision-SAID relation. The fold's slot predicate and threshold
arithmetic are written against that shape. When the keripy commission swaps the encoding to
real ACDC edge groups and adds the semantics pin, the substrate changes and the fold does not.

The trap this deliberately avoids, in Custos's own words: an implementer who "wires the
substrate's threshold evaluator to an edge group and concludes the obligation is discharged has
discharged the arithmetic and none of the slot dispositions." keripy's `Tholder` is a key-state
threshold over signature indices and cannot answer a governance question, which is why
`utina.fold` computes the slot predicate itself.
