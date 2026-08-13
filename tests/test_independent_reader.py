"""The one claim utina's own code cannot make about itself.

Everywhere else in this suite, the thing computing the answer and the thing
checking it share a codebase. Here they do not: ``utina`` writes a key log to
disk with ``--substrate keripy --store DIR``, and ``tools/read-keri-log.py``
opens that LMDB environment with a bare keripy ``Baser`` — no Habery, no
keystore, and, checked below by reading its source, no import of utina at all —
walks the logs, re-derives every event's identifier through keripy's own
verifying constructor, and reports which establishment event anchors the
board-seating amendment.

If this passes, the demo is not asserting that it wrote KERI. Somebody else's
reader is.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip(
    "utina.fold.corpus",
    reason="the fold has no Corpus yet — there is no record to write down",
)

READER = Path(__file__).resolve().parent.parent / "tools" / "read-keri-log.py"


def run(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """One command, with its output captured, in a directory of its own."""
    cwd.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [sys.executable, *argv],
        capture_output=True,
        text=True,
        cwd=cwd,
        env={**os.environ, "PYTHONHASHSEED": "random"},
    )


def seat_the_board(store: Path) -> str:
    """The identifier of Acme's board-seating amendment, from utina's side."""
    from utina.cli.world import world

    with world("keripy", store=store) as record:
        return str(record.said("seat-the-board"))


def test_the_reader_shares_no_code_with_utina() -> None:
    """A reader that imported utina would be checking utina against itself."""
    tree = ast.parse(READER.read_text(encoding="utf-8"), filename=str(READER))
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
    assert "utina" not in imported
    assert "keri" in imported, "a reader that does not use keripy proves nothing"


def test_an_independent_keripy_reader_finds_the_anchor_utina_wrote(tmp_path: Path):
    """Beat D4, checked from outside: the amendment really does ride a rotation."""
    store = tmp_path / "acme-kel"
    written = run(
        "-c", "from utina.cli import main; raise SystemExit(main())",
        "log", "--at", "board-seated",
        "--substrate", "keripy", "--store", str(store),
        cwd=tmp_path / "writer",
    )
    assert written.returncode == 0, written.stderr
    assert (store / "keri" / "db" / "utina").is_dir()

    expected = seat_the_board(tmp_path / "another-store")
    read = run(str(READER), str(store), "--expect", expected, cwd=tmp_path / "reader")

    assert read.returncode == 0, read.stderr
    assert f"FOUND  {expected}" in read.stdout
    assert "every SAID re-derives: True" in read.stdout
    assert "  sn 1  rot  " in read.stdout


def test_the_reader_refuses_a_digest_nothing_anchors(tmp_path: Path):
    """Fail closed: 'I found it' has to be capable of being 'I did not'."""
    store = tmp_path / "acme-kel"
    written = run(
        "-c", "from utina.cli import main; raise SystemExit(main())",
        "log", "--substrate", "keripy", "--store", str(store),
        cwd=tmp_path / "writer",
    )
    assert written.returncode == 0, written.stderr

    read = run(str(READER), str(store), "--expect", "E" + "z" * 43, cwd=tmp_path / "reader")

    assert read.returncode == 1
    assert "NOT FOUND" in read.stderr


def test_the_reader_says_so_when_there_is_no_log(tmp_path: Path):
    empty = tmp_path / "nothing"
    read = run(str(READER), str(empty), cwd=tmp_path / "reader")

    assert read.returncode == 1
    assert "no key log found" in read.stderr
