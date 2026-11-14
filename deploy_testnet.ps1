# deploy_testnet.ps1 - one command to make the budget on-chain
#
#   cd D:\temp\opencode\near-agent-wallet
#   .\deploy_testnet.ps1
#
# What it does, in order:
#   1. checks the NEAR CLI exists
#   2. creates (or reuses) a THROWAWAY testnet account
#   3. adds a function-call key scoped to one contract, one method, 0.5 NEAR
#   4. verifies the key is really scoped (and aborts if it is FullAccess)
#   5. proves the chain refuses an out-of-policy call
#
# It NEVER touches a mainnet account. It refuses any account not ending .testnet.
#
# Prerequisite:  npm install -g near-cli
# Then:          near login     (once, opens a browser)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

$Account   = if ($env:NEAR_TEST_ACCOUNT) { $env:NEAR_TEST_ACCOUNT } else { "zyphonos-test.testnet" }
$Contract  = "data.market.testnet"
$Allowance = "0.5"

function Step($n, $text) { Write-Host "`n[$n] $text" -ForegroundColor Cyan }
function Ok($text)       { Write-Host "    OK   $text" -ForegroundColor Green }
function Fail($text)     { Write-Host "    FAIL $text" -ForegroundColor Red; exit 1 }

# ---------------------------------------------------------------- guard rail
if ($Account -notmatch '\.testnet$') {
    Fail "refusing to run against '$Account' - only .testnet accounts are allowed here"
}

# ---------------------------------------------------------------- step 1
Step 1 "NEAR CLI present?"
try { $ver = (& near --version) 2>&1 } catch { Fail "near CLI not found. Run: npm install -g near-cli" }
Ok "near $ver"

# ---------------------------------------------------------------- step 2
Step 2 "Testnet account: $Account"
$exists = $false
try {
    $keys = (& near account view-keys $Account --json) 2>&1 | Out-String
    if ($keys -match 'public_key') { $exists = $true }
} catch { $exists = $false }

if ($exists) {
    Ok "already exists - reusing"
} else {
    Write-Host "    creating (uses the testnet faucet, no real money)..."
    try {
        & near account create-account $Account --useFaucet --initialBalance 10
    } catch {
        Fail @"
could not create the account automatically.

Do this instead (3 minutes, browser):
  1. https://wallet.testnet.near.org
  2. create a free account
  3. run:  `$env:NEAR_TEST_ACCOUNT = 'your-name.testnet'; .\deploy_testnet.ps1
"@
    }
    Ok "created"
}

# ---------------------------------------------------------------- step 3
Step 3 "Adding the policy-bound key (one method, one contract, $Allowance NEAR)"
Write-Host "    the budget stops being Python and becomes a chain rule..."

try {
    & near account add-key $Account `
        --contract-id $Contract `
        --method-names pay `
        --allowance $Allowance `
        --permission function-call
} catch {
    Fail "add-key failed. Run 'near account add-key --help' - CLI flags change between versions."
}
Ok "key added"

# ---------------------------------------------------------------- step 4
Step 4 "Verifying the key is actually scoped"
$keysJson = (& near account view-keys $Account --json) 2>&1 | Out-String

if ($keysJson -match 'FullAccess') {
    Fail "a FullAccess key exists on this account - the claim is void. Delete it and rerun."
}

$hasScoped = ($keysJson -match [regex]::Escape($Contract)) -and ($keysJson -match 'pay')
if (-not $hasScoped) { Fail "scoped key not found in view-keys output" }

Ok "key is scoped to [$Contract] method [pay]"
Write-Host "`n    raw view-keys output (paste this into the README):" -ForegroundColor DarkGray
Write-Host $keysJson -ForegroundColor DarkGray

# ---------------------------------------------------------------- step 5
Step 5 "Proving the chain refuses (this is the demo)"
Write-Host "    calling a method that is NOT 'pay' - the chain must reject it..."

try {
    & near contract call-function as-transaction $Contract not_pay `
        json-args '{}' prepaid-gas '30.0 Tgas' attached-deposit '0 NEAR' `
        sign-as $Account network-config testnet sign-with-keychain send 2>&1 | Out-String
    Write-Host "    NOTE: call returned without an obvious error. Check the explorer." -ForegroundColor Yellow
} catch {
    Ok "refused - the key cannot call 'not_pay'"
}

# ---------------------------------------------------------------- done
Write-Host "`n================ RESULT ================" -ForegroundColor Cyan
Write-Host "  Account : $Account"
Write-Host "  Contract: $Contract"
Write-Host "  Method  : pay only"
Write-Host "  Cap     : $Allowance NEAR, subtracted by the chain"
Write-Host ""
Write-Host "  Paste into README.md under 'What is built':"
Write-Host "    Testnet account: $Account"
Write-Host "    Key scope: $Contract / pay / $Allowance NEAR"
Write-Host "    Verified: view-keys shows no FullAccess"
Write-Host "========================================" -ForegroundColor Cyan
