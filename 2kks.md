# U1.2: the governance registry — keri.vdr.Regery under keripy, a facade analogue, and registry state inside the evidence bundle
kind: todo
tags: demo2-u1
created: 2026-09-10T18:22Z

- 2026-09-10T22:21Z 2026-09-10: substrate half done in 2d1fee5 (intent 4f81324, this.i @exy3u4t7). open_registry / revoke_acdc / registry_state + a registry= keyword on issue_acdc, both backends, 13 conformance cases. Real keri.vdr TEL under keripy; determinism needs the nonce pinned, Vrsn_1_0 on the vcp, and a fixed dt on iss/rev. Fixed two durable-store bugs found on the way: the Reger was landing under /usr/local/var/keri and nothing closed it. STILL OWED (the half the tick is really about): registry state as a member of the evidence bundle — the Constructor must commit issuance and revocation as governance events and the fold must fold those, because the fold cannot and must not call registry_state. That lands with U1.3's seat credential.
