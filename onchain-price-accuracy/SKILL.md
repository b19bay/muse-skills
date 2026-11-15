---
name: onchain_price_accuracy
description: Mandatory price-accuracy protocol for ALL NFT listings, price binding, smart contract interactions, and marketplace transactions. User-issued 2026-10-30 as a CRITICAL SKILL. Use before any listing, repricing, offer, buy, or other price-bearing on-chain action.
---

# CRITICAL SKILL: ON-CHAIN PRICE ACCURACY

For ALL NFT listings, price binding, smart contract interactions, and marketplace transactions:

1. ALWAYS identify the blockchain, payment token contract, token decimals, and marketplace ABI before setting a price.
2. NEVER assume decimals. Native BNB uses 18 decimals, but tokens such as USDT must be verified directly from their contract using `decimals()`.
3. Convert human-readable prices into base units using precision-safe BigInt arithmetic. Never use floating-point calculations for on-chain amounts.
4. Encode the value into HEX/ABI using the exact format expected by the marketplace.
5. BEFORE signing or broadcasting, simulate the transaction and decode the encoded price back into human-readable units.
6. Verify that the decoded listing price EXACTLY matches the user's requested price and currency.
7. If anything is uncertain or mismatched, STOP. Never guess, silently round, or execute an unverified price.

**ABSOLUTE RULE: USER PRICE = MARKETPLACE LISTING PRICE. ZERO TOLERANCE FOR DECIMAL, HEX, OR PRICE-BINDING ERRORS.**

## How this combines with the user's standing rules

- This protocol runs IN ADDITION TO the standing nominal-confirmation rule (confirm exact amount in original currency + IDR with quoted rate/time + fees/gas/total, wait for the user's confirmation for that specific item and nominal) — it does not replace it.
- Order of operations for any price action: identify chain/token/decimals/ABI → BigInt conversion → encode → user nominal confirmation → simulate → decode the price back from the simulated/encoded transaction → exact match check → only then sign/broadcast.
- After broadcasting, re-read the listing on-chain and verify the stored price equals the requested price; report any mismatch immediately.
