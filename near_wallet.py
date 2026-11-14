"""
near_wallet.py - the part that makes the budget survive the model.

WHY THIS IS DIFFERENT FROM AN "AGENT WALLET":
    Most agent-wallet projects put a spending limit in the prompt, or in the
    application code, or in a dashboard. All three are soft: they live in the
    same process the model can talk its way around.

    NEAR has a native primitive that is not soft - a FUNCTION CALL ACCESS KEY.
    It is an on-chain key that:
      * can only call named methods on one named contract,
      * carries a hard allowance that the CHAIN subtracts from,
      * and cannot transfer, add keys, or delete the account.

    So the budget is not a rule the agent follows. It is a boundary the agent
    physically cannot cross. That is the whole thesis, and it is why the limit
    belongs on chain rather than in a system prompt.

This module builds and validates that key spec. It does not hold secrets.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

YOCTO_DEC = Decimal(10) ** 24   # 1 NEAR == 10**24 yoctoNEAR
YOCTO = 10 ** 24


def near(amount: float | str | Decimal) -> int:
    """Convert NEAR to yoctoNEAR exactly, or refuse.

    Uses Decimal, never float: 0.5 * 10**24 overflows float precision and
    silently lands on 499999999999999991611392 instead of 5e23. In a money
    module that is the difference between a budget and a leak.
    """
    try:
        d = Decimal(str(amount))
    except InvalidOperation as exc:
        raise ValueError(f"{amount!r} is not a decimal number") from exc
    if d <= 0:
        raise ValueError(f"{amount!r} must be greater than zero")
    yocto = int(d * YOCTO_DEC)
    if Decimal(yocto) / YOCTO_DEC != d:
        raise ValueError(f"{amount!r} NEAR is not representable exactly in yoctoNEAR")
    return yocto


def human(yocto: int) -> str:
    return f"{Decimal(yocto) / YOCTO_DEC:.6f} NEAR"


def build_function_call_key(
    *, allowance_yocto: int, receiver_id: str, method_names: list[str]
) -> dict:
    """Build the access-key payload NEAR expects for a policy-bound wallet.

    Mirrors the documented shape:
        {"type": "function_call",
         "permission": {"FunctionCall": {"allowance": "<yocto>",
                                         "receiver_id": "<account>",
                                         "method_names": ["<method>", ...]}}}
    """
    if allowance_yocto <= 0:
        raise ValueError("allowance must be greater than zero")
    if not receiver_id:
        raise ValueError("receiver_id is required")
    if not method_names:
        raise ValueError("at least one method name is required")
    if any(not m or " " in m for m in method_names):
        raise ValueError("method names must be non-empty and contain no spaces")

    return {
        "type": "function_call",
        "permission": {
            "FunctionCall": {
                "allowance": str(allowance_yocto),
                "receiver_id": receiver_id,
                "method_names": list(method_names),
            }
        },
    }


def assert_valid_key_spec(spec: dict) -> None:
    """Fail closed if the spec would grant more than the policy allows."""
    if spec.get("type") != "function_call":
        raise ValueError("refusing: key is not a function_call key")

    perm = spec.get("permission", {}).get("FunctionCall")
    if not perm:
        raise ValueError("refusing: no FunctionCall permission present")

    allowance = perm.get("allowance")
    if not isinstance(allowance, str) or not allowance.isdigit():
        raise ValueError("refusing: allowance must be a digit string")
    if int(allowance) <= 0:
        raise ValueError("refusing: allowance is zero or negative")

    if not perm.get("receiver_id"):
        raise ValueError("refusing: receiver_id missing - key would be unscoped")

    methods = perm.get("method_names")
    if not methods:
        raise ValueError("refusing: no method_names - key could call anything")
    if any(m in ("*", "transfer", "add_key", "delete_key") for m in methods):
        raise ValueError(
            "refusing: key grants transfer/add_key/delete_key - that is full access"
        )

    # A full-access key is the failure mode this module exists to prevent.
    if spec.get("type") == "full_access":
        raise ValueError("refusing: full access key")


def describe(spec: dict) -> str:
    """One line a judge can read without knowing NEAR."""
    assert_valid_key_spec(spec)
    perm = spec["permission"]["FunctionCall"]
    methods = ", ".join(perm["method_names"])
    return (
        f"policy-bound key: may call [{methods}] on {perm['receiver_id']} only, "
        f"and may spend at most {human(int(perm['allowance']))} in total. "
        f"The chain subtracts from that allowance and stops the key at zero."
    )
