"""Choosing a substrate by name, without importing the one you did not choose.

The quarantine (this.i @343xvm) is only real if ``--substrate facade`` loads no
KERI library at all, so the keripy backend is imported here, lazily, inside the
one branch that asks for it. The import is relative on purpose: no module above
``utina/substrate/keri*.py`` names a KERI package, and ``tests/test_purity.py``
checks that by reading the source rather than by trusting this comment.

Both backends are context managers, because one of them has to be — a ``Habery``
owns a keystore and two LMDB environments and must be closed — and a composition
root that has to remember which is which will eventually forget.
"""

from __future__ import annotations

from pathlib import Path

from .errors import SUBSTRATE_UNKNOWN
from .facade import FacadeSubstrate
from .protocol import Substrate

#: The pure-Python backend. The default everywhere, by decision (this.i @dxs27r).
FACADE = "facade"

#: The real one: keripy AIDs, Blake3 SAIDs, Ed25519 signatures, a real KEL.
KERIPY = "keripy"

#: Every name a caller may ask for, in the order a help screen should list them.
NAMES = (FACADE, KERIPY)


def substrate_named(name: str, *, store: Path | None = None) -> Substrate:
    """The substrate ``name`` selects, ready to be entered as a context manager.

    ``store`` is where a backend that keeps a database keeps it. ``None`` means
    an ephemeral one, which is what tests want; a path means a durable store an
    independent KERI tool can be pointed at afterwards. The facade keeps nothing
    and ignores it.
    """
    if name == FACADE:
        return FacadeSubstrate()
    if name == KERIPY:
        from .keripy import KeripySubstrate

        return KeripySubstrate(store=store)
    raise SUBSTRATE_UNKNOWN(name=name, known=", ".join(NAMES))
