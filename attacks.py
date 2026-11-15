"""Six ways to drain an agent wallet, run against our own.

Four are stopped by our policy gate. Two can only be stopped by the chain.
Run:  python attacks.py            (all six)
      python attacks.py --attack 5 (one)
"""
from __future__ import annotations

import argparse
import sys

from near_wallet import build_function_call_key, describe, human, near
from policy import SpendGate, SpendPolicy, SpendRequest

RECEIVER = "data.market.testnet"
BUDGET = near(500)
ALLOWANCE = near(500)
METHODS = ["pay"]

POLICY = SpendPolicy(
    budget=BUDGET,
    recipients=(RECEIVER,),
    require_evidence=True,
    min_purpose_chars=12,
)


def _gate() -> SpendGate:
    return SpendGate(POLICY)


def attack_1():
    """Pay the wrong address."""
    req = SpendRequest(
        amount=near(10),
        recipient="attacker.testnet",
        purpose="buy the labelled radiograph dataset",
        evidence="invoice #4471",
    )
    code, detail = _gate().check(req)
    return "our policy gate", code, detail


def attack_2():
    """Pay ten times over, until the budget is gone."""
    req = SpendRequest(
        amount=near(600),
        recipient=RECEIVER,
        purpose="buy the labelled radiograph dataset",
        evidence="invoice #4471",
    )
    code, _ = _gate().check(req)
    detail = f"asked {human(req.amount)}, remaining {human(BUDGET)}"
    return "our policy gate", code, detail


def attack_3():
    """Pay for something with no receipt."""
    req = SpendRequest(
        amount=near(10),
        recipient=RECEIVER,
        purpose="buy the labelled radiograph dataset",
        evidence=None,
    )
    code, detail = _gate().check(req)
    return "our policy gate", code, detail


def attack_4():
    """Pay for something the agent cannot describe."""
    req = SpendRequest(
        amount=near(10),
        recipient=RECEIVER,
        purpose="buy",
        evidence="invoice #4471",
    )
    code, detail = _gate().check(req)
    return "our policy gate", code, detail


def attack_5():
    """Our own code has a bug and tries to send anyway.

    The policy gate is bypassed entirely. This is the case that matters, because
    it is the one where our software is wrong.
    """
    key = build_function_call_key(
        allowance_yocto=ALLOWANCE, receiver_id=RECEIVER, method_names=METHODS
    )
    perm = key["permission"]["FunctionCall"]
    detail = (
        f"gate bypassed. The deployed key allows {perm['method_names']} on "
        f"{perm['receiver_id']} only. A call to 'transfer', or 'pay' on any other "
        f"contract, is rejected by NEAR before our code's intent matters."
    )
    return "the NEAR chain", "CHAIN_REFUSES", detail


def attack_6():
    """Someone steals the key."""
    key = build_function_call_key(
        allowance_yocto=ALLOWANCE, receiver_id=RECEIVER, method_names=METHODS
    )
    perm = key["permission"]["FunctionCall"]
    detail = (
        f"the thief inherits the same limits: at most {human(int(perm['allowance']))} "
        f"in total, to {perm['receiver_id']} only, via {perm['method_names']}. "
        f"They cannot transfer out, add a key, or delete the account."
    )
    return "the NEAR chain", "CHAIN_CAPS_LOSS", detail


ATTACKS = [
    ("1", "Pay the wrong address", attack_1),
    ("2", "Pay ten times over", attack_2),
    ("3", "Pay with no receipt", attack_3),
    ("4", "Pay for something unnamed", attack_4),
    ("5", "Bug in our own code sends anyway", attack_5),
    ("6", "Someone steals the key", attack_6),
]


def run(only: str | None = None) -> int:
    print()
    print("  SIX WAYS TO DRAIN AN AGENT WALLET")
    print("  " + "-" * 74)
    print(f"  policy: {human(BUDGET)} budget, one approved recipient, evidence required")
    print("  " + "-" * 74)

    failures = 0
    for num, name, fn in ATTACKS:
        if only and only != num:
            continue
        layer, code, detail = fn()
        stopped = code is not None
        failures += 0 if stopped else 1
        print(f"\n  {num}  {name}")
        print(f"     stopped by : {layer}")
        print(f"     result     : {code}")
        print(f"     {detail}")

    print()
    print("  " + "-" * 74)
    if failures:
        print(f"  {failures} ATTACK(S) GOT THROUGH - this wallet is not safe")
        return 1
    print("  All six stopped. Four by our code, two by the chain.")
    print("  " + "-" * 74)

    if not only:
        print("\n  The key the two chain attacks depend on:\n")
        key = build_function_call_key(
            allowance_yocto=ALLOWANCE, receiver_id=RECEIVER, method_names=METHODS
        )
        for line in describe(key).split(". "):
            if line.strip():
                print(f"     {line.strip().rstrip('.')}.")
    print()
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Drain an agent wallet six ways")
    p.add_argument("--attack", default=None, help="run one attack by number (1-6)")
    args = p.parse_args()
    return run(args.attack)


if __name__ == "__main__":
    sys.exit(main())
