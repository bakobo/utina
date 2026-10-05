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
``tick note <id> <detail>``. The title carries the survivor's stable id as ``[m:<id>]``, and the
note opens with ``mutant-id: <id>``. A survivor whose id already appears in a
``mutation-survivor`` tick, open or closed, is not filed again, so a survivor someone dismissed
stays dismissed; but if that tick's body lacks the note's ``mutant-id`` line, the note never
landed (``tick note`` failed after ``tick add`` succeeded), and it is added now.

A survivor whose mutation only changes the text of a message literal is counted in the closing
summary and not ticked. That is decided by ``mutate.classify`` from the record's own diff and
its ``message_sink``, never from the stored ``class``, and it files whenever it cannot tell: a
record without a sink is behavioural. A report that is not the shape ``mutate.py`` writes is
refused whole, with the code below and the record it tripped on, before anything is filed. No
tick mark is placed in the code, since a survivor is a question about the tests and the line it
names moves.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mutate import STRING_ONLY, classify  # a sibling script, not a package

TAG = "mutation-survivor"
WORKFLOW = "mutation.yml"
ARTIFACT = "mutation-report"
REPORT = "mutation-report.json"
ID_IN_TITLE = re.compile(r"\[m:([0-9a-f]{12})\]")
MUTANT_ID = re.compile(r"[0-9a-f]{12}")
MALFORMED = "e.input.malformed.mutation-report.f"
NEXT_STEP = ("Either a test is missing an assertion that would notice this, or the mutation is "
             "equivalent and the tick can be closed with a note saying why.")


class MalformedReportError(Exception):
    """A report, or one record in it, is not the shape mutate.py writes."""


def _strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def _integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def check_record(s: object) -> None:
    """Raise MalformedReportError naming the first field missing or of the wrong type."""
    if not isinstance(s, dict):
        raise MalformedReportError(f"it is a {type(s).__name__}, not an object")
    if not (isinstance(s.get("id"), str) and MUTANT_ID.fullmatch(s["id"])):
        raise MalformedReportError("its id is not 12 lowercase hex digits")
    for key in ("mutmut_name", "file", "function"):
        if not isinstance(s.get(key), str):
            raise MalformedReportError(f"its {key} is not text")
    if not _integer(s.get("line")):
        raise MalformedReportError("its line is not an integer")
    mutation = s.get("mutation")
    if not (isinstance(mutation, dict) and _strings(mutation.get("removed"))
            and _strings(mutation.get("added")) and isinstance(mutation.get("diff"), str)):
        raise MalformedReportError(
            "its mutation lacks removed and added lists of lines, or a diff")
    result = s.get("test_result")
    if not (isinstance(result, dict) and isinstance(result.get("command"), str)
            and _integer(result.get("tests_run")) and _integer(result.get("exit_code"))):
        raise MalformedReportError("its test_result lacks a command, tests_run or exit_code")
    if not isinstance(s.get("message_sink"), (str, type(None))):
        raise MalformedReportError("its message_sink is neither text nor null")


def check_report(data: object) -> None:
    if not isinstance(data, dict):
        raise MalformedReportError(f"the report is a {type(data).__name__}, not an object")
    if not isinstance(data.get("commit"), str):
        raise MalformedReportError("the report names no commit")
    if not isinstance(data.get("survivors"), list):
        raise MalformedReportError("the report's survivors are not a list")
    for index, record in enumerate(data["survivors"]):
        try:
            check_record(record)
        except MalformedReportError as error:
            raise MalformedReportError(
                f"survivor {index} in the report is malformed: {error}") from None


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


def ticked(tick: str) -> dict[str, str]:
    """Mutant id to tick id, for every mutation-survivor tick, closed ones included."""
    found = {}
    for line in run([tick, "ls", "--all", "--tag", TAG]).splitlines():
        match = ID_IN_TITLE.search(line)
        if match:
            found.setdefault(match.group(1), line.split()[0])
    return found


def title(s: dict) -> str:
    return f"mutation survivor [m:{s['id']}] {s['file']}:{s['line']} in {s['function']}"


def detail(s: dict, data: dict) -> str:
    result = s["test_result"]
    opening = (f"A mutant of {s['function']} in {s['file']} survived the nightly mutation run "
               f"at commit {data['commit']}: {result['tests_run']} tests cover the function, "
               f"and all of them passed with this change in place "
               f"(exit {result['exit_code']}).")
    name = f"mutmut name: {s['mutmut_name']} (the ordinal is only meaningful for that run)."
    return "\n".join([
        f"mutant-id: {s['id']}",
        opening,
        "",
        s["mutation"]["diff"],
        "",
        f"Test command: {result['command']}",
        name,
        NEXT_STEP,
    ])


def file_ticks(data: dict, tick: str, dry_run: bool) -> tuple[list[str], int, int, int]:
    """Returns (ids filed, count already ticked, count re-noted, count string-only)."""
    have = ticked(tick)
    done: set[str] = set()
    filed: list[str] = []
    skipped = renoted = strings = 0
    for s in data["survivors"]:
        mutation = s["mutation"]
        kind = classify(mutation["removed"], mutation["added"], s.get("message_sink"))
        if kind == STRING_ONLY:
            strings += 1
            continue
        if s["id"] in done:
            skipped += 1
            continue
        done.add(s["id"])
        if s["id"] in have:
            tick_id = have[s["id"]]
            if f"mutant-id: {s['id']}" in run([tick, "show", tick_id]):
                skipped += 1
            elif dry_run:
                print(f"would re-note {tick_id}: {title(s)}")
                renoted += 1
            else:
                run([tick, "note", tick_id, detail(s, data)])
                print(f"re-noted {tick_id}: {title(s)}")
                renoted += 1
            continue
        if dry_run:
            print(f"would file: {title(s)}")
        else:
            out = run([tick, "add", "--kind", "debt", "--tag", TAG, title(s)])
            tick_id = out.split()[0]
            run([tick, "note", tick_id, detail(s, data)])
            print(f"filed {tick_id}: {title(s)}")
        filed.append(s["id"])
    return filed, skipped, renoted, strings


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
    if isinstance(data, dict) and data.get("failure"):
        print(f"the run that produced this report failed, so it holds no results:\n"
              f"{data['failure']}", file=sys.stderr)
        return 1
    try:
        check_report(data)
    except MalformedReportError as error:
        print(f"{MALFORMED}: {error}. Nothing was filed; regenerate the report with "
              "tools/mutation/mutate.py.", file=sys.stderr)
        return 2
    filed, skipped, renoted, strings = file_ticks(data, args.tick, args.dry_run)
    verb = "would file" if args.dry_run else "filed"
    print(f"{verb} {len(filed)}; {skipped} already ticked; {renoted} re-noted; {strings} "
          f"string-only survivors not ticked; {len(data['survivors'])} survivors in the report")
    return 0


if __name__ == "__main__":
    sys.exit(main())
