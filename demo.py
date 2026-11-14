"""
demo.py - the whole claim in one run.

    python demo.py

Prints, in order:
  1. the policy a human set before the agent ran,
  2. four spend attempts and the gate's verdict on each,
  3. the NEAR key that enforces the same budget on chain,
  4. the receipt ledger, verified.

No network. No keys. Runs in under a second.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from ledger import Ledger
from near_wallet import build_function_call_key, describe, human, near
from policy import Refusal, SpendGate, SpendPolicy, SpendRequest

LEDGER = Path(__file__).with_name("receipts.jsonl")
API_SELLER = "data.market.near"
SHADY = "unknown.seller.near"


def main() -> int:
    if LEDGER.exists():
        LEDGER.unlink()

    ledger = Ledger(LEDGER)

    # 1. THE HUMAN SETS THE BOUNDARY. The agent cannot change this.
    policy = SpendPolicy(
        budget=near(0.50),
        recipients=(API_SELLER,),
        require_evidence=True,
    )
    gate = SpendGate(policy)

    print("=" * 72)
    print("1. POLICY  (set by the human, before the agent ran)")
    print("=" * 72)
    print(f"   budget      : {human(policy.budget)}")
    print(f"   counterparty: {', '.join(policy.recipients)}")
    print(f"   evidence    : {'required' if policy.require_evidence else 'not required'}")
    print()

    # 2. THE AGENT ASKS. Four requests, three of which must fail.
    attempts = [
        (
            "buy a labelled dataset",
            SpendRequest(
                amount=near(0.20),
                recipient=API_SELLER,
                purpose="buy the labelled radiograph dataset, 2,000 images",
                evidence="invoice #4471 from data.market.near",
            ),
        ),
        (
            "buy a premium tier, no receipt",
            SpendRequest(
                amount=near(0.10),
                recipient=API_SELLER,
                purpose="upgrade to premium tier for faster responses",
                evidence=None,
            ),
        ),
        (
            "buy from an unknown seller",
            SpendRequest(
                amount=near(0.05),
                recipient=SHADY,
                purpose="buy the same dataset cheaper from another seller",
                evidence="screenshot of a price",
            ),
        ),
        (
            "spend past the budget",
            SpendRequest(
                amount=near(0.40),
                recipient=API_SELLER,
                purpose="buy a second dataset for the same project",
                evidence="invoice #4488 from data.market.near",
            ),
        ),
    ]

    print("=" * 72)
    print("2. SPEND ATTEMPTS")
    print("=" * 72)
    for label, req in attempts:
        detail = ""
        try:
            remaining = gate.spend(req)
            verdict = f"ALLOW  -> remaining {human(remaining)}"
            ledger.append(
                {
                    "type": "spend_approved",
                    "amount": req.amount,
                    "recipient": req.recipient,
                    "purpose": req.purpose,
                    "evidence": req.evidence,
                }
            )
        except Refusal as exc:
            verdict = f"REFUSE -> {exc.code}"
            detail = exc.detail
            ledger.append(
                {
                    "type": "spend_refused",
                    "amount": req.amount,
                    "recipient": req.recipient,
                    "purpose": req.purpose,
                    "code": exc.code,
                    "detail": exc.detail,
                }
            )
        print(f"   {label:32s} {verdict}")
        if detail:
            print(f"   {'':32s}   {detail}")
    print()

    # 3. THE SAME BUDGET, ENFORCED BY THE CHAIN INSTEAD OF BY PYTHON.
    key = build_function_call_key(
        allowance_yocto=policy.budget,
        receiver_id=API_SELLER,
        method_names=["pay"],
    )
    print("=" * 72)
    print("3. NEAR FUNCTION CALL KEY  (same budget, now unbreakable)")
    print("=" * 72)
    print(f"   {describe(key)}")
    print()
    print("   raw payload:")
    print(json.dumps(key, indent=2).replace("\n", "\n   "))
    print()

    # 4. RECEIPTS.
    ok, msg = ledger.verify()
    print("=" * 72)
    print("4. RECEIPT LEDGER")
    print("=" * 72)
    print(f"   rows      : {ledger.count()}")
    print(f"   chain     : {'INTACT' if ok else 'BROKEN'} - {msg}")
    print(f"   summary   : {gate.report()}")
    print()
    print("RESULT:", "PASS" if ok and gate.spent == near(0.20) else "FAIL")
    return 0 if ok and gate.spent == near(0.20) else 1


if __name__ == "__main__":
    sys.exit(main())
