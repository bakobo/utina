"""Threshold arithmetic: add up weights, compare against unity. That is all.

This module is deliberately trivial, and deliberately its own file. Custos
withdrew the claim that KERI's threshold algebra transfers to the evidence tier —
the two constructions are "the same satisfaction shape over differently typed slot
judgments, never one algebra" (``custos-4.2.md:1956-1958``) — because the question
of *what enters the sum* is a fold question and never the substrate's. An
implementer who "wires the substrate's threshold evaluator to an edge group and
concludes the obligation is discharged has discharged the arithmetic and none of
the slot dispositions."

So the arithmetic is separated from the predicate on purpose, and the separation
is visible in the file listing (``this.i`` @mw6dxh): everything here would be
satisfied by keripy's ``Tholder``, and everything in ``slots.py`` is what
``Tholder`` cannot answer.

Weights are :class:`fractions.Fraction`. Unity has to be exactly decidable, and
Acme's own clause B2 puts three slots at ``1/3`` on the critical path, where
binary floating point does not sum to one.
"""

from __future__ import annotations

from collections.abc import Iterable
from fractions import Fraction

__all__ = ["UNITY", "reaches_unity", "total"]

UNITY = Fraction(1)
"""The threshold is the fixed constant 1. There is no separate count field: how many
endorsements are enough, and how much each is worth, lives entirely in the weights
(the dossier specification's threshold mechanics, ``dossier-spec-body.md:353``)."""


def total(weights: Iterable[Fraction]) -> Fraction:
    """The exact sum of ``weights``, which is zero when there are none."""
    return sum(weights, Fraction(0))


def reaches_unity(amount: Fraction) -> bool:
    """Whether ``amount`` reaches the threshold. *At least* unity, so this is inclusive."""
    return amount >= UNITY
