"""Demo 2's run-of-show: an opener, thirteen live beats in six kernels, a coda.

Like ``demo.py`` this module computes nothing. A beat is a title, a line of
narration and the argv of a command a person could have typed, and the walk
echoes the command and dispatches it through the same entry point a shell
reaches. If a screen appears here that the CLI cannot produce, the demo's own
claim is the first thing it fails to show (``this.i`` @cldemo).

**The shape is ``docs/demo-2-script.md``'s and the register is Daniel's.** The
narration below is a draft written so the run is not mute; it is not taste being
claimed. What is structural, and should survive rewording: the three parts, the
kernel grouping, the beat order, and the cut list.

The three parts are separate commands rather than one long walk because they are
played differently. The opener is recorded and runs at full screen density under
keripy, with real prefixes, so the room sees this is really KERI once and the
live part never argues it again. The live part is brief-screened and paced for
narration. The leave-behind is the whole twenty-five, recorded, sent afterwards.

**Timing.** Compute is free — demo 1's ten beats execute in 0.22 s on the facade
and 1.30 s under keripy — so every minute in the room is narration. The live
thirteen are budgeted at 17 to 19 minutes, of which beats 8 and 16 are screens
rather than evaluations and run in well under a minute each.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING

from utina.acme import LABEL_UNKNOWN
from utina.cli.render import MARGIN, RULE, WRAP
from utina.cli.style import SCAFFOLD, Style
from utina.substrate import FACADE, KERIPY

if TYPE_CHECKING:  # pragma: no cover - the import exists only for the annotation
    from utina.cli.app import Console

__all__ = [
    "CUT_ORDER",
    "KERNELS",
    "LEAVE_BEHIND",
    "LIVE",
    "OPENER",
    "Beat",
    "Kernel",
    "coordinate_of",
    "walk2",
]


@dataclass(frozen=True)
class Beat:
    """One beat: what to call it, what it is for, and what to run.

    ``refuses`` marks a beat whose command is *meant* to exit non-zero — beat 14
    is an endorsement the toolchain refuses, and a driver that treated its exit
    status as failure would report the demo broken at the moment it worked.

    There is no "not built yet" flag any more. Beat 20 was the last beat that
    needed one and it was ruled on 2026-09-15, so the run-of-show is the whole
    run-of-show. If a beat is ever blocked again, the five lines that printed a
    NOT BUILT card are in this file's history rather than carried unused here.
    """

    id: str
    title: str
    narration: str
    argv: tuple[str, ...] = ()
    refuses: bool = False


@dataclass(frozen=True)
class Kernel:
    """A run of beats, with what the room expects and what actually happens.

    The expectation is on the card because the beats were chosen on one test —
    where this audience's own intuition is wrong — and a beat that lands only if
    the wrong intuition was voiced first is a beat that needs it voiced.
    """

    title: str
    expects: str
    happens: str
    beats: tuple[Beat, ...] = field(default_factory=tuple)


OPENER = (
    Beat(
        "1",
        "The law Acme committed at inception",
        "Three clauses, two founders, half the weight each, and the digest of the "
        "semantics the clauses are written in. Nothing is judged yet. A law that did "
        "not pin its semantics would be refused rather than read at whatever revision "
        "happens to be installed.",
        ("law", "--at", "inception"),
    ),
    Beat(
        "2",
        "Open a bank account",
        "Both founders endorse and unity is reached. The affirmation carries the "
        "endorsements that reached it rather than asserting that they did.",
        ("eval", "open-bank-account", "--at", "d1"),
    ),
    Beat(
        "3",
        "Hire a VP of Sales",
        "Marta has endorsed and Dev has not acted. Pending is not a hedge: it names "
        "the slot whose act would discharge it. Left pending on purpose — beat 9 "
        "comes back for it.",
        ("eval", "hire-vp-sales", "--at", "d2"),
    ),
    Beat(
        "4",
        "Sign the office lease, after Dev declines",
        "A signed no spends its slot, so the weight that could still arrive no longer "
        "reaches unity. Watch the reachable row, not the endorsed one.",
        ("eval", "sign-office-lease", "--at", "d3"),
    ),
    Beat(
        "5",
        "Release escrowed founder equity",
        "The founders' own clause, which the amendment at beat 7 will not touch. Also "
        "left pending on purpose, and for a different reason than beat 3 was.",
        ("eval", "release-escrowed-equity", "--at", "b5"),
    ),
    Beat(
        "6",
        "May the board declare a dividend?",
        "No clause governs distributions. The engine refuses rather than legislating, "
        "and the refusal names what is missing. Not a fifth verdict, and the screen "
        "says so in as many words.",
        ("eval", "declare-dividend", "--at", "d8"),
    ),
)

KERNELS = (
    Kernel(
        "The amendment as hinge",
        "a document is adopted",
        "a seat AID is delegated, a seat credential is issued, and the enactment "
        "declares what it disturbs",
        (
            Beat(
                "7",
                "Seat the board: the amendment itself",
                "The enactment that changes the law is judged under the law it "
                "replaces — clause A2, not the B2 it commits. Succession is never "
                "retroactive, and everything after this beat uses the board this one "
                "creates.",
                ("eval", "--said", "seat-the-board", "--at", "d4", "--brief"),
            ),
        ),
    ),
    Kernel(
        "What the amendment did to two pending acts",
        "an amendment changes everything, or nothing",
        "the cure path closes for one and stays open for the other, decided by "
        "whether the clause moved",
        (
            Beat(
                "9",
                "The hire, re-asked after the amendment",
                "Beat 3's question, from the far side. Clause A1 is repealed, so the "
                "cure path is shut and the enactment that shut it is the ground. Still "
                "pending — but a different species of pending, and it names which.",
                ("eval", "hire-vp-sales", "--at", "board-seated", "--brief"),
            ),
            Beat(
                "10",
                "The equity release, re-asked after the amendment",
                "Beat 5's question, from the same coordinate, and the opposite answer. "
                "Clause A3 was carried across byte-identical, so it is the same clause "
                "and the cure path never closed. Same amendment, two pending acts, two "
                "outcomes, decided by whether the rule under each one moved.",
                ("eval", "release-escrowed-equity", "--at", "board-seated", "--brief"),
            ),
        ),
    ),
    Kernel(
        "Same signed no, two answers",
        'a "no" means no',
        "defeat under two slots, pending under three. The Constitution changed; the "
        "arithmetic did the rest",
        (
            Beat(
                "13",
                "The Q2 forecast, after Dev declines",
                "The same signed no as beat 4, from the same person, "
                "under the board's clause. Defeat became pending, because with three "
                "slots the ceiling still clears unity. Nothing about the declination "
                "changed.",
                ("eval", "approve-budget", "--at", "b13", "--brief"),
            ),
        ),
    ),
    Kernel(
        "Two currents, unmerged",
        "the credential check *is* the answer",
        "the toolchain rejects an unseated endorser before any fold runs, and the "
        "fold answers separately",
        (
            Beat(
                "8",
                "Board seat 3, and the two bindings that make it an office",
                "KERI's half is a delegation, dual-anchored: seat 3 signed its own dip "
                "naming Acme, and Acme sealed that inception into its own key log. It "
                "proves a relationship and confers nothing. ACDC's half is the "
                "credential that confers, and it is the half that can be revoked.",
                ("seat", "acme:seat3", "--at", "b8"),
            ),
            Beat(
                "12",
                "The annual budget, on two slots of three",
                "Unity is reached while a party has never acted at all. Presence is "
                "not the question; reachable weight is. Seat 3's endorsement carries "
                "an edge to its seat credential, and the toolchain checked that edge "
                "before the record ever saw it.",
                ("eval", "approve-budget", "--at", "d5", "--brief"),
            ),
            Beat(
                "14",
                "Quinn endorses without a seat",
                "Quinn cites a seat credential whose issuee he is not. This is the "
                "beat where the two currents separate: edge validation refuses the "
                "citation before any fold runs, so nothing is committed and the fold "
                "is never consulted. Re-ask beat 13 afterwards and the answer has not "
                "moved, because the governance current never heard about this.",
                (
                    "enact", "endorse",
                    "--as", "acme:quinn",
                    "--on", "approve-q2-forecast",
                    "--citing", "seat-credential",
                ),
                refuses=True,
            ),
        ),
    ),
    Kernel(
        "Revocation, and what it cannot do",
        "revoking undoes the decision",
        "it changes the next answer and not the last one — and then duplicity, which "
        "does reach back",
        (
            Beat(
                "16",
                "Acme revokes the seat credential",
                "The registry moves and nothing else does. Seat 3's key log is "
                "untouched and its keys still verify. Registry state is evidence, and "
                "the screen names the act that moved it, because a state with no act "
                "behind it is a claim rather than a record.",
                ("registry", "--at", "b16"),
            ),
            Beat(
                "17",
                "The Q3 budget, a new question after the revocation",
                "Seat 3's slot is now unfilled — not refused, unfilled, because the "
                "office is an office nobody holds until a credential says otherwise. "
                "The finding names what would fill it rather than treating the "
                "revocation as a verdict.",
                ("eval", "approve-budget", "--at", "b17", "--brief"),
            ),
            Beat(
                "19",
                "Beat 12's question, re-asked after the revocation",
                "The surprising half. Same answer, over demonstrably different "
                "evidence: the credential stood when it was cited, and nothing "
                "committed later unmakes that. A revocation that reached back would "
                "let any issuer unmake any past finding at any distance, alone.",
                ("eval", "--said", "approve-budget", "--at", "b17", "--brief"),
            ),
            Beat(
                "20",
                "Duplicity at seat 3's signing position",
                "And the contrast. Beat 19 re-asked and the answer held; this re-asks "
                "the same question after seat 3 was seen signing two contradictory "
                "key events, and the answer moves. Not backwards — beat 12 still "
                "stands at its own coordinate — but the voice is poisoned from here "
                "on, and no amount of further evidence cures it. Only an act of seat "
                "3's own does. Revocation and undercut are different mechanisms and "
                "the engine keeps them on separate code paths.",
                ("eval", "--said", "approve-budget", "--at", "b20", "--brief"),
            ),
        ),
    ),
    Kernel(
        "What a rule change costs",
        "changing a rule is free, or at worst controversial",
        "it ends live matters nobody voted down, and the record says which",
        (
            Beat(
                "22",
                "The second amendment: lower the ordinary-acts bar",
                "The board passes it unanimously, all three slots, unity reached. It is "
                "entirely lawful and nobody cheated. Hold that, because the next beat is "
                "what it cost.",
                ("eval", "--said", "lower-the-bar", "--at", "b22", "--brief"),
            ),
            Beat(
                "23",
                "The three decisions that can now never finish",
                "Lowering the bar replaced the clause three acts were gathering "
                "endorsements under, so the endorsements they were waiting for can no "
                "longer discharge them. Nobody voted them down; they simply cannot "
                "complete. Any stranger holding the log computes this same list from "
                "the same committed bytes — and an act whose own clause the amendment "
                "left alone is untouched, which is what stops this being a way to kill "
                "anything inconvenient.",
                ("disturbance", "lower-the-bar", "--at", "b23"),
            ),
        ),
    ),
    Kernel(
        "A certification that lies",
        "a decision is authorized when the votes add up",
        "it is authorized when the domain CERTIFIES that they did — and a certification "
        "the record refutes convicts the sponsor on their own signature",
        (
            Beat(
                "26",
                "Marta certifies an act that never carried",
                "The founders table the equity release again. Marta endorses, Dev signs a "
                "no, and Marta — sponsoring the tally — cites her own endorsement at full "
                "weight and leaves the no out. The domain admits it, because what the "
                "domain checks is that the cited weights add to one, and they do. What it "
                "does not do is re-fold its own record first. So the lie is well formed "
                "and it is on the record, and the fold convicts it on the bytes Marta "
                "signed: the proof names the certification and the declination it was "
                "written around, and any stranger holding the log recomputes it. This is "
                "the fourth verdict, and it is a governance failure rather than a lost "
                "key.",
                ("eval", "--said", "equity-retabled", "--at", "b26", "--brief"),
            ),
        ),
    ),
)

LIVE = tuple(beat for kernel in KERNELS for beat in kernel.beats)

#: The beats the opener and the live thirteen leave out, at full screen density.
#: Sent with the follow-up rather than played, because the likeliest thing this
#: audience does next is try to read the specification.
LEAVE_BEHIND = (
    Beat(
        "11",
        "The equity release, cured across the amendment",
        "Beat 10's question once Dev acts. Cured under the clause that never moved.",
        ("eval", "release-escrowed-equity", "--at", "b11"),
    ),
    Beat(
        "15",
        "Nina endorses from her delegated device",
        "The third delegation stratum. The device signs with its own key and fills "
        "seat 3's slot, because the seat granted it authority in a credential the "
        "seat can revoke — never because the delegation exists.",
        ("eval", "approve-budget", "--at", "b15"),
    ),
    Beat(
        "18",
        "Beat 12's question, re-asked at beat 12's own position",
        "Byte-identical to the original finding, ground included. Beat 19 is the "
        "same answer over a grown bundle; this is the same answer over the same one.",
        ("eval", "--said", "approve-budget", "--at", "d5"),
    ),
    Beat(
        "21",
        "The capital plan",
        "A second question pending under B1, alongside beat 17's. Two questions in "
        "flight is what makes beat 23's computed set a set rather than a singleton.",
        ("eval", "--said", "approve-capital-plan", "--at", "b21"),
    ),
    Beat(
        "24",
        "The first decision, re-asked from the end of the record",
        "The past is recomputable under the law in force then: still affirmed, still "
        "under A1, asked from a position where A1 is no longer the law.",
        ("eval", "--said", "open-bank-account", "--at", "d9"),
    ),
    Beat(
        "25",
        "Refold the whole log in permuted arrival order",
        "Binding at custos-4.2.md:3101, and one command. The same committed bytes in "
        "a different arrival order fold to a byte-identical Constitution.",
        ("replay", "--at", "board-seated"),
    ),
)

#: What to drop, in order, if the clock runs out in the room. The script's own
#: list, kept here so the decision is made now rather than at the lectern:
#: beat 12 first, since 14 recomputes the fold's answer anyway and kernel 4
#: survives on 8 and 14 alone; then 17, at the cost of the cleanest statement
#: that the NEXT answer changes; then 10, which collapses kernel 2 to a narrated
#: sentence and is expensive, because rule 2 is the half nobody guesses; then 13,
#: demo 1's centerpiece, and only if desperate.
CUT_ORDER = ("12", "17", "10", "13")

PARTS = ("opener", "live", "leave-behind", "full")


def _sequence(part: str) -> tuple[Beat, ...]:
    if part == "opener":
        return OPENER
    if part == "live":
        return LIVE
    if part == "leave-behind":
        return LEAVE_BEHIND
    return OPENER + LIVE + LEAVE_BEHIND


def _named(identifier: str) -> Beat:
    """The beat that identifier names, or a refusal naming the ones that exist."""
    for beat in OPENER + LIVE + LEAVE_BEHIND:
        if beat.id == identifier:
            return beat
    raise LABEL_UNKNOWN(
        label=identifier,
        known=", ".join(beat.id for beat in OPENER + LIVE + LEAVE_BEHIND),
    )


def _kernel_of(beat: Beat) -> Kernel | None:
    """The kernel a beat opens, or ``None`` where it does not open one."""
    for kernel in KERNELS:
        if kernel.beats and kernel.beats[0].id == beat.id:
            return kernel
    return None


def walk2(
    console: Console,
    *,
    part: str = "live",
    beat: str | None = None,
    pause: bool = True,
    substrate: str = FACADE,
    store: Path | None = None,
) -> int:
    """Walk one part of demo 2, echoing each command and running it.

    The opener defaults to keripy and the live part to whatever the caller asked
    for. That is not a convenience: the opener's job is the this-is-really-KERI
    claim, with real prefixes on screen, and a recorded opener that ran on the
    facade would make the claim in words while showing the opposite.
    """
    from utina.cli.app import run

    backend = KERIPY if part == "opener" and substrate == FACADE else substrate
    sequence = _sequence(part) if beat is None else (_named(beat),)
    status = 0
    since = ""
    for index, one in enumerate(sequence):
        kernel = _kernel_of(one)
        if kernel is not None:
            for line in _kernel_card(kernel, console.style):
                console.out.write(line + "\n")
        # What the record committed while nobody was looking, before the beat that
        # arrives at the far end of it. A command like any other, because this module
        # computes nothing (this.i @cldemo, @eelnh6dn) — so the span is read off the
        # beats' own argv and handed to `utina meanwhile` to answer.
        upto = coordinate_of(one)
        if since and upto and since != upto:
            span = ("meanwhile", "--from", since, "--to", upto)
            status = max(status, run(span + _backend_argv(backend, store), console))
        since = upto or since
        argv = one.argv + _backend_argv(backend, store)
        for line in _announce(one, argv, console.style):
            console.out.write(line + "\n")
        # A beat whose refusal IS the beat prints it into the transcript rather
        # than onto the error stream. Beat 14's whole content is the toolchain
        # declining, and a recording that carried it on a separate stream would
        # show the demo's best moment out of order or not at all.
        where = replace(console, err=console.out) if one.refuses else console
        outcome = run(argv, where)
        status = max(status, 0 if one.refuses else outcome)
        if pause and index < len(sequence) - 1:
            console.pause()
    return status


def coordinate_of(beat: Beat) -> str:
    """The label this beat asks its question at, or ``""`` where it asks at none.

    Read off the beat's own ``argv`` rather than held in a second field beside it. A
    ``--at`` duplicated into a ``Beat.at`` would be two literals free to disagree, and
    the failure that buys is a meanwhile card describing a span the beat is not asked
    at (``this.i`` @eelnh6dn).

    Beat 14 is the one with no coordinate: an endorsement the toolchain refuses is not
    asked anywhere, so the span carries the previous beat's coordinate forward rather
    than resetting — which is right, because nothing on that beat moved the record.
    """
    argv = beat.argv
    if "--at" not in argv:
        return ""
    return argv[argv.index("--at") + 1]


def _backend_argv(substrate: str, store: Path | None) -> tuple[str, ...]:
    """The backend flags a beat inherits, written only when they say something."""
    argv = () if substrate == FACADE else ("--substrate", substrate)
    return argv if store is None else (*argv, "--store", str(store))


def _kernel_card(kernel: Kernel, style: Style) -> list[str]:
    """The card that opens a kernel: what the room expects, and what happens.

    The two labels are painted and the two claims are not, because the claims are the
    thing being read and a label is where to look. `expects` and `happens` are a
    contradiction the kernel is about to resolve, and neither side of it is a governance
    verdict, so neither takes a semantic color.
    """
    return [
        "",
        "",
        "",
        MARGIN + style.paint(RULE, SCAFFOLD),
        f"{MARGIN}{style.strong('KERNEL')}  {kernel.title}",
        *_claim(style, "expects", kernel.expects),
        *_claim(style, "happens", kernel.happens),
    ]


def _claim(style: Style, label: str, text: str) -> list[str]:
    """One of a kernel card's two claims, wrapped, with its label painted after the wrap.

    Painting before the wrap would put the escape sequence's bytes into ``textwrap``'s
    width budget and could split one across lines, which is the same constraint
    ``render.wrapped`` documents.
    """
    lines = textwrap.wrap(
        f"{label}: {text}",
        width=WRAP,
        initial_indent=MARGIN,
        subsequent_indent=MARGIN + "  ",
    )
    cut = len(MARGIN) + len(label) + 1
    head = MARGIN + style.paint(f"{label}:", SCAFFOLD) + lines[0][cut:]
    return [head, *lines[1:]]


def _announce(beat: Beat, argv: tuple[str, ...], style: Style) -> list[str]:
    """The card that introduces a beat, and the command as though it were typed.

    Chrome, not content: a scaffolding rule, a bold ``BEAT`` tag, prose narration, and
    the echoed command bold behind a scaffolding prompt, so a room scanning for where the
    next command starts finds the one bright line. Nothing on the card carries a
    governance meaning, so nothing on it takes a semantic color.
    """
    # Three blank lines above the rule, not one. A beat card describes the screen
    # BELOW it, and with one line of air the card sat as close to the previous
    # beat's ground block as to its own command — so a reader scanning a scrollback
    # had to work out which way the narration pointed (Daniel, after giving it).
    return [
        "",
        "",
        "",
        MARGIN + style.paint(RULE, SCAFFOLD),
        f"{MARGIN}{style.strong(f'BEAT {beat.id:<6}')}{beat.title}",
        *textwrap.wrap(
            beat.narration, width=WRAP, initial_indent=MARGIN, subsequent_indent=MARGIN
        ),
        "",
        f"{MARGIN}{style.paint('$', SCAFFOLD)} {style.strong('utina ' + ' '.join(argv))}",
        "",
    ]
