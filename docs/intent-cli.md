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
  superseded_in_part_by: clcoia
  note: >
    The half of this decision that renders a PARTY as a truncated prefix is withdrawn by
    @clcoia: it is a security antipattern, not merely a terse rendering. The half that makes
    `--said` and `--on` accept a prefix stands, and @clwhoi extends it — a prefix remains a
    good thing to type and is no longer a good thing to print.

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

A party is shown by a COIA alias, never by a truncated identifier = decision:
  id: clcoia
  why: >
    Every screen named its parties with a 12-character prefix and an ellipsis — `acme:marta`
    under the facade, `EPFtMUsnh_BZ...` under keripy. Both are wrong, and not for the same
    reason. The facade form is a coincidence: an identifier that happens to read like a name
    because the facade returns its argument, which teaches an audience that identifiers are
    legible and makes the keripy screen look like a regression. The keripy form is the real
    fault. A truncated prefix beside a name invites a reader to decide that two identifiers are
    the same by comparing what they can see, and it cannot support that decision:
    `~/code/me/papers/amp-diff.md` section 4.3.8 treats a prefix as an ENTROPY channel —
    faithful, but unable to amplify a difference — so an attacker who wants to match the twelve
    characters on the screen grinds twelve characters, which is cheap.
    `~/code/me/entviz-js/packages/react/docs/pill-design.md` section 2.1 draws the line this
    repo now holds: recognition is not verification, the collapsed form affords locate, expand
    and copy, and NO equality decision may be made from it. Section 3.3 rejects the short
    head-and-tail teaser by name, and is careful that the objection is to the SHORT inline
    teaser and not to a full value.
    Chose COIA aliases (`~/code/me/coia/README.md`) as what the screens name a party by, in
    every position where an identifier used to appear: the slot column, the defeat subcode and
    citation, the pending requirement, the log gloss and the enact line. Rejected keeping the
    prefix alongside the alias, which is the antipattern with a label attached and is strictly
    worse than either alone — it supplies exactly the twelve characters an eye will compare.
    Rejected showing the full 44-character identifier in the slot column, which is safe but
    does not fit, and which spends the audience's attention on the one thing they cannot check.
    Tradeoff accepted: an alias is creator-local, so the screens now show something that is
    meaningful to Acme and to nobody else. That is what @cldspl is about.

An alias is display-only, and a fitness function enforces it = constraint:
  id: cldspl
  why: >
    COIA is explicit that an alias is a private nickname: it delivers Zooko's human-meaningful
    corner "only for the person who creates it", it "is not a commitment to meaning" for anyone
    else, it "can evolve without warning to suit its creator's fancy", and parsing someone
    else's alias for strong meaning is named in the spec as a dangerous antipattern. An alias
    therefore carries no security claim and must never acquire one by accident. Driving
    constraint: an alias must never enter committed bytes, must never be an input to the fold,
    and must never affect a finding. Chose to make that structural rather than careful — the
    alias table lives in `utina.cli`, the display plane, and is built at the CLI's composition
    root from the identifiers inception returned, so `utina.fold`, `utina.enact` and
    `utina.acme` cannot see it at all. `tests/test_purity.py` gains a second quarantine of the
    same shape as the KERI one and by AST inspection for the same reason: a lazy import inside
    a function body is exactly how this boundary would erode. `utina.cli` is the one exempt
    plane, because it is the plane whose entire job is display. Rejected hanging the alias off
    the `Acme` record in `utina.acme`, which is the obvious home and which would put a
    display-only string one attribute away from the code that writes committed bytes.

Acme's demo identifiers carry COIA flag 9 = decision:
  id: clflg9
  why: >
    COIA's flag 9 means the aliased identifier belongs to an experimental, test or demo
    environment with no real-world consequences to reputation, governance or cost, and must not
    be used where consequential production side effects are intended. That is a literal
    description of Acme: the log is rebuilt from committed bytes on every invocation, the
    keripy salt is a fixture in the source, and no decision on any screen binds anybody. Chose
    to carry the flag rather than to omit it, so that the aliases the audience reads are the
    aliases the spec would actually produce here, and so the screens say out loud that this is
    a demo instead of leaving a viewer to infer it from the company being fictional. Rejected
    flag 0 (unverified), which would be false: every party was incepted by this process, so
    there is no MITM to warn about. Rejected the unflagged form, which is the one COIA reserves
    for identifiers that are verified, public and usable in production, and which is the single
    most misleading thing these screens could claim.

The short alias in columns, the full alias where there is room = decision:
  id: clscop
  why: >
    Truncating an alias is safe and truncating an identifier is not, and the asymmetry is the
    whole of @clcoia: an alias makes no security claim, so shortening it costs nothing that was
    ever there. Within Acme's own screens the scope is constant — everything on them is at
    Acme — so COIA's empty-scope form is not an abbreviation of the alias but a legitimate
    alias in its own right, and `9-marta-as-founder` is eighteen characters, which is the slot
    column's existing budget. Chose the short form in the arithmetic table and the law screen's
    slot list, and the full scoped form wherever the line has room for it: `utina whois`, the
    law screen's header, and the ground block. Chose to state the constant scope once, in the
    law screen header, so the short form is disclosed rather than merely convenient. Rejected
    the full form everywhere, which overflows the law screen's slot line at 106 columns.
    Rejected a per-screen truncation of the full form, which would put an ellipsis back on the
    screen and blur the one distinction this commission exists to teach.

`utina whois` is the one place a full identifier appears = decision:
  id: clwhoi
  why: >
    Removing the prefix from the screens removes the only way an audience could see an
    identifier at all, and sometimes seeing one is the point — a viewer who wants to check
    Acme's log against another KERI tool needs the real prefix. Chose an explicit command over
    a flag or a wider column: `utina whois <alias-or-prefix>` prints the alias, the full
    untruncated identifier, and the substrate that produced it. This is the pill's expand
    affordance (pill-design section 2.1): verification routes through a deliberate act, never
    through a glance at a table. The query is normalized before lookup exactly as COIA's
    Comparing section requires, so a narrator may type `Marta as Founder at Acme` or
    `9-marta-as-founder` or a raw prefix and reach the same party. Rejected a `--full` flag on
    every command, which is a branch on every screen and a token to fumble on stage; rejected
    printing the identifier in a footer, which is a table by another name.

Rejected for now: a fingerprint tag beside the alias = decision:
  id: clnotg
  why: >
    A five-character Crockford base32 tag over a domain-separated digest of the identifier is
    the right long-term answer to the question an alias cannot answer — whether two aliases
    that read alike label the same bytes — and it is the rejection test amp-diff argues for: a
    discrete channel, injective on its input, in an alphabet with no confusable glyphs.
    Rejected for this commission on schedule grounds and stated here rather than left implicit.
    Nobody verifies an identifier during the demo; the tag would be a channel nobody reads.
    Adding one the night before means a new column budget on the widest screen, which is the
    law screen, and a wrapped line at nine in the morning. Revisit when a screen exists whose
    job is comparison; `utina whois` is where it would land first.

Rejected for now: extending the no-truncation rule to event SAIDs and digests = decision:
  id: clsaid
  why: >
    @clcoia removes the truncated PARTY identifier. The screens still print a truncated event
    SAID, law head, clause digest, evidence bundle and signature — `932f0ab892df...` — and the
    same amp-diff argument reaches them: a reader comparing two law heads by their first twelve
    characters is making the equality decision section 2.1 forbids. Rejected acting on it now,
    for two reasons that are about this change rather than about the argument. COIA aliases
    exist for ACTORS and the spec says so — a hash is "passive and stuck in a single, static
    role" and the conventions "make less sense" for it — so there is no alias to put in a
    digest's place, and the replacement would have to be invented: a committed name where the
    record has one, a coordinate where it does not. That is a redesign of the log screen's
    columns rather than a substitution into them, and the brief for this commission asks that
    everything else keep working exactly as it does now. Note the mitigation already present:
    the replay screen does not ask a viewer to compare its two heads by eye, it prints the
    machine's own verdict on the comparison (`IDENTICAL`), which is the correct pattern and the
    one a later commission should extend. Revisit as its own commission, with the log screen's
    layout in scope.

Exit status reports whether the command answered, not what it answered = decision:
  id: clexit
  why: >
    Chose 0 for any command that produced a screen, including a defeated finding and a refusal,
    and 2 for an error. A defeated finding is a correct and complete answer, and a shell that
    treats it as a failure would make `utina eval ... && echo ok` mean something the engine
    never said. Rejected mapping the four verdicts onto four exit codes, which invites exactly
    that confusion and would make `utina demo` exit non-zero on the beats it is proudest of.
