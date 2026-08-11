# utina — Intent Tree (this.i)
#
# Source of truth for utina's design intentions and the decisions that follow from them,
# per the Bakobo intent-first methodology (../dev/methodology.md). Code and docs/ are DERIVED
# artifacts. Record each consequential decision here, in its own commit, BEFORE the code
# commit it justifies.
#
# Node ids are opaque base32 [a-z2-7], stable across renames. NEVER parse them, never make
# them semantic.

Make Custos's replayable governance useful to a real organization = goal:
  id: rk4mzq
  why: >
    Custos specifies governed domains whose law is committed and whose judgment is computed,
    and promises that any stranger holding the logs recomputes the same Constitution. Nothing
    has ever shown an organization actually governed that way. utina exists to close that gap:
    a company's operating agreement expressed as committed law, and its decisions answered —
    confirmed, denied, or not-yet — with a ground a stranger can check. Chose "useful engine"
    over the falsification posture of its sibling thesmo (bakobo/thesmo), which deliberately
    optimizes for a defect register and accepts being slow to production. That posture is
    right for thesmo and wrong here: an engine that will not resolve an ambiguity cannot be
    demonstrated. Tradeoff accepted: utina's readings are NOT independent evidence about the
    specification, and it must never be cited as a second implementation confirming thesmo.
  children:
    Express Acme's thresholds domain-natively, in the dossier's shape = decision:
      id: ta7vle
      why: >
        Custos section 9 carries exactly one BCP-14 keyword: the composition rule MUST be
        committed, and MAY be expressed in the ACDC edge grammar as the dossier specification
        profiles it. Expressing it as real ACDC edge groups makes the dossier specification an
        external semantics, which axiom 4 then requires be pinned by committed digest with
        anything unpinned refused. Chose a domain-native committed clause predicate whose
        STRUCTURE is isomorphic to the dossier's threshold operators — same operator/slot/weight
        shape, same unity threshold, same three dispositions, same disp and act field names —
        over both a bespoke shape and real ACDC edges. Rejected a bespoke shape because the
        long-term destination is genuine ACDC edge groups and a different shape would make that
        a rewrite. Rejected real ACDC edges now because the semantics pin and the refusal
        machinery it obliges are not needed to show the value and would not fit the schedule.
        Tradeoff accepted: utina is NOT dossier-conformant today, and must not claim to be.
    The fold computes the slot predicate itself; the substrate cannot = constraint:
      id: mw6dxh
      why: >
        Custos withdrew the claim that KERI's threshold algebra transfers to the evidence tier:
        the two constructions are analogous, never one algebra, because the predicate deciding
        what enters the sum is a fold question and not the substrate's. keripy's Tholder is a
        key-state threshold over verified signature indices and cannot answer whether a slot is
        Endorsed — that needs the referenced endorsement's issuer, disposition, subject SAID and
        revocation status. Driving constraint: wiring a substrate threshold evaluator to an edge
        group discharges the arithmetic and none of the slot dispositions. So threshold
        arithmetic and the slot predicate are separate modules, and the arithmetic is the
        trivial one.
