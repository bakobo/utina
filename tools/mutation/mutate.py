#!/usr/bin/env python3
"""Mutation-test the source modules the default branch changed recently, and report survivors.

Part of a two-week mutation-testing pilot that began 2026-10-05. Branch coverage says a line ran
under some test; a surviving mutant says no test would notice that line being wrong. The pilot
measures how many survivors there are and whether they point at real gaps in the tests.

    uv run python tools/mutation/mutate.py [--since "7 days ago"] [--ref HEAD]
        [--module src/<pkg>/x.py ...] [--budget-minutes 300] [--out mutation-out]

Which modules: every ``.py`` file under ``[tool.mutmut].source_paths`` that a first-parent
commit on ``--ref`` touched since ``--since``, minus anything ``[tool.mutmut].do_not_mutate``
excludes. ``--module`` names the files explicitly instead, for a local run. ``mutmut`` itself
reads the rest of its configuration (the pytest arguments) from ``pyproject.toml``.

Writes ``<out>/mutation-report.json`` (one record per surviving mutant) and
``<out>/summary.md``. Exits 0 whether or not any mutant survived, including when nothing
changed or the time budget ran out; exits 2 only when the run itself could not be carried out —
mutmut crashed, or the unmutated suite failed — because a harness failure that reported success
would look exactly like a clean night.

Each record's ``class`` is ``string-only`` when the mutation changes nothing but the text inside
string literals that are message text, which during the pilot is counted rather than ticked,
and ``behavioural`` otherwise. A literal is message text only when ``message_sink`` traces it,
in the source, into an exception constructor in a ``raise``, a ``print``, a logging call or
``warnings.warn``; the record carries that sink as ``message_sink``, null when there is none.
``classify`` decides from the diff and that sink, and leans behavioural whenever it cannot vouch
for the change.

A record's ``id`` is a digest of the file, the function and the mutated text, with no line
number or mutmut ordinal in it, so the same surviving mutation keeps its id across nights while
the code around it moves. ``tools/mutation/ticks.py`` dedupes on it.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import fnmatch
import hashlib
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import tokenize
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA = "bakobo.mutation-report/1"
PASSED = "passed: every test covering this function passed with the mutant in place"
STRING_NOTE = "only the text of a message literal changed; counted, not ticked"
# mutmut mangles a method name with U+01C1 (LATIN LETTER LATERAL CLICK) as its separator:
# x<sep>Class<sep>method. Spelled as an escape so no reader mistakes it for two pipes.
METHOD_SEP = "\u01c1"
NOTHING_MATCHES = "Filtered for specific mutants, but nothing matches"
# Seconds mutmut gets to stop its workers after SIGTERM before the group is killed outright.
TERM_GRACE = 30

BEHAVIOURAL = "behavioural"
STRING_ONLY = "string-only"
# Tokens whose text is a string literal's content.
STRING_TOKENS = {tokenize.STRING, tokenize.FSTRING_MIDDLE, tokenize.TSTRING_MIDDLE}
# Tokens that carry no meaning a mutation could change.
LAYOUT_TOKENS = {tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
                 tokenize.ENDMARKER, tokenize.COMMENT}
# A literal next to one of these is compared, tested for membership, used as a key or used as
# an index, so changing its text can change what the code does.
DECIDING = {"==", "!=", "<", ">", "<=", ">=", "in", "is", "[", "]", ":"}
# The one tokenize failure that still yields every token: a fragment of a call whose closing
# bracket is on a line the diff did not show.
OPEN_BRACKET = "unexpected EOF in multi-line statement"


@dataclass
class Survivor:
    id: str
    mutmut_name: str
    file: str
    line: int
    function: str
    removed: list[str]
    added: list[str]
    diff: str
    tests: int
    kind: str = BEHAVIOURAL
    sink: str | None = None

    def record(self, pytest_args: list[str]) -> dict:
        return {
            "id": self.id,
            "mutmut_name": self.mutmut_name,
            "file": self.file,
            "line": self.line,
            "function": self.function,
            "class": self.kind,
            "message_sink": self.sink,
            "mutation": {"removed": self.removed, "added": self.added, "diff": self.diff},
            "test_result": {
                "command": " ".join(["pytest", *pytest_args]),
                "tests_run": self.tests,
                "exit_code": 0,
                "outcome": PASSED,
            },
        }


@dataclass
class Outcome:
    modules: list[str]
    complete: bool = True
    failure: str | None = None
    note: str | None = None
    counts: dict[str, int] = field(default_factory=dict)
    survivors: list[Survivor] = field(default_factory=list)


def load_config(root: Path) -> dict:
    data = tomllib.loads((root / "pyproject.toml").read_text("utf-8"))
    return data.get("tool", {}).get("mutmut", {})


def changed_modules(root: Path, ref: str, since: str, cfg: dict, git: str = "git") -> list[str]:
    """Source files a first-parent commit on ``ref`` touched since ``since`` that still exist.

    ``--diff-merges=first-parent`` makes a merge commit list what the merge brought onto the
    branch, so a pull request whose own commits are older than the window still counts on the
    day it landed.
    """
    sources = cfg.get("source_paths", ["src"])
    out = subprocess.run(
        [git, "log", "--first-parent", "--diff-merges=first-parent", f"--since={since}",
         "--name-only", "--format=", ref, "--", *sources],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout
    paths = {line.strip() for line in out.splitlines() if line.strip()}
    return sorted(p for p in paths if p.endswith(".py") and (root / p).is_file()
                  and not excluded(p, cfg))


def excluded(path: str, cfg: dict) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in cfg.get("do_not_mutate", []))


def module_name(path: str) -> str:
    """The dotted name mutmut gives a source file (mutmut's format_utils.get_mutant_name)."""
    name = path.removesuffix(".py").replace("/", ".").removeprefix("src.")
    return name.removesuffix(".__init__")


def globs_for(path: str) -> list[str]:
    """Patterns selecting this module's mutants and no submodule's.

    Every mutant name is ``<module>.x_<function>`` or ``<module>.x<sep><Class><sep><method>``,
    so a pattern ending in ``.x_*`` cannot match ``<module>.<submodule>.x_*`` (fnmatch's ``*``
    crosses dots, which is why the bare ``<module>.*`` is not used).
    """
    mod = module_name(path)
    return [f"{mod}.x_*", f"{mod}.x{METHOD_SEP}*"]


def has_functions(source: str) -> bool:
    """Whether mutmut could mutate anything here: it mutates functions and methods only."""
    funcs = (ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.parse(source).body:
        if isinstance(node, funcs):
            return True
        if isinstance(node, ast.ClassDef) and any(isinstance(n, funcs) for n in node.body):
            return True
    return False


def function_of(mutmut_name: str, path: str) -> str:
    """``saidify`` or ``Class.method`` from a mutant name."""
    mangled = mutmut_name.partition("__mutmut_")[0]
    local = mangled.removeprefix(module_name(path) + ".")
    if local.startswith("x" + METHOD_SEP):
        return ".".join(part for part in local.split(METHOD_SEP)[1:] if part)
    return local.removeprefix("x_")


def parse_diff(diff: str) -> tuple[int, list[str], list[str]]:
    """(function-relative line of the first change, removed lines, added lines)."""
    removed: list[str] = []
    added: list[str] = []
    first = 0
    line = 0
    for text in diff.splitlines():
        if text.startswith(("---", "+++")):
            continue
        if text.startswith("@@"):
            line = int(text.split()[1].lstrip("-").split(",")[0])
            continue
        if text.startswith("-"):
            removed.append(text[1:])
            first = first or line
            line += 1
        elif text.startswith("+"):
            added.append(text[1:])
            first = first or line
        else:
            line += 1
    return first, removed, added


def _tokens(lines: list[str]) -> list[tuple[int, str]] | None:
    """The meaningful tokens of a diff fragment, or None if tokenize could not read it all."""
    text = "\n".join(line.strip() for line in lines)
    found = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type not in LAYOUT_TOKENS:
                found.append((tok.type, tok.string))
    except tokenize.TokenError as error:
        if error.args[0] != OPEN_BRACKET:
            return None
    return found


def classify(removed: list[str], added: list[str], sink: str | None) -> str:
    """``string-only`` if the mutation changes only the text inside message literals.

    ``sink`` is where ``message_sink`` found the mutated lines' literals going; without one, a
    changed literal is a returned value, an argument, a key or a pattern, and behavioural.

    Both sides must tokenize completely to the same sequence, differing only in string-literal
    tokens, none of which sits beside a comparison, a membership test, a subscript or a key.
    Anything else, including a change too fragmentary to read, is ``behavioural``: a survivor
    wrongly called string-only is a test gap nobody hears about, while one wrongly called
    behavioural costs a tick someone closes.
    """
    before, after = _tokens(removed), _tokens(added)
    if sink is None or not before or not after or len(before) != len(after):
        return BEHAVIOURAL
    changed = [i for i, (old, new) in enumerate(zip(before, after, strict=True)) if old != new]
    if not changed:
        return BEHAVIOURAL
    for i in changed:
        (old_type, _), (new_type, _) = before[i], after[i]
        if old_type != new_type or old_type not in STRING_TOKENS:
            return BEHAVIOURAL
        neighbours = before[max(i - 1, 0):i] + before[i + 1:i + 2]
        if any(text in DECIDING for _, text in neighbours):
            return BEHAVIOURAL
    return STRING_ONLY


LOG_OWNERS = {"logging", "log", "logger", "_log", "_logger", "LOG", "LOGGER"}
LOG_METHODS = {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}


def _sink_of_call(call: ast.Call, parent: ast.AST | None) -> str | None:
    """What kind of message a call delivers, or None if it is not a message sink."""
    func = call.func
    if isinstance(parent, ast.Raise) and parent.exc is call:
        return f"raise {ast.unparse(func)}"
    if isinstance(func, ast.Name) and func.id == "print":
        return "print"
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        owner, method = func.value.id, func.attr
        if (owner == "warnings" and method == "warn") or (
                owner in LOG_OWNERS and method in LOG_METHODS):
            return f"{owner}.{method}"
    return None


def _sink_of_literal(node: ast.AST, parents: dict) -> str | None:
    """Follow a literal's value up through concatenation and formatting to a call argument."""
    while True:
        parent = parents.get(node)
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, (ast.Add, ast.Mod)):
            node = parent
        elif isinstance(parent, ast.Attribute) and parent.attr == "format":
            call = parents.get(parent)
            if not (isinstance(call, ast.Call) and call.func is parent):
                return None
            node = call
        elif isinstance(parent, ast.keyword):
            node = parent
        elif isinstance(parent, ast.Call) and node is not parent.func:
            return _sink_of_call(parent, parents.get(parent))
        else:
            return None


def message_sink(source: str, first: int, last: int) -> str | None:
    """Where the string literals on lines ``first``..``last`` end up, if all are messages.

    A literal is message text when its value, after any ``+``, ``%`` or ``.format``, is passed
    straight to an exception constructor in a ``raise``, to ``print``, to a logging method or to
    ``warnings.warn``. Returns that sink when every literal touching the lines is one, else None
    — a line holding no literal, or one literal that is anything else, is not vouched for.
    """
    tree = ast.parse(source)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}

    def inside_fstring(node: ast.AST) -> bool:
        while (node := parents.get(node)) is not None:
            if isinstance(node, ast.JoinedStr):
                return True
        return False

    literals = [n for n in ast.walk(tree)
                if (isinstance(n, ast.JoinedStr)
                    or (isinstance(n, ast.Constant) and isinstance(n.value, str)))
                and n.lineno <= last and (n.end_lineno or n.lineno) >= first
                and not inside_fstring(n)]
    sinks = [_sink_of_literal(n, parents) for n in literals]
    if not sinks or None in sinks:
        return None
    return sinks[0]


def function_span(source: str, function: str) -> tuple[int, int] | None:
    """First and last line of ``function`` (``name`` or ``Class.name``), decorators included."""
    tree = ast.parse(source)
    *owner, name = function.split(".")
    body = tree.body
    if owner:
        classes = [n for n in body if isinstance(n, ast.ClassDef) and n.name == owner[0]]
        body = classes[0].body if classes else []
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            return start, node.end_lineno or node.lineno
    return None


def locate(source: str, function: str, relative: int, removed: list[str]) -> int:
    """The file line a mutation sits on.

    mutmut's diff numbers lines from the function's own first line, which may be a leading
    comment rather than the ``def``, so the removed text is looked for inside the function and
    the occurrence nearest the diff's own offset wins. A mutation that removes nothing falls
    back to that offset.
    """
    span = function_span(source, function)
    if span is None:
        return 0
    start, end = span
    guess = start + max(relative, 1) - 1
    if removed:
        lines = source.splitlines()
        target = removed[0].strip()
        hits = [n for n in range(start, end + 1) if lines[n - 1].strip() == target]
        if hits:
            return min(hits, key=lambda n: abs(n - guess))
    return min(guess, end)


def mutant_id(path: str, function: str, removed: list[str], added: list[str],
              seen: dict) -> str:
    """Stable across nights: no line number and no mutmut ordinal goes into it.

    Two identical mutations in one function (the same line written twice) are told apart by
    their order of appearance, which is the one thing that distinguishes them.
    """
    key = "\0".join([path, function, "\n".join(s.strip() for s in removed),
                     "\n".join(s.strip() for s in added)])
    ordinal = seen.get(key, 0)
    seen[key] = ordinal + 1
    if ordinal:
        key += f"\0{ordinal}"
    return hashlib.sha256(key.encode()).hexdigest()[:12]


def run_mutmut(mutmut: str, globs: list[str], budget: float, log: Path,
               root: Path) -> tuple[int | None, str]:
    """Run mutmut in its own process group; on budget exhaustion stop the whole group.

    Returns (exit code, or None if the budget ran out; combined output).
    """
    with log.open("w") as sink:
        proc = subprocess.Popen([mutmut, "run", *globs], cwd=root, stdout=sink,
                                stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code: int | None = proc.wait(timeout=budget)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=TERM_GRACE)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            code = None
    return code, log.read_text(errors="replace")


def statuses(mutmut: str, root: Path) -> dict[str, str]:
    out = subprocess.run([mutmut, "results", "--all", "true"], cwd=root, capture_output=True,
                         text=True, check=True).stdout
    result = {}
    for line in out.splitlines():
        name, sep, status = line.strip().rpartition(": ")
        if sep and "__mutmut_" in name:
            result[name] = status
    return result


def survivor(mutmut: str, root: Path, name: str, path: str, seen: dict) -> Survivor:
    diff = subprocess.run([mutmut, "show", name], cwd=root, capture_output=True, text=True,
                          check=True).stdout
    diff = "\n".join(line for line in diff.splitlines() if not line.startswith("# "))
    tests = subprocess.run([mutmut, "tests-for-mutant", name], cwd=root, capture_output=True,
                           text=True, check=True).stdout
    relative, removed, added = parse_diff(diff)
    function = function_of(name, path)
    source = (root / path).read_text("utf-8")
    line = locate(source, function, relative, removed)
    sink = message_sink(source, line, line + max(len(removed), 1) - 1)
    return Survivor(
        id=mutant_id(path, function, removed, added, seen),
        mutmut_name=name, file=path, line=line,
        function=function, removed=removed, added=added, diff=diff,
        tests=len([t for t in tests.splitlines() if t.strip()]),
        kind=classify(removed, added, sink), sink=sink,
    )


def mutate(root: Path, modules: list[str], mutmut: str, budget: float, out: Path) -> Outcome:
    outcome = Outcome(modules=modules)
    if not modules:
        outcome.note = "No source module changed in the window, so there was nothing to mutate."
        return outcome
    mutable = [m for m in modules if has_functions((root / m).read_text("utf-8"))]
    if not mutable:
        outcome.note = "The changed modules define no functions or methods, which is all " \
                       "mutmut mutates."
        return outcome
    globs = [g for m in mutable for g in globs_for(m)]
    code, output = run_mutmut(mutmut, globs, budget, out / "mutmut-run.log", root)
    if code is None:
        outcome.complete = False
        outcome.note = f"The {budget / 60:.0f}-minute budget ran out; mutants still marked " \
                       "'not checked' were never run."
    elif code != 0:
        if NOTHING_MATCHES in output:
            outcome.note = "mutmut generated no mutants for the changed modules."
            return outcome
        outcome.failure = f"mutmut exited {code}; see mutmut-run.log. The last lines were:\n" \
                          + "\n".join(output.splitlines()[-15:])
        return outcome
    owner = {g: m for m in mutable for g in globs_for(m)}
    seen: dict = {}
    for name, status in sorted(statuses(mutmut, root).items()):
        path = next((owner[g] for g in owner if fnmatch.fnmatch(name, g)), None)
        if path is None:
            continue
        outcome.counts[status] = outcome.counts.get(status, 0) + 1
        if status == "survived":
            outcome.survivors.append(survivor(mutmut, root, name, path, seen))
    return outcome


def report(outcome: Outcome, cfg: dict, commit: str, since: str) -> dict:
    return {
        "schema": SCHEMA,
        "commit": commit,
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "since": since,
        "modules": outcome.modules,
        "complete": outcome.complete,
        "failure": outcome.failure,
        "note": outcome.note,
        "counts": outcome.counts,
        "classes": {kind: sum(s.kind == kind for s in outcome.survivors)
                    for kind in (BEHAVIOURAL, STRING_ONLY)},
        "survivors": [s.record(cfg.get("pytest_add_cli_args", [])) for s in outcome.survivors],
    }


def cell(text: str) -> str:
    text = text.strip().replace("|", "\\|").replace("`", "'")
    return text if len(text) <= 80 else text[:77] + "..."


def summary(data: dict) -> str:
    scope = (f"Commit `{data['commit'][:12]}`; modules changed since {data['since']}: "
             f"{len(data['modules'])}.")
    lines = ["# Mutation testing (pilot)", "", scope, ""]
    if data["failure"]:
        lines += ["**The run failed, so nothing below is a result.**", "", "```",
                  data["failure"], "```", ""]
    if data["note"]:
        lines += [data["note"], ""]
    if data["counts"]:
        lines += ["| status | mutants |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in sorted(data["counts"].items())]
        lines.append("")
    survivors = data["survivors"]
    if survivors:
        classes = data["classes"]
        split = (f"{classes[BEHAVIOURAL]} behavioural, {classes[STRING_ONLY]} string-only "
                 f"({STRING_NOTE}).")
        lines += [f"## {len(survivors)} surviving mutants", "", split, "",
                  "| id | class | where | function | mutation |", "|---|---|---|---|---|"]
        for s in survivors:
            change = " / ".join(cell(x) for x in s["mutation"]["removed"]) or "(nothing)"
            change += " &rarr; " + (" / ".join(cell(x) for x in s["mutation"]["added"])
                                    or "(removed)")
            lines.append(f"| `{s['id']}` | {s['class']} | `{s['file']}:{s['line']}` | "
                         f"`{s['function']}` | {change} |")
        lines.append("")
    elif not data["failure"]:
        lines += ["No mutant survived.", ""]
    if data["modules"]:
        lines += ["<details><summary>Modules</summary>", ""]
        lines += [f"- `{m}`" for m in data["modules"]]
        lines += ["", "</details>", ""]
    return "\n".join(lines)


def find_mutmut() -> str:
    beside = Path(sys.executable).parent / "mutmut"
    return str(beside) if beside.exists() else (shutil.which("mutmut") or "mutmut")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--since", default="7 days ago")
    parser.add_argument("--module", action="append", default=[],
                        help="mutate this file instead of the changed ones (repeatable)")
    parser.add_argument("--budget-minutes", type=float, default=300)
    parser.add_argument("--out", type=Path, default=Path("mutation-out"))
    parser.add_argument("--mutmut", default=None, help="the mutmut executable")
    parser.add_argument("--git", default="git")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    out = args.out if args.out.is_absolute() else root / args.out
    out.mkdir(parents=True, exist_ok=True)
    cfg = load_config(root)
    modules = sorted(args.module) or changed_modules(root, args.ref, args.since, cfg, args.git)
    commit = subprocess.run([args.git, "rev-parse", args.ref], cwd=root, capture_output=True,
                            text=True, check=True).stdout.strip()
    outcome = mutate(root, modules, args.mutmut or find_mutmut(), args.budget_minutes * 60, out)
    since = "an explicit module list" if args.module else args.since
    data = report(outcome, cfg, commit, since)
    (out / "mutation-report.json").write_text(json.dumps(data, indent=2) + "\n")
    text = summary(data)
    (out / "summary.md").write_text(text)
    print(text)
    return 2 if outcome.failure else 0


if __name__ == "__main__":
    sys.exit(main())
