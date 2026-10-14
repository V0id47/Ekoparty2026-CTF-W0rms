# Web3

All eight challenges were solved. Private keys, cookies, RPC endpoints, deployment addresses and transaction hashes were removed because they belonged to ephemeral instances.

## Ledger Room

- **Points:** 150
- **Flag:** `HIK_WEB3_PUBLIC_SECRET_8894f43439a31f9ea8a7db54f9900e23`

The vault derived a supposedly private storage location with `keccak256("vault" || player)`. Both consecutive storage words were public through `eth_getStorageAt`; hashing their concatenation and submitting it to the unlock selector solved the challenge.

## Executive Desk

- **Points:** 200
- **Flag:** `HIK_WEB3_OWNER_d2ce1f78f8c8ca6f7d8dbe56c3f87c25`

The ownership workflow had nomination, acceptance and execution stages, but nomination lacked access control. We nominated the player, read the public nonce, accepted ownership, and called the owner-only completion function.

## Guest List

- **Points:** 250
- **Flag:** `HIK_WEB3_TX_ORIGIN_dc5af32981f437fcff8bcb0451acdae7`

The wallet authenticated its owner with `tx.origin`. An owner-visit endpoint made the owner EOA call a player-selected contract. Our callback contract registered itself as a guest and released the wallet's funds to the player in the same transaction.

The exploit reverted when either low-level call failed. That detail forced the bot's gas estimation to include both storage writes; silently ignoring failures had previously left the wallet unchanged.

## Night Deposit

- **Points:** 350
- **Flag:** `HIK_WEB3_REENTRANCY_dad10f80581c314acbd6b05882eea348`

The bank sent Ether before reducing the caller's recorded balance. We deposited the player's 1 ETH through an attacker contract and recursively called `withdraw()` from its fallback ten times, draining the bank's initial 10 ETH plus the deposit. The bank balance of zero was the successful proof.

## Voucher Window

- **Points:** 400
- **Flag:** `HIK_WEB3_REPLAY_9759e40c35b84c764c492e99f5811b72`

The claim signature covered the recipient and amount but the replay guard indexed the wrong calldata word. Supplying the signed amount as the first argument and zero as the tracked index made the signature valid while leaving the intended claim marker untouched.

Replaying the same voucher ten times accumulated 1000 tokens and satisfied `Setup.isSolved()`. The final token balance was used as the ticket proof.

## Maintenance Hatch

- **Points:** 500
- **Flag:** `HIK_WEB3_DELEGATECALL_0a120cd108615c37945edfb76256d326`

The proxy delegated into an implementation whose maintenance function wrote to storage without preserving the proxy's ownership layout. Calling the exposed takeover selector through the proxy replaced the owner slot with the player address. The new owner then invoked the completion selector, setting the solved bit.

This was a classic delegatecall/storage-layout failure: authorization in the implementation operated on the proxy's storage, not on an isolated implementation state.

## Carcara Markets

- **Points:** 450
- **Flag:** `HIK_WEB3_ORACLE_d6036e30b782007df2b879030f515065`

The lending contract priced collateral from the DEX's instantaneous reserves. An attacker contract took a 2000-token flash loan, swapped the borrowed stablecoin into the collateral token to distort the spot price, deposited the overpriced collateral, and borrowed the lending pool's full 10,000-token balance.

It repaid the 2000-token flash loan inside the callback and retained 8000 tokens while the lending pool ended at zero. No time-weighted price or manipulation-resistant oracle was used.

## Assembly Floor

- **Points:** 400
- **Flag:** `HIK_WEB3_GOVERNANCE_15b08a0f18c1597b0a59df205b66dfc2`

Voting power was based on the caller's current token balance rather than a snapshot. Our callback borrowed governance tokens, created a proposal to spend the treasury, voted with the temporary balance, and repaid the flash loan in the same transaction.

After advancing through the voting period and timelock, we queued and executed the proposal. The treasury balance fell from 50 ETH to zero.

## Takeaway

Public storage is not secret storage; every state transition needs explicit authorization; `tx.origin` is not an identity boundary; external calls must follow checks-effects-interactions; signatures need a correctly enforced nonce; proxy layouts must be compatible; spot reserves are not robust price oracles; and governance needs checkpointed voting power.
