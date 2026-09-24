"""A second implementation of the fold's arithmetic, written from the text rather than the code.

utina's threshold sums, its canonical defeat selection and its requirement-set
order are each a few lines, and each is exactly the kind of line where a bug
shared between the code and the test that checks it passes unseen. This script
recomputes all three from ``custos-4.2.md`` and the readings pinned in
``docs/custos-questions.md``, using the standard library alone, and
``tests/test_independent_arithmetic.py`` checks — by reading this file's
source — that it imports nothing from utina.

It reads one JSON object on stdin and writes one on stdout:

- ``threshold``: a list of ``{"slots": [[party, "n/d"], ...], "held": {party:
  "endorsed" | "declined" | "pending"}}``; each answer is ``{"satisfied",
  "reachable", "outstanding"}``.
- ``selection``: a list of lists of ``[class, clause, subcode]``; each answer is
  the index of the citation selected.
- ``requirements``: a list of lists of ``[party, kind, clause, species, schema,
  ground]``; each answer is the deduplicated set in canonical order.

The readings encoded here, so that a disagreement can be traced to one:

- Unity is a sum of exact rationals reaching 1 (``:1946-1951``). A declined slot's
  weight can never arrive; a pending one still can. A party the law does not
  slot contributes nothing.
- Defeat selection is the lexicographic minimum of (defeater-class rank,
  citation identifier, subcode), with the classes ranked crypto, authority,
  merit, superseded (``:1766-1779``), and an empty subcode ordering after every
  present one (Q7).
- A requirement set is ordered by party, kind, clause bytes and species
  (``:1650-1651``), with species ranked in the order the text enumerates them
  (Q5), and then by schema and ground; deduplication sees all six fields
  (``this.i`` @fdhqffc3). Text compares as UTF-8 octets.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction

CLASS_RANK = {"crypto": 0, "authority": 1, "merit": 2, "superseded": 3}
SPECIES_RANK = {"absent": 0, "window-open": 1, "unresolved-conflict": 2, "expired/abandoned": 3}


def threshold(case: dict[str, list[list[str]] | dict[str, str]]) -> dict[str, object]:
    slots = [(party, Fraction(weight)) for party, weight in case["slots"]]
    held = case["held"]

    def state(party: str) -> str:
        return held.get(party, "pending") if isinstance(held, dict) else "pending"

    endorsed = sum((w for p, w in slots if state(p) == "endorsed"), Fraction(0))
    possible = sum((w for p, w in slots if state(p) != "declined"), Fraction(0))
    return {
        "satisfied": endorsed >= 1,
        "reachable": possible >= 1,
        "outstanding": [p for p, _ in slots if state(p) == "pending"],
    }


def selection(citations: list[list[str]]) -> int:
    def key(index: int) -> tuple[int, bytes, int, bytes]:
        kind, clause, subcode = citations[index]
        return (CLASS_RANK[kind], clause.encode(), 1 if subcode == "" else 0, subcode.encode())

    return min(range(len(citations)), key=key)


def requirements(elements: list[list[str]]) -> list[list[str]]:
    def key(element: list[str]) -> tuple[bytes, bytes, bytes, int, bytes, bytes]:
        party, kind, clause, species, schema, ground = element
        return (
            party.encode(),
            kind.encode(),
            clause.encode(),
            SPECIES_RANK[species],
            schema.encode(),
            ground.encode(),
        )

    unique = {key(element): element for element in elements}
    return [unique[k] for k in sorted(unique)]


def main() -> None:
    cases = json.load(sys.stdin)
    json.dump(
        {
            "threshold": [threshold(case) for case in cases["threshold"]],
            "selection": [selection(case) for case in cases["selection"]],
            "requirements": [requirements(case) for case in cases["requirements"]],
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
