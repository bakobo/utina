"""What a governed domain's record is, and how any domain commits its law.

Domain-neutral by construction. ``utina.acme`` and ``utina.bank`` are two fixtures that
build a :class:`Record` through this encoding; nothing here knows which, and no command
above it has to (``this.i`` @s34hkwkv).

The plane is quarantined exactly as the fixtures it was lifted out of are: no KERI
library, and no alias machinery. A display name is a string a fixture supplies, never a
COIA alias, which is ``utina.cli``'s alone (@cldspl).
"""

from .errors import LABEL_UNKNOWN, LABELS_ABSENT, NAME_UNKNOWN, POSITION_OUT_OF_RANGE
from .law import (
    CERTIFICATION_FIELD,
    clause,
    even,
    seat_slot,
    seated_by,
    semantics_block,
    slot,
)
from .record import SEQ_DIGITS, Record, is_sequence

__all__ = [
    "CERTIFICATION_FIELD",
    "LABELS_ABSENT",
    "LABEL_UNKNOWN",
    "NAME_UNKNOWN",
    "POSITION_OUT_OF_RANGE",
    "SEQ_DIGITS",
    "Record",
    "clause",
    "even",
    "is_sequence",
    "seat_slot",
    "seated_by",
    "semantics_block",
    "slot",
]
