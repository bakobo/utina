# Three renderings of the D3 screen

*For the maintainer to choose from. D3 carries the most narration in
`docs/demo-script.md` — it is the first half of the centerpiece, and the beat where the
audience has to see that a signed no did not merely fail to help but made unity
unreachable. Everything below is the same command over the same committed record, and
every identifier, weight and sentence is the real one: `utina eval hire-vp-sales --at
d3` against Acme's log, clause A1, Marta endorsed, Dev declined.*

Assumptions the three share, because they are not what is being chosen: about 100
columns, ANSI colour when the stream is a terminal and nothing when it is not (shown
here in the plain form), ASCII only, and the ground on the screen every time.

One thing changed under all three after they were written, and it is not a choice
between them. Every candidate named its parties `acme:marta` and `acme:dev` — under
keripy, `EPFtMUsnh_BZ...`. A truncated identifier beside a name invites a reader to
decide two identifiers are the same by comparing what they can see, and it cannot
support that decision (`this.i` @clcoia, and `amp-diff.md` §4.3.8). Parties are now
named by a COIA alias in all three, the unscoped form in columns and the scoped form
in prose and in the ground. Nothing else about the three renderings moved, so the
comparison below is still between the same three shapes.

**Candidate A ships as the default.** The reasoning is at the end.

---

## Candidate A — the ledger

Verdict first, then the header fields, then an aligned table whose last two rows are the
sums, then the ground as a labelled block.

```
utina eval hire-vp-sales --at d3

  DEFEATED    may Acme perform an act of the class hire-vp-sales?
  ------------------------------------------------------------------------------------

  position    d3 (seq 6)
  law head    932f0ab892df...          clause A1 (MxN), unity 1
  subject     E1rffWC9X3TbAvOb7uva7RUxD1CvqcQ6ovLHW64URWxY

  slot              weight   disposition   committed act
  9-marta-as-founder   1/2   endorsed      ENzStORRBBmE...
  9-dev-as-founder     1/2   declined      ENETeOGqyXf3...
                    ------
  endorsed             1/2   of 1          unity not reached
  reachable            1/2   of 1          unity unreachable: a declined slot is spent

  ground
    clause      A1
    defeater    authority (the actor lacked the invoked power)
    subcode     9-dev-as-founder-at-acme
    citation    the declination ENETeOGqyXf3... committed by 9-dev-as-founder-at-acme
    reason      Unity is unreachable under clause A1: 9-dev-as-founder-at-acme committed
                a signed declination, which spends that slot's weight, and the weight
                that can still arrive no longer reaches unity.
```

Good at: the verdict is unmissable and the two sum rows sit directly under the slots
they are computed from, so an audience can check 1/2 + nothing against unity without
reading a sentence, and D3 against D6 differ visibly on the `reachable` row alone.

Bad at: it is a dense screen that rewards scanning rather than reading, so a viewer who
does read it top to bottom is competing with the narrator; and the ground block's five
labels are the most typographically fussy thing in the CLI.

---

## Candidate B — sentence-led

The verdict as a one-word paragraph, then a plain-English account of why, then the
ground and the arithmetic as two quiet appendices.

```
utina eval hire-vp-sales --at d3

  Defeated.

  Acme may not hire a VP of Sales at position d3. Clause A1 governs acts of this class
  and carries when its endorsed slots reach a weight of 1. 9-marta-as-founder-at-acme
  endorsed, which contributes 1/2. 9-dev-as-founder-at-acme committed a signed
  declination, which contributes nothing and spends the slot, so the 1/2 it held can
  never arrive. The most this decision can still reach is 1/2, and it needs 1.

  The ground

      clause        A1, in force at d3 under the law head 932f0ab892df...
      defeater      authority - the actor lacked the invoked power
      citation      the declination ENETeOGqyXf3... committed by 9-dev-as-founder-at-acme
      subcode       9-dev-as-founder-at-acme

  The arithmetic

      9-marta-as-founder   1/2   endorsed   counts
      9-dev-as-founder     1/2   declined   spent
                                            endorsed 1/2, reachable 1/2, unity 1
```

Good at: it stands alone. A screenshot of this in a slide deck, or pasted into an email
to a lawyer, explains itself with no narrator, and the paragraph is the only one of the
three that says *why* a declination is different from silence.

Bad at: it competes with the narrator for the audience's attention — people read prose
on a projector instead of listening — and burying the arithmetic in an appendix
undersells the one thing the audience came to check.

---

## Candidate C — arithmetic first

The screen is a derivation: premises, then a gauge showing the ceiling against unity,
then the verdict as the conclusion at the bottom.

```
utina eval hire-vp-sales --at d3

  may Acme perform an act of the class hire-vp-sales?          at d3 (seq 6)

  clause A1   MxN over 2 slots, satisfied at unity = 1         law head 932f0ab892df...

      9-marta-as-founder   1/2   endorsed   [##########..........]  +1/2
      9-dev-as-founder     1/2   declined   [....................]  spent, unreclaimable
                                            ----
      endorsed                              [##########..........]   1/2 of 1
      reachable                             [##########..........]   1/2 of 1  <- ceiling

  Unity is 1. The ceiling is 1/2. No arrangement of the acts that can still arrive
  reaches it, so:

  DEFEATED    clause A1, authority (the actor lacked the invoked power)
              subcode 9-dev-as-founder-at-acme
              cited: the declination ENETeOGqyXf3... committed by 9-dev-as-founder-at-acme
```

Good at: it argues rather than asserts, and the gauge makes the centerpiece visual —
at D3 the endorsed and reachable bars are the same length, at D6 the reachable bar
fills, and that difference reads across a room in a way that `1/2` and `1` do not.

Bad at: the verdict is at the bottom, so on a scrolling terminal the audience reads the
premises while the narrator has already said the answer; and the gauge quantizes exact
rationals into twenty character cells, which invites someone to check the picture rather
than the fraction.

---

## Why A ships as the default

Because of the room. The narrator supplies the sentences, so B's paragraph is a second
voice saying the same thing more slowly, and the audience will read it instead of
listening. C makes the better argument and I would take it for a written artifact, but a
verdict below the fold is a verdict the room has to wait for, and the beat after this one
is a contrast that only lands if D3's answer is already settled in the audience's head.

A's real advantage is narrower than either of those, and it is the reason to keep it:
the `endorsed` and `reachable` rows are in the same columns as the slot weights above
them, so the sum is checkable by eye against its own inputs. That is what makes the
screen an argument rather than an announcement, and it is what the demo is claiming.

What A borrows from the others, and what it should keep borrowing: C's `reachable` row
carrying an explicit consequence (`unity unreachable: a declined slot is spent`) rather
than a bare fraction, and B's insistence that the citation name the declining party in
words, not only in a subcode.
