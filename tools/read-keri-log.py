"""Read a key log utina wrote, using keripy and nothing of utina's.

This is the only claim in the repository that utina's own test suite cannot
make. Everywhere else, the thing computing the answer and the thing checking it
share a codebase; here they do not. Point this at the store left behind by

    utina demo --substrate keripy --store DIR --no-pause

and it opens that LMDB environment read-only with a bare ``keri.db.basing.Baser``
— no keystore, no Habery, no utina import anywhere — walks every key log in it,
prints each event's literal bytes, re-derives each event's own SAID to check the
digests hold, and reports the seals. Given ``--expect SAID`` it says which
establishment event anchors that digest, which is beat D4's whole assertion:
Acme's board-seating amendment rides a rotation.

Usage:
    uv run python tools/read-keri-log.py DIR [--expect SAID]

Exit status is 0 if the log read cleanly and any expected anchor was found, and
1 otherwise, so it is usable as a check rather than only as a demonstration.
"""

import argparse
import sys

from keri.core import serdering
from keri.db import basing

#: The name utina files its keystore and event database under.
STORE_NAME = "utina"


def rederives(serder) -> bool:
    """Whether an event's own identifier really is the digest of the event.

    Re-parsed from the stored bytes through keripy's own verifying constructor,
    which re-derives every self-addressing field the event carries — for a
    self-addressing inception that is the prefix as well as the SAID, since
    there the two are the same digest. A tampered byte anywhere in the log
    fails here rather than being reported as a fact.
    """
    try:
        again = serdering.SerderKERI(raw=bytes(serder.raw), verify=True)
    except Exception:
        return False
    return bool(again.said == serder.said and again.pre == serder.pre)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("store", help="the directory utina --store was pointed at")
    parser.add_argument("--expect", metavar="SAID", help="a digest that should be anchored")
    args = parser.parse_args(argv)

    db = basing.Baser(
        name=STORE_NAME,
        base="",
        headDirPath=args.store,
        temp=False,
        reopen=True,
        readonly=True,
    )

    logs: dict[str, list[object]] = {}
    for keys, serder in db.evts.getTopItemIter():
        logs.setdefault(keys[0], []).append(serder)

    if not logs:
        print(f"no key log found under {args.store}", file=sys.stderr)
        return 1

    anchors: dict[str, tuple[str, str]] = {}
    digests_hold = True

    for prefix in sorted(logs):
        events = sorted(logs[prefix], key=lambda serder: serder.sn)
        print(f"\nKEL {prefix}  ({len(events)} events)")
        for serder in events:
            derived = rederives(serder)
            digests_hold = digests_hold and derived
            print(f"  sn {serder.sn}  {serder.ilk}  {serder.said}  said re-derives: {derived}")
            print(f"    {bytes(serder.raw).decode()}")
            for seal in serder.sad.get("a") or ():
                sealed = seal.get("d")
                if sealed:
                    anchors[sealed] = (prefix, serder.said)
                    print(f"    ANCHORS {sealed}")

    print(f"\n{len(anchors)} anchored digest(s); every SAID re-derives: {digests_hold}")

    if args.expect:
        found = anchors.get(args.expect)
        if found is None:
            print(f"NOT FOUND: nothing in this log anchors {args.expect}", file=sys.stderr)
            return 1
        prefix, establishment = found
        print(f"\nFOUND  {args.expect}")
        print(f"  anchored by establishment event {establishment}")
        print(f"  in the key log of {prefix}")

    return 0 if digests_hold else 1


if __name__ == "__main__":
    raise SystemExit(main())
