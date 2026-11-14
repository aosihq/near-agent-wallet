# VIDEO SCRIPT - timings match demo.mp4 EXACTLY

**File:** `D:\temp\opencode\near-agent-wallet\demo.mp4` (1920x1080, 56.0s, 3.55 MB)
**Re-render:** `python make_video.py` (~5 min)
**Verify:** `python verify_video.py` (checks text is present in every sampled frame)

Timings below are the real scene boundaries in the rendered file. Read at roughly
**2.5 words per second** - the word counts are budgeted to fit each scene.

---

## 0:00 - 0:03 · title card

**On screen:** AN AGENT WITH A WALLET IT CANNOT OVERSPEND / NEAR HACKATHON 2026

**Say (nothing, or):**
> "NEAR Hackathon."

---

## 0:03 - 0:10 · the policy  (7s - about 17 words)

**On screen:** section 1 - budget 0.5 NEAR, counterparty, evidence required

**Say:**
> "I gave this agent half a NEAR to spend. I set that limit before it ran, and it cannot change it."

---

## 0:10 - 0:25 · the four attempts  (15s - about 37 words)

**On screen:** one ALLOW, then three REFUSE lines in red, each with its reason

**Say:**
> "Four things it wanted to buy. One was approved — a dataset, with an invoice. Three were refused: no receipt, an unknown seller, and more money than it had."

**Let the red lines sit. Do not talk over the third refusal.**

---

## 0:25 - 0:33 · the payload  (8s - about 20 words)

**On screen:** section 3 - the function call key JSON

**Say:**
> "Then I moved that same limit onto NEAR itself. One contract, one method, and a hard allowance."

---

## 0:33 - 0:46 · THE CHAIN  (13s - about 32 words)

**On screen:** `near list-keys` real output - the FunctionCall block in amber

**Say:**
> "This is the real testnet account. The chain stores exactly what my code generates — allowance 0.5 NEAR, one method, one contract. Even if my Python is wrong, the chain still stops it."

**Point at the allowance line. Three seconds of silence here is worth ten words.**

---

## 0:46 - 0:52 · receipts  (6s - about 15 words)

**On screen:** ledger rows, chain INTACT

**Say:**
> "Every decision is written to a hash-chained ledger. Change one row and the chain breaks."

---

## 0:52 - 0:56 · close  (4s - about 10 words)

**On screen:** "The budget is a boundary, not an instruction."

**Say:**
> "The budget is a boundary, not an instruction."

---

## Recording notes

- **Microphone:** phone voice memo is fine. Record audio separately, then lay it over
  the video — easier to retake than doing both live.
- **Do not narrate the code.** Narrate the refusal. The refusal is the product.
- **Silence is allowed.** The pauses at 0:10–0:25 and 0:33–0:46 carry more than words.
- **If you rewrite any line, keep the word budget** for that scene or it will run over
  and drift into the next scene.

---

## Checklist before posting

- [ ] voiceover laid over demo.mp4, in sync at 0:33 (the chain scene)
- [ ] all three REFUSE lines visible around 0:15–0:24
- [ ] post text under 280 chars (drafts in `X_POST.md` — 257 and 243)
- [ ] post mentions **NEAR HACKATHON**
- [ ] repo public
- [ ] you have rewritten the post lines into your own voice

---

## What NOT to do

- No music. It reads as an ad, not a demo.
- No speed-up. The pauses are the credibility.
- No claim the video did not show.
