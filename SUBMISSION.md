# SUBMISSION — NEAR HACKATHON 2026

Copy-paste fields for `nearhackathon.com`. One submission, cannot be edited after sending.

---

## Project name

**An Agent With a Wallet It Cannot Overspend**

---

## Description (20–2,000 characters)

Every agent wallet today puts the spending limit in a prompt, in application code, or in
a dashboard — all inside the thing being limited. This project moves the limit to a NEAR
function call access key, so the chain subtracts from the budget and stops the key at
zero. Two layers that fail independently: a deterministic policy gate that can explain a
refusal (named codes: OVER_BUDGET, NO_EVIDENCE, RECIPIENT_NOT_ALLOWED, PURPOSE_TOO_VAGUE),
and an on-chain key that cannot be argued with. Every decision, approved or refused, is
written to a hash-chained receipt ledger where tampering is detectable. The demo runs
with no network and no keys: four spend attempts, one approved, three refused for named
reasons, including a prompt-injection attempt that cannot raise the budget. 21 checks
pass, both directions. The claim is falsifiable: the budget is a boundary, not an
instruction.

---

## Tracks (submit BOTH — one submission, multiple track ids allowed)

- `agents` — **Agent Economy**
- `security` — **AI Security & Defense**

---

## Team lead

Ebuka — `zyphon.os.you@gmail.com` — team size **1**

---

## Payout

**A NEAR account address** — not yet created. Free at `wallet.near.org`, 3 minutes,
needs your finger. Without it the form cannot be submitted.

---

## Links

- **Repository:** not yet public. Must be public by 2026-11-14 23:59 UTC.
- **Demo post on X:** not yet posted. Must mention **NEAR HACKATHON** and carry a video.

---

## README check before sending

- [x] numbered "do X, see Y" steps
- [x] expected output pasted for every step
- [x] exit codes stated
- [x] what is NOT built stated plainly (no live testnet tx yet)
- [x] honest limit of the hash chain named
- [ ] testnet transaction hash added (needs Step 4 of DEPLOY_TESTNET)
- [ ] public repo URL added

---

## What the judges will actually do

Illia Polosukhin, Mert Mumtaz, Eddy Lazzarin, Avichal Garg, Kain Warwick,
Haseeb Qureshi, Stepan Gershuni — plus **Claude Code and Codex as AI judges**.

An AI judge cannot be impressed by prose. It can only run the steps and compare output.
That is why every step above has its expected result written out verbatim, and why the
README states its own gaps before anyone else can find them.

---

## Prize reality (so nobody over-promises)

$250,000 is the whole pool across 13 tracks plus a $55,000 grand prize.
**Each track pays $10,000 / $3,000 / $2,000 for the top three.**

A good outcome here is **$2,000–$10,000**. Real money, not a jackpot.
