# Acme, Inc. — demo 2 script and acceptance oracle

*Written 2026-09-09. Successor to [`demo-script.md`](demo-script.md), which stays in force until this one ships. Same contract as its predecessor: this file is the oracle, nothing gets built that it does not call for, and every row below is a test before it is a demo beat.*

Audience: KERI Foundation members who know KERI deeply and have treated governance as a separate problem from verifiable key state. The demo's thesis is that it is the same problem one tier up, and that KERI's own reflexes — replay, duplicity-evidence, no ambient authority, cooperative delegation — already answer it. The closing ask is co-sponsorship of a ToIP work item.

Beat numbers in this file are demo-2 numbering and do **not** correspond to demo-1's `D1`–`D10`. Where a demo-1 beat survives, the mapping is noted in the table.

## Running order and budget

The slot is a one-hour meeting in which Nicholas presents for 20–30 minutes first, teaching the main ideas. **Our part is 30 minutes or less**, to an audience that will have just been taught the four-valued codomain, the fold, and the ground axiom, and therefore does not need them taught again.

The governing measurement: demo 1 took 45 minutes for 10 beats, and the full 10-beat run executes in **0.22 s** on the facade and **1.30 s** under keripy. Compute is free. The entire budget is narration, so the only lever that matters is how many things get explained, and the way to spend 30 minutes well is breadth — the range of what the engine answers — rather than the depth of any one answer.

That yields three artifacts of decreasing liveness and increasing depth.

**Recorded opener, ~4 minutes, played first.** Beats 1–6 under `--substrate keripy`, with real prefixes, closing on `tools/read-keri-log.py` reading Acme's key log with keripy alone and no utina code. This establishes both the ground and the this-is-really-KERI claim, so the live part never has to argue either, and it leaves beats 3 and 5 pending as the live part's setup. Recorded rather than live because it is recap for this audience, and because a pre-baked segment is the right place to spend the fragile minutes.

**Live, ~18 minutes, 12 beats in five kernels.** Chosen on one test: the beats where this audience's own intuition is wrong. Ordered so that the amendment is the hinge — everything after it uses the board it creates, and the act ends with an amendment being convicted, which rhymes with the amendment that opened it.

| Kernel | Beats | What the audience expects | What happens |
|---|---|---|---|
| 1. The amendment as hinge | 7 | a document is adopted | a seat AID is delegated, a seat credential is issued, and the enactment declares what it disturbs |
| 2. What the amendment did to two pending acts | 9, 10 | an amendment changes everything, or nothing | the cure path closes for one and stays open for the other, decided by whether the clause moved |
| 3. Same signed "no", two answers | 13 | a "no" means no | defeat under two slots, pending under three. The Constitution changed; the arithmetic did the rest |
| 4. Two currents, unmerged | 8, 12, 14 | the credential check *is* the answer | the toolchain rejects an unseated endorser before any fold runs, and the fold answers separately |
| 5. Revocation, and what it cannot do | 16, 17, 19, 20 | revoking undoes the decision | it changes the next answer and not the last one — and then duplicity, which does reach back |
| 6. The amendment that lies | 22, 23 | law is a document | a document cannot be convicted of lying about itself; this one is, on its own bytes |

Six kernels, not five — kernel 3 is one beat and rides on the recorded opener's beat 4, which costs a single sentence of recap. Thirteen live beats, of which 8 and 16 are screens rather than evaluations and run in well under a minute, so the realistic live total is 17 to 19 minutes. With the opener and an introduction that leaves five or six minutes of questions inside the half hour, and questions from this room are worth more than a fourteenth beat.

**Leave-behind: the full 25-beat run, recorded, sent with the follow-up.** Not played in the room. This is where beats 5→11's cure, 15's third delegation stratum, 18, 21, 24 and 25 live, at full screen density. The most likely thing this audience does next is try to read the spec, so the leave-behind travels with the readable 4.3 draft and not on its own.

**Substrate: run live under `--substrate keripy`.** It costs 1.3 s for the whole record, so there is no speed argument for the facade, and every identifier on screen being a real prefix is worth more than it costs. Keep `--substrate facade` as the in-room fallback if anything hangs, and say plainly what changed if you use it.

**One implementation ask falls out of this.** A demo-1 eval screen is about 24 lines — right for a depth demo to one person who already knows the system, too much to read aloud in 90 seconds. The live beats need a compact form: verdict, the slot table, and the ground, in eight to ten lines, with the full screen still available and still what the leave-behind records. Call it `--brief`. Every live row below assumes it; every recorded row assumes the full screen.

## Parties

| Party | Role | Alias, as the screens show it | Identifier |
|---|---|---|---|
| Acme, Inc. | the governed domain (gAID) | `9-acme-as-governed-domain` | `acme:gaid` under the facade; a real prefix under keripy |
| Acme's governance registry | the TEL the seat credential is issued under | `9-acme-as-governance-registry` | a real registry identifier under keripy |
| Marta Reyes | founder | `9-marta-as-founder` | `acme:marta` |
| Dev Patel | founder | `9-dev-as-founder` | `acme:dev` |
| Board seat 3 | the office — a **delegated AID of the gAID** | `9-acme-as-board-seat-3` | `acme:seat3` |
| Nina Adeyemi | outside director; holds seat 3's current keys | `9-nina-as-director` | shown as the seat's controller, never as a slot's endorser |
| Nina's signing device | a delegated AID of seat 3 | `9-nina-as-device` | `acme:nina-device` |
| Quinn Osei | an outsider who endorses without a seat | `9-quinn-as-outsider` | `acme:quinn` |

Two changes from demo 1, both load-bearing.

**The seat is an identifier, not a person.** Demo 1 slotted `9-nina-as-director` directly. Demo 2 slots `9-acme-as-board-seat-3`, an office whose keys Nina holds. This is `custos-4.2.md:2139-2148` taken literally — seated organs SHOULD be delegated identifiers of the gAID, so that delegation "dual-anchors the seat's key events (the organ signs; the delegator seals)" and "gives the charter's delegation strata KERI's delegation semantics rather than a metaphor." It also makes tenure expressible: a director leaving is a rotation on the seat, not a reissued credential, which is `custos-4.2.md`'s own claim that tenure is rotation policy.

**A fourth and fifth party exist to be refused.** Quinn endorses without holding the seat, and Nina's device endorses while holding a delegated AID of the seat. One fails credential verification and one passes, and neither outcome is a finding. That contrast is the whole point of Act II.

The middle column is what every screen prints — a [COIA](https://github.com/dhh1128/coia) alias, display-only, never entering a committed byte, with `9` marking a demo environment. Screens never print a fragment of an identifier; `utina whois <alias>` is one command away. Unchanged from demo 1 (`this.i` @clcoia, @cldspl).

## The law

Acme's committed law expresses every composition rule as a **real ACDC edge group** carrying a dossier threshold operator in its `o` field: `MxN` for issuance, `RMxN` for revocation, each member edge a slot naming its expected endorser through the issuer of the ACDC it references, carrying a weight in its reserved `w` field, satisfied when the weights of the **Endorsed** slots sum to at least unity.

This is the upgrade demo 1 deferred. Demo 1's law was a domain-native predicate *isomorphic to* the dossier's shape (`this.i` @ta7vle, tick `5psg`); demo 2's law is the shape itself. Two consequences follow and both are demo material. The dossier specification becomes an external semantics, which axiom 4 (`custos-4.2.md:290`) then requires be pinned by committed digest — so Acme's founding law carries a semantics-declaration block naming the dossier spec by SAID, and an unpinned or unrecognized semantics is **refused**, never assumed at whatever revision happens to be installed. And `custos-4.2.md:1945`'s single BCP-14 keyword in §9 is satisfied in its permissive branch rather than its minimal one: the composition rule MUST be committed, and MAY be expressed in the ACDC edge grammar. Acme now takes the MAY.

**This beat depends on the dossier threshold operators landing in `bakobo/keripy`.** If they do not, the fallback is demo 1's domain-native encoding with the semantics-declaration block still present and still refusing when unpinned — the fold does not change either way (`this.i` @mw6dxh), only the carriage does. The fallback costs beat 1's second screen and the axiom-4 refusal beat, and nothing else in this script.

Each slot is in exactly one disposition, per the dossier specification's own three:

- **Pending** — no signed act from the named endorser. Contributes nothing. A pending slot and an absent slot are equivalent in trust terms.
- **Endorsed** — a signed endorsement ACDC from the named endorser, `disp: "endorse"`, `act: "issue"`, whose `said` attribute equals the decision's SAID. Its weight is added.
- **Declined** — the same signed act with `disp: "decline"`. Contributes nothing to the sum, records attributable dissent, and *spends* the slot, so its weight is no longer reachable.

An active "no" is always a signed declination, never a silent slot.

### Edition 1 — from inception (clauses A1, A2, A3)

| Clause | Governs | Slots | Effect |
|---|---|---|---|
| A1 | ordinary acts | Marta `w=1/2`, Dev `w=1/2` | both required |
| A2 | amendment of the operating agreement | Marta `w=1/2`, Dev `w=1/2` | both required |
| A3 | release of escrowed founder equity | Marta `w=1/2`, Dev `w=1/2` | both required |

### Edition 2 — after beat 7 seats the board (clauses B1, B2, and A3 carried forward)

| Clause | Governs | Slots | Effect |
|---|---|---|---|
| B1 | ordinary acts | Marta `w=1/2`, Dev `w=1/2`, seat 3 `w=1/2` | any two reach unity |
| B2 | amendment of the operating agreement | Marta `w=1/3`, Dev `w=1/3`, seat 3 `w=1/3` | all three required |
| A3 | release of escrowed founder equity | Marta `w=1/2`, Dev `w=1/2` | **unchanged bytes, unchanged SAID** |

A3 is the most important row in this document, and it is the fixture change tick `6ms6` asks for. Demo 1's amendment replaced every clause, so no beat could show a pending act *surviving* an amendment, and issue #82's rule 2 was unshowable. Escrowed founder equity is a founders' matter by construction: seating a board distributes ordinary authority and the authority to amend, and deliberately does not reach the founders' own equity. So A3 is carried into edition 2 byte-identical, and because a clause is its bytes, it is the same clause with the same SAID. Amendment still replaces the edition rather than adding to it (`this.i` @wg3jr6); a clause that does not change is re-committed unchanged.

The retained higher bar at B2 is demo 1's point and survives: seating a board distributes ordinary authority without distributing the authority to change the rules.

### The disturbance set

Every amending enactment carries a declared **disturbance set**: the pending questions whose requirement space it claims to disturb. This is determination 5 of issue #82, ruled 2026-08-27 — the amender declares, the fold computes the true set, and a mismatch convicts the declaration. Acme's first amendment declares truthfully and its second does not, which is Act IV.

## The beats

E = Endorsed, P = Pending, D = Declined. "Ground it must carry" is asserted by the oracle, not just the verdict — a finding that reaches the right value without its ground fails the row (`this.i` @cl1grd, @ppnadi).

### Act I — law is computed, not asserted

**All six beats are the recorded opener.** Full screen density, `--substrate keripy`, and it closes on `tools/read-keri-log.py`.

| # | Question | Clause | Slots | Sum | Expected | Ground it must carry | demo-1 |
|---|---|---|---|---|---|---|---|
| 1 | `law --at inception` | — | — | — | **the Constitution** | three clauses with their SAIDs, their operators, their slots and weights; the pinned dossier-semantics digest | prologue |
| 2 | Open a bank account | A1 | Marta E, Dev E | 1.0 | **affirmed** | clause A1 + both endorsement SAIDs | D1 |
| 3 | Hire a VP of Sales | A1 | Marta E, Dev P | 0.5 | **pending** | typed requirement naming Dev's slot: required schema, expected issuer, citing clause. Species `absent` | D2 |
| 4 | Sign the office lease | A1 | Marta E, Dev **D** | 0.5 | **defeated** | Dev's declination SAID + clause A1; unity unreachable | D3 |
| 5 | Release escrowed founder equity | A3 | Marta E, Dev P | 0.5 | **pending** | typed requirement naming Dev's slot under A3. Species `absent` | new |
| 6 | May the board declare a dividend? | — | — | — | **refusal** | names the missing rule; not a finding | D8 |

Beats 3 and 5 are deliberately left pending. They are Act II's material.

### Act II — delegation, and the two currents

**Live: 7, 8, 9, 10, 12, 13, 14, in that order. Leave-behind: 11, 15.**

| # | Question | Clause | Slots | Sum | Expected | Ground it must carry |
|---|---|---|---|---|---|---|
| 7 | Seat the board (the amendment itself) | **A2** | Marta E, Dev E | 1.0 | **affirmed** | judged under the law it replaces; the delegating seal's coordinate in Acme's KEL; the `dip` in seat 3's KEL; the seat credential's issuance event in Acme's registry; the declared disturbance set `{hire-vp-sales}` |
| 8 | `seat 9-acme-as-board-seat-3` | — | — | — | **two bindings** | KERI: Acme's delegating seal + seat 3's `dip` naming Acme in `di`. ACDC: the seat credential, issuee = seat 3, issued under Acme's registry, registry state `issued` |
| 9 | Hire a VP of Sales, re-asked after the amendment | A1 **repealed** | — | — | **pending** | species `expired/abandoned`; ground is **the amending enactment's SAID**; cure is re-presentation |
| 10 | Release escrowed founder equity, re-asked after the amendment | A3 | Marta E, Dev P | 0.5 | **pending** | species `absent`, same requirement as beat 5; the three-part stability check shown: same clause SAID, same requirement space, same pinned lens |
| 11 | Release escrowed founder equity, after Dev endorses it | A3 | Marta E, Dev E | 1.0 | **affirmed** | clause A3 + both endorsement SAIDs — cured across an amendment, under the clause that never moved |
| 12 | Approve the annual budget | B1 | Marta E, seat 3 E, Dev P | 1.0 | **affirmed** | unity reached though one party never acted; seat 3's endorsement carries its DI2I edge to the seat credential |
| 13 | Approve the Q2 forecast, after Dev declines | B1 | Marta E, Dev **D**, seat 3 P | 0.5 | **pending** | seat 3's slot still reachable |
| 14 | Quinn endorses the Q2 forecast without a seat | B1 | — | — | **credential verification fails** | the DI2I edge names a seat credential whose issuee Quinn is not; rejected by edge validation *before any fold runs*. The fold's answer to beat 13's question is then recomputed and is unchanged |
| 15 | Nina endorses from her delegated device | B1 | Marta E, Dev **D**, seat 3 **E** via device | 1.0 | **affirmed** | DI2I validates: the issuer is a delegated AID of the issuee. Same slot, different key, no law change |

### Act III — revocation, and what it cannot do

**Live: 16, 17, 19, 20. Leave-behind: 18.** Beat 18 re-asks at the *original* position and beat 19 re-asks at a *later* one; 19 is the surprising half and subsumes 18 for a room that is short on time.

| # | Question | Clause | Slots | Sum | Expected | Ground it must carry |
|---|---|---|---|---|---|---|
| 16 | `registry --at revocation` | — | — | — | **registry state** | a `rev` event in Acme's governance registry against the seat credential; seat 3's KEL untouched and its keys still valid |
| 17 | Approve the Q3 budget (a new question, after the revocation) | B1 | Marta E, seat 3 **unfilled**, Dev P | 0.5 | **pending** | typed requirement naming seat 3's slot: required schema, expected issuer, citing clause |
| 18 | Re-ask beat 12's question at beat 12's position | B1 | as beat 12 | 1.0 | **affirmed** | byte-identical to beat 12's finding, ground included |
| 19 | Re-ask beat 12's question at a position **after** the revocation | B1 | as beat 12 | 1.0 | **affirmed** | the credential stood at that position; prospective revocation falsifies no cited ground |
| 20 | Re-ask beat 12's question over a bundle containing duplicity at seat 3's signing position | B1 | — | — | **self-convicted** | the canonical proof package naming the contradictory pair, and the statement that KERI's superseding-recovery rules do not reconcile it |

### Act IV — the amendment that lies

**Live: 22, 23. Leave-behind: 21**, whose pending act the live part narrates in one sentence rather than running.

| # | Question | Clause | Slots | Sum | Expected | Ground it must carry |
|---|---|---|---|---|---|---|
| 21 | Approve the capital plan | B1 | Marta E, Dev P, seat 3 P | 0.5 | **pending** | a second question pending under B1, alongside beat 17's |
| 22 | Lower the ordinary-acts bar (the second amendment) | B2 | Marta E, Dev E, seat 3 E | 1.0 | *declared* affirmed | the enactment's declared disturbance set names **only** the Q3 budget, and not the capital plan |
| 23 | `disturbance <the second amendment>` | — | — | — | **self-convicted** | declared set vs. computed set, side by side; the computed set contains both B1 questions; the mismatch is the proof |

### Coda

**Leave-behind, both.** They are the cheapest beats in the document and the least surprising to this audience, which is exactly the combination that loses to a question.

| # | Question | Clause | Slots | Sum | Expected | Ground it must carry | demo-1 |
|---|---|---|---|---|---|---|---|
| 24 | Re-ask beat 2's question at the end of the log | A1 | as beat 2 | 1.0 | **affirmed** | under clause A1, the law in force *then* | D9 |
| 25 | Refold the whole log with events in permuted arrival order | — | — | — | **byte-identical Constitution and findings** | `custos-4.2.md:3101`, binding | D10 |

## What each beat is for

**Act I is the ground the audience already stands on**, run fast. Beat 4 against beat 13 is demo 1's centerpiece and is preserved intact: the same signed "no" from the same party is *defeat* under two slots and *pending* under three, not because the engine treats anyone differently but because with two slots a declination makes unity unreachable and with three it does not. The Constitution changed; the arithmetic did the rest. Beat 6 is the axiom-3 beat — the engine refuses rather than legislating, and names what is missing. For this audience that is KERI's own no-ambient-authority reflex, and it is worth naming as such out loud.

**Act II is the new material, and beat 14 is its point.** The seat credential and its DI2I edge are `custos-4.2.md:1423-1434`, which says that "the warrantor holds the seat it claims" is checked by edge validation in the existing toolchain *before any fold runs*, and that "an unseated warrantor's warranty fails credential verification" — then adds the sentence the demo exists to show: "That check is evidence the fold consumes, never a verdict: the two currents stay unmerged." Beat 14 runs both currents on one screen. Quinn's endorsement fails a check this audience already owns, in code they already run, and the fold's four-valued answer is computed separately and is unaffected. Nobody has built this; the spec has mandated it since 4.1.

Beat 15 is the third delegation stratum and the most KERI-native thing in the demo: gAID → seat → device, each stratum a real cooperative delegation, and DI2I is the ACDC operator that makes the second hop checkable at the credential layer. It is marked cuttable only because it is the one beat whose absence costs no argument.

Beats 9, 10 and 11 are issue #82's rules 1 and 2, side by side, which is the contrast tick `6ms6` says is currently unshowable and which the A3 fixture change makes showable. Beat 9: the cited clause is amended, the requirement space the pending finding declared at birth is unreachable, the cure path closes, and the ground is the amending enactment itself — determination 1's widened `expired/abandoned`, admitting the amending enactment as a second committed ground rather than minting a fifth species. Beat 10: a clause elsewhere changed and this one did not, so the three-part stability test passes and the cure path stays open. Beat 11: it is then actually cured. The line to say over beat 9 is that the finding at its own position stands forever, as every finding does; what it loses is any path to a terminal value.

**Act III answers the sharpest objection the 4.1 KERI panel raised**, which was that there was no lawful motion for prospective revocation of a grounding credential (issue #7, since closed). Beat 17 is §9's doctrine in one screen — `custos-4.2.md:1916`, "Registry state is evidence. Standing is judgment. The committed covenant set is the function between them," and `:1927`, "A relying party that treats registry state as authority has skipped the law and trusted the ledger." Beats 18 and 19 are the pair that surprises people: the earlier finding is untouched, *and so is the later one*, because a prospective revocation falsifies nothing — the credential did stand at that position. Your own sentence from #82, which Nicholas banked verbatim: evidence does not un-arrive. Beat 20 is the contrast that keeps this from sounding like a dodge. Duplicity at the signing position *is* evidence falsifying a cited ground, it bears on the question, and it does reach back. Revocation and undercut never share a code path.

**Act IV is the beat to end on.** An amending enactment must declare what it disturbs. This one under-declares. The fold computes the true set from the same committed bytes, the mismatch is visible by inspection, and the amendment is convicted on its own testimony — no judge, no vote, no quorum, no appeal to anything outside the log. That is KERI's duplicity-evidence doctrine lifted one tier, and it is the single strongest answer available to "why is governance not just a document?" A document cannot lie about itself in a way a stranger can compute.

**The coda is cheap and binding.** Beat 24 is the utility claim — the past is recomputable under the law in force then. Beat 25 is one command and is normative text.

Cut order inside the live thirteen, if the clock runs out in the room: beat 12 first, since beat 14 recomputes the fold's answer anyway and kernel 4 survives on 8 and 14 alone. Then beat 17, at the cost of the cleanest statement that the *next* answer changes. Then beat 10, which collapses kernel 2 to beat 9 plus a narrated sentence — expensive, because rule 2 is the subtle half and the half nobody guesses. Then beat 13, which is demo 1's centerpiece, and only if desperate.

**Beats 7, 9, 14, 19, 20 and 23 are never cut.** They are the six rows the argument rests on: the hinge, the cure path that closes, the two currents that stay unmerged, the revocation that does not reach back, the undercut that does, and the amendment convicted by its own declaration.

**The build risk is concentrated in beat 20.** A duplicity fixture at seat 3's signing position, and bearing machinery that distinguishes it from revocation without sharing a code path, is the deepest new work in this script and it sits on a never-cut row. If it is going to slip, it will be visible early, and the fallback is to narrate the contrast against a static screen rather than to run it — which costs the beat its force but not its point. Decide that by the halfway mark, not in the last week.

## Open readings this demo pins

Two rows above rest on readings the ratified text does not settle. Both follow `custos-questions.md`'s discipline: state the span, state the readings, pin one, and file the question against Custos.

**Beat 23 — what value does an under-declaring amendment return?** Determination 5 says a mismatch "convicts the declaration" and that the amender "has testified falsely about its own amendment, in committed bytes," but it does not say which of the four values the enactment's own lawfulness question returns. Reading A: **defeated**, citation = the mismatch, on the ground that the enactment violated a committed requirement. Reading B: **self-convicted**, on the ground that the enactment commits two things that cannot both be true of the same bytes — the declared set, and the law change whose consequences the fold computes — which is `custos-4.2.md:1499-1530`'s "two voices where its constitution demands one." **Pinned: B.** It is the stronger reading and by far the better demo, and it is the reading that makes the disturbance-set declaration worth its one field. This is DIVERGENT and goes to Custos as a question; 4.3 owes the sentence.

**Beat 9 — is `expired/abandoned` reachable at all today?** `PendingSpecies.EXPIRED_ABANDONED` exists in utina's type and is currently unreachable under the shipped `UNREACHABLE_YIELDS = Defeated` pin (`this.i` @dozrtx). Beat 9 is a *new producer* of it, on the amendment path, and does not touch that constant. The two must not be conflated in the implementation, and the oracle asserts the species and its ground rather than merely the value.

## Decision notes

**Why the seat is an identifier and not a person.** `custos-4.2.md:2139-2148`. Slotting the office rather than the officer buys three things the demo shows and one it only names: dual-anchored key events, custodial recovery of a compromised organ inside KERI's own delegated-recovery rules, delegation strata with KERI's semantics rather than a metaphor — and, named only, tenure as rotation policy. It also fixes a smaller thing: demo 1's screens slotted a person, which quietly implied that a governance power is attached to a human rather than to an office a human currently holds.

**Why revocation is a registry operation and an `RMxN` operator in the law, and not a field on the credential.** This is already the ruling of record in tick `56js`: the dossier's Endorsed predicate is signed + `disp` + `act` + expected issuer + anchored, with revocation not a term in it and no registry field in the normative schema. The seat credential is registry-bound because `custos-4.2.md:1420-1422` requires a standing-conferring credential to be revocable through its registry; the endorsements stay registry-less because nothing in their predicate reaches for one. Two credential kinds with different obligations, and the demo shows both.

**Why the semantics-declaration block is in the founding law rather than in the engine.** Axiom 4. An unpinned external semantics is refused, never assumed at whatever revision happens to be installed — which is exactly the discipline `companions/engagement-companion.md` was written to enforce, after three of 4.1's five pinned artifacts moved *after* ratification. Demo 2's law carries the dossier spec's digest, and flipping that digest to an unrecognized value produces a refusal rather than a wrong answer. If there is spare time, that is the best unscheduled beat available.

**Why `utina demo2` and not a replacement.** The current `utina demo` is a passing acceptance oracle at 100% branch coverage, and it is the fallback if any of this slips. Keep it running untouched through the build, add `demo2` beside it, and promote `demo2` to `demo` once this script is the one we show — at which point demo 1 either retires or survives as `demo --edition 1`. The cost is one extra command name for about three weeks, and the benefit is never being between two oracles on demo day.

## Known objections, and the beat that answers each

Drawn from `reviews/keri-panel-custos-4.1/` and `reviews/keri-native-review.md` in the Custos repo. This audience raised these; assume they will again.

| Objection | Where it comes from | The beat, or the answer |
|---|---|---|
| "Why not just a TEL? Why a third log?" | KERI-native review | There isn't a third log — a GEL *is* a TEL. The novelty is a third *fold*, whose transition rule is committed data in the log it reads. `why-a-gel-and-not-a-tel.md:243` |
| "Registry state already tells me whether the credential is good." | the assumption the whole audience shares | Beats 17–19 |
| "Governance is Layer 2 human judgment on purpose; ACDC's `r` section already carries rules." | first-principles skeptic, SKP-F1 | Beat 23. A rule section is a document; it cannot be convicted of lying about itself |
| "Your replay promise rests on a re-folding population that does not exist." | protocol-security reviewer and the hostile DAO/L2 lens, independently | Concede it. Issue #16, Exit B — the claim is bounded, not designed away. Say it before being asked |
| "Kever/Tever are keripy class names, not spec names; 'Gever' overreaches." | KERI-native review, KN-03 | Attribute the naming to the reference implementation out loud, and frame Gever as extending an implementation convention |
| "`MxN`/`RMxN` are not in the ACDC spec." | true | They are in the dossier specification, as a documented extension following ACDC operator conventions. Do not attribute them to ACDC |
| "Byte-identity is claimed but the encoding is deferred." | SPC-F3 | Today's grade is semantic full-payload equality; byte-identity follows by construction when a carriage encoding ratifies. `custos-4.2.md:167-170`, verbatim |
| "You've minted ilks and reserved a CESR genus without steward recognition." | governance reviewer, GOV-F1 | The reduction in `why-a-gel-and-not-a-tel.md` removes the need for both. The genus ask is the one open item, and naming it as an ask is the point of the working-group conversation |

## What this demo does not claim

Say these before being asked, per issue #18's own advice that leading with the debts is better positioning than being asked for them.

One implementation and a half — utina here, `thesmo` as the blind sibling built to find where the spec underdetermines a conforming engine. Cross-implementation agreement is an open debt (issue #14). The warranty dispute economics are undesigned and fenced, not silent (issue #16). Cross-frame composition is not claimed: Custos commits no canonical comparison algorithm across frames, congruence is evidence and confers nothing, and the property being demonstrated is *intra-frame* replayable governance. The spec is not yet in ToIP house style and its readability is under active repair — which is the second half of the ask.
