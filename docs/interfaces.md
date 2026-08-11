# The contract

*The seam between utina's parts, fixed before they are built in parallel. If you
are implementing one of these modules, you own the names in your section and you
may assume — never redefine — the names in the others.*

`tests/test_acceptance_oracle.py` is the binding statement of this contract; where
this file and the oracle disagree, the oracle wins and this file is the bug.

Everything under `utina.fold` is pure: no KERI library, no I/O, no clock, no
randomness. Values in, values out.

## Vocabulary

- **AID** — `str`, an identifier. `"acme:marta"` under the facade substrate.
- **SAID** — `str`, a self-addressing digest of committed bytes.
- **Position** — an appraisal coordinate. Opaque to callers; ordered.
- **Act kind** — `str`, e.g. `"open-bank-account"`, `"amend-operating-agreement"`.

## `utina.fold.triple` — the closed three-input type

Custos closes the fold's inputs at exactly three committed values. Nothing else
may influence a result.

```python
@dataclass(frozen=True)
class Position:
    seq: int                      # ordering is by committed coordinate, never arrival
    def __lt__(self, other: Position) -> bool: ...

@dataclass(frozen=True)
class LawHead:
    said: SAID                    # digest of the law in force

@dataclass(frozen=True)
class EvidenceBundle:
    events: tuple[Event, ...]     # committed, in canonical order

@dataclass(frozen=True)
class AppraisalTriple:
    evidence: EvidenceBundle
    law_head: LawHead
    position: Position
```

## `utina.fold.finding` — the four-valued codomain

Each value carries its ground as a component of the type. A value that arrives
without its ground is not a member; constructors enforce this.

```python
class Finding: ...                          # sum type; never instantiated bare

@dataclass(frozen=True)
class Affirmed(Finding):
    clauses: tuple[str, ...]                # clause ids the appraisal ran under
    endorsements: tuple[SAID, ...]          # the endorsements that reached unity
    bundle: SAID

@dataclass(frozen=True)
class Defeated(Finding):
    citation: Citation

@dataclass(frozen=True)
class Pending(Finding):
    requirement: tuple[RequirementElement, ...]   # canonically ordered, non-empty

@dataclass(frozen=True)
class SelfConvicted(Finding):
    proof: Proof

@dataclass(frozen=True)
class Citation:
    clause: str
    declination: Declination | None = None  # set when a signed no defeated it
    reason: str = ""

@dataclass(frozen=True)
class RequirementElement:
    endorser: AID
    clause: str

@dataclass(frozen=True)
class Declination:
    endorser: AID
    said: SAID
```

## `utina.fold.refusal` — not a fifth value

A refusal is an operational fact, not a finding: the evaluator declining an
ill-posed question rather than legislating the missing rule. It is **not** a
subclass of `Finding` and must never appear inside one.

```python
@dataclass(frozen=True)
class Refusal:
    missing: str                  # what the law does not supply, named concretely
    detail: str
```

## `utina.fold.question` — the two constructors

```python
@dataclass(frozen=True)
class Proposal:                   # "may we do this?" — evaluated before the fact
    act: str

@dataclass(frozen=True)
class Committed:                  # "was this act lawful?" — evaluated after
    said: SAID

Question = Proposal | Committed
```

## `utina.fold.group` — slot groups, the shape of a composition rule

Structurally isomorphic to the dossier specification's threshold operators, but
Acme's own committed law (`this.i` @ta7vle). Weights are exact rationals —
`fractions.Fraction`, never float, because unity must be decidable.

```python
class Disposition(StrEnum):
    PENDING = "pending"           # no signed act; contributes nothing
    ENDORSED = "endorsed"         # signed, disp="endorse"; weight counts
    DECLINED = "declined"         # signed, disp="decline"; spends the slot

@dataclass(frozen=True)
class Slot:
    endorser: AID
    weight: Fraction

@dataclass(frozen=True)
class Group:
    operator: str                 # "MxN"
    slots: tuple[Slot, ...]
    def satisfied_by(self, endorsers: AbstractSet[AID]) -> bool: ...
    def reachable(self, dispositions: Mapping[AID, Disposition]) -> bool: ...
```

`satisfied_by` is the convenience form used by tests and the CLI: the endorsed
weights of the named endorsers sum to at least 1. `reachable` answers whether
unity is *still attainable* given what has been spent — a declined slot's weight
is gone. Q1 in `custos-questions.md` records that Custos does not say which
finding an unreachable threshold produces; we pin `Defeated`.

## `utina.fold.clause` / `utina.fold.constitution`

```python
@dataclass(frozen=True)
class Clause:
    id: str                       # "A1", "B2"
    governs: tuple[str, ...]      # act kinds this clause rules
    group: Group

@dataclass(frozen=True)
class Constitution:
    law_head: LawHead
    clauses: tuple[Clause, ...]
    @classmethod
    def at(cls, corpus: Corpus, position: Position) -> Constitution: ...
    def clause(self, id: str) -> Clause: ...
    def governing(self, act: str) -> Clause | None: ...   # None => refusal
    def canonical_bytes(self) -> bytes: ...
```

`canonical_bytes` is what makes replay checkable: the same committed inputs must
produce the same bytes, and a stream in permuted arrival order must fold to a
byte-identical Constitution. Order clause sub-blocks lexicographically by clause
SAID; that concatenation order is ours to choose and Custos says so.

## `utina.fold.corpus` — committed evidence and its canonical order

```python
@dataclass(frozen=True)
class Event:
    said: SAID
    kind: str                     # "inception" | "enactment" | "endorsement" | "act"
    position: Position
    body: Mapping[str, object]    # committed payload; opaque to the walk

class Corpus:
    @classmethod
    def load(cls, events: Iterable[Event]) -> Corpus: ...
    def upto(self, position: Position) -> tuple[Event, ...]: ...   # canonical order
    def event(self, said: SAID) -> Event | None: ...
```

The walk derives its order from committed bytes alone — anchoring order first,
then intra-anchor order as the anchoring event states. Arrival order, storage
order and any ambient sequence are forbidden inputs.

## The law body — the other silent seam

`utina.acme` writes the committed law and `utina.fold.constitution` reads it. Same hazard
as the endorsement body: disagree on a key and the Constitution folds to nothing, with no
error. This shape is authoritative.

```python
{"clauses": [
    {"id": "A1",
     "governs": ["open-bank-account", "hire-vp-sales", ...],
     "group": {"operator": "MxN",
               "slots": [{"endorser": "acme:marta", "weight": "1/2"},
                         {"endorser": "acme:dev",   "weight": "1/2"}]}},
    ...
]}
```

`weight` is a **string** in the committed body — `"1/2"`, `"1/3"` — parsed to
`fractions.Fraction` on the way in. A float in committed bytes would make canonical bytes
platform-dependent and unity undecidable, which defeats the replay property outright.

**An amendment replaces the law; it does not add to it.** The clause set in force at a
position is the one the most recent enactment committed, not the union of every enactment
so far. Under the additive reading A1 and B1 would both govern ordinary acts and
`governing()` would have two answers — see QL4 in the questions register. Custos does not
settle it; utina pins replacement.

## `utina.fold.evaluate` — the entry point

```python
def evaluate(corpus: Corpus, question: Question, *, at: Position) -> Finding | Refusal: ...
```

Order of operations, and it matters:

1. Find the governing clause. **No governing clause is a `Refusal`**, not a
   finding — the law is silent, so the question is not evaluable.
2. Build the question's complete requirement space from that clause. Never
   short-circuit: no finding is terminal while an enumerated check sits
   unexamined, so compute the whole space before returning anything.
3. Classify every slot's disposition from committed evidence at or before `at`.
4. If the endorsed weights reach unity — `Affirmed`.
5. Else if unity is unreachable — `Defeated`, citing the declination that spent
   the slot.
6. Else — `Pending`, with the outstanding slots as typed requirement elements,
   canonically ordered.

## `utina.substrate` — the facade

One protocol; the demo runs a pure-Python backend and keripy arrives later as a
second implementation of the same protocol.

```python
class Substrate(Protocol):
    def said(self, body: Mapping[str, object]) -> SAID: ...
    def sign(self, aid: AID, body: Mapping[str, object]) -> str: ...
    def verify(self, aid: AID, body: Mapping[str, object], signature: str) -> bool: ...
    def incept(self, alias: str) -> AID: ...
    def rotate(self, aid: AID, anchor: SAID) -> Event: ...
```

`rotate` exists because Custos binds law-amending enactments to anchor in an
establishment event: Acme's board-seating amendment rides a rotation.

## The endorsement body — field names are contract, not preference

An endorsement's field names are load-bearing across the enact/slots seam: if the writer
and the predicate disagree on a name, every slot silently reads PENDING and every decision
is pending forever. Names are the dossier specification's, so the later move to real ACDC
endorsements is a re-encoding rather than a rename.

```python
{"i": AID,          # issuer — the endorser, and the slot's expected party
 "disp": str,       # "endorse" | "decline"
 "act": str,        # "issue" | "revoke"
 "said": SAID}      # the subject: the decision this endorsement is about
```

A slot is ENDORSED only when a committed, signed endorsement carries `i` equal to the
slot's endorser, `disp == "endorse"`, `act == "issue"`, and `said` equal to the subject.
Anything else — including anything unverifiable — is PENDING. `disp == "decline"` with a
matching `i` and `said` is DECLINED.

## `utina.enact` — the constructor's verb

```python
class Constructor:
    def __init__(self, substrate: Substrate, gaid: AID) -> None: ...
    def incept_domain(self, founding_law: Mapping[str, object]) -> Event: ...
    def enact_amendment(self, law: Mapping[str, object]) -> Event: ...
    def propose(self, act: str) -> Event: ...
    def endorse(self, aid: AID, subject: SAID) -> Event: ...
    def decline(self, aid: AID, subject: SAID) -> Event: ...
```

Nothing here judges, and nothing in `utina.fold` writes.

## Errors

Every raised error uses a `bakobo.errors.ErrorCode` declared as a module-scope
literal, `<sorter>.<descriptor>[.<sub>].<disposition>`, classified by the
obstacle rather than by the component, disposition trailing. Reserve this branch:

`bakobo.errors` enforces a **closed descriptor set** — `env`, `feature`, `grant`, `id`,
`input`, `party`, `proof`, `rule`, `self`, `state` — and requires at least one
sub-descriptor. `e.law.*` and a bare `e.input.malformed.f` are both refused at import.
Governance rules live under `rule`.

| Code | Meaning |
|---|---|
| `e.input.event-malformed.f` | committed bytes will not parse as the event they claim to be |
| `e.state.ground-missing.f` | a finding was constructed without its ground |
| `e.state.order-ambient.f` | the walk was asked to consume an uncommitted order |
| `e.rule.clause-unknown.f` | a clause id that the law in force does not define |

A refusal is **not** an error and never raises.
