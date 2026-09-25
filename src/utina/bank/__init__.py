"""Meridian Bank — the second governed domain, and the one that makes ``--domain`` true.

A flag that resolves one value is not a flag. This fixture exists so the fold can be
shown folding a record it was not written around, and so that a domain committing **no
position labels** is a case the suite covers rather than a case the prose asserts
(``this.i`` @qprzacju).

Deliberately minimal, and deliberately **not** the two-constitution bank beat: that beat
needs cross-domain ground, an evaluation-seal credential and Meridian folding Acme's GEL,
its design is agreed and unbuilt, and the session that builds it should read everything
here as scaffolding rather than as settled.
"""

from .build import build
from .law import (
    CREDIT_ACTS,
    DISPLAY,
    DOMAIN,
    GAID,
    GOVERNANCE_REGISTRY,
    OFFICERS,
    PRIYA,
    TOMAS,
    charter,
)

__all__ = [
    "CREDIT_ACTS",
    "DISPLAY",
    "DOMAIN",
    "GAID",
    "GOVERNANCE_REGISTRY",
    "OFFICERS",
    "PRIYA",
    "TOMAS",
    "build",
    "charter",
]
