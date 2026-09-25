"""Meridian Bank — the second governed domain, and the one that makes governance compose.

A second governed domain is pointless unless it intersects the first, because
composability is the point of having one (``this.i`` @rc5fibel). Acme approves opening a
bank account under its own governance — already beat D1, certified. Meridian's own law
obliges it to confirm that a prospective customer could lawfully take that action, so it
folds Acme's log, commits what it relied on and what it checked, and only then does its
own arithmetic carry.

Neither domain reads the other's law. What crosses the boundary is a certified result
over committed inputs, which is what keeps this clear of the portable clause language
``custos-4.2.md:2044`` defers.
"""

from .build import CUSTOMER_ACT, CUSTOMER_COORDINATE, build
from .law import (
    ACCOUNT_ACTS,
    DILIGENCE_FIELD,
    DISPLAY,
    DOMAIN,
    GAID,
    GOVERNANCE_REGISTRY,
    OFFICERS,
    OPEN_ACCOUNT,
    PRIYA,
    TOMAS,
    charter,
)

__all__ = [
    "ACCOUNT_ACTS",
    "CUSTOMER_ACT",
    "CUSTOMER_COORDINATE",
    "DILIGENCE_FIELD",
    "DISPLAY",
    "DOMAIN",
    "GAID",
    "GOVERNANCE_REGISTRY",
    "OFFICERS",
    "OPEN_ACCOUNT",
    "PRIYA",
    "TOMAS",
    "build",
    "charter",
]
