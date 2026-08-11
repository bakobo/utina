"""The fold. Pure, and kept that way by test.

Custos §1.4 axiom 2 closes the fold's inputs at exactly three committed values —
the committed evidence bundle, the committed law head, and the appraisal
position — and admits no other influence on the result. That closure is why this
package needs no KERI library: everything here is a function of committed values
handed in by the caller, and producing those values from CESR streams is
``utina.substrate``'s job.

The boundary is enforced by ``tests/test_fold_purity.py`` rather than by
convention, because an architectural claim defended only by a comment decays the
first time someone needs a digest in a hurry.
"""

# The substrate-forbidden list the purity test enforces. Adding a name here is a
# decision that belongs in this.i before the import that motivates it.
FORBIDDEN_IMPORTS = frozenset(
    {"keri", "keria", "cesride", "parside", "hio", "blake3", "lmdb"}
)

# The fold's public surface: what it is asked, and what answers. The value types
# stay in their own modules — a caller who wants Affirmed knows it is a finding —
# but the two names an application actually calls are re-exported here, because
# the acceptance oracle's import is the contract's own statement of that surface.
# Imported after FORBIDDEN_IMPORTS so the constant is bound before any submodule
# that reads it during its own import.
from utina.fold.constitution import Constitution  # noqa: E402
from utina.fold.evaluate import evaluate  # noqa: E402

__all__ = ["FORBIDDEN_IMPORTS", "Constitution", "evaluate"]
