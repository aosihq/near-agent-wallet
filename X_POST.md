# X DEMO POST - draft for EBVKA's finger

**Requirement:** must mention **NEAR HACKATHON** and carry a video or screenshots.
Screenshots alone are not enough when a judge cannot open the demo - **record the run.**

**How to record it:** open a terminal in `near-agent-wallet`, run `python demo.py`,
screen-record the whole thing. 40-60 seconds. The refusal lines are the moment that matters.

---

## Primary (257 characters - measured)

```
Every agent wallet puts the spending limit in a prompt.

A prompt can be argued with.

So I moved the limit onto NEAR itself - a key that can only call one method, on one contract, until the allowance hits zero.

The chain doesn't negotiate.

NEAR HACKATHON
```

---

## Variant B - leads with the failure, not the fix (243 characters - measured)

```
I tried to talk my own agent into overspending.

It refused. Not because I told it to - because the budget lives on NEAR, not in a prompt.

Four attempts. One approved. Three refused with a reason.

The chain doesn't negotiate.

NEAR HACKATHON
```

---

## Reply 1 (add as a reply on the post, not a second post)

```
What "refused with a reason" looks like:

NO_EVIDENCE - no receipt for what is being bought
RECIPIENT_NOT_ALLOWED - not an approved counterparty
OVER_BUDGET - asked 0.4, had 0.3

Every one written to a hash-chained ledger. Edit a row and the chain breaks.
```

---

## Reply 2

```
The claim is falsifiable, so here it is:

21 checks pass.
Run `python demo.py` - four attempts, one approved, three refused.
Try to raise the budget with a prompt. You can't.

Repo in the next post.
```

---

## Rules this draft follows (self-check)

- **Writer's Law (rule 58):** this is a *draft for EBVKA to rewrite in his own mouth*,
  not final copy. The words are his or they do not ship.
- **Media mandatory (rule 16):** the demo video is required, not optional.
- **Agreement named (rule 47):** the post opens a **proof** agreement - a stranger can
  reproduce the result without us explaining it.
- **No unproven claim:** every number in it is checked in this repo (21 tests, four
  attempts, three refusal codes). Nothing here is aspirational.
- **No fake scarcity, no invented customer, no revenue claim.**

---

## What must be true before this is fired

- [ ] `python demo.py` passes on a clean machine
- [ ] video recorded, refusal lines visible
- [ ] repo public
- [ ] EBVKA has rewritten the lines into his own voice
- [ ] EBVKA fires it on his phone (manual rails - no automation, ever)
