"""Acme, Inc. — the demo's governed domain, its law, and its committed log.

``build`` drives ``utina.enact`` through every beat of ``docs/demo-script.md``
and returns the record the acceptance oracle reads. It takes the fold's value
constructors rather than importing the fold (this.i @tvaq2s), so the writing
plane stays loadable and testable on its own.
"""

from .build import build
from .errors import LABEL_UNKNOWN, NAME_UNKNOWN
from .law import (
    AMENDMENT_ACTS,
    BOARD,
    BOARD_LAW,
    DEV,
    FOUNDERS,
    FOUNDING_LAW,
    GAID,
    MARTA,
    NINA,
    ORDINARY_ACTS,
    UNGOVERNED_ACT,
)
from .record import Acme

__all__ = [
    "AMENDMENT_ACTS",
    "BOARD",
    "BOARD_LAW",
    "DEV",
    "FOUNDERS",
    "FOUNDING_LAW",
    "GAID",
    "LABEL_UNKNOWN",
    "MARTA",
    "NAME_UNKNOWN",
    "NINA",
    "ORDINARY_ACTS",
    "UNGOVERNED_ACT",
    "Acme",
    "build",
]
