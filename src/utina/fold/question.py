"""The two constructors of a question the fold can be asked.

``Proposal`` asks whether an act *may* be performed; ``Committed`` asks whether a
performed act *was* lawful. Both are answered from the same closed triple, and
the difference between them is which bytes exist: Custos's evidence is committed
bytes (``custos-4.2.md:259-262``), and a proposal's un-committed approvals are
not evidence at all.

That is why a proposal is not a refusal and not an error. The law still governs
the act class, the requirement space is still committed ex-ante
(``:1620-1624``), and the endorsements that have not arrived are exactly what a
pending finding's typed requirement names. The same question therefore answers
``pending`` before the last endorsement commits and ``affirmed`` after, with
nothing else changing — U12 in ``../../thesmo-demo/audit-spec-requirements.md``,
and the clearest thing the demo has to show about a closed input triple.

The proposition itself is deliberately **not** a fourth member of the triple: the
axiom closes the inputs at evidence, law head and position, and a question is
what the evaluator is asked *about* them.
"""

import dataclasses

from utina.fold.errors import MALFORMED_INPUT, require
from utina.fold.triple import SAID

__all__ = ["Committed", "Proposal", "Question"]


def _named(value: object, field: str, expected: str) -> None:
    require(
        isinstance(value, str) and value != "",
        MALFORMED_INPUT,
        field=field,
        expected=expected,
        found=repr(value),
    )


@dataclasses.dataclass(frozen=True)
class Proposal:
    """"May we do this?" — evaluated before the fact, over the act's class."""

    act: str

    def __post_init__(self) -> None:
        _named(
            self.act,
            "a proposal's act class",
            "the name of an act class the law may govern, such as open-bank-account",
        )


@dataclasses.dataclass(frozen=True)
class Committed:
    """"Was this act lawful?" — evaluated after, over the act's committed bytes."""

    said: SAID

    def __post_init__(self) -> None:
        _named(
            self.said,
            "a committed question's act",
            "the self-addressing identifier of the committed act",
        )


Question = Proposal | Committed
"""What the fold can be asked. Two constructors, and the union of exactly those.

Written as a union rather than a ``type`` alias so that ``isinstance(q,
Question)`` works: callers discriminate on the constructor, and a check that
cannot be run at runtime would push them back to comparing class names.
"""
