#!/usr/bin/env python3
"""File one ``tick`` per surviving mutant in the latest nightly mutation report.

RUN BY HAND during the mutation-testing pilot (two weeks from 2026-10-05); nothing schedules it.
Survivors are triaged by a person before they become anyone's work, and whether they deserve a
tick at all is one of the things the pilot is measuring.

    uv run python tools/mutation/ticks.py               # latest successful mutation.yml run
    uv run python tools/mutation/ticks.py --run-id N    # a particular run
    uv run python tools/mutation/ticks.py --report F    # a report already on disk
    ... --dry-run                                       # say what would be filed, file nothing

Each survivor becomes ``tick add --kind debt --tag mutation-survivor "<title>"`` followed by
``tick note <id> <detail>``. The title carries the survivor's stable id as ``[m:<id>]``, and a
survivor whose id already appears in any ``mutation-survivor`` tick, open or closed, is skipped:
a survivor someone dismissed stays dismissed. No tick mark is placed in the code, since a
survivor is a question about the tests and the line it names moves.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TAG = "mutation-survivor"
WORKFLOW = "mutation.yml"
ARTIFACT = "mutation-report"
REPORT = "mutation-report.json"
ID_IN_TITLE = re.compile(r"\[m:([0-9a-f]{12})\]")


def run(argv: list[str]) -> str:
    return subprocess.run(argv, capture_output=True, text=True, check=True).stdout


def download(gh: str, run_id: str | None, into: Path) -> Path:
    if run_id is None:
        run_id = run([gh, "run", "list", "--workflow", WORKFLOW, "--status", "success",
                      "--limit", "1", "--json", "databaseId", "--jq", ".[0].databaseId"])
        run_id = run_id.strip()
        if not run_id:
            raise SystemExit(f"no successful {WORKFLOW} run to download a report from")
    run([gh, "run", "download", run_id, "--name", ARTIFACT, "--dir", str(into)])
    return into / REPORT


def ticked(tick: str) -> set[str]:
    """Mutant ids already recorded in a mutation-survivor tick, closed ones included."""
    return set(ID_IN_TITLE.findall(run([tick, "ls", "--all", "--tag", TAG])))


def title(s: dict) -> str:
    return f"mutation survivor [m:{s['id']}] {s['file']}:{s['line']} in {s['function']}"


def detail(s: dict, data: dict) -> str:
    result = s["test_result"]
    return "\n".join([
        f"A mutant of {s['function']} in {s['file']} survived the nightly mutation run at "
        f"commit {data['commit']}: {result['tests_run']} tests cover the function, and all of "
        f"them passed with this change in place (exit {result['exit_code']}).",
        "",
        s["mutation"]["diff"],
        "",
        f"Test command: {result['command']}",
        f"mutmut name: {s['mutmut_name']} (the ordinal is only meaningful for that run).",
        "Either a test is missing an assertion that would notice this, or the mutation is "
        "equivalent and the tick can be closed with a note saying why.",
    ])


def file_ticks(data: dict, tick: str, dry_run: bool) -> tuple[list[str], int]:
    """Returns (ids filed, count skipped as already ticked)."""
    have = ticked(tick)
    filed: list[str] = []
    skipped = 0
    for s in data["survivors"]:
        if s["id"] in have:
            skipped += 1
            continue
        have.add(s["id"])
        if dry_run:
            print(f"would file: {title(s)}")
        else:
            out = run([tick, "add", "--kind", "debt", "--tag", TAG, title(s)])
            tick_id = out.split()[0]
            run([tick, "note", tick_id, detail(s, data)])
            print(f"filed {tick_id}: {title(s)}")
        filed.append(s["id"])
    return filed, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--report", type=Path, help="a mutation-report.json already on disk")
    source.add_argument("--run-id", help="the mutation.yml run to download the report from")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--gh", default="gh")
    parser.add_argument("--tick", default="tick")
    args = parser.parse_args(argv)

    with tempfile.TemporaryDirectory() as scratch:
        path = args.report or download(args.gh, args.run_id, Path(scratch))
        data = json.loads(path.read_text("utf-8"))
    if data.get("failure"):
        print(f"the run that produced this report failed, so it holds no results:\n"
              f"{data['failure']}", file=sys.stderr)
        return 1
    filed, skipped = file_ticks(data, args.tick, args.dry_run)
    verb = "would file" if args.dry_run else "filed"
    print(f"{verb} {len(filed)}; {skipped} already ticked; "
          f"{len(data['survivors'])} survivors in the report")
    return 0


if __name__ == "__main__":
    sys.exit(main())
