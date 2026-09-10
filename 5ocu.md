# U1.3: the seat credential — a second ACDC kind, schema-typed and registry-bound, issuee = the seat AID (custos-4.2.md:1420-1425)
kind: todo
tags: demo2-u1
created: 2026-09-10T18:22Z

- 2026-09-10T23:18Z Done 2026-09-10 in ac42a9f. schemas/acme-seat.json + SEAT_SCHEMA pinned in acme/law.py (the domain names its own schemas, custos-4.2.md:1924); tests/test_schemas.py recomputes the pin with keripy's Schemer. Constructor.seat issues it: domain as issuer, seat AID as issuee, under the governance registry, refused before a registry is opened. Record: acme:seat3 delegated from the gAID, credential issued at label b8. NOT done here: slots still name Nina, not the seat (7tvh), and the endorsement's DI2I edge (5fam).
