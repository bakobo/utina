# Intent — the command-line interface

*this.i nodes for `utina.cli`, kept here rather than in the root tree while the CLI
commission is in flight. The shape is `../this.i`'s: a title, a kind, an id, and a `why`
that carries its own rebuttal surface. Fold into `this.i` at integration.*

The CLI is a **read surface over the fold plus the constructor's verb**. It computes no
governance of its own; every verdict on a screen came out of `utina.fold.evaluate`, and every
committed byte out of `utina.enact`. Where a screen shows something the fold does not return —
the slot arithmetic, most of all — the CLI derives it from the same committed values the fold
read, and a test pins the two together.

---

Show the ground on every screen that shows a verdict = constraint:
  id: cl1grd
  why: >
    Custos's Ground Axiom (custos-4.2.md:1502-1507) makes the ground a component of what a
    finding IS: "a value that does not carry its ground is not a member of this type, whatever
    else it may be." A renderer that prints DEFEATED and stops has therefore not abbreviated
    the finding, it has displayed something that is not one. Chose to make the ground
    structurally unskippable — the finding renderer emits the verdict line and the ground block
    from one function, and there is no code path that produces one without the other. Rejected
    a `--terse` flag that would print the verdict alone, which is exactly the screen the axiom
    forbids and exactly the screen a hurried narrator would reach for. Tradeoff accepted: the
    smallest eval screen is about fifteen lines, and a demo of many evaluations scrolls.

Show the arithmetic, not just its conclusion = decision:
  id: clarth
  why: >
    The audience is being asked to believe that a governance answer is checkable rather than
    oracular. The claim is only visible if the slots, their weights, their dispositions and the
    sum against unity are all on the screen: "DEFEATED under clause A1" is still an assertion,
    while "1/2 endorsed, 1/2 spent, 1/2 reachable, unity 1" is a calculation the audience can
    do in their heads and catch us getting wrong. Chose to render both sums — endorsed and
    still-reachable — because the demo's centerpiece (D3 against D6) turns entirely on the
    second one, and a screen showing only the endorsed sum makes D3 and D6 look identical at
    1/2 and the differing verdicts look arbitrary. Rejected showing only the outstanding slots,
    which is what the Pending finding itself carries: it answers "who else must act" and not
    "why is this dead."

The CLI derives the slot table itself, and a test forbids it from disagreeing = decision:
  id: clxchk
  why: >
    `evaluate()` returns a Finding, and a Finding carries its ground but not the slot table:
    Affirmed names the endorsements that reached unity, Defeated names the one declination it
    cites, Pending names only the outstanding slots. None of them carries every slot with its
    weight and disposition, which is what @clarth requires on the screen. So the CLI recomputes
    it, from the same committed values, with `utina.fold.slots.classify` over the clause the
    Constitution supplies. That introduces a second path to a governance-relevant fact, and a
    second path can diverge silently — the exact failure mode this repo warns about at the
    enact/slots seam. Chose to close it with a cross-check test that walks every beat and
    asserts the derived table implies the fold's verdict: satisfied iff Affirmed, unreachable
    iff Defeated, otherwise Pending, and the clause the CLI renders is the clause the finding
    cites. Rejected calling `utina.fold.evaluate`'s private helpers, which would remove the
    divergence but make the CLI a client of another package's internals. Rejected inferring the
    clause from the finding instead of from `Constitution.governing`, which would be
    self-consistent by construction and would therefore prove nothing.

Refusal is rendered in a different shape, not a fifth verdict colour = decision:
  id: clrfsl
  why: >
    A refusal is an operational fact and not a member of the codomain (custos-4.2.md:1896-1902,
    and `utina.fold.refusal`). A screen that renders it as a fifth verdict banner in a fifth
    colour teaches the audience the opposite of what the engine implements, and D8 exists
    precisely to teach that distinction. Chose three carried differences rather than one: the
    banner reads REFUSED — NOT EVALUABLE and says in words that it is not a verdict; the slot
    table and the sums are absent entirely, because with no governing clause there is no
    arithmetic to show; and in their place the screen lists what the law in force DOES govern,
    so the absence is visible rather than asserted. Rejected relying on colour, which fails on
    a projector, in a pipe, and for a colour-blind viewer.

Colour is decided by the stream, never by a flag = decision:
  id: clcolr
  why: >
    Chose `isatty()` plus the NO_COLOR and FORCE_COLOR conventions over a `--color` option.
    Every flag on the base parser is a branch that has to be covered and a token the narrator
    can fumble on stage, and the three cases that matter — projector terminal, piped to a file,
    captured in a test — are all decided correctly without one. Colour never carries meaning on
    its own: every verdict is a word first and a colour second, so `NO_COLOR=1` loses nothing
    but emphasis. Tradeoff accepted: a narrator who wants colour through a pager needs
    `FORCE_COLOR=1`, which is documented in the epilog rather than discoverable in `--help`'s
    option list.

Identifiers are abbreviated to a prefix that is also a valid handle = decision:
  id: clhndl
  why: >
    A SAID is 44 characters and a law head is 64, and three of them on one line push past the
    100-column budget the projector allows. Chose to render a 12-character prefix followed by
    an ellipsis in every table, and to make `--said` and `--on` accept a prefix, so what the
    screen prints is what the narrator can type back. Rejected a `--full` flag (a branch, and a
    flag nobody remembers on stage) and rejected a middle-elision like `E1rff...RWxY`, which is
    unambiguous to a reader and useless as input. The one place the full identifier appears is
    the subject line of an eval screen, where it fits and where a viewer copying it has a
    reason to.

`utina enact` continues the record in memory, and does not persist = decision:
  id: clphmr
  why: >
    Acme's log is rebuilt deterministically from `utina.acme.build` on every invocation, so an
    act committed by one process is gone by the next. Chose to make the verb honest within its
    own invocation rather than to add a state file: the screen shows the committed event —
    identifier, coordinate, body fields, signature, and the fact that the substrate verified it
    before it was recorded — and then shows the subject's finding before and after the act, so
    the audience sees a constructor acting onto the record and the record answering differently
    because of it. Rejected persisting the log to disk, which would make replay depend on the
    filesystem and would let a fumbled rehearsal leave state that changes what Friday's demo
    prints. Tradeoff accepted: the effect does not outlive the process, and the screen says so
    in one line rather than implying otherwise by silence.

`utina enact` adopts an existing record through attributes `utina.enact` does not expose = deviation:
  id: cladpt
  why: >
    `Constructor` has no public way to resume a record it did not itself write: `_emit` takes
    its coordinate from `len(self._emitted)`, `_dispose` checks `self._saids`, and every verb
    checks `self._founded`. The CLI needs all three set from Acme's committed log. Chose to set
    them in one small documented adapter, because the alternative is to re-implement `_emit` in
    the CLI, and that would duplicate the committed byte layout — the field order, the
    coordinate-before-identifier rule, the signature-verified-before-recorded rule — across a
    seam that fails silently when the two copies drift. Reaching into another package's
    internals is the smaller and the louder of the two wrongs. Filed as a tick against
    `utina.enact` for a public `Constructor.resume(events)`; a test pins the adapter's
    invariants so the deviation cannot rot unnoticed.

The demo driver computes nothing = constraint:
  id: cldemo
  why: >
    `utina demo` is a table of beats, each holding the argv of a command a person could type,
    and a loop that echoes the command and dispatches it through the same entry point the shell
    reaches. Driving constraint: if the driver can produce a screen the query CLI cannot, then
    what the audience is watching on Friday is a slideshow with a governance engine somewhere
    behind it, and the demo's own claim — that these are real answers to real questions — is
    the first thing it fails to demonstrate. Rejected letting the driver format even the beat's
    expected verdict, which would have made a beat that regressed still look right.

Exit status reports whether the command answered, not what it answered = decision:
  id: clexit
  why: >
    Chose 0 for any command that produced a screen, including a defeated finding and a refusal,
    and 2 for an error. A defeated finding is a correct and complete answer, and a shell that
    treats it as a failure would make `utina eval ... && echo ok` mean something the engine
    never said. Rejected mapping the four verdicts onto four exit codes, which invites exactly
    that confusion and would make `utina demo` exit non-zero on the beats it is proudest of.
