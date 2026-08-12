"""The screens. Assume a projector, a hundred columns, and someone talking over them.

Two rules shape everything here, and both come from Custos rather than from taste.

**The verdict is never alone** (this.i @cl1grd). The Ground Axiom makes the ground a
component of what a finding is, so a screen that shows ``DEFEATED`` and stops has not
abbreviated a finding — it has shown something that is not one. The verdict line and the
ground block are emitted by one function and there is no path that produces one without
the other.

**The arithmetic is on the screen** (this.i @clarth). Slots, weights, dispositions, both
sums, and unity. An audience that can check the sum is watching a calculation; an
audience that cannot is watching an oracle, and the demo's claim is the first one.

A refusal is rendered in a different shape rather than a fifth colour (this.i @clrfsl):
it says in words that it is not a verdict, it has no arithmetic because with no governing
clause there is none to have, and in its place it prints what the law in force *does*
govern, so the silence is visible rather than asserted.
"""

from __future__ import annotations

import textwrap
from collections.abc import Iterable
from fractions import Fraction
from typing import cast

from utina.cli.appraisal import Appraisal
from utina.cli.style import GREEN, REFUSAL_COLOUR, VERDICT_COLOUR, Style
from utina.fold.clause import Clause
from utina.fold.constitution import Constitution
from utina.fold.corpus import Event
from utina.fold.finding import (
    Affirmed,
    Defeated,
    Finding,
    Pending,
    SelfConvicted,
)
from utina.fold.refusal import Refusal
from utina.fold.slots import ACT_FIELD, DISPOSITION_FIELD, ENDORSE, ISSUER_FIELD, SUBJECT_FIELD
from utina.fold.triple import Position

__all__ = [
    "abbrev",
    "enact_screen",
    "eval_screen",
    "ground_of",
    "law_screen",
    "log_screen",
    "rational",
    "replay_screen",
    "replay_verdict",
    "verdict_word",
]

#: Every screen is inset by this much, so a line never starts hard against the frame.
MARGIN = "  "

#: The rule under a headline. Eighty-four characters plus the margin sits inside a
#: hundred-column terminal with room for a scrollbar, and it is a single ASCII character
#: rather than box drawing, which not every projector's font has.
RULE = "-" * 84

#: The width a field label occupies before its value starts.
FIELD = 12

#: Where prose wraps. Under the hundred columns the projector gives, with the margin and
#: a field label's worth of hanging indent already counted.
WRAP = 88

_NOT_A_VERDICT = (
    "This is not a verdict. A refusal is an operational fact: the evaluator declining an "
    "ill-posed question rather than legislating the missing rule."
)


# --- the small pieces ---------------------------------------------------------


def abbrev(value: str, keep: int = 12) -> str:
    """An identifier shortened to a prefix that is still a usable handle.

    Truncation from the front rather than an elision through the middle, because
    ``--said`` and ``--on`` accept a prefix: what the screen prints is what the narrator
    can type back (this.i @clhndl).
    """
    if len(value) <= keep:
        return value
    return value[:keep] + "..."


def rational(value: Fraction) -> str:
    """An exact weight, written the way the committed law writes it."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def field(style: Style, label: str, value: str, indent: int = 2) -> str:
    """One labelled line. Padded before it is painted, so both forms align."""
    return f"{' ' * indent}{style.label(f'{label:<{FIELD}}')}{value}"


def wrapped(style: Style, label: str, text: str, indent: int = 2) -> list[str]:
    """One labelled line whose value is prose, hanging under its own label."""
    pad = " " * (indent + FIELD)
    lines = textwrap.wrap(text, width=WRAP, initial_indent=pad, subsequent_indent=pad)
    head = " " * indent + style.label(f"{label:<{FIELD}}") + lines[0][indent + FIELD :]
    return [head, *lines[1:]]


def _row(slot: str, weight: str, disposition: str, note: str) -> str:
    """One line of the arithmetic table, in the columns every other line uses."""
    return f"{MARGIN}{slot:<18}{weight:>6}   {disposition:<14}{note}".rstrip()


def _screen(lines: Iterable[str]) -> str:
    return "\n".join(line.rstrip() for line in lines) + "\n"


# --- utina eval ---------------------------------------------------------------


def eval_screen(appraisal: Appraisal, style: Style) -> str:
    """One appraisal, rendered as a finding or — visibly differently — as a refusal."""
    outcome = appraisal.outcome
    if isinstance(outcome, Refusal):
        return _screen(_refusal_lines(appraisal, outcome, style))
    return _screen(_finding_lines(appraisal, outcome, style))


def _finding_lines(appraisal: Appraisal, finding: Finding, style: Style) -> list[str]:
    # A finding is returned only where a clause governs the act, and the appraisal
    # derives its clause from the same call the evaluator makes, so this is not an
    # assumption about luck: tests/test_cli.py asserts it beat by beat.
    clause = cast(Clause, appraisal.clause)
    word = finding.verdict.value.upper()
    return [
        MARGIN
        + style.banner(f"{word:<10}", VERDICT_COLOUR[finding.verdict])
        + f"  {appraisal.headline}",
        MARGIN + RULE,
        "",
        field(style, "position", f"{appraisal.label} (seq {appraisal.position.seq})"),
        field(
            style,
            "law head",
            f"{abbrev(appraisal.law.law_head.said):<25}"
            f"clause {clause.id} ({clause.group.operator}), unity 1",
        ),
        field(
            style,
            "subject",
            appraisal.subject or "nothing of this class has been tabled at this position",
        ),
        "",
        *_arithmetic(appraisal, clause, style),
        "",
        *ground_of(finding, style),
    ]


def _arithmetic(appraisal: Appraisal, clause: Clause, style: Style) -> list[str]:
    """The slots, their weights, what each holds, and both sums against unity."""
    held = {one.endorser: one.disposition for one in appraisal.slots}
    header = f"{'slot':<18}{'weight':>6}   {'disposition':<14}committed act"
    lines = [MARGIN + style.label(header)]
    for slot, disposition in zip(clause.group.slots, appraisal.slots, strict=True):
        acted = "-" if disposition.said is None else abbrev(disposition.said)
        lines.append(
            _row(slot.endorser, rational(slot.weight), disposition.disposition.value, acted)
        )
    lines.append(_row("", "------", "", ""))
    lines.append(
        _row(
            "endorsed",
            rational(clause.group.endorsed_weight(held)),
            "of 1",
            "unity reached" if clause.group.satisfied(held) else "unity not reached",
        )
    )
    lines.append(
        _row(
            "reachable",
            rational(clause.group.reachable_weight(held)),
            "of 1",
            "unity still reachable"
            if clause.group.reachable(held)
            else "unity unreachable: a declined slot is spent",
        )
    )
    return lines


def ground_of(finding: Finding, style: Style) -> list[str]:
    """The ground the finding carries, which is part of what the finding is.

    Four values, four grounds, and no default case: a codomain with a fifth member would
    fail here loudly rather than print a verdict with nothing under it.
    """
    if isinstance(finding, Affirmed):
        return [
            MARGIN + style.strong("ground"),
            field(style, "clauses", ", ".join(finding.clauses), indent=4),
            field(
                style,
                "reached by",
                ", ".join(abbrev(said) for said in finding.endorsements),
                indent=4,
            ),
            field(style, "evidence", abbrev(finding.bundle, 16), indent=4),
        ]
    if isinstance(finding, Defeated):
        return _defeat_ground(finding, style)
    if isinstance(finding, Pending):
        lines = [MARGIN + style.strong("ground - what would discharge this")]
        for element in finding.requirement:
            lines.append(
                field(
                    style,
                    element.endorser,
                    f"{element.kind} under clause {element.clause}, {element.species.name_}",
                    indent=4,
                )
            )
            lines.append(" " * (4 + FIELD) + element.species.cure)
        return lines
    convicted = cast(SelfConvicted, finding)
    return [
        MARGIN + style.strong("ground"),
        field(style, "proof", abbrev(convicted.proof.package, 16), indent=4),
        field(
            style,
            "pair",
            ", ".join(abbrev(said) for said in convicted.proof.pair)
            if convicted.proof.pair
            else "none carried; the proof package names them",
            indent=4,
        ),
    ]


def _defeat_ground(finding: Defeated, style: Style) -> list[str]:
    citation = finding.citation
    lines = [
        MARGIN + style.strong("ground"),
        field(style, "clause", citation.clause, indent=4),
        field(
            style,
            "defeater",
            f"{citation.defeater_class.name.lower()} ({citation.defeater_class.gloss})",
            indent=4,
        ),
        field(
            style,
            "subcode",
            citation.subcode or "none: the cited clause defines no discriminator",
            indent=4,
        ),
    ]
    if citation.declination is not None:
        lines.append(
            field(
                style,
                "citation",
                f"the declination {abbrev(citation.declination.said)} "
                f"committed by {citation.declination.endorser}",
                indent=4,
            )
        )
    lines.extend(wrapped(style, "reason", citation.reason, indent=4))
    return lines


def _refusal_lines(appraisal: Appraisal, refusal: Refusal, style: Style) -> list[str]:
    lines = [
        MARGIN + style.banner("REFUSED - NOT EVALUABLE", REFUSAL_COLOUR),
        MARGIN + RULE,
        *textwrap.wrap(
            _NOT_A_VERDICT, width=WRAP, initial_indent=MARGIN, subsequent_indent=MARGIN
        ),
        "",
        field(style, "question", appraisal.headline),
        field(style, "position", f"{appraisal.label} (seq {appraisal.position.seq})"),
        field(style, "law head", abbrev(appraisal.law.law_head.said)),
        "",
        *wrapped(style, "missing", refusal.missing),
        *wrapped(style, "detail", refusal.detail),
        "",
        MARGIN + style.strong("the law in force here governs"),
    ]
    for clause in appraisal.law.clauses:
        lines.append(f"    {style.label(f'{clause.id:<{FIELD}}')}{', '.join(clause.governs)}")
    return lines


# --- utina law ----------------------------------------------------------------


def law_screen(law: Constitution, label: str, position: Position, style: Style) -> str:
    """The law in force: its head, and every clause with its slots and weights."""
    lines = [
        MARGIN + style.strong(f"LAW IN FORCE AT {label} (seq {position.seq})"),
        MARGIN + RULE,
        "",
        field(
            style,
            "head",
            f"{abbrev(law.law_head.said):<25}"
            f"over {len(law.clauses)} clauses, ordered by clause SAID",
        ),
        field(
            style,
            "bytes",
            f"{len(law.canonical_bytes())} canonical bytes, digested SHA-256",
        ),
    ]
    for clause in law.clauses:
        total = sum((slot.weight for slot in clause.group.slots), Fraction(0))
        lines.extend(
            [
                "",
                MARGIN
                + style.strong(f"clause {clause.id:<5}")
                + f"{f'{clause.group.operator}, unity 1':<38}{abbrev(clause.said())}",
                _clause_line(style, "governs", ", ".join(clause.governs)),
                _clause_line(
                    style,
                    "slots",
                    ", ".join(
                        f"{slot.endorser} {rational(slot.weight)}"
                        for slot in clause.group.slots
                    ),
                ),
                _clause_line(style, "weights", _weight_note(total)),
            ]
        )
    return _screen(lines)


def _clause_line(style: Style, label: str, value: str) -> str:
    return f"    {style.label(f'{label:<10}')}{value}"


def _weight_note(total: Fraction) -> str:
    """What the slot weights add up to, and what that means for who must act."""
    if total == 1:
        return "the slots sum to 1, so every slot is required"
    return (
        f"the slots sum to {rational(total)}, so unity is reachable without every slot"
    )


# --- utina log ----------------------------------------------------------------


def log_screen(
    events: tuple[Event, ...], label: str, position: Position, style: Style
) -> str:
    """The committed events, in the one order the fold consumes them in."""
    lines = [
        MARGIN + style.strong(f"COMMITTED LOG AT {label} (seq {position.seq})"),
        MARGIN + RULE,
        "",
        f"{MARGIN}{len(events)} events, in canonical order: anchoring coordinate first, "
        "then identifier.",
        f"{MARGIN}Arrival order is not consulted and there is nowhere here to read one from.",
        "",
        MARGIN + style.label(f"{'seq':>3}  {'kind':<12} {'identifier':<18} what it commits"),
    ]
    for event in events:
        lines.append(
            f"{MARGIN}{event.position.seq:>3}  {event.kind:<12} "
            f"{abbrev(event.said):<18} {_gloss(event)}"
        )
    return _screen(lines)


def _gloss(event: Event) -> str:
    """One line saying what this event puts on the record."""
    if event.kind == "inception":
        return "the founding law of the domain"
    if event.kind == "enactment":
        return f"a successor law, amending under the class {event.body.get(ACT_FIELD)}"
    if event.kind == "act":
        return f"an act of the class {event.body.get(ACT_FIELD)}"
    verb = "endorses" if event.body.get(DISPOSITION_FIELD) == ENDORSE else "declines"
    return (
        f"{event.body.get(ISSUER_FIELD)} {verb} "
        f"{abbrev(str(event.body.get(SUBJECT_FIELD)))}"
    )


# --- utina replay -------------------------------------------------------------


def replay_verdict(straight: bytes, shuffled: bytes) -> str:
    """Whether the two folds agree, which is the binding at custos-4.2.md:3101."""
    if straight == shuffled:
        return "IDENTICAL"
    return "DIFFERENT: this fold consulted something that is not committed"


def replay_screen(
    straight: Constitution,
    shuffled: Constitution,
    label: str,
    position: Position,
    seed: int,
    style: Style,
) -> str:
    """The Constitution recomputed twice, from the same bytes in two arrival orders."""
    canonical = straight.canonical_bytes()
    lines = [
        MARGIN + style.strong(f"REPLAY AT {label} (seq {position.seq})"),
        MARGIN + RULE,
        "",
        field(
            style,
            "committed",
            f"{abbrev(straight.law_head.said, 16):<25}"
            f"over {len(canonical)} canonical bytes, {len(straight.clauses)} clauses",
        ),
        field(
            style,
            "permuted",
            f"{abbrev(shuffled.law_head.said, 16):<25}"
            f"the same events, presented in arrival order seed {seed}",
        ),
        field(style, "result", replay_verdict(canonical, shuffled.canonical_bytes())),
        "",
        *textwrap.wrap(
            "custos-4.2.md:3101 binds this: a stream presented in permuted arrival order "
            "folds to a byte-identical Constitution. Byte-identical, not merely "
            "equivalent, which is why the two heads above are compared over the bytes "
            "they digest and not over the clauses they mean.",
            width=WRAP,
            initial_indent=MARGIN,
            subsequent_indent=MARGIN,
        ),
        "",
        MARGIN + style.strong("clause sub-blocks, in the order the head ranges over them"),
    ]
    for clause in sorted(straight.clauses, key=lambda one: one.said()):
        lines.append(f"    {style.label(f'{abbrev(clause.said(), 16):<20}')}{clause.id}")
    return _screen(lines)


# --- utina enact --------------------------------------------------------------


def verdict_word(outcome: Finding | Refusal) -> str:
    """What to call an outcome in one word, refusal included and kept distinct."""
    if isinstance(outcome, Refusal):
        return "REFUSED"
    return outcome.verdict.value.upper()


def enact_screen(
    event: Event, before: Appraisal, after: Appraisal, style: Style
) -> str:
    """A committed act, and what the record says about its subject because of it."""
    disposition = str(event.body.get(DISPOSITION_FIELD))
    verb = "endorses" if disposition == ENDORSE else "declines"
    committed = " ".join(
        f"{name}={event.body.get(name)}"
        for name in (ISSUER_FIELD, ACT_FIELD, DISPOSITION_FIELD)
    )
    lines = [
        MARGIN
        + style.banner(f"{'ENACTED':<10}", GREEN)
        + f"  {event.body.get(ISSUER_FIELD)} {verb} "
        f"{abbrev(str(event.body.get(SUBJECT_FIELD)))}",
        MARGIN + RULE,
        "",
        MARGIN + style.strong("committed event"),
        field(style, "coordinate", f"seq {event.position.seq}", indent=4),
        field(style, "kind", event.kind, indent=4),
        field(style, "identifier", event.said, indent=4),
        field(style, "body", committed, indent=4),
        field(
            style,
            "signature",
            f"{abbrev(str(event.body.get('sig')), 16)} "
            "(verified by the substrate before the event was recorded)",
            indent=4,
        ),
        "",
        *textwrap.wrap(
            "A constructor cannot act except by producing the evidence of its act, so "
            "this is the act. It stands for this invocation only: Acme's log is rebuilt "
            "from committed bytes on every run and nothing here is written to disk.",
            width=WRAP,
            initial_indent=MARGIN,
            subsequent_indent=MARGIN,
        ),
        "",
        MARGIN + style.strong("what the record says about the subject"),
        field(style, "before", verdict_word(before.outcome), indent=4),
        field(style, "after", verdict_word(after.outcome), indent=4),
        "",
    ]
    return _screen(lines) + eval_screen(after, style)
