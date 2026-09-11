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
    DEVICE,
    DEVICE_ROLE,
    EQUITY_ACTS,
    FOUNDERS,
    FOUNDING_LAW,
    GAID,
    GOVERNANCE_REGISTRY,
    MARTA,
    NINA,
    ORDINARY_ACTS,
    Q2_FORECAST,
    Q3_BUDGET,
    QUINN,
    SEAT,
    SEAT_ACTS,
    SEAT_OFFICE,
    SEAT_REGISTRY,
    UNGOVERNED_ACT,
)
from .record import Acme

__all__ = [
    "AMENDMENT_ACTS",
    "BOARD",
    "BOARD_LAW",
    "DEV",
    "DEVICE",
    "DEVICE_ROLE",
    "EQUITY_ACTS",
    "FOUNDERS",
    "FOUNDING_LAW",
    "GAID",
    "GOVERNANCE_REGISTRY",
    "LABEL_UNKNOWN",
    "MARTA",
    "NAME_UNKNOWN",
    "NINA",
    "ORDINARY_ACTS",
    "Q2_FORECAST",
    "Q3_BUDGET",
    "QUINN",
    "SEAT",
    "SEAT_ACTS",
    "SEAT_OFFICE",
    "SEAT_REGISTRY",
    "UNGOVERNED_ACT",
    "Acme",
    "build",
]
