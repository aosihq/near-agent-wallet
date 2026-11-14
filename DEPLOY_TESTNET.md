# DEPLOY_TESTNET — one command to make it on-chain

**Status: NOT YET RUN.** This file is the path, not a claim. Nothing below has been
executed. When it has, this file gets a result line with the transaction hash.

You need one thing: a NEAR testnet account. It is free and takes three minutes.

---

## Step 1 — get a testnet account (3 minutes, needs a browser)

1. Go to **https://wallet.testnet.near.org**
2. Create a free account — pick a name, e.g. `zyphonos-test.testnet`
3. Save the seed phrase offline. Testnet has no real money, but the habit matters.

**Expected:** you can see your account at `https://explorer.testnet.near.org/accounts/<your>.testnet`

---

## Step 2 — install the CLI

```bash
npm install -g near-cli
```

**Expected:** `near --version` prints a version.

> CLI syntax changes between major versions. If a flag below is rejected, run
> `near account add-key --help` and match the current spelling. Do not guess past an
> error — the whole point of this project is that errors are read.

---

## Step 3 — log in

```bash
near login
```

**Expected:** a browser opens, you approve, and `~/.near-credentials/testnet/<your>.testnet.json`
appears.

---

## Step 4 — add the policy-bound key

This is the moment the budget leaves Python and becomes a chain rule.

```bash
near account add-key <your>.testnet \
  --contract-id data.market.testnet \
  --method-names pay \
  --allowance 0.5 \
  --permission function-call
```

**Expected:** `Adding key ... to <your>.testnet` and a transaction hash.

The key may now call **only** `pay` on **only** `data.market.testnet`, and may spend
**at most 0.5 NEAR total**. The chain subtracts from that allowance on every call.

---

## Step 5 — verify the key is really scoped

```bash
near account view-keys <your>.testnet --permission function-call
```

**Expected:** one key showing `receiver_id: data.market.testnet`,
`method_names: ["pay"]`, `allowance: 500000000000000000000000`.

If it shows `FullAccess` anywhere, **stop** — the key was created wrong and the entire
claim is void. Delete it and start Step 4 again.

---

## Step 6 — prove the chain refuses

Send a call that exceeds the allowance, or call a method that is not `pay`.

**Expected:** the transaction is rejected by the node. The refusal comes from NEAR, not
from this repository's Python.

That rejection is the demo. Record it.

---

## What goes in the README when this works

```
Testnet transaction: <hash>
Explorer: https://explorer.testnet.near.org/transactions/<hash>
Key: view-keys output pasted above
Refusal: <hash of the rejected tx>
```

Until those lines exist, the README says **"not yet run"** — because a demo that was
never executed is a claim, and this project exists to refuse claims.
