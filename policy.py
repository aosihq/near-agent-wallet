"""
policy.py - the spend gate.

THE CLAIM THIS FILE MAKES:
    An agent's budget is enforced by deterministic code, not by the model's
    good behaviour. The model may ASK. Only the gate may ALLOW.

Every refusal carries a stable reason code, so a refusal is legible and
auditable rather than a silent no. Nothing here calls a model.
"""
from __future__ import annotations

from dataclasses import dataclass


class Refusal(Exception):
    """Raised when a spend request does not satisfy the policy."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class SpendRequest:
    """One thing the agent wants to buy."""

    amount: int            # smallest unit (yoctoNEAR on chain, kobo off chain)
    recipient: str         # named counterparty - never "the market"
    purpose: str           # what is being bought, in words
    evidence: str | None = None   # the receipt that the thing exists


@dataclass
class SpendPolicy:
    """Human-defined constraints. Set before the agent runs, not by the agent."""

    budget: int
    recipients: tuple[str, ...]
    require_evidence: bool = True
    min_purpose_chars: int = 12

    def __post_init__(self) -> None:
        if self.budget <= 0:
            raise ValueError("budget must be greater than zero")
        if not self.recipients:
            raise ValueError("at least one approved recipient is required")


class SpendGate:
    """Holds the budget and decides. The only object that can approve."""

    def __init__(self, policy: SpendPolicy, spent: int = 0) -> None:
        if spent < 0 or spent > policy.budget:
            raise ValueError("spent must be within [0, budget]")
        self.policy = policy
        self.spent = spent
        self.approved: list[SpendRequest] = []
        self.refused: list[tuple[SpendRequest, str]] = []

    @property
    def remaining(self) -> int:
        return self.policy.budget - self.spent

    # -- the decision -----------------------------------------------------
    def check(self, req: SpendRequest) -> tuple[str | None, str | None]:
        """Return (code, detail) on refusal, or (None, None) on approval."""
        p = self.policy

        if req.amount <= 0:
            return "AMOUNT_NOT_POSITIVE", "amount must be greater than zero"

        if req.amount > self.remaining:
            return (
                "OVER_BUDGET",
                f"asked {req.amount}, remaining {self.remaining}",
            )

        if req.recipient not in p.recipients:
            return (
                "RECIPIENT_NOT_ALLOWED",
                f"{req.recipient!r} is not an approved counterparty",
            )

        if len((req.purpose or "").strip()) < p.min_purpose_chars:
            return (
                "PURPOSE_TOO_VAGUE",
                f"purpose needs at least {p.min_purpose_chars} characters",
            )

        if p.require_evidence and not (req.evidence or "").strip():
            return (
                "NO_EVIDENCE",
                "no receipt for what is being bought - refusing to pay a claim",
            )

        return None, None

    def spend(self, req: SpendRequest) -> int:
        """Approve and record. Returns the remaining budget.

        Raises Refusal - and records the refusal - if the policy is not met.
        """
        code, detail = self.check(req)
        if code is not None:
            self.refused.append((req, code))
            raise Refusal(code, detail)

        self.spent += req.amount
        self.approved.append(req)
        return self.remaining

    # -- reporting --------------------------------------------------------
    def report(self) -> dict:
        return {
            "budget": self.policy.budget,
            "spent": self.spent,
            "remaining": self.remaining,
            "approved": len(self.approved),
            "refused": len(self.refused),
            "refusal_codes": [c for _, c in self.refused],
        }
