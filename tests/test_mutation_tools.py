"""The mutation-testing pilot's tooling: tools/mutation/mutate.py and tools/mutation/ticks.py.

mutmut, gh and tick are replaced by small stub executables that answer from a JSON spec and log
what they were asked, so nothing here runs a mutation, reaches GitHub, or touches a real ledger.
git is the real one, over a scratch repository, because which modules count as changed is
exactly the kind of thing a stub would get wrong in the same way as the code under test.
"""

from __future__ import annotations

import importlib.util
import json
import os
import runpy
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "tools" / "mutation"


def load(name):
    spec = importlib.util.spec_from_file_location(f"mutation_{name}", TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses looks its defining module up by name
    spec.loader.exec_module(module)
    return module


mutate = load("mutate")
ticks = load("ticks")

SEP = "\u01c1"

STUB = """\
#!{python}
import json, os, signal, sys, time
from pathlib import Path
here = Path(__file__).resolve().parent
spec = json.loads((here / "spec.json").read_text())
with (here / "calls.log").open("a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
answer = spec.get(sys.argv[1], {{}})
if isinstance(answer, dict) and "by_arg" in answer:
    answer = answer["by_arg"].get(sys.argv[-1], answer.get("default", {{}}))
if isinstance(answer, str):
    answer = {{"out": answer}}
if answer.get("ignore_term"):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
time.sleep(answer.get("sleep", 0))
if "copy" in answer:
    dest = Path(sys.argv[sys.argv.index("--dir") + 1])
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "mutation-report.json").write_text(Path(answer["copy"]).read_text())
sys.stdout.write(answer.get("out", ""))
sys.exit(answer.get("exit", 0))
"""


def stub(directory: Path, name: str, spec: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(STUB.format(python=sys.executable))
    path.chmod(0o755)
    (directory / "spec.json").write_text(json.dumps(spec))
    return path


def calls(directory: Path) -> list[list[str]]:
    log = directory / "calls.log"
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def git(root: Path, *args: str, date: str | None = None) -> str:
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    return subprocess.run(["git", *args], cwd=root, env=env, check=True, capture_output=True,
                          text=True).stdout


MODULE = '''\
"""A module to mutate."""


def saidify(sad, label="d"):
    if label not in sad:
        raise ValueError("no label")
    return dict(sad)


class Box:
    # a leading comment mutmut's diff counts as the method's first line
    @staticmethod
    def open(x):
        return x + 1
'''

DIFF_SAIDIFY = """\
--- src/pkg/mod.py
+++ src/pkg/mod.py
@@ -1,4 +1,4 @@
 def saidify(sad, label="d"):
     if label not in sad:
-        raise ValueError("no label")
+        raise ValueError(None)
     return dict(sad)"""

DIFF_OPEN = """\
--- src/pkg/mod.py
+++ src/pkg/mod.py
@@ -2,3 +2,3 @@
 @staticmethod
 def open(x):
-    return x + 1
+    return x - 1"""

NAME_SAIDIFY = "pkg.mod.x_saidify__mutmut_3"
NAME_OPEN = f"pkg.mod.x{SEP}Box{SEP}open__mutmut_1"

RESULTS = "\n".join([
    "this line is not a result",
    f"    {NAME_SAIDIFY}: survived",
    "    pkg.mod.x_saidify__mutmut_1: killed",
    f"    {NAME_OPEN}: survived",
    "    pkg.mod.x_saidify__mutmut_2: no tests",
    "    pkg.other.x_f__mutmut_1: survived",
]) + "\n"


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "src" / "pkg").mkdir(parents=True)
    (root / "pyproject.toml").write_text(textwrap.dedent("""\
        [tool.mutmut]
        source_paths = ["src/pkg"]
        do_not_mutate = ["*/pkg/vendored.py"]
        pytest_add_cli_args = ["-n0", "--no-cov"]
        """))
    (root / "src" / "pkg" / "mod.py").write_text(MODULE)
    (root / "src" / "pkg" / "consts.py").write_text("X = 1\n")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "base", date="2020-01-01T00:00:00")
    return root


def run_spec(**run):
    return {
        "run": run or {"out": "done\n"},
        "results": RESULTS,
        "show": {"by_arg": {NAME_SAIDIFY: f"# {NAME_SAIDIFY}: survived\n{DIFF_SAIDIFY}\n",
                            NAME_OPEN: DIFF_OPEN + "\n"}},
        "tests-for-mutant": {"by_arg": {NAME_SAIDIFY: "tests/a.py::t1\ntests/a.py::t2\n"},
                             "default": "tests/b.py::t\n"},
    }


def run_main(repo, mutmut, *extra):
    code = mutate.main(["--root", str(repo), "--module", "src/pkg/mod.py", "--mutmut",
                        str(mutmut), "--out", "out", *extra])
    data = json.loads((repo / "out" / "mutation-report.json").read_text())
    return code, data, (repo / "out" / "summary.md").read_text()


# --- the pure parts ---------------------------------------------------------------------------


def test_module_names_follow_mutmut():
    assert mutate.module_name("src/pkg/a/b.py") == "pkg.a.b"
    assert mutate.module_name("src/pkg/a/__init__.py") == "pkg.a"
    assert mutate.globs_for("src/pkg/a/__init__.py") == ["pkg.a.x_*", f"pkg.a.x{SEP}*"]


def test_globs_do_not_reach_into_submodules():
    import fnmatch

    globs = mutate.globs_for("src/pkg/a/__init__.py")
    assert any(fnmatch.fnmatch("pkg.a.x_f__mutmut_1", g) for g in globs)
    assert any(fnmatch.fnmatch(f"pkg.a.x{SEP}C{SEP}m__mutmut_1", g) for g in globs)
    assert not any(fnmatch.fnmatch("pkg.a.sub.x_f__mutmut_1", g) for g in globs)


def test_has_functions():
    assert mutate.has_functions("def f():\n    pass\n")
    assert mutate.has_functions("async def f():\n    pass\n")
    assert mutate.has_functions("class C:\n    def m(self):\n        pass\n")
    assert not mutate.has_functions("class C:\n    x = 1\n")
    assert not mutate.has_functions("X = 1\n")


def test_function_of():
    assert mutate.function_of(NAME_SAIDIFY, "src/pkg/mod.py") == "saidify"
    assert mutate.function_of(NAME_OPEN, "src/pkg/mod.py") == "Box.open"
    assert mutate.function_of("pkg.x_f__mutmut_1", "src/pkg/__init__.py") == "f"


def test_parse_diff():
    assert mutate.parse_diff(DIFF_SAIDIFY) == (
        3, ['        raise ValueError("no label")'], ["        raise ValueError(None)"])
    added_only = "--- a\n+++ a\n@@ -5,2 +5,3 @@\n x = 1\n+y = 2\n z = 3"
    assert mutate.parse_diff(added_only) == (6, [], ["y = 2"])


def test_locate_finds_the_removed_line_in_the_file():
    assert mutate.locate(MODULE, "saidify", 3, ['        raise ValueError("no label")']) == 6
    # The diff counts the method's leading comment, so its offset is one off; the text wins.
    assert mutate.locate(MODULE, "Box.open", 3, ["    return x + 1"]) == 14


def test_locate_falls_back_to_the_offset():
    assert mutate.locate(MODULE, "saidify", 2, []) == 5
    assert mutate.locate(MODULE, "saidify", 0, ["no such line"]) == 4
    assert mutate.locate(MODULE, "saidify", 99, []) == 7


def test_locate_without_the_function():
    assert mutate.locate(MODULE, "missing", 1, []) == 0
    assert mutate.locate(MODULE, "Nope.open", 1, []) == 0


def test_mutant_ids_are_stable_and_distinguish_repeats():
    first = mutate.mutant_id("f.py", "g", ["a"], ["b"], {})
    assert first == mutate.mutant_id("f.py", "g", ["  a"], ["b  "], {})
    seen: dict = {}
    twice = [mutate.mutant_id("f.py", "g", ["a"], ["b"], seen) for _ in range(2)]
    assert twice[0] == first and twice[1] != first
    assert mutate.mutant_id("f.py", "h", ["a"], ["b"], {}) != first


def test_cell_escapes_and_truncates():
    assert mutate.cell(" a|b `c` ") == "a\\|b 'c'"
    assert mutate.cell("x" * 100) == "x" * 77 + "..."


def test_load_config_without_a_mutmut_table(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    assert mutate.load_config(tmp_path) == {}


def test_find_mutmut(monkeypatch, tmp_path):
    (tmp_path / "python").touch()
    monkeypatch.setattr(mutate.sys, "executable", str(tmp_path / "python"))
    monkeypatch.setattr(mutate.shutil, "which", lambda name: None)
    assert mutate.find_mutmut() == "mutmut"
    (tmp_path / "mutmut").touch()
    assert mutate.find_mutmut() == str(tmp_path / "mutmut")


# --- which modules changed (real git) ---------------------------------------------------------


def test_changed_modules(repo):
    old, new = "2020-01-02T00:00:00", "2030-01-01T00:00:00"
    pkg = repo / "src" / "pkg"
    # A branch whose commits are older than the window, merged inside it, still counts.
    git(repo, "checkout", "-q", "-b", "topic")
    (pkg / "merged.py").write_text("def f():\n    pass\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "topic", date=old)
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "-m", "merge", "topic", date=new)
    (pkg / "mod.py").write_text(MODULE + "\n")
    (pkg / "vendored.py").write_text("def f():\n    pass\n")
    (pkg / "notes.txt").write_text("x\n")
    (repo / "outside.py").write_text("def f():\n    pass\n")
    (pkg / "consts.py").unlink()
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "recent", date=new)
    cfg = mutate.load_config(repo)
    assert mutate.changed_modules(repo, "HEAD", "2029-12-01", cfg) == [
        "src/pkg/merged.py", "src/pkg/mod.py"]
    assert mutate.changed_modules(repo, "HEAD", "2031-01-01", cfg) == []


def test_changed_modules_defaults_to_src(repo):
    assert mutate.changed_modules(repo, "HEAD", "2019-01-01", {}) == [
        "src/pkg/consts.py", "src/pkg/mod.py"]


# --- a whole run against a stub mutmut --------------------------------------------------------


def test_survivors_are_reported(repo, tmp_path, capsys):
    mutmut = stub(tmp_path / "bin", "mutmut", run_spec())
    code, data, text = run_main(repo, mutmut)
    assert code == 0
    assert calls(tmp_path / "bin")[0] == ["run", "pkg.mod.x_*", f"pkg.mod.x{SEP}*"]
    assert data["schema"] == mutate.SCHEMA
    assert data["commit"] == git(repo, "rev-parse", "HEAD").strip()
    assert data["since"] == "an explicit module list"
    assert data["complete"] is True and data["failure"] is None and data["note"] is None
    assert data["counts"] == {"killed": 1, "no tests": 1, "survived": 2}
    # Sorted by mutmut name, and its method separator sorts after "_".
    first, second = data["survivors"]
    assert first["mutmut_name"] == NAME_SAIDIFY and first["line"] == 6
    assert first["mutation"]["removed"] == ['        raise ValueError("no label")']
    assert not first["mutation"]["diff"].startswith("#")
    assert first["test_result"] == {
        "command": "pytest -n0 --no-cov", "tests_run": 2, "exit_code": 0,
        "outcome": "passed: every test covering this function passed with the mutant in place"}
    assert second["mutmut_name"] == NAME_OPEN
    assert (second["file"], second["line"], second["function"]) == ("src/pkg/mod.py", 14,
                                                                    "Box.open")
    assert second["test_result"]["tests_run"] == 1
    assert len({first["id"], second["id"]}) == 2
    assert "## 2 surviving mutants" in text and "`src/pkg/mod.py:14`" in text
    assert "| survived | 2 |" in text and "- `src/pkg/mod.py`" in text
    assert "## 2 surviving mutants" in capsys.readouterr().out


def test_no_survivors(repo, tmp_path):
    spec = run_spec()
    spec["results"] = "    pkg.mod.x_saidify__mutmut_1: killed\n"
    _, data, text = run_main(repo, stub(tmp_path / "bin", "mutmut", spec))
    assert data["survivors"] == [] and "No mutant survived." in text


def test_nothing_changed_exits_cleanly(repo, tmp_path):
    mutmut = stub(tmp_path / "bin", "mutmut", run_spec())
    code = mutate.main(["--root", str(repo), "--since", "2031-01-01", "--mutmut", str(mutmut),
                        "--out", str(tmp_path / "abs-out")])
    data = json.loads((tmp_path / "abs-out" / "mutation-report.json").read_text())
    assert code == 0 and calls(tmp_path / "bin") == []
    assert data["modules"] == [] and data["since"] == "2031-01-01"
    assert "nothing to mutate" in data["note"]
    text = (tmp_path / "abs-out" / "summary.md").read_text()
    assert "No mutant survived." in text and "<details>" not in text


def test_modules_without_functions(repo, tmp_path):
    mutmut = stub(tmp_path / "bin", "mutmut", run_spec())
    code = mutate.main(["--root", str(repo), "--module", "src/pkg/consts.py", "--mutmut",
                        str(mutmut)])
    data = json.loads((repo / "mutation-out" / "mutation-report.json").read_text())
    assert code == 0 and calls(tmp_path / "bin") == []
    assert "define no functions" in data["note"]


def test_no_mutants_generated(repo, tmp_path):
    mutmut = stub(tmp_path / "bin", "mutmut",
                  run_spec(exit=1, out=f"AssertionError: {mutate.NOTHING_MATCHES}\n"))
    code, data, _ = run_main(repo, mutmut)
    assert code == 0 and data["failure"] is None
    assert data["note"] == "mutmut generated no mutants for the changed modules."


def test_a_harness_failure_fails_the_run(repo, tmp_path):
    spec = run_spec(exit=1, out="Failed to run clean test\n")
    mutmut = stub(tmp_path / "bin", "mutmut", spec)
    code, data, text = run_main(repo, mutmut)
    assert code == 2
    assert data["failure"].startswith("mutmut exited 1")
    assert "Failed to run clean test" in data["failure"]
    assert "The run failed" in text and "No mutant survived." not in text


def test_the_budget_stops_the_run_and_keeps_what_finished(repo, tmp_path):
    mutmut = stub(tmp_path / "bin", "mutmut", run_spec(sleep=30))
    code, data, text = run_main(repo, mutmut, "--budget-minutes", "0.01")
    assert code == 0 and data["complete"] is False
    assert "budget ran out" in data["note"] and len(data["survivors"]) == 2
    assert "budget ran out" in text


def test_a_run_ignoring_sigterm_is_killed(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(mutate, "TERM_GRACE", 0.5)
    mutmut = stub(tmp_path / "bin", "mutmut", run_spec(sleep=30, ignore_term=True))
    code, data, _ = run_main(repo, mutmut, "--budget-minutes", "0.01")
    assert code == 0 and data["complete"] is False


def test_entry_point(repo, tmp_path, monkeypatch):
    mutmut = stub(tmp_path / "bin", "mutmut", run_spec())
    monkeypatch.setattr(sys, "argv", ["mutate.py", "--root", str(repo), "--since", "2031-01-01",
                                      "--mutmut", str(mutmut)])
    with pytest.raises(SystemExit) as exit_:
        runpy.run_path(str(TOOLS / "mutate.py"), run_name="__main__")
    assert exit_.value.code == 0


# --- filing ticks -----------------------------------------------------------------------------


def survivor(id_, line=6):
    return {
        "id": id_, "mutmut_name": NAME_SAIDIFY, "file": "src/pkg/mod.py", "line": line,
        "function": "saidify",
        "mutation": {"removed": ["a"], "added": ["b"], "diff": "-a\n+b"},
        "test_result": {"command": "pytest -n0 --no-cov", "tests_run": 2, "exit_code": 0,
                        "outcome": "passed"},
    }


@pytest.fixture
def sample(tmp_path):
    data = {"schema": mutate.SCHEMA, "commit": "c0ffee", "failure": None,
            "survivors": [survivor("aaaaaaaaaaaa"), survivor("bbbbbbbbbbbb", 9),
                          survivor("bbbbbbbbbbbb", 9), survivor("cccccccccccc", 12)]}
    path = tmp_path / "mutation-report.json"
    path.write_text(json.dumps(data))
    return path


def tick_stub(tmp_path):
    return stub(tmp_path / "tickbin", "tick", {
        "ls": "2abc  debt   mutation survivor [m:aaaaaaaaaaaa] src/pkg/mod.py:6 in saidify\n"
              "3def  debt   mutation survivor [m:dddddddddddd] x.py:1 in f  (closed)\n",
        "add": "4ghi  mutation survivor ...\npaste the mark  ~4ghi  wherever this lives\n",
        "note": "noted on 4ghi\n",
    })


def test_ticks_files_only_new_survivors(sample, tmp_path, capsys):
    tick = tick_stub(tmp_path)
    assert ticks.main(["--report", str(sample), "--tick", str(tick)]) == 0
    log = calls(tmp_path / "tickbin")
    assert log[0] == ["ls", "--all", "--tag", "mutation-survivor"]
    adds = [c for c in log if c[0] == "add"]
    assert [c[-1] for c in adds] == [
        "mutation survivor [m:bbbbbbbbbbbb] src/pkg/mod.py:9 in saidify",
        "mutation survivor [m:cccccccccccc] src/pkg/mod.py:12 in saidify"]
    assert adds[0][:5] == ["add", "--kind", "debt", "--tag", "mutation-survivor"]
    notes = [c for c in log if c[0] == "note"]
    assert len(notes) == 2 and notes[0][1] == "4ghi"
    assert "commit c0ffee" in notes[0][2] and "-a\n+b" in notes[0][2]
    assert "Test command: pytest -n0 --no-cov" in notes[0][2]
    assert "filed 2; 2 already ticked; 4 survivors" in capsys.readouterr().out


def test_ticks_dry_run_files_nothing(sample, tmp_path, capsys):
    tick = tick_stub(tmp_path)
    assert ticks.main(["--report", str(sample), "--tick", str(tick), "--dry-run"]) == 0
    assert [c[0] for c in calls(tmp_path / "tickbin")] == ["ls"]
    out = capsys.readouterr().out
    assert "would file: mutation survivor [m:bbbbbbbbbbbb]" in out
    assert "would file 2; 2 already ticked" in out


def test_ticks_downloads_the_latest_run(sample, tmp_path):
    gh = stub(tmp_path / "ghbin", "gh", {"run": {"by_arg": {
        ".[0].databaseId": {"out": "123\n"}}, "default": {"copy": str(sample)}}})
    tick = tick_stub(tmp_path)
    assert ticks.main(["--gh", str(gh), "--tick", str(tick), "--dry-run"]) == 0
    first, second = calls(tmp_path / "ghbin")
    assert first[:4] == ["run", "list", "--workflow", "mutation.yml"]
    assert second[:5] == ["run", "download", "123", "--name", "mutation-report"]


def test_ticks_downloads_a_named_run(sample, tmp_path):
    gh = stub(tmp_path / "ghbin", "gh", {"run": {"copy": str(sample)}})
    tick = tick_stub(tmp_path)
    assert ticks.main(["--run-id", "77", "--gh", str(gh), "--tick", str(tick),
                       "--dry-run"]) == 0
    assert calls(tmp_path / "ghbin")[0][:3] == ["run", "download", "77"]


def test_ticks_without_a_successful_run(tmp_path):
    gh = stub(tmp_path / "ghbin", "gh", {"run": {"out": "\n"}})
    with pytest.raises(SystemExit, match=r"no successful mutation\.yml run"):
        ticks.main(["--gh", str(gh)])


def test_ticks_refuses_a_failed_report(tmp_path, capsys):
    path = tmp_path / "r.json"
    path.write_text(json.dumps({"failure": "mutmut exited 1", "survivors": []}))
    assert ticks.main(["--report", str(path), "--tick", "/nonexistent"]) == 1
    assert "mutmut exited 1" in capsys.readouterr().err


def test_ticks_entry_point(sample, tmp_path, monkeypatch):
    tick = tick_stub(tmp_path)
    monkeypatch.setattr(sys, "argv", ["ticks.py", "--report", str(sample), "--tick", str(tick),
                                      "--dry-run"])
    with pytest.raises(SystemExit) as exit_:
        runpy.run_path(str(TOOLS / "ticks.py"), run_name="__main__")
    assert exit_.value.code == 0
