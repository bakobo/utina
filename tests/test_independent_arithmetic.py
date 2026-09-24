"""The fold's arithmetic, checked against a second implementation that shares none of its code.

``tools/independent-arithmetic.py`` recomputes threshold sums, canonical defeat
selection and the requirement set's order and deduplication from the text, with
the standard library alone, in a separate process. This file generates cases,
asks both, and compares. It is the fold's counterpart to
``test_independent_reader.py``, which does the same for the KERI the substrate
writes: a bug shared between a computation and the test that checks it passes
unseen, and a second implementation is the one check that cannot share it.

The cases are generated from a fixed seed, so a failure reproduces, and are
shaped to hit the edges: weights that reach unity only as rationals, empty and
present subcodes, and elements that tie on the four ordered fields.
"""

from __future__ import annotations

import ast
import json
import random
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from utina.fold.finding import (
    Citation,
    DefeaterClass,
    PendingSpecies,
    RequirementElement,
    canonical_requirement_set,
    select_defeat,
)
from utina.fold.group import Disposition, Group, Slot

CHECKER = Path(__file__).resolve().parent.parent / "tools" / "independent-arithmetic.py"
SCHEMAS = ("E" + "s" * 43, "E" + "t" * 43)
PARTIES = ("acme:dev", "acme:marta", "acme:nina", "acme:ömer", "acme:zed")
WEIGHTS = ("1/2", "1/3", "1/4", "2/3", "1/6", "1", "3/4")
CLAUSES = ("A1", "A2", "B1", "É1")
SPECIES = tuple(PendingSpecies)
CLASSES = tuple(DefeaterClass)
CASES = 400


def ask(cases: dict[str, object]) -> dict[str, list[object]]:
    """The second implementation's answers, from a process that never loaded utina."""
    done = subprocess.run(
        [sys.executable, str(CHECKER)],
        input=json.dumps(cases),
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    answers: dict[str, list[object]] = json.loads(done.stdout)
    return answers


def test_the_checker_shares_no_code_with_utina() -> None:
    """A checker that imported utina would be checking utina against itself."""
    tree = ast.parse(CHECKER.read_text(encoding="utf-8"), filename=str(CHECKER))
    imported = {
        alias.name.partition(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.partition(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert imported <= {"__future__", "json", "sys", "fractions"}


def test_threshold_sums_agree() -> None:
    rng = random.Random(0x7A11)
    cases = []
    expected = []
    for _ in range(CASES):
        parties = rng.sample(PARTIES, rng.randint(1, len(PARTIES)))
        weights = [rng.choice(WEIGHTS) for _ in parties]
        # Some parties the group never slots, whose disposition must count for nothing.
        held = {
            party: rng.choice(("endorsed", "declined", "pending"))
            for party in rng.sample(PARTIES, rng.randint(0, len(PARTIES)))
        }
        group = Group(
            "MxN",
            tuple(
                Slot(party, Fraction(weight), SCHEMAS[0])
                for party, weight in zip(parties, weights, strict=True)
            ),
        )
        dispositions = {party: Disposition(state) for party, state in held.items()}
        slotted = [list(pair) for pair in zip(parties, weights, strict=True)]
        cases.append({"slots": slotted, "held": held})
        expected.append(
            {
                "satisfied": group.satisfied(dispositions),
                "reachable": group.reachable(dispositions),
                "outstanding": [slot.endorser for slot in group.outstanding(dispositions)],
            }
        )

    answers = ask({"threshold": cases, "selection": [], "requirements": []})

    assert answers["threshold"] == expected
    assert any(one["satisfied"] for one in expected)
    assert any(not one["reachable"] for one in expected)


def test_defeat_selection_agrees() -> None:
    rng = random.Random(0xDEFE)
    cases = []
    expected = []
    for _ in range(CASES):
        drawn = [
            (rng.choice(CLASSES), rng.choice(CLAUSES), rng.choice(("", *PARTIES)))
            for _ in range(rng.randint(1, 6))
        ]
        citations = [
            Citation(clause=clause, defeater_class=kind, subcode=subcode)
            for kind, clause, subcode in drawn
        ]
        cases.append([[kind.name.lower(), clause, subcode] for kind, clause, subcode in drawn])
        expected.append(select_defeat(citations).selection_key())

    answers = ask({"threshold": [], "selection": cases, "requirements": []})

    picks = zip(cases, answers["selection"], strict=True)
    chosen = [citations_key(case[index]) for case, index in picks]
    assert chosen == expected


def citations_key(citation: list[str]) -> tuple[int, str, bool, str]:
    """A selection answer is an index; compare what it selects, since ties are equal."""
    kind, clause, subcode = citation
    return Citation(
        clause=clause, defeater_class=DefeaterClass[kind.upper()], subcode=subcode
    ).selection_key()


def test_requirement_sets_agree() -> None:
    rng = random.Random(0x5E75)
    cases = []
    expected = []
    for _ in range(CASES):
        drawn = []
        for _ in range(rng.randint(1, 8)):
            species = rng.choice(SPECIES)
            ground = rng.choice(("", "E" + "g" * 43)) if species.rank == 3 else ""
            drawn.append(
                RequirementElement(
                    endorser=rng.choice(PARTIES),
                    clause=rng.choice(CLAUSES),
                    schema=rng.choice(SCHEMAS),
                    kind=rng.choice(("endorsement", "certification")),
                    species=species,
                    ground=ground,
                )
            )
        # Repeats, so deduplication has something to do.
        drawn += rng.sample(drawn, rng.randint(0, len(drawn)))
        rng.shuffle(drawn)
        cases.append([row(one) for one in drawn])
        expected.append([row(one) for one in canonical_requirement_set(drawn)])

    answers = ask({"threshold": [], "selection": [], "requirements": cases})

    assert answers["requirements"] == expected


def row(element: RequirementElement) -> list[str]:
    return [
        element.endorser,
        element.kind,
        element.clause,
        element.species.value[1],
        element.schema,
        element.ground,
    ]
