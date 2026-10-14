# Web3

All eight challenges were solved. Private keys, cookies, RPC endpoints, deployment addresses and transaction hashes were removed because they belonged to ephemeral instances.

## Ledger Room

- **Points:** 150

The vault derived a supposedly private storage location with `keccak256("vault" || player)`. Both consecutive storage words were public through `eth_getStorageAt`; hashing their concatenation and submitting it to the unlock selector solved the challenge.

## Executive Desk

- **Points:** 200

The ownership workflow had nomination, acceptance and execution stages, but nomination lacked access control. I nominated the player, read the public nonce, accepted ownership, and called the owner-only completion function.

## Guest List

- **Points:** 250

The wallet authenticated its owner with `tx.origin`. An owner-visit endpoint made the owner EOA call a player-selected contract. My callback contract registered itself as a guest and released the wallet's funds to the player in the same transaction.

The exploit reverted when either low-level call failed. That detail forced the bot's gas estimation to include both storage writes; silently ignoring failures had previously left the wallet unchanged.

## Night Deposit

- **Points:** 350

The bank sent Ether before reducing the caller's recorded balance. I deposited the player's 1 ETH through an attacker contract and recursively called `withdraw()` from its fallback ten times, draining the bank's initial 10 ETH plus the deposit. The bank balance of zero was the successful proof.

## Voucher Window

- **Points:** 400

The claim signature covered the recipient and amount but the replay guard indexed the wrong calldata word. Supplying the signed amount as the first argument and zero as the tracked index made the signature valid while leaving the intended claim marker untouched.

Replaying the same voucher ten times accumulated 1000 tokens and satisfied `Setup.isSolved()`. The final token balance was used as the ticket proof.

## Maintenance Hatch

- **Points:** 500

The proxy delegated into an implementation whose maintenance function wrote to storage without preserving the proxy's ownership layout. Calling the exposed takeover selector through the proxy replaced the owner slot with the player address. The new owner then invoked the completion selector, setting the solved bit.

The maintenance code ran with `delegatecall`, so its writes landed in the proxy's storage. That was enough to replace the owner slot and finish the challenge.

## Carcara Markets

- **Points:** 450

The lending contract priced collateral from the DEX's instantaneous reserves. An attacker contract took a 2000-token flash loan, swapped the borrowed stablecoin into the collateral token to distort the spot price, deposited the overpriced collateral, and borrowed the lending pool's full 10,000-token balance.

It repaid the 2000-token flash loan inside the callback and retained 8000 tokens while the lending pool ended at zero. No time-weighted price or manipulation-resistant oracle was used.

## Assembly Floor

- **Points:** 400

Voting power was based on the caller's current token balance rather than a snapshot. My callback borrowed governance tokens, created a proposal to spend the treasury, voted with the temporary balance, and repaid the flash loan in the same transaction.

After advancing through the voting period and timelock, I queued and executed the proposal. The treasury balance fell from 50 ETH to zero.

The set was varied, but the common pattern was trusting live chain state too much: public storage used as a secret, current balances used for governance and spot reserves used as an oracle. The transaction traces made each assumption visible.
