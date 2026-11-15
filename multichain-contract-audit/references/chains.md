# Chain registry — per-chain parameters for the multichain audit

Everything chain-specific lives here. If a chain is not listed, the method still
applies: find an RPC, confirm `eth_chainId`, use Sourcify with that chainId and
DexScreener for pair discovery — and write the depth band as `unknown` rather than
importing another chain's.

## Universal endpoints (work for every EVM chain)

| Need | Endpoint |
|---|---|
| Verified source | `https://sourcify.dev/server/v2/contract/<chainId>/<address>` |
| Explorer API (creation, source, ABI) | `https://api.etherscan.io/v2/api?chainid=<chainId>&...` (one key, all supported chains) |
| Pair discovery | `https://api.dexscreener.com/latest/dex/tokens/<address>` — check each pair's `chainId` |
| Honeypot/tax sim | `https://api.honeypot.is/v2/IsHoneypot?address=<addr>&chainID=<chainId>` — only where the chain is covered; otherwise simulate on the real pair |
| GoPlus (optional lead) | `https://api.gopluslabs.io/api/v1/token_security/<chainId>?contract_addresses=<addr>` |

**Derive, don't trust pins:** from any V2 pair you can read `factory()`, `token0()`,
`token1()` directly on the pair contract. From a token, the pair address on
DexScreener plus `factory()` on-chain beats any table — including this one. Pins
below are starting points for the majors, confirmed against the DEXs' own docs.

## Registry

### Ethereum — chainId 1
- RPC: `https://eth.drpc.org` · `https://rpc.mevblocker.io` · `https://ethereum-rpc.publicnode.com`
- Native: ETH · Wrapped: WETH `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
- DEX: Uniswap V2 factory `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f`, router `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D`; Uniswap V3 factory `0x1F98431c8aD98523631AE4a59f267346ea31F984`, position manager `0xC36442b4a4522E871399CD717aBDD847Ab11FE88`
- Depth (native side): thin < 2 ETH · fair 2–20 ETH · deep > 20 ETH
- Notes: full holder reconstruction needs an archive-capable RPC; public log windows are small. Marketplaces: OpenSea / Blur.

### BNB Smart Chain — chainId 56
- **Hand off to `bsc-contract-audit`** — deeper there (Binance audit API, BNB bands, PancakeSwap/UNCX pins).

### Base — chainId 8453
- RPC: `https://mainnet.base.org` · `https://base-rpc.publicnode.com`
- Native: ETH · Wrapped: WETH `0x4200000000000000000000000000000000000006`
- DEX: Uniswap V3 (factory as Ethereum); Aerodrome is the dominant venue — discover its pairs via DexScreener and read `factory()` off the pair.
- Depth: use the portable USD band (thin < $10k · fair $10k–250k · deep > $250k).
- Notes: cheap logs; full holder reconstruction is practical. Coinbase-verified pools are not a safety signal.

### Arbitrum One — chainId 42161
- RPC: `https://arb1.arbitrum.io/rpc` · `https://arbitrum-one-rpc.publicnode.com`
- Native: ETH · Wrapped: WETH `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1`
- DEX: Uniswap V3 (factory as Ethereum); Camelot is a major local venue — discover via DexScreener.
- Depth: portable USD band.

### Optimism — chainId 10
- RPC: `https://mainnet.optimism.io` · `https://optimism-rpc.publicnode.com`
- Native: ETH · Wrapped: WETH `0x4200000000000000000000000000000000000006`
- DEX: Uniswap V3 (factory as Ethereum); Velodrome dominant locally — discover via DexScreener.
- Depth: portable USD band.

### Polygon — chainId 137
- RPC: `https://polygon-rpc.com` · `https://polygon-bor-rpc.publicnode.com`
- Native: POL (ex-MATIC) · Wrapped: WPOL `0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270`
- DEX: QuickSwap V2 factory `0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32`; Uniswap V3 also live.
- Depth: portable USD band. Notes: very low fees — dust liquidity is common; weight the depth band strictly.

### Avalanche C-Chain — chainId 43114
- RPC: `https://api.avax.network/ext/bc/C/rpc`
- Native: AVAX · Wrapped: WAVAX `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7`
- DEX: Trader Joe (LB pairs are not V2-shaped — prefer DexScreener reserves and treat the V2 probes as not applicable); Pangolin legacy.
- Depth: portable USD band.

### Linea 59144 · zkSync Era 324 · Scroll 534352 · Mantle 5000 · Blast 81457
- RPC: Linea `https://rpc.linea.build` · zkSync `https://mainnet.era.zksync.io` · Scroll `https://rpc.scroll.io` · Mantle `https://rpc.mantle.xyz` · Blast `https://rpc.blast.io`
- Method applies unchanged; discover pairs via DexScreener, read `factory()` off the pair, portable USD depth band, mark anything not directly probed `unknown`.

## Lockers (recognised LP-lock addresses — verify the live balance, always)

| Locker | Chains | Note |
|---|---|---|
| UNCX Network | BSC, Ethereum, Arbitrum, Polygon, Avalanche, Base and more | Per-chain locker contracts differ; resolve the address from the pair's LP holder list and UNCX's own app/docs, then read the balance + lock end date |
| Team Finance | Ethereum, BSC, Polygon, Arbitrum, Base and more | Same resolution rule |
| PinkLock | Primarily BSC | See bsc-contract-audit |
| Burn | All | LP balance at `0x000000000000000000000000000000000000dEaD` — compare against the pair's `totalSupply`; accidental burns land at the null address `0x0`, which also counts as irrecoverable |

A lock with an end date is a **timed** lock: record the unlock timestamp. "Locked"
with an unlock next week is a delayed rug window, not safety.

## V3 / concentrated liquidity (all chains with Uniswap V3 forks)

Liquidity is an NFT position, not a fungible LP token. Read `ownerOf(positionId)` on
the chain's NonfungiblePositionManager and check whether that NFT sits with the
deployer (withdrawable at will → treat as unlocked), a locker, or the burn address.
A "locked V3 pool" claim needs the position NFT in a locker that supports V3.

## Solana

Not EVM — see [solana.md](solana.md). Public RPC: `https://api.mainnet-beta.solana.com`
(rate-limited; fine for single audits).

## Environment note (this workspace's VM)

Egress runs through an HTTP proxy that intermittently cuts urllib responses
(`IncompleteRead` / connection closed) against some RPC hosts — observed on
eth.drpc.org and rpc.mevblocker.io during the skill's live tests on 2026-11-10,
while Base and Solana reads went through clean. A failed read here is a transport
event, not a contract result: retry the same call (a short retry loop succeeded),
or fall back to curl for one-off JSON-RPC reads. Never record a transport failure
as `unknown` evidence about the contract itself.
