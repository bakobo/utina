"""Two processes, sharing nothing, building Acme twice.

Replay is the whole claim: a stranger holding the committed logs recomputes the
same Constitution. Inside one interpreter that is nearly free — the same objects
do the same arithmetic — so the property is checked where it can actually fail.
Each of these builds Acme from scratch in a fresh interpreter, with a randomized
hash seed, and compares the committed bytes.

Under keripy this rests on a structural fact worth stating: a KERI key event
carries no timestamp. What does vary is pinned deliberately — the salt, the
order the composition root incepts in, and the stretch tier (this.i @7jrbt3) —
and every one of those is a literal in the source rather than an environment.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from utina.substrate import NAMES

pytest.importorskip(
    "utina.fold.corpus",
    reason="the fold has no Corpus yet — determinism is a claim about its inputs",
)

#: Builds Acme and prints everything a second run would have to match: every
#: committed body's canonical bytes, every identifier, every signature, the
#: parties' identifiers, and the Constitution the fold computes from all of it.
BUILD = """
import json, sys
from utina.acme import build
from utina.cli.world import RealValues
from utina.fold.constitution import Constitution
from utina.substrate import canonical_bytes, substrate_named

with substrate_named(sys.argv[1]) as substrate:
    record = build(values=RealValues(), substrate=substrate)
    law = Constitution.at(record.corpus, record.at("board-seated"))
    print(json.dumps({
        "aids": dict(record.aids),
        "saids": [event.said for event in record.events],
        "bodies": [canonical_bytes(event.body).decode() for event in record.events],
        "law": law.canonical_bytes().decode(),
        "anchor": record.substrate.anchoring_event(record.said("seat-the-board")),
    }))
"""


def acme_in_a_separate_process(name: str, where: Path) -> dict[str, object]:
    """Acme, built by an interpreter that shares nothing with this one."""
    where.mkdir(parents=True, exist_ok=True)
    script = where / "build_acme.py"
    script.write_text(BUILD, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(script), name],
        capture_output=True,
        text=True,
        check=True,
        cwd=where,
        env={**os.environ, "PYTHONHASHSEED": "random"},
    )
    parsed: dict[str, object] = json.loads(completed.stdout)
    return parsed


@pytest.mark.parametrize("name", NAMES)
def test_two_processes_build_a_byte_identical_acme(name: str, tmp_path: Path):
    """Every committed byte, both backends, across a process boundary."""
    first = acme_in_a_separate_process(name, tmp_path / "first")
    second = acme_in_a_separate_process(name, tmp_path / "second")

    assert first["bodies"] == second["bodies"]
    assert first["saids"] == second["saids"]
    assert first["aids"] == second["aids"]
    assert first["law"] == second["law"]
    assert first["anchor"] == second["anchor"]


@pytest.mark.parametrize("name", NAMES)
def test_the_thing_being_compared_is_not_empty(name: str, tmp_path: Path):
    """A comparison of two empty logs would pass forever and mean nothing."""
    built = acme_in_a_separate_process(name, tmp_path / "only")

    assert len(built["saids"]) == len(set(built["saids"])) > 15  # type: ignore[arg-type]
    assert len(set(built["aids"].values())) == 4  # type: ignore[union-attr]
    assert built["anchor"], "the board-seating amendment is anchored, or D4 is a story"


def test_the_two_backends_do_not_produce_the_same_record(tmp_path: Path):
    """Different digests and different identifiers, as Q23 says they must be.

    Sameness across processes is the claim. Sameness across *backends* would
    mean one of them was not doing what it says: keripy's identifiers are
    Blake3-256 over KERI's own JSON and the facade's are Blake2b over its own.
    """
    facade = acme_in_a_separate_process("facade", tmp_path / "facade")
    keripy = acme_in_a_separate_process("keripy", tmp_path / "keripy")

    assert facade["saids"] != keripy["saids"]
    assert facade["aids"] != keripy["aids"]
