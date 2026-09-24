# GEL events are not sealed into the gAID's KEL, which custos-4.2.md:1114-1120 requires
kind: debt
tags: fold
created: 2026-09-23T18:13Z

- 2026-09-24T15:55Z Design notes from the 2026-09-24 outside comparison. A genesis knot binds the designated GEL to the domain in three events: the gAID's inception seals the founding law; the registry inception names the gAID; the first rotation seals both. The fold then checks the knot before folding anything. Doing this also retires Q24 (writer-assigned order), since order then comes from KEL anchoring and seal index, and lets the determinism permutation test catch an ordering defect, which today it cannot because the order is simulated. Touches the constructor's output and so every demo coordinate: after the demo.
