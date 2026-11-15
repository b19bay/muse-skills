# Solana annex — the four gates without EVM

Solana has no owner(), no selectors, no LP tokens in the EVM sense. The questions are
the same; the probes are these. Public RPC: `https://api.mainnet-beta.solana.com`
(rate-limited — fine for a single audit, useless for bulk scanning).

```bash
MINT=<base58 mint address>
RPC=https://api.mainnet-beta.solana.com
```

## Gate 0 — What is this mint?

```bash
curl -s $RPC -X POST -H 'Content-Type: application/json' -d "{
  \"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"getAccountInfo\",
  \"params\":[\"$MINT\",{\"encoding\":\"jsonParsed\"}]}" | jq '.result.value'
```

Read from the result:

- `owner` (the account's program): `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA` =
  classic SPL token; `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb` = **Token-2022**
  (extension traps possible — see Gate 3).
- `data.parsed.info`: `supply`, `decimals`, `mintAuthority`, `freezeAuthority`.

## Gate 1 — Can it be sold?

- A live pair with real depth and recent transactions (DexScreener, Gate 4). No pair,
  or a pair with dust liquidity, = no observable exit.
- **A live `freezeAuthority` overrides everything**: the authority can freeze any
  holder's token account, which is a per-wallet sell block — the Solana honeypot.
  Treat exactly like the EVM transfer-block cap (40) for any buy recommendation.
- Token-2022 `non-transferable` extension = soulbound: same cap.

## Gate 2 — Who owns the supply?

```bash
curl -s $RPC -X POST -H 'Content-Type: application/json' -d "{
  \"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"getTokenLargestAccounts\",
  \"params\":[\"$MINT\"]}" | jq '.result.value[] | {address, uiAmountString}'
```

- Sum the top accounts against `supply` (mind the decimals). Strip pool vaults
  (identify them from the pair's vault addresses on DexScreener / the DEX's own page)
  before judging concentration — same rule as EVM.
- `mintAuthority: null` = supply frozen forever. A live mint authority held by the
  deployer = uncapped supply with team mint (EVM cap 60 applies by analogy).
- Note WHO the authorities are: a treasury/project wallet is a live counterparty;
  a known burn or a multisig with public signers is a different risk class. Record
  the address verbatim.

## Gate 3 — Contract traps (Solana edition)

| EVM trap | Solana equivalent | Probe |
|---|---|---|
| Hidden mint | `mintAuthority` still set | Gate 0 read |
| Blacklist / freeze | `freezeAuthority` still set | Gate 0 read — **the single most important Solana check** |
| Adjustable tax | Token-2022 `transferFee` extension (mutable fee + withdraw authority) | jsonParsed `extensions` on Token-2022 mints |
| Owner drain | Token-2022 `permanentDelegate` extension (delegate can move/burn any holder's tokens) | Same |
| Soulbound | Token-2022 `nonTransferable` extension | Same |
| Mutable metadata (baseURI swap) | Metaplex metadata `isMutable: true` + live `updateAuthority` | Metadata account (below) |
| Proxy upgrade | No proxy pattern; program upgrade authority matters for custom programs, not for plain SPL mints | Only when the "token" is a custom program |

Metaplex metadata: the metadata PDA is derived from seeds
`["metadata", mpl_token_metadata_program, mint]`. Reading it raw over RPC means
base64-decoding the account; the practical route is a DAS `getAsset` call (Helius
and other providers) — aggregator-level evidence, mark it as such, and re-prove
`isMutable` from the raw account when the finding is decisive.

## Gate 4 — Is liquidity safe?

```bash
curl -s "https://api.dexscreener.com/latest/dex/tokens/$MINT" \
  | jq '.pairs[] | select(.chainId=="solana") | {dexId,pairAddress,liq:.liquidity.usd,vol24:.volume.h24,txns:.txns.h24}'
```

Venues: Raydium, Meteora, Orca, PumpSwap (post-pump.fun graduations). LP safety:

- Classic AMM LP mint: read the LP mint's own Gate 0/Gate 2 — burned LP shows as
  supply held by incinerator `1nc1nerator11111111111111111111111111111111` or a
  zero-authority mint with the pool's LP tokens out of circulation. "LP burned"
  claims from the site are claims — verify against the LP mint's largest accounts.
- Meteora DLMM / DAMM and Orca Whirlpools use position NFTs (Solana NFTs, not EVM):
  the position owner can withdraw — identify who holds the position before calling
  liquidity locked.
- Portable USD depth band applies: thin < $10k · fair $10k–250k · deep > $250k.

## Worked example — $BROK (checked 2026-11-05)

Mint `BRKLn3cHBhWCyXeTm6jz6S7CvBqxhUCTsP9yrLUEq3Wu`:

- Supply 1,000,000,000 (6 decimals); `mintAuthority = null` ✔ (supply frozen).
- **`freezeAuthority` = project treasury `FXBxAgSdD17KTbYqF7kUzTmKMxT3Ew17TYXkuXLVvvWh`**
  — live: any holder can be frozen at the project's discretion.
- Market: one Meteora pool vs SOL, liquidity ≈ $2,342 (thin band), FDV ≈ $52k.
- Verdict shape: tradeable today, but a live freeze authority + thin liquidity =
  CAUTION at best for any buy; the freeze authority alone caps the score like an
  EVM honeypot risk until it is renounced (set to null) on-chain.

## Scoring on Solana

Map the annex onto the same /100 rubric, scoring only what was actually probed and
marking the rest `unknown`: Security ← authorities + extensions + metadata;
Investor protection ← exit route + freeze risk; Anti-manipulation ← largest-account
concentration + LP status; Transparency ← site claims vs Gate 0 reads + team;
Market viability ← pair depth/volume/age. Same verdict bands, same DECISION line,
same hard caps by analogy (freeze authority live → cap 40 for buy purposes;
mint authority live + concentrated → cap 60; thin unlocked liquidity → cap 55).
