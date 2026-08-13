# utina

**A Custos evaluation engine.** It computes a governed domain's Constitution from that
domain's committed logs, and answers, for any position in the log, whether a decision
holds — returning a finding that carries its ground.

[Custos](https://github.com/Nicholas-Keystate/custos) specifies *Governed Autonomic
Replayable Domains*: KERI-based domains whose law is committed to a governance event log,
and whose judgment is **computed** from that log rather than asserted by a judge. The
property it promises is replayable governance — any stranger holding the logs computes the
same Constitution, the same findings, the same refusals.

utina is an implementation built to be **useful**. Its sibling
[thesmo](https://github.com/bakobo/thesmo) is built to be *blind*, as an instrument for
finding where the specification underdetermines a conforming engine; utina inherits
thesmo's readings and spends them on a working engine instead of on a defect register.

## The name

*utina*, from εὔθυνα (*euthyna*) — the audit every Athenian magistrate faced at the end of
their term, the "setting straight." It is the closest ancient word for what this does: any
past decision can be recomputed and checked, under the law that was in force when it was
made.

## What it does

```python
from utina.fold import Corpus, Constitution, evaluate

corpus = Corpus.load(...)                     # committed evidence: the logs
law    = Constitution.at(corpus, position)    # the law in force, and who holds what standing
finding = evaluate(corpus, question, at=position)
```

A finding is one of four values and each carries its ground: **affirmed** with the evidence
and clauses it rested on, **defeated** with the citation that defeats it, **pending** with
the typed requirement that would discharge it, and **self-convicted** with the proof from
the subject's own committed bytes. Where no committed rule makes a question evaluable at
all, the engine **refuses** and names what is missing, rather than legislating the gap.

Two planes, and no object performs both. `utina.fold` reads and computes; it writes
nothing and imports no KERI library, enforced by a test. `utina.enact` is the
constructor's verb — it produces committed events. `utina.substrate` holds everything
KERI-facing behind one interface.

## Two substrates, one engine

That interface has two implementations, and the same suite runs against both. The
default is a pure-Python facade: deterministic, dependency-free, and honest that its
signatures are keyed MACs rather than public-key signatures. `--substrate keripy` swaps
in [keripy](https://github.com/bakobo/keripy), and then every identifier is a real KERI
prefix, every digest is Blake3-256 over KERI's own JSON, every signature is Ed25519, and
the board-seating amendment is anchored by a seal in a real rotation.

```sh
uv run utina demo --no-pause                                    # the facade
uv run utina demo --substrate keripy --no-pause                 # real KERI
uv run utina log --substrate keripy --store /tmp/acme-kel       # leave the key log on disk
uv run python tools/read-keri-log.py /tmp/acme-kel              # read it with keripy alone
```

The last of those imports no utina code. It is the only claim in this repository that
utina's own tests cannot make.

Nothing above `utina/substrate/keri*.py` may import a KERI library, so `--substrate
facade` loads none of it; `tests/test_purity.py` enforces that by reading the source
rather than by trusting the convention.

## Status

**Pre-alpha, under active construction.** The working demo models a company that starts
with two founders under unanimity and amends itself into a board of three under a
two-of-three threshold — see [`docs/demo-script.md`](docs/demo-script.md), which is the
acceptance oracle before it is a demo.

## From a fresh clone

```sh
uv sync
uv run pytest
```

Tests gate at 100% branch coverage.

## License

Apache-2.0. See [`NOTICE`](NOTICE) for the provenance of derived work. The Custos
specification this implements is separately licensed by its author under the Community
Specification License 1.0; utina implements it and does not redistribute it.
