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

**A party is named by its alias, never by its identifier** (this.i @clcoia). No screen
here prints a truncated party identifier, because a prefix beside a name invites an
equality decision it cannot support. Every screen function therefore takes an
:class:`~utina.cli.aliases.Aliases` alongside its ``Style``, and the full identifier is
reachable only through ``utina whois``. What remains truncated is the digest of a
committed event — a law head, a clause, an evidence bundle — which is recorded as a
known gap rather than an oversight (this.i @clsaid).
"""

from __future__ import annotations

import textwrap
from collections.abc import Iterable, Mapping, Sequence
from fractions import Fraction
from typing import cast

from utina.cli.aliases import Aliases
from utina.cli.appraisal import Appraisal
from utina.cli.style import (
    AWAITING,
    DISPOSITION_COLOR,
    NOT_EVALUABLE,
    REACHED,
    REFUSAL_COLOR,
    SCAFFOLD,
    SPECIES_COLOR,
    SPENT,
    VERDICT_COLOR,
    Style,
)
from utina.domain import is_sequence
from utina.fold import bearing, certification
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
from utina.fold.slots import (
    ACT_FIELD,
    ATTRIBUTE_ISSUEE_FIELD,
    DISPOSITION_FIELD,
    ENDORSE,
    ENDORSEMENT_KIND,
    ISSUANCE_KIND,
    ISSUER_FIELD,
    REVOCATION_KIND,
    REVOKES_FIELD,
    SCHEMA_FIELD,
    SUBJECT_FIELD,
    attributes,
    credential,
)
from utina.fold.triple import SAID, Position
from utina.substrate import ISSUED, REVOKED

__all__ = [
    "abbrev",
    "aliased",
    "enact_screen",
    "eval_screen",
    "ground_of",
    "law_screen",
    "log_screen",
    "meanwhile_screen",
    "rational",
    "replay_screen",
    "replay_verdict",
    "verdict_word",
    "whois_screen",
]

#: Every screen is inset by this much, so a line never starts hard against the frame.
MARGIN = "  "

#: The rule under a headline. Eighty-four characters plus the margin sits inside a
#: hundred-column terminal with room for a scrollbar, and it is a single ASCII character
#: rather than box drawing, which not every projector's font has.
RULE = "-" * 84

#: The width a field label occupies before its value starts.
FIELD = 12

#: The width of the slot column in the arithmetic table. Also the budget an unscoped
#: alias has to fit, which is why the short form is the one the columns use (this.i
#: @clscop). ``nina-board-seat-3,6`` is nineteen and the longest Acme has; the extra
#: column is headroom, and ``tests/test_aliases.py`` fails rather than truncating if a
#: later party outgrows it.
SLOT = 20

#: The act column on the disturbance screen, wide enough for the record's own
#: names in full. A truncated name is unreadable from the back of a room, and
#: that screen has two columns rather than the slot table's five, so the width
#: is there to spend.
QUESTION = 26

#: Where prose wraps. Under the hundred columns the projector gives, with the margin and
#: a field label's worth of hanging indent already counted.
WRAP = 88

_NOT_A_VERDICT = (
    "This is not a verdict. A refusal is an operational fact: the evaluator declining an "
    "ill-posed question rather than legislating the missing rule."
)


# --- the small pieces ---------------------------------------------------------


def abbrev(value: str, keep: int = 12) -> str:
    """A digest shortened to a prefix that is still a usable handle.

    Truncation from the front rather than an elision through the middle, because
    ``--said`` and ``--on`` accept a prefix: what the screen prints is what the narrator
    can type back (this.i @clhndl).

    **Never call this on a party identifier.** That was its original job and it is now
    a security antipattern (this.i @clcoia): a prefix beside a name lets a reader
    believe they have checked an identity they have only glanced at. Parties go through
    :class:`~utina.cli.aliases.Aliases`, which never truncates. What is left here is the
    digest of a committed event — a law head, a clause, an evidence bundle — where the
    replacement would have to be invented rather than looked up, and which this.i
    @clsaid records as a known gap for a later commission.

    Safe on an alias, which is the other thing it is called on. An alias makes no
    security claim, so shortening one costs nothing that was ever there.
    """
    if len(value) <= keep:
        return value
    return value[:keep] + "..."


def aliased(text: str, aliases: Aliases) -> str:
    """Prose from the fold, with any party identifier in it replaced by an alias.

    The fold composes a defeat's ``reason`` and a refusal's ``detail`` itself, and it
    cannot know an alias — the display plane is above it and by decision invisible to it
    (this.i @cldspl). So the substitution happens here, on the way to the screen, and
    what is substituted is a whole identifier for a whole alias. Longest first, so that
    one identifier which is a prefix of another cannot be half-replaced.

    This is display rewriting of a display string. Nothing the fold computed changes,
    and the same sentence with the identifiers left in is still what the fold returned.
    """
    for identifier in sorted(aliases.identifiers(), key=len, reverse=True):
        text = text.replace(identifier, aliases.full(identifier))
    return text


def rational(value: Fraction) -> str:
    """An exact weight, written the way the committed law writes it."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def field(style: Style, label: str, value: str, indent: int = 2, width: int = FIELD) -> str:
    """One labelled line. Padded before it is painted, so both forms align.

    ``width`` exists for the one caller whose label is a whole alias rather than a word:
    a label longer than the column would otherwise run straight into its own value with
    no space between them, which is what a keripy party did here before it had a name.
    """
    return f"{' ' * indent}{style.label(f'{label:<{width}}')}{value}"


def wrapped(
    style: Style,
    label: str,
    text: str,
    indent: int = 2,
    *,
    mark: str | None = None,
    tint: str | None = None,
) -> list[str]:
    """One labelled line whose value is prose, hanging under its own label.

    Never broken at a hyphen. Every alias on these screens is one hyphenated token, and
    a wrap that split ``marta-founder-acme,6`` across two lines would leave a
    fragment on each of them that reads like a shorter alias — which is a smaller
    version of the confusion this whole commission exists to remove.

    ``mark`` is one word inside ``text`` to paint in ``tint``, and it is applied **after**
    the wrap and after the head is sliced, for two reasons that are both about escape
    sequences having bytes and no width: ``textwrap`` would count them towards ``WRAP``
    and wrap short, and a break could land in the middle of one. Painting last means the
    wrap is computed on the plain text and no escape can be split. If a wrap happens to
    divide ``mark`` anyway, no color is applied and the word is still the word — which is
    the direction this has to fail in.
    """
    pad = " " * (indent + FIELD)
    lines = textwrap.wrap(
        text, width=WRAP, initial_indent=pad, subsequent_indent=pad, break_on_hyphens=False
    )
    head = " " * indent + style.label(f"{label:<{FIELD}}") + lines[0][indent + FIELD :]
    painted = [head, *lines[1:]]
    if mark is not None and tint is not None:
        painted = [one.replace(mark, style.paint(mark, tint)) for one in painted]
    return painted


#: What a credential's registry state is painted in. **A revocation is AWAITING and not
#: SPENT**, which is a decision and not an oversight (this.i @w6bpgbwi): beat 16's whole
#: argument is that revoking is ordinary and bounded — the registry moves and nothing
#: else does — and red would put a malfunction into the one beat built to show there is
#: none. Amber says the slot is now awaiting a credential, which is exactly what beat 17
#: then shows. Anything else, including the "unknown" the fold returns where nothing
#: committed issues that credential here, reads as a thing there is no standing to answer.
_STATE_COLOR = {ISSUED: REACHED, REVOKED: AWAITING}


def state_tint(state: str) -> str:
    """What to paint a registry state in, for the two screens that print one."""
    return _STATE_COLOR.get(state, NOT_EVALUABLE)


def headline(style: Style, text: str, sgr: str = SCAFFOLD) -> list[str]:
    """A headline and the rule under it, which is painted in the headline's color.

    One rule with no exceptions: gray under a neutral heading, the verdict's color under
    a verdict banner, blue under a refusal. Eighty-four characters of color is the most
    legible thing on the screen from the back of a room, and it carries no meaning the
    banner above it did not already carry in words.

    ``text`` arrives already painted, because a banner is bold and a heading is not.
    """
    return [MARGIN + text, MARGIN + style.paint(RULE, sgr)]


def _row(
    slot: str,
    weight: str,
    disposition: str,
    note: str,
    *,
    style: Style | None = None,
    tint: str | None = None,
    note_tint: str | None = None,
) -> str:
    """One line of the arithmetic table, in the columns every other line uses.

    Two painting rules, both forced by the ``rstrip`` below. The disposition column is
    padded before it is painted, so the columns align in both forms — but only when a
    note follows it, because a *trailing* painted field keeps the padding that the plain
    form's ``rstrip`` removes, and the two forms would then differ by whitespace inside
    an escape sequence. The note is last, so it is painted without padding and there is
    nothing to strip in either form. Dropping the pad when the note is empty changes no
    plain output, since ``rstrip`` was already removing it.
    """
    cell = f"{disposition:<14}" if note else disposition
    if style is not None and tint is not None:
        cell = style.paint(cell, tint)
    tail = note
    if style is not None and note_tint is not None and note:
        tail = style.paint(note, note_tint)
    return f"{MARGIN}{slot:<{SLOT}}{weight:>6}   {cell}{tail}".rstrip()


def _screen(lines: Iterable[str]) -> str:
    return "\n".join(line.rstrip() for line in lines) + "\n"


# --- utina eval ---------------------------------------------------------------


def eval_screen(appraisal: Appraisal, aliases: Aliases, style: Style) -> str:
    """One appraisal, rendered as a finding or — visibly differently — as a refusal."""
    outcome = appraisal.outcome
    if isinstance(outcome, Refusal):
        return _screen(_refusal_lines(appraisal, outcome, aliases, style))
    return _screen(_finding_lines(appraisal, outcome, aliases, style))


def brief_screen(appraisal: Appraisal, aliases: Aliases, style: Style) -> str:
    """The same appraisal in eight to ten lines, for a beat that has to be held.

    The live half of demo 2 is a dozen-odd beats in about eighteen minutes, so the
    binding constraint is not compute — the whole ten-beat demo-1 run executes in
    0.22 seconds — it is how much screen a room can take in while somebody talks
    over it. This drops what a reader can reconstruct and keeps what they came to
    check.

    **What survives every cut, and why.** The verdict, because it is the answer.
    The law head, because a verdict with no law head is an opinion and the digest
    is what makes the answer checkable against a record. The slot table with its
    weights and both sums, because the audience is here to check arithmetic and
    arithmetic with the subtrahend missing is not checkable (``this.i`` @clarth).
    And the ground, because the Ground Axiom makes it part of what a finding IS
    rather than an annotation on it — a brief screen that cut it would be asking
    to be believed.

    What goes: the column header, the separator rule above the sums, the subject
    identifier, and the per-element cure lines, which collapse to one. A refusal
    keeps the four words that make it visibly not a fifth verdict and loses the
    paragraph explaining them, because by that point in the run it has been said.
    """
    outcome = appraisal.outcome
    if isinstance(outcome, Refusal):
        return _screen(
            [
                *headline(
                    style,
                    style.banner("REFUSED - NOT EVALUABLE", REFUSAL_COLOR),
                    REFUSAL_COLOR,
                ),
                MARGIN + f"{appraisal.label} (seq {appraisal.position.seq})",
                "",
                *wrapped(style, "missing", aliased(outcome.missing, aliases)),
            ]
        )
    clause = cast(Clause, appraisal.clause)
    held = {one.key: one.disposition for one in appraisal.slots}
    word = outcome.verdict.value.upper()
    tint = VERDICT_COLOR[outcome.verdict]
    satisfied = clause.group.satisfied(held)
    reachable = clause.group.reachable(held)
    return _screen(
        [
            *headline(
                style,
                style.banner(f"{word:<10}", tint) + f"  {appraisal.headline}",
                tint,
            ),
            MARGIN
            + f"{appraisal.label} (seq {appraisal.position.seq}), "
            + f"clause {clause.id} ({clause.group.operator}), unity 1, "
            + f"law head {abbrev(appraisal.law.law_head.said)}",
            "",
            *_arithmetic(appraisal, clause, aliases, style)[1:-3],
            # The two phrases the full screen puts on its own sums rows, collapsed onto
            # one line and painted the same way, so the brief form makes the same claim
            # in the same colors as the form it abbreviates.
            MARGIN
            + f"endorsed {rational(clause.group.endorsed_weight(held))} of 1, "
            + style.paint(
                "unity reached" if satisfied else "not reached",
                REACHED if satisfied else AWAITING,
            )
            + f"; reachable {rational(clause.group.reachable_weight(held))}, "
            + style.paint(
                "still reachable" if reachable else "unreachable",
                REACHED if reachable else SPENT,
            ),
            "",
            *wrapped(
                style,
                "ground",
                _brief_ground(outcome, aliases),
                mark=_species_mark(outcome),
                tint=_species_tint(outcome),
            ),
        ]
    )


def _species_mark(finding: Finding) -> str | None:
    """The discharge species named in a pending finding's ground, or ``None``.

    Only a pending finding has one, and the ground names the first requirement element's,
    which is the element the brief line reports. Painting it is the finest-grained thing
    color says here: whether this act is waiting on evidence that can still arrive, or on
    a cure path the record has closed.
    """
    return finding.requirement[0].species.name_ if isinstance(finding, Pending) else None


def _species_tint(finding: Finding) -> str | None:
    if not isinstance(finding, Pending):
        return None
    return SPECIES_COLOR[finding.requirement[0].species]


def _brief_ground(finding: Finding, aliases: Aliases) -> str:
    """One line of ground, whatever the verdict — never no line.

    Four values and no default case, for the reason :func:`ground_of` has none: a
    codomain that grew a fifth member should fail here loudly rather than print a
    verdict with nothing under it.
    """
    if isinstance(finding, Affirmed):
        return (
            f"clause {', '.join(finding.clauses)}, reached by "
            + ", ".join(abbrev(said) for said in finding.endorsements)
        )
    if isinstance(finding, Defeated):
        citation = finding.citation
        spent = citation.declination
        where = "" if spent is None else f", spent by {aliases.full(spent.endorser)}"
        return (
            f"clause {citation.clause}, {citation.defeater_class.name.lower()}{where}"
        )
    if isinstance(finding, Pending):
        first = finding.requirement[0]
        return (
            ", ".join(aliases.full(one.endorser) for one in finding.requirement)
            + f" - {first.kind} under clause {first.clause}, {first.species.value[1]}"
        )
    convicted = cast(SelfConvicted, finding)
    package = abbrev(convicted.proof.package, 16)
    if not convicted.proof.pair:
        return f"self-convicted on its own bytes, proof {package}"
    # The brief form carries the PAIR where there is one, because on beat 26 the pair is
    # the whole content: a certification, and the declination it was written around. A
    # brief screen that showed only the package would make the room ask what contradicted
    # what and then wait while somebody fetched it.
    contradicted = ", ".join(
        abbrev(said, 16) for said in convicted.proof.pair if said != convicted.proof.package
    )
    return f"self-convicted on its own bytes: {package} contradicts {contradicted}"


def _finding_lines(
    appraisal: Appraisal, finding: Finding, aliases: Aliases, style: Style
) -> list[str]:
    # A finding is returned only where a clause governs the act, and the appraisal
    # derives its clause from the same call the evaluator makes, so this is not an
    # assumption about luck: tests/test_cli.py asserts it beat by beat.
    clause = cast(Clause, appraisal.clause)
    word = finding.verdict.value.upper()
    tint = VERDICT_COLOR[finding.verdict]
    return [
        *headline(
            style,
            style.banner(f"{word:<10}", tint) + f"  {appraisal.headline}",
            tint,
        ),
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
        *_arithmetic(appraisal, clause, aliases, style),
        "",
        *ground_of(finding, aliases, style),
    ]


def _arithmetic(
    appraisal: Appraisal, clause: Clause, aliases: Aliases, style: Style
) -> list[str]:
    """The slots, their weights, what each holds, and both sums against unity."""
    held = {one.key: one.disposition for one in appraisal.slots}
    header = f"{'slot':<{SLOT}}{'weight':>6}   {'disposition':<14}committed act"
    lines = [MARGIN + style.label(header)]
    for slot, disposition in zip(clause.group.slots, appraisal.slots, strict=True):
        acted = "-" if disposition.said is None else abbrev(disposition.said)
        lines.append(
            _row(
                abbrev(aliases.short(disposition.endorser), SLOT),
                rational(slot.weight),
                disposition.disposition.value,
                acted,
                style=style,
                tint=DISPOSITION_COLOR[disposition.disposition],
            )
        )
    lines.append(_row("", "------", "", ""))
    # The two sums are where the health of the clause is stated, so they carry the two
    # colors that say it. "Not reached" is AWAITING and not SPENT: the endorsed sum
    # falling short of unity is an act in flight, and the row below is the one that says
    # whether it can still land. So red appears on exactly the screens where the path is
    # dead, which is what makes D3 against D6 legible at a glance (this.i @w6bpgbwi).
    satisfied = clause.group.satisfied(held)
    reachable = clause.group.reachable(held)
    lines.append(
        _row(
            "endorsed",
            rational(clause.group.endorsed_weight(held)),
            "of 1",
            "unity reached" if satisfied else "unity not reached",
            style=style,
            note_tint=REACHED if satisfied else AWAITING,
        )
    )
    lines.append(
        _row(
            "reachable",
            rational(clause.group.reachable_weight(held)),
            "of 1",
            "unity still reachable"
            if reachable
            else "unity unreachable: a declined slot is spent",
            style=style,
            note_tint=REACHED if reachable else SPENT,
        )
    )
    return lines


def ground_of(finding: Finding, aliases: Aliases, style: Style) -> list[str]:
    """The ground the finding carries, which is part of what the finding is.

    Four values, four grounds, and no default case: a codomain with a fifth member would
    fail here loudly rather than print a verdict with nothing under it.

    The ground block is one of the places with room for the full scoped alias
    (this.i @clscop), so a party named here is named completely rather than in the
    column's short form.
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
        return _defeat_ground(finding, aliases, style)
    if isinstance(finding, Pending):
        lines = [MARGIN + style.strong("ground - what would discharge this")]
        for element in finding.requirement:
            label = aliases.full(element.endorser)
            # The label is a whole alias, so the column widens to fit it and the cure
            # hangs under the value rather than at a fixed indent. A keripy party used
            # to run straight into its own value here with no space between them.
            width = max(FIELD, len(label) + 1)
            # The species and its cure are one claim in two sentences, so they take one
            # color: AWAITING while the missing evidence can still arrive, SPENT where
            # the record closed the path, CONVICTED where only the party's own act cures.
            # `field` pads the label and never the value, so painting inside the value is
            # safe here in a way it is not inside anything `wrapped` touches.
            tint = SPECIES_COLOR[element.species]
            lines.append(
                field(
                    style,
                    label,
                    f"{element.kind} under clause {element.clause}, "
                    + style.paint(element.species.name_, tint),
                    indent=4,
                    width=width,
                )
            )
            lines.append(" " * (4 + width) + style.paint(element.species.cure, tint))
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


def _defeat_ground(finding: Defeated, aliases: Aliases, style: Style) -> list[str]:
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
            # A subcode discriminates by naming the party, so it is a party identifier
            # wearing a different label, and it is named the same way as one.
            aliases.full(citation.subcode)
            if citation.subcode
            else "none: the cited clause defines no discriminator",
            indent=4,
        ),
    ]
    if citation.declination is not None:
        lines.append(
            field(
                style,
                "citation",
                f"the declination {abbrev(citation.declination.said)} "
                f"committed by {aliases.full(citation.declination.endorser)}",
                indent=4,
            )
        )
    lines.extend(wrapped(style, "reason", aliased(citation.reason, aliases), indent=4))
    return lines


def _refusal_lines(
    appraisal: Appraisal, refusal: Refusal, aliases: Aliases, style: Style
) -> list[str]:
    lines = [
        *headline(
            style,
            style.banner("REFUSED - NOT EVALUABLE", REFUSAL_COLOR),
            REFUSAL_COLOR,
        ),
        *textwrap.wrap(
            _NOT_A_VERDICT, width=WRAP, initial_indent=MARGIN, subsequent_indent=MARGIN
        ),
        "",
        field(style, "question", appraisal.headline),
        field(style, "position", f"{appraisal.label} (seq {appraisal.position.seq})"),
        field(style, "law head", abbrev(appraisal.law.law_head.said)),
        "",
        *wrapped(style, "missing", aliased(refusal.missing, aliases)),
        *wrapped(style, "detail", aliased(refusal.detail, aliases)),
        "",
        MARGIN + style.strong("the law in force here governs"),
    ]
    for clause in appraisal.law.clauses:
        lines.append(f"    {style.label(f'{clause.id:<{FIELD}}')}{', '.join(clause.governs)}")
    return lines


# --- utina law ----------------------------------------------------------------


def law_screen(
    law: Constitution, label: str, position: Position, aliases: Aliases, style: Style
) -> str:
    """The law in force: its head, and every clause with its slots and weights.

    The widest screen, which is why the slot lists below carry the unscoped alias. The
    header carries the scoped one, so the shared ``at acme`` every column drops is
    disclosed once rather than merely assumed (this.i @clscop).
    """
    lines = [
        *headline(style, style.strong(f"LAW IN FORCE AT {label} (seq {position.seq})")),
        "",
        field(
            style,
            "semantics",
            # An unpinned semantics is the same fact a refusal carries, arriving earlier:
            # the law cannot be read, so nothing under it can be evaluated. It takes the
            # refusal's color rather than a verdict's, because it is not an answer.
            (
                f"{abbrev(law.semantics, 16)}   the dossier specification, pinned"
                if law.semantics
                else style.paint(
                    "none pinned, so this law is not evaluable (axiom 4)", NOT_EVALUABLE
                )
            ),
        ),
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
        *wrapped(style, "parties", ", ".join(aliases.every_alias())),
        *wrapped(
            style,
            "aliases",
            f"Display names, not identifiers, and local to {aliases.scope}. The slot "
            f"lists below drop the shared 'at {aliases.scope.lower()}'. Run utina whois "
            "<alias> for the identifier behind one.",
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
                        f"{aliases.short(slot.key)} {rational(slot.weight)}"
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


def meanwhile_screen(
    events: tuple[Event, ...],
    since: str,
    upto: str,
    aliases: Aliases,
    style: Style,
) -> str:
    """What the record committed between two marked beats, which the room never sees.

    **It shortens the live run.** A room reads a screen faster than it hears a
    sentence, so the span the narrator used to cover in speech is cheaper on the
    projector (``this.i`` @eelnh6dn).

    Certifications are counted out separately because after M6 every affirmation rests
    on one, and a room that never saw them would come away thinking an endorsement
    authorized something.

    The closing note is the third thing this screen owes, and the least obvious: the
    beat labels are OURS. ``d1`` and ``b17`` are this demo's names for coordinates and
    are committed nowhere — the record has sequence numbers. Saying it here costs two
    lines and is the same disclosure the law screen's alias header already makes about
    party names.

    **It names only the coordinates that really are labels.** A domain with no label
    table is addressed by sequence number (``this.i`` @qtm5ntkg), and a note telling a
    reader that ``0`` and ``6`` are this demo's names for coordinates would be false
    about the two things on the screen it points at — which is a worse failure than the
    silence it was written to fix. Where both are numbers there is nothing to disclose
    and the note is absent.
    """
    certifications = sum(1 for one in events if one.kind == certification.CERTIFICATION_KIND)
    lines = [
        *headline(style, style.strong(f"MEANWHILE, between {since} and {upto}")),
        "",
        f"{MARGIN}{_tally(len(events), certifications)}",
        "",
        MARGIN + style.label(f"{'seq':>3}  {'kind':<13} {'identifier':<18} what it commits"),
    ]
    for event in events:
        lines.append(
            f"{MARGIN}{event.position.seq:>3}  {event.kind:<13} "
            f"{abbrev(event.said):<18} {_gloss(event, aliases)}"
        )
    ours = tuple(one for one in (since, upto) if not is_sequence(one))
    if ours:
        lines.extend(["", *wrapped(style, "labels", _labels_are_ours(ours))])
    return _screen(lines)


def _labels_are_ours(ours: tuple[str, ...]) -> str:
    """The closing note, naming the one or two coordinates that are a demo's names.

    The two-coordinate wording is unchanged to the byte, because every tracked demo
    artifact pins a card that carries it and a rephrasing would move five files to say
    the same thing.
    """
    if len(ours) == 1:
        return (
            f"{ours[0]} is this demo's name for a coordinate and is committed nowhere. "
            "The record has sequence numbers, which is what the seq column above shows "
            "and what a stranger folding the same log would address it by."
        )
    return (
        f"{ours[0]} and {ours[1]} are this demo's names for coordinates and are "
        "committed nowhere. The record has sequence numbers, which is what "
        "the seq column above shows and what a stranger folding the same log "
        "would address it by."
    )


def _tally(events: int, certifications: int) -> str:
    """The span's size, and how much of it is the domain admitting a tally.

    Never called with an empty span: ``meanwhile_command`` prints nothing at all rather
    than a screen saying nothing happened, because where the demo's play order steps
    back the record is not empty — the room has simply already seen it.
    """
    what = "event" if events == 1 else "events"
    if not certifications:
        return f"{events} committed {what}, and no certification among them."
    which = "certification" if certifications == 1 else "certifications"
    return f"{events} committed {what}, of which {certifications} {which}."


def log_screen(
    events: tuple[Event, ...],
    label: str,
    position: Position,
    aliases: Aliases,
    style: Style,
) -> str:
    """The committed events, in the one order the fold consumes them in."""
    lines = [
        *headline(style, style.strong(f"COMMITTED LOG AT {label} (seq {position.seq})")),
        "",
        f"{MARGIN}{len(events)} events, in the order the domain's key log sealed them: "
        "key event first, then seal list.",
        f"{MARGIN}Arrival order is not consulted and there is nowhere here to read one from.",
        "",
        MARGIN + style.label(f"{'seq':>3}  {'kind':<13} {'identifier':<18} what it commits"),
    ]
    for event in events:
        lines.append(
            f"{MARGIN}{event.position.seq:>3}  {event.kind:<13} "
            f"{abbrev(event.said):<18} {_gloss(event, aliases)}"
        )
    return _screen(lines)


def _gloss(event: Event, aliases: Aliases) -> str:
    """One line saying what this event puts on the record.

    The issuer of a disposition is a party, so it is named by its unscoped alias: the
    gloss sits in the rightmost column of the widest table on this screen, which is
    exactly the position the short form exists for.
    """
    if event.kind == "inception":
        return "the founding law of the domain"
    if event.kind == "enactment":
        return f"a successor law, enacted as {event.body.get(ACT_FIELD)}"
    if event.kind == "act":
        return f"an act of the class {event.body.get(ACT_FIELD)}"
    if event.kind == certification.CERTIFICATION_KIND:
        subject = str(event.body.get(certification.CERTIFIES_FIELD, ""))
        return f"the domain certifies {abbrev(subject)}"
    if event.kind == bearing.DUPLICITY_KIND:
        return f"duplicity observed at {aliases.short(str(bearing.convicted(event)))}"
    if event.kind == ISSUANCE_KIND:
        return _issued(event, aliases)
    if event.kind == REVOCATION_KIND:
        return f"revokes {abbrev(str(event.body.get(SUBJECT_FIELD, '')))}"
    if REVOKES_FIELD in event.body:
        # A retraction, keyed on the field rather than on a kind constant: the fold reads
        # `revokes` wherever it appears and the substrate commits no dedicated kind for
        # one (tick 3z6a), so a constant here would be inventing a name for it.
        who = aliases.short(str(event.body.get(ISSUER_FIELD, "")))
        return f"{who} withdraws {abbrev(str(event.body.get(REVOKES_FIELD, '')))}"
    # **Every event kind is named above, and the fall-through is a disposition.** It used
    # to be the other way round: anything this function had no reading for was rendered
    # through the disposition path, which put "marta-founder,6 declines …" against a
    # certification the domain committed, "None declines None" against a duplicity
    # observation, and "acme-governed-domain,6 declines None" against a credential
    # issuance — that last one six times over in the tracked transcripts, because an
    # issuance HAS a non-empty attributes block and an earlier guard on emptiness let it
    # straight through. A glossary that guesses is worse than one that says nothing, so
    # an unreadable kind now says so.
    block = attributes(event)
    if event.kind != ENDORSEMENT_KIND or not block:
        return "—"
    verb = "endorses" if block.get(DISPOSITION_FIELD) == ENDORSE else "declines"
    return (
        f"{aliases.short(str(credential(event).get(ISSUER_FIELD)))} {verb} "
        f"{abbrev(str(block.get(SUBJECT_FIELD)))}"
    )


def _issued(event: Event, aliases: Aliases) -> str:
    """A credential issuance, named by who holds it.

    The office the credential seats them in is deliberately NOT repeated here, even
    though the row is about the office being filled: a COIA alias already carries the
    holder's role, so ``nina-board-seat-3,6`` says the seat in the same breath as the
    person. Naming it twice pushed this row to 105 columns against the projector's 96
    (``tests/test_cli.py``), which is a cost paid for no information.
    """
    issuee = attributes(event).get(ATTRIBUTE_ISSUEE_FIELD, "")
    return f"a credential to {aliases.short(str(issuee))}"


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
        *headline(style, style.strong(f"REPLAY AT {label} (seq {position.seq})")),
        "",
        field(
            style,
            "canonical",
            f"{abbrev(straight.law_head.said, 16):<25}"
            f"over {len(canonical)} canonical bytes, {len(straight.clauses)} clauses",
        ),
        field(
            style,
            "permuted",
            f"{abbrev(shuffled.law_head.said, 16):<25}"
            f"the same events, presented in arrival order seed {seed}",
        ),
        # The determinism claim, and the one line the last beat of both demos exists
        # for. Identical is REACHED; a difference means this fold consulted something
        # that is not committed, which is the worst answer any screen here can give.
        field(
            style,
            "result",
            style.paint(
                replay_verdict(canonical, shuffled.canonical_bytes()),
                REACHED if canonical == shuffled.canonical_bytes() else SPENT,
            ),
        ),
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


# --- utina whois --------------------------------------------------------------


def whois_screen(
    identifier: str, aliases: Aliases, substrate: str, style: Style
) -> str:
    """One party, named three ways: the alias, the identifier, and where it came from.

    The identifier is printed whole and on its own line. That is the point of the
    command and it is also what makes it safe: pill-design section 3.3 rejects the short
    head-and-tail teaser precisely because it is glanceable and grindable, and is
    explicit that the objection does not reach a full value, which is too long to grind
    and too long to compare at a glance without meaning to.

    The substrate is named because it is what produced the identifier, and because the
    same alias answers with different bytes under the facade and under keripy — which
    is a thing an audience should be told rather than left to discover.
    """
    return _screen(
        [
            *headline(style, style.strong(f"WHOIS {aliases.full(identifier)}")),
            "",
            field(style, "alias", aliases.full(identifier)),
            field(style, "in columns", aliases.short(identifier)),
            field(style, "identifier", identifier),
            field(style, "substrate", f"{substrate}, which produced that identifier"),
            "",
            *textwrap.wrap(
                "An alias is a display name, local to this domain and chosen by it. It "
                "is not a commitment to meaning, it carries no security claim, and it "
                "never enters a committed byte. The identifier above is the value the "
                "record actually holds; compare on that, in full, and never on a piece "
                "of it.",
                width=WRAP,
                initial_indent=MARGIN,
                subsequent_indent=MARGIN,
            ),
        ]
    )


# --- utina seat ---------------------------------------------------------------


def seat_screen(
    seat: str,
    label: str,
    position: Position,
    delegation: Mapping[str, object],
    credential: Mapping[str, object],
    aliases: Aliases,
    style: Style,
) -> str:
    """One office, and the two independent bindings that make it one.

    **Draft register — Daniel's to overwrite.** The narration below is written so
    the screen is not mute, not because its wording is settled.

    The two halves are shown side by side because the demo's claim is that they
    are separate and that only one of them confers anything. KERI's half says a
    relationship exists and is dual-anchored — the organ signed its own ``dip``
    naming Acme, and Acme sealed that inception into its own key log, and neither
    alone is a delegation. It says nothing about what the office may do. ACDC's
    half is the credential that says so, and it is the half a revocation can take
    back (``this.i`` @cglayqvw).

    Registry state is the FOLD's, read from committed events at this position,
    not the substrate's answer about now. The two can disagree — after beat 16
    they do — and the one that belongs on a screen headed by a coordinate is the
    one computed at that coordinate.
    """
    state = credential.get("state")
    return _screen(
        [
            *headline(style, style.strong(f"SEAT {aliases.full(seat)}")),
            "",
            field(style, "position", f"{label} (seq {position.seq})"),
            "",
            MARGIN + style.strong("KERI — a relationship, dual-anchored"),
            field(style, "identifier", seat, indent=4),
            field(
                style,
                "delegator",
                f"{aliases.full(str(delegation['delegator']))}, named in the dip's di",
                indent=4,
            ),
            field(
                style,
                "seal",
                f"{abbrev(str(delegation['seal']), 16)}   the delegator's own approving event",
                indent=4,
            ),
            "",
            MARGIN + style.strong("ACDC — the credential that confers the authority"),
            field(style, "credential", abbrev(str(credential["said"]), 16), indent=4),
            field(style, "schema", abbrev(str(credential["schema"]), 16), indent=4),
            field(style, "issuer", aliases.full(str(credential["issuer"])), indent=4),
            field(style, "issuee", aliases.full(str(credential["issuee"])), indent=4),
            field(style, "registry", abbrev(str(credential["registry"]), 16), indent=4),
            field(
                style,
                "state",
                style.paint(
                    str(state) if state else "no standing to read",
                    state_tint(str(state)) if state else NOT_EVALUABLE,
                )
                + ", as the fold reads it here",
                indent=4,
            ),
            field(style, "may", str(credential.get("acts", "")), indent=4),
            "",
            *textwrap.wrap(
                "The two bindings are independent and only the second one confers. A "
                "delegation of ilk delegation proves that a relationship exists, and "
                "the same fact would hold of an identifier delegated to greet visitors; "
                "it is permanent, and nothing can undo it. What the office may do is "
                "the credential's business, and because it is a credential it can be "
                "revoked — at which point this slot empties and the office is an office "
                "nobody holds.",
                width=WRAP,
                initial_indent=MARGIN,
                subsequent_indent=MARGIN,
            ),
        ]
    )


# --- utina registry -----------------------------------------------------------


def registry_screen(
    registry: str,
    controller: str,
    label: str,
    position: Position,
    holdings: Sequence[Mapping[str, object]],
    aliases: Aliases,
    style: Style,
) -> str:
    """What a registry says about every credential in it, at one coordinate.

    **Draft register — Daniel's to overwrite.**

    Every row is folded from committed events rather than read off a transaction
    log: registry state is "a member of the evidence bundle rather than an
    ambient condition read against it" (issue #82 rule 3), so a screen that
    asked the substrate would be showing something the fold is not allowed to
    use. The revoking event is named on the row it moved, because a state with
    no act behind it is a claim rather than a record.
    """
    lines = [
        *headline(style, style.strong(f"REGISTRY {abbrev(registry, 16)}")),
        "",
        field(style, "position", f"{label} (seq {position.seq})"),
        field(style, "controller", aliases.full(controller)),
        "",
        MARGIN
        + style.label(f"{'credential':<{SLOT}}{'at seq':>6}   {'state here':<14}moved by"),
    ]
    for held in holdings:
        state = str(held["state"])
        lines.append(
            _row(
                abbrev(str(held["said"]), 12),
                f"{held['issued']}",
                state,
                "" if not held.get("moved") else abbrev(str(held["moved"]), 12),
                style=style,
                tint=state_tint(state),
            )
        )
    lines.extend(
        [
            "",
            *textwrap.wrap(
                "Registry state is evidence, and standing is judgment. A revocation "
                "moves what this registry says about a credential and moves nothing "
                "else: the office's key log is untouched, its keys still verify, and "
                "every finding that cited the credential while it stood still stands "
                "at its own coordinate. What a revocation reaches is the next act, not "
                "the last one.",
                width=WRAP,
                initial_indent=MARGIN,
                subsequent_indent=MARGIN,
            ),
        ]
    )
    return _screen(lines)


# --- utina disturbance --------------------------------------------------------


def disturbance_screen(
    amendment: SAID,
    label: str,
    position: Position,
    computed: Sequence[SAID],
    names: Mapping[SAID, str],
    style: Style,
) -> str:
    """Which acts that were in flight this amendment ended.

    **Draft register — Daniel's to overwrite.**

    This screen used to carry two columns, declared against computed, and the
    beat was that a document had been caught lying about itself. The declaration
    is gone (this.i @ow6dzro4): it gated nothing, so it existed only to create
    something that could be false, and an obligation that changes no outcome is
    not one governance should impose.

    What is left is the half that was always doing the work. Changing a rule can
    end matters that are still in flight — nobody votes them down, they simply
    can never be completed — and a reader is owed which ones. Any stranger
    holding the log computes this same list from the same committed bytes, with
    no judge and no appeal to anything outside the record. That claim survives
    the removal intact, because it was never the declaration that made it true.

    Named by the record's own labels where it has one, because
    ``approve-capital-plan`` is the thing a room can hold and a 44-character
    identifier is not — the identifier is there too, abbreviated, since the label
    is a display name and the identifier is what was committed.
    """
    lines = [
        *headline(style, style.strong(f"DISTURBANCE {abbrev(amendment)}")),
        "",
        field(style, "position", f"{label} (seq {position.seq})"),
        field(
            style,
            "ended",
            f"{len(computed)} act{'' if len(computed) == 1 else 's'} that "
            + ("was" if len(computed) == 1 else "were")
            + " in flight",
        ),
        "",
        MARGIN + style.label(f"{'act':<{QUESTION}}identifier"),
    ]
    for said in sorted(computed):
        lines.append(
            f"{MARGIN}"
            + style.paint(f"{abbrev(names.get(said, said), QUESTION - 3):<{QUESTION}}", SPENT)
            + abbrev(said)
        )
    lines.extend(
        [
            "",
            *textwrap.wrap(
                "Each act above was still in flight when this amendment took force, and its "
                "cure path is shut after it: the clause it was gathering endorsements under "
                "is gone, so the endorsements it was waiting for can no longer discharge it. "
                "An act whose own clause the amendment left alone is untouched, which is what "
                "keeps this from being a way to kill an inconvenient matter by amending "
                "something irrelevant.",
                width=WRAP,
                initial_indent=MARGIN,
                subsequent_indent=MARGIN,
            ),
        ]
    )
    return _screen(lines)


# --- utina enact --------------------------------------------------------------


def verdict_word(outcome: Finding | Refusal) -> str:
    """What to call an outcome in one word, refusal included and kept distinct."""
    if isinstance(outcome, Refusal):
        return "REFUSED"
    return outcome.verdict.value.upper()


def verdict_tint(outcome: Finding | Refusal) -> str:
    """What to paint an outcome in, refusal included and kept distinct.

    The companion to :func:`verdict_word`, and it keeps a refusal out of
    ``VERDICT_COLOR`` for the reason that mapping has no entry for one: a refusal is not
    a member of the codomain, and a table that gave it one would be the first step
    towards a fifth verdict (this.i @clrfsl).
    """
    if isinstance(outcome, Refusal):
        return REFUSAL_COLOR
    return VERDICT_COLOR[outcome.verdict]


def enact_screen(
    event: Event,
    before: Appraisal,
    after: Appraisal,
    aliases: Aliases,
    style: Style,
    *,
    anchor: str | None = None,
) -> str:
    """A committed act, and what the record says about its subject because of it.

    The credential block is the one place on any screen where a party appears as a
    full identifier rather than as an alias, and it is deliberate: the block is
    labelled as committed bytes, an alias never enters committed bytes (this.i
    @cldspl), and printing one there would assert the opposite of what the decision
    says. Values are wrapped rather than truncated, because a full value is not the
    antipattern — a short teaser is.

    ``anchor`` is the key-log event the credential's identifier is sealed into,
    asked of the substrate by the caller: the dossier's Endorsed predicate requires
    the anchor (this.i @7db5c4), so the screen shows it rather than implying it.
    """
    acdc = credential(event)
    block = attributes(event)
    issuer = str(acdc.get(ISSUER_FIELD))
    disposition = str(block.get(DISPOSITION_FIELD))
    subject = abbrev(str(block.get(SUBJECT_FIELD)))
    verb = "endorses" if disposition == ENDORSE else "declines"
    lines = [
        # ENACTED is a commit receipt rather than a verdict — the record took the act,
        # which says nothing yet about whether the act is lawful. It is REACHED because
        # the evidence arrived, and the block at the foot of this screen is where the
        # judgment is, in the two verdict words this now paints.
        *headline(
            style,
            style.banner(f"{'ENACTED':<10}", REACHED)
            + f"  {aliases.full(issuer)} {verb} {subject}",
            REACHED,
        ),
        "",
        MARGIN + style.strong("committed event"),
        field(style, "coordinate", f"seq {event.position.seq}", indent=4),
        field(style, "kind", event.kind, indent=4),
        field(style, "identifier", event.said, indent=4),
        # Whole, and wrapped. A keripy signature is the establishment event's SAID, a
        # dot, and the indexed signature (this.i @zk27gz) — and for a party that has
        # never rotated, that leading SAID *is* their identifier, because a KERI prefix
        # is the digest of its own inception event. Truncating this field therefore
        # printed a sixteen-character party prefix, which is precisely the thing
        # @clcoia removes; tests/test_cli.py caught it by grep and not by eye.
        *wrapped(
            style,
            "signature",
            f"{event.body.get('sig')} (the substrate verified it before recording)",
            indent=4,
        ),
        "",
        MARGIN + style.strong("embedded credential (a registry-less ACDC, this.i @7db5c4)"),
        field(style, "identifier", str(acdc.get("d")), indent=4),
        field(style, "schema", str(acdc.get(SCHEMA_FIELD)), indent=4),
        *wrapped(style, "issuer", issuer, indent=4),
        *wrapped(
            style,
            "attributes",
            f"{ACT_FIELD}={block.get(ACT_FIELD)} "
            f"{DISPOSITION_FIELD}={disposition} "
            f"{SUBJECT_FIELD}={subject} dt={block.get('dt')}",
            indent=4,
        ),
        field(
            style,
            "anchor",
            f"sealed at {abbrev(anchor)} in the issuer's key log"
            if anchor
            else "not found in the issuer's key log",
            indent=4,
        ),
        *wrapped(
            style,
            "signature",
            f"{event.body.get('acdc_sig')} (a stranger verifies this with KERI tooling "
            "and the key log alone)",
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
        # The same words that head an eval screen, so they take the same colors. This is
        # the pair the block exists for, and "pending -> affirmed" should read in one
        # glance rather than being spelled out twice in prose.
        field(
            style,
            "before",
            style.paint(verdict_word(before.outcome), verdict_tint(before.outcome)),
            indent=4,
        ),
        field(
            style,
            "after",
            style.paint(verdict_word(after.outcome), verdict_tint(after.outcome)),
            indent=4,
        ),
        "",
    ]
    return _screen(lines) + eval_screen(after, aliases, style)
