"""What the mutation pilot's three tools share, kept free of any dependency beyond the stdlib.

``mutate.py`` and ``ticks.py`` run inside the repo's environment, but ``pilot_review.py`` runs
from cron under the system Python, so whatever it imports has to stand on the stdlib alone. That
is the classification of a survivor (``classify``, ``message_sink``), the report's schema, and
the bounded reading of a report someone else produced (``read_report``).
"""

from __future__ import annotations

import ast
import io
import json
import tokenize
from pathlib import Path

SCHEMA = "bakobo.mutation-report/1"
# The most a report may hold before it is refused unread: 16 MiB. A night's report is one record
# per surviving mutant, around a kilobyte each, so this allows thousands of survivors while
# keeping a corrupt or hostile artifact from being loaded whole.
MAX_REPORT_BYTES = 16 * 1024 * 1024

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


class UnreadableReportError(Exception):
    """A report could not be read as JSON within the size bound; the message says why."""


def read_report(path: Path) -> object:
    """The parsed report, bounded to MAX_REPORT_BYTES before any of it is decoded."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read(MAX_REPORT_BYTES + 1)
    except OSError as error:
        problem = f"the report could not be read ({error.strerror})"
        raise UnreadableReportError(problem) from None
    if len(raw) > MAX_REPORT_BYTES:
        raise UnreadableReportError(f"the report is larger than {MAX_REPORT_BYTES} bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise UnreadableReportError("the report is not UTF-8") from None
    try:
        return json.loads(text)
    except ValueError:
        raise UnreadableReportError("the report is not JSON") from None


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
