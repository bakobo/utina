"""The KERI-facing plane: AIDs, signing, SAIDs, seals, anchoring.

Everything in here is behind one protocol so the fold can be handed committed
values without ever importing a KERI library. The demo runs against a pure
Python facade backend; the keripy backend arrives as its own commission.
"""

from .canonical import SAID_LENGTH, SAID_PLACEHOLDER, canonical_bytes, digest
from .errors import AID_UNKNOWN, ALIAS_TAKEN, NOT_CANONICAL
from .facade import FacadeSubstrate
from .protocol import AID, SAID, Corpus, Event, FoldValues, Position, Substrate

__all__ = [
    "AID",
    "AID_UNKNOWN",
    "ALIAS_TAKEN",
    "NOT_CANONICAL",
    "SAID",
    "SAID_LENGTH",
    "SAID_PLACEHOLDER",
    "Corpus",
    "Event",
    "FacadeSubstrate",
    "FoldValues",
    "Position",
    "Substrate",
    "canonical_bytes",
    "digest",
]
