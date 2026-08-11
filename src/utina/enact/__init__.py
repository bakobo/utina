"""The constructor's verb: producing committed governance events.

Custos §1.3 — a constructor cannot act except by producing the evidence of its
act. Nothing here judges; nothing in ``utina.fold`` writes.
"""

from .constructor import Constructor
from .errors import (
    DOMAIN_INCEPTED,
    DOMAIN_UNINCEPTED,
    SIGNATURE_UNVERIFIABLE,
    SUBJECT_UNKNOWN,
)

__all__ = [
    "DOMAIN_INCEPTED",
    "DOMAIN_UNINCEPTED",
    "SIGNATURE_UNVERIFIABLE",
    "SUBJECT_UNKNOWN",
    "Constructor",
]
