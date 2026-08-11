"""The KERI-facing plane: AIDs, signing, SAIDs, seals, anchoring.

Everything in here is behind one protocol so the fold can be handed committed
values without ever importing a KERI library. The demo runs against a pure
Python facade backend; the keripy backend arrives as its own commission.
"""
