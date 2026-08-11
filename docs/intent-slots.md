# Intent — the slot predicate and the threshold arithmetic

*Decisions taken while building `utina.fold.group`, `utina.fold.threshold` and
`utina.fold.slots`. Written in `this.i` node format so it can be grafted under
the constraint it elaborates — `The fold computes the slot predicate itself; the
substrate cannot` (@mw6dxh) — once the parallel build converges. Kept out of
`this.i` itself only because four agents were writing at once and the intent tree
is not mergeable by machine.*

```yaml
    Weights are exact rationals; a float weight is refused, never converted = decision:
      id: qpqo3z
      why: >
        Unity has to be exactly decidable, and B2 puts three slots at 1/3 on the demo's
        critical path: in binary floating point 1/3 + 1/3 + 1/3 is not 1, so the retained
        amendment bar would be satisfied or not according to rounding. Chose
        fractions.Fraction throughout, and refused a float at construction rather than
        converting it. Rejected accepting a float and coercing it, because the coercion is
        where the lie enters — Fraction(0.1) is not 1/10, and a law that reads 1/10 in its
        committed bytes would compute as 3602879701896397/36028797018963968 with nobody the
        wiser. Refusing makes the wrong type a loud error at the law's boundary.

    A slot weight is strictly positive = decision:
      id: anoz6j
      why: >
        The dossier specification bounds only the SUM ("at least unity", dossier-spec-body.md:353)
        and says nothing about an individual weight. Chose to refuse w <= 0 at construction.
        A negative weight makes an endorsement subtract, so an endorser could defeat a
        decision by endorsing it — an anti-endorsement, which is a security property nobody
        wrote down and nobody wants. A zero weight puts an endorser in the requirement space
        who can never discharge anything, so the finding names a cure that does not cure.
        Rejected permitting both and letting the arithmetic speak, because arithmetic that
        happens to work is not a rule anyone can rely on. Logged as S6 in questions-slots.md.

    A group is non-empty and slots one endorser at most once = decision:
      id: mfkox5
      why: >
        MxN contains "exactly N slots, one per candidate endorser"
        (dossier-spec-body.md:371), so two slots naming one endorser is outside the shape we
        claim isomorphism with, and it makes the disposition map ambiguous — one AID, two
        weights, no rule for which. An empty group is refused because it can never reach
        unity and would discharge as a pending finding whose requirement set is empty, which
        the codomain forbids (interfaces.md: requirement is non-empty). Rejected permitting
        an empty group as a lawful "nobody may do this", because the domain expresses that by
        not writing a clause, and the fold then refuses under axiom 3 instead of inventing a
        finding.

    An endorser the group does not slot contributes nothing, and does not raise = decision:
      id: 3smud6
      why: >
        satisfied_by and reachable ignore names that match no slot. Chose silence over a
        raise because both are read paths the CLI runs to DISPLAY a verdict, and a display
        path that throws turns a governance answer into a stack trace. The security property
        that matters is preserved and directly tested: an unslotted endorser can never add
        weight, so an endorsement from the wrong AID cannot help. Rejected raising on an
        unknown endorser, which would have caught a caller's typo at the cost of making the
        two most-called methods partial.

    Reachable weight is endorsed plus still-pending; a declined slot is spent = decision:
      id: dnsovg
      why: >
        reachable() asks whether unity is still attainable, which is the endorsed weight plus
        every weight that could still arrive. A declination is an authenticated act by the
        one party who could have filled that slot, so its weight is gone — that is what makes
        D3 defeat and D6 merely pending under the same signed refusal. Rejected treating a
        declination as recoverable (an endorser who might change their mind), because the
        dossier makes a declination an attributable act rather than a mood, and a
        reachability that assumes people will reverse themselves can never report unreachable
        at all.

    The predicate matches endorsements by issuer and subject, not by pointer = decision:
      id: 2pfkyg
      why: >
        In the dossier the slot POINTS at its endorsement through the `n` field
        (dossier-spec-body.md:358) and the expected endorser is the issuer of the ACDC the
        slot references. utina's committed evidence is a flat event log with no edge block, so
        there is no pointer to follow: the fold instead searches committed evidence for an
        endorsement whose issuer is the slot's endorser and whose subject SAID is the
        decision's. Rejected carrying a pointer in the law, because the law is written before
        the endorsements exist and would then have to be amended to be endorsed. The
        divergence this creates is logged as S4 in questions-slots.md.

    A declination is decisive: conflicting acts resolve to declined = decision:
      id: tdsrgi
      why: >
        Where one endorser has committed both an endorsement and a declination naming the same
        subject, the slot is DECLINED whatever the committed order. Chose the reading that
        never grants authority: an endorser who has signed a refusal has spent the slot, and
        the later endorsement is at best a second act the law did not authorize them to take.
        Rejected last-committed-wins, which is the more natural "they changed their mind"
        reading and which we may be wrong to reject — it is logged as S5, DIVERGENT, and the
        pin is fail-closed rather than confident.

    The endorsement's field names are the dossier's, as module literals = decision:
      id: pj3xhi
      why: >
        An endorsement event's body carries `i` (issuer), `disp`, `act` and `said`, matching
        the dossier's own names so that swapping the encoding for real ACDC edge groups is a
        substrate change and not a rewrite (@ta7vle). Rejected friendlier names like
        `endorser` and `subject`, which would read better in Python and would silently break
        the isomorphism claim the demo makes out loud. They are module-scope literals rather
        than inline strings, so the seam with utina.enact is one line to reconcile.

    The fold checks attribution; only the substrate checks signatures = decision:
      id: yrkrqj
      why: >
        "Signed by exactly the expected endorser" is enforced in the fold as: this event is of
        kind endorsement, it is in the committed evidence, and its issuer field is the slot's
        endorser. The cryptography is not re-run here, because axiom 2 closes the fold's inputs
        at committed values and a fold that verified signatures would need a KERI library the
        purity test forbids. Rejected carrying a signature into the event body for the fold to
        check, which would have looked more rigorous while actually being weaker — a signature
        the fold cannot verify is decoration.

    Provisional AID/SAID aliases and a structural event protocol = decision:
      id: yenp2x
      why: >
        group.py declares AID and SAID as local aliases for str, and slots.py accepts any
        object with said, kind and body via a structural Protocol rather than importing
        utina.fold.corpus.Event. Chose this because the corpus was being written by another
        agent at the same moment and an import of a module that does not exist yet cannot be
        driven red-to-green. Rejected defining an Event of our own, which the contract forbids;
        the protocol is a read-only VIEW of the contract's Event and the real one satisfies it
        unchanged. Both should collapse to the shared definitions at integration.

    Error codes sit under e.input and e.rule; there is no e.law branch = decision:
      id: cd5dnc
      why: >
        docs/interfaces.md reserves `e.law.clause-unknown.f`, which bakobo.errors refuses at
        import: `law` is not one of the ten first descriptors, and the taxonomy says adding one
        is a change to the standard rather than to a registry. A malformed committed law is
        material we were handed, so it sorts under e.input; the closest standing descriptor for
        a norm we enforce is e.rule. Rejected minting `law`, which would not have imported, and
        rejected e.state, which describes the condition of the target rather than the shape of
        what arrived.
```
