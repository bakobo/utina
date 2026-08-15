"""The KERI-facing plane: AIDs, signing, SAIDs, seals, anchoring.

Everything in here is behind one protocol so the fold can be handed committed
values without ever importing a KERI library. The demo runs against a pure
Python facade backend; the keripy backend arrives as its own commission.
"""

from .canonical import SAID_LENGTH, SAID_PLACEHOLDER, canonical_bytes, digest
from .errors import AID_UNKNOWN, ALIAS_TAKEN, NOT_CANONICAL, SUBSTRATE_UNKNOWN
from .facade import FacadeSubstrate
from .protocol import (
    ACDC_DT,
    AID,
    ENDORSEMENT_SCHEMA,
    SAID,
    Corpus,
    Event,
    FoldValues,
    OpenSubstrate,
    Position,
    Substrate,
)
from .select import FACADE, KERIPY, NAMES, substrate_named

__all__ = [
    "ACDC_DT",
    "AID",
    "AID_UNKNOWN",
    "ALIAS_TAKEN",
    "ENDORSEMENT_SCHEMA",
    "FACADE",
    "KERIPY",
    "NAMES",
    "NOT_CANONICAL",
    "SAID",
    "SAID_LENGTH",
    "SAID_PLACEHOLDER",
    "SUBSTRATE_UNKNOWN",
    "Corpus",
    "Event",
    "FacadeSubstrate",
    "FoldValues",
    "OpenSubstrate",
    "Position",
    "Substrate",
    "canonical_bytes",
    "digest",
    "substrate_named",
]
