#!/usr/bin/env python3
"""semveto-verify: checks a daily seal of SEMVETO (50 v0.2 §2) against a copy of the ledger, without trusting Azure
or the authors. Standard library only; it does not import the engine.

    python semveto_verify.py --manifest manifiesto_2026-11-10.json --system base --ledger-dir <events> [--ots FILE]

1. The chain of the ledger is recomputed from its genesis up to the event of the manifest: every event's hash is the
   SHA-256 of its canonical JSON without the field "hash" (sorted keys, no spaces, UTF-8), and every prev_hash is the
   hash of the event before (the first: "GENESIS"). The count, event_id and hash must be the manifest's.
2. The SHA-256 of the manifest is computed: it is what the OpenTimestamps proof commits to.
3. The proof (FILE, by default the manifest's name + ".ots", or "-bitcoin.ots" when present) is checked with the
   OpenTimestamps client if it is installed (`ots verify`, which needs a Bitcoin Core node; a pruned one is fine).
   Without it, the tool says how to check it on https://opentimestamps.org (upload the proof and the manifest).

Exit codes: 0 the ledger matches the manifest (and the proof verified, if it could be checked); 1 a mismatch;
2 usage; 3 the ledger matches but the proof could not be checked here.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

GENESIS = "GENESIS"


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def head_at(ledger_dir: Path, n_target: int) -> tuple[int, str | None, str | None, str | None]:
    """(events read, event_id and hash of event n_target, error): the chain checked up to that event."""
    prev, n = None, 0
    for path in sorted(ledger_dir.glob("events_*.jsonl")):
        with open(path, "rb") as f:
            for lineno, raw in enumerate(f, start=1):
                if not raw.endswith(b"\n"):
                    return n, None, None, f"{path.name}:{lineno}: incomplete line"
                e = json.loads(raw)
                expected = GENESIS if prev is None else prev
                if e.get("prev_hash") != expected:
                    return n, None, None, f"{path.name}:{lineno}: prev_hash does not follow the chain"
                body = {k: v for k, v in e.items() if k != "hash"}
                if hashlib.sha256(canonical(body)).hexdigest() != e.get("hash"):
                    return n, None, None, f"{path.name}:{lineno}: the event's content does not give its hash"
                prev, n = e["hash"], n + 1
                if n == n_target:
                    return n, e.get("event_id"), e["hash"], None
    return n, None, None, f"the ledger has {n} events, fewer than the manifest's {n_target}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="semveto-verify", description=__doc__.split("\n\n")[0])
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--system", required=True, help="base or A, as in the manifest")
    ap.add_argument("--ledger-dir", type=Path, required=True, help="the directory of events_*.jsonl")
    ap.add_argument("--ots", type=Path, help="the proof (default: next to the manifest)")
    args = ap.parse_args(argv)
    data = args.manifest.read_bytes()
    m = json.loads(data)
    s = (m.get("systems") or {}).get(args.system)
    if s is None:
        print(f"the manifest has no system {args.system!r}: {sorted(m.get('systems') or {})}", file=sys.stderr)
        return 2
    n, event_id, h, error = head_at(args.ledger_dir, int(s["n_events"]))
    if error or event_id != s["event_id"] or h != s["hash"]:
        print(f"MISMATCH: {error or 'the event of the manifest is not the ledger event ' + str(n)}")
        return 1
    print(f"ledger OK: event {n} of the chain is {event_id}, hash {h}")
    print(f"manifest SHA-256: {hashlib.sha256(data).hexdigest()} (the digest the proof commits to)")
    ots = args.ots
    if ots is None:
        bitcoin = Path(str(args.manifest) + "-bitcoin.ots")
        ots = bitcoin if bitcoin.exists() else Path(str(args.manifest) + ".ots")
    if not ots.exists():
        print(f"no proof at {ots}")
        return 3
    if shutil.which("ots") is None:
        print(
            "the OpenTimestamps client is not installed (pip install opentimestamps-client); to check without "
            f"it, upload {ots.name} and {args.manifest.name} to https://opentimestamps.org"
        )
        return 3
    r = subprocess.run(["ots", "verify", "-f", str(args.manifest), str(ots)], capture_output=True, text=True)  # noqa: S603, S607
    print((r.stdout + r.stderr).strip())
    return 0 if r.returncode == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
