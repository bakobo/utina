# U1.4: the DI2I edge on endorsements, validated pre-fold, with the result entering the bundle as evidence and never as a verdict
kind: todo
tags: demo2-u1
created: 2026-09-10T18:22Z

- 2026-09-11T02:52Z Done 2026-09-11 in 60aac1d (substrate) and this commit (constructor). verify_edges at the seam with DI2I on both backends, keripy answering through its own verifyChain from the forward-ported #1564; issue_acdc takes edges; endorse/decline take a qualification the endorser cites, which attaches the qp edge under DI2I and is validated before commitment. An unvalidated edge refuses the commitment (this.i @x7crwavm, Daniel's tentative ruling) and a citation the record does not carry is refused separately. Acme's seat cites its credential at D5 and D7. Beat 14's negative is unit-level until Quinn joins the record with U4.3.
