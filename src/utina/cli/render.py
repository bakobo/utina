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
from collections.abc import Iterable
from fractions import Fraction
from typing import cast

from utina.cli.aliases import Aliases
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
from utina.fold.slots import (
    ACT_FIELD,
    DISPOSITION_FIELD,
    ENDORSE,
    ISSUER_FIELD,
    SCHEMA_FIELD,
    SUBJECT_FIELD,
    attributes,
    credential,
)
from utina.fold.triple import Position

__all__ = [
    "abbrev",
    "aliased",
    "enact_screen",
    "eval_screen",
    "ground_of",
    "law_screen",
    "log_screen",
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
#: alias has to fit: ``9-nina-as-director`` is exactly this long, which is why the
#: short form is the one the columns use (this.i @clscop).
SLOT = 18

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


def wrapped(style: Style, label: str, text: str, indent: int = 2) -> list[str]:
    """One labelled line whose value is prose, hanging under its own label.

    Never broken at a hyphen. Every alias on these screens is one hyphenated token, and
    a wrap that split ``9-marta-as-founder-at-acme`` across two lines would leave a
    fragment on each of them that reads like a shorter alias — which is a smaller
    version of the confusion this whole commission exists to remove.
    """
    pad = " " * (indent + FIELD)
    lines = textwrap.wrap(
        text, width=WRAP, initial_indent=pad, subsequent_indent=pad, break_on_hyphens=False
    )
    head = " " * indent + style.label(f"{label:<{FIELD}}") + lines[0][indent + FIELD :]
    return [head, *lines[1:]]


def _row(slot: str, weight: str, disposition: str, note: str) -> str:
    """One line of the arithmetic table, in the columns every other line uses."""
    return f"{MARGIN}{slot:<{SLOT}}{weight:>6}   {disposition:<14}{note}".rstrip()


def _screen(lines: Iterable[str]) -> str:
    return "\n".join(line.rstrip() for line in lines) + "\n"


# --- utina eval ---------------------------------------------------------------


def eval_screen(appraisal: Appraisal, aliases: Aliases, style: Style) -> str:
    """One appraisal, rendered as a finding or — visibly differently — as a refusal."""
    outcome = appraisal.outcome
    if isinstance(outcome, Refusal):
        return _screen(_refusal_lines(appraisal, outcome, aliases, style))
    return _screen(_finding_lines(appraisal, outcome, aliases, style))


def _finding_lines(
    appraisal: Appraisal, finding: Finding, aliases: Aliases, style: Style
) -> list[str]:
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
        *_arithmetic(appraisal, clause, aliases, style),
        "",
        *ground_of(finding, aliases, style),
    ]


def _arithmetic(
    appraisal: Appraisal, clause: Clause, aliases: Aliases, style: Style
) -> list[str]:
    """The slots, their weights, what each holds, and both sums against unity."""
    held = {one.endorser: one.disposition for one in appraisal.slots}
    header = f"{'slot':<{SLOT}}{'weight':>6}   {'disposition':<14}committed act"
    lines = [MARGIN + style.label(header)]
    for slot, disposition in zip(clause.group.slots, appraisal.slots, strict=True):
        acted = "-" if disposition.said is None else abbrev(disposition.said)
        lines.append(
            _row(
                abbrev(aliases.short(slot.endorser), SLOT),
                rational(slot.weight),
                disposition.disposition.value,
                acted,
            )
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
            lines.append(
                field(
                    style,
                    label,
                    f"{element.kind} under clause {element.clause}, {element.species.name_}",
                    indent=4,
                    width=width,
                )
            )
            lines.append(" " * (4 + width) + element.species.cure)
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
                        f"{aliases.short(slot.endorser)} {rational(slot.weight)}"
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
    events: tuple[Event, ...],
    label: str,
    position: Position,
    aliases: Aliases,
    style: Style,
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
    block = attributes(event)
    verb = "endorses" if block.get(DISPOSITION_FIELD) == ENDORSE else "declines"
    return (
        f"{aliases.short(str(credential(event).get(ISSUER_FIELD)))} {verb} "
        f"{abbrev(str(block.get(SUBJECT_FIELD)))}"
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
            MARGIN + style.strong(f"WHOIS {aliases.full(identifier)}"),
            MARGIN + RULE,
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


# --- utina enact --------------------------------------------------------------


def verdict_word(outcome: Finding | Refusal) -> str:
    """What to call an outcome in one word, refusal included and kept distinct."""
    if isinstance(outcome, Refusal):
        return "REFUSED"
    return outcome.verdict.value.upper()


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
        MARGIN
        + style.banner(f"{'ENACTED':<10}", GREEN)
        + f"  {aliases.full(issuer)} {verb} {subject}",
        MARGIN + RULE,
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
        field(style, "before", verdict_word(before.outcome), indent=4),
        field(style, "after", verdict_word(after.outcome), indent=4),
        "",
    ]
    return _screen(lines) + eval_screen(after, aliases, style)
