"""Refusal: an operational fact, and deliberately not a fifth finding value.

Custos, ``custos-4.2.md:1896-1900``:

    when two committed authorities meet with no committed rule for composing
    them, the evaluator refuses the invocation. Refusal is not a fifth finding
    value — it is the evaluator declining to answer an ill-posed question,
    recorded as an operational fact.

The line between a refusal and a pending finding is **rule-presence, not
evidence-presence**. Where committed evidence runs short *under a committed
rule*, the finding is pending and names the typed requirement that would
discharge it; where no committed rule makes the invocation evaluable at all, the
evaluator refuses (``:225-231``). "Not missing evidence under a rule, but a
missing rule."

Three decisions follow, and each is defended by a test in
``tests/test_refusal.py``:

- ``Refusal`` is **not** a subclass of ``Finding`` and never appears inside one.
  An engine that made it one would pass every other test in the suite and would
  have lost the distinction the separation rule exists to draw.
- A refusal is a **value**, not an exception. The document calls it a recorded
  operational fact, and you cannot record what you threw (this.i @zztcbs).
- A refusal **names what is missing** — axiom 3, ``:277-278``: "Where committed
  law runs out, the fold refuses rather than legislates. The refusal names what
  is missing." A refusal naming nothing is the discretion replay exists to
  eliminate, so ``missing`` is a ground and its absence raises
  ``e.state.ground-missing.f``.

The refusal record's *form* is deliberately not committed by Custos — §16 holds
that question open — so this shape is utina's and it carries no self-addressing
identifier. Giving one to a refusal would resolve an openness question the
document is still holding open.
"""

import dataclasses

from utina.fold.errors import GROUND_MISSING, MALFORMED_INPUT, require

__all__ = ["Refusal"]


@dataclasses.dataclass(frozen=True)
class Refusal:
    """The evaluator declining an ill-posed question, with its ground named.

    ``missing`` names what the law does not supply, concretely enough that a
    reader can go and commit it — an act class with no composition rule, a seam
    with no ordering. ``detail`` amplifies for a human reader and may be empty;
    it is not the ground.
    """

    missing: str
    detail: str

    def __post_init__(self) -> None:
        for value, field in ((self.missing, "missing"), (self.detail, "detail")):
            require(
                isinstance(value, str),
                MALFORMED_INPUT,
                field=f"a refusal's {field}",
                expected="prose naming what the committed law does not supply",
                found=repr(value),
            )
        require(
            self.missing != "",
            GROUND_MISSING,
            value="a refusal",
            ground="a concrete name for what is missing from the committed law",
        )
