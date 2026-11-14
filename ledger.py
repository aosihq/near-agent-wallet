"""
ledger.py - append-only receipts.

Every approved spend and every refusal is written as one JSON line with the
hash of the previous line. Nothing is ever rewritten. If a row is edited or
removed, the chain breaks and `verify()` says so.

This is deliberately boring. A receipt that can be quietly edited is not a
receipt.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

GENESIS = "0" * 64


def _hash(payload: dict, prev: str) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev + body).encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # -- write ------------------------------------------------------------
    def append(self, event: dict) -> dict:
        prev = self.last_hash()
        row = {"seq": self.count(), "prev": prev, "event": event}
        row["hash"] = _hash(row, prev)
        with self.path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    # -- read -------------------------------------------------------------
    def rows(self) -> list[dict]:
        if not self.path.exists():
            return []
        out = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def count(self) -> int:
        return len(self.rows())

    def last_hash(self) -> str:
        rows = self.rows()
        return rows[-1]["hash"] if rows else GENESIS

    def verify(self) -> tuple[bool, str]:
        """Recompute the chain. Returns (ok, message)."""
        prev = GENESIS
        for i, row in enumerate(self.rows()):
            if row.get("seq") != i:
                return False, f"row {i}: sequence gap"
            if row.get("prev") != prev:
                return False, f"row {i}: prev hash does not match"
            expected = _hash(
                {"seq": row["seq"], "prev": row["prev"], "event": row["event"]}, prev
            )
            if row.get("hash") != expected:
                return False, f"row {i}: hash does not recompute - row was edited"
            prev = row["hash"]
        return True, f"chain intact across {len(self.rows())} rows"
