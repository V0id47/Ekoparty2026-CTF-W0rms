# Web3

All addresses, cookies, private keys and RPC endpoints in the working notes were removed from this public version.

## Ledger Room

- **Points:** 150
- **Flag:** `HIK_WEB3_PUBLIC_SECRET_8894f43439a31f9ea8a7db54f9900e23`

The `Vault` contract derived a supposedly private storage location as:

```solidity
keccak256(bytes.concat("vault", bytes20(player)))
```

Privacy was only syntactic: both consecutive storage words were readable with `eth_getStorageAt`. The required argument was:

```text
keccak256(word0 || word1)
```

Submitting that `bytes32` to selector `0x4186ed2e` set `solved()` and `solver()`. The same lowercase hex value was used as the ticket proof.

## Executive Desk

- **Points:** 200
- **Flag:** `HIK_WEB3_OWNER_d2ce1f78f8c8ca6f7d8dbe56c3f87c25`

The intended ownership flow had three stages, but nomination lacked access control:

1. Call selector `0xb332180b` with the player address to nominate the player.
2. Read the nonce and accept it through `0x9f773348(bytes32 nonce)`.
3. As the new owner, call `0xac2f2c9b` to set the solved state.

The final owner's lowercase address without `0x` was the proof.

## Guest List

- **Points:** 250
- **Status:** solved on-chain and confirmed by the final platform state; exact flag not retained.

The wallet used `tx.origin` as an authorization boundary. An owner-visit endpoint caused the owner EOA to call a contract chosen by the player. The exploit contract used that callback to register itself as a guest and release the funds during the same transaction.

The first version ignored low-level call results, which allowed gas estimation to under-allocate and left state unchanged. Reverting on either failed call forced estimation to account for the storage writes. The resulting transaction drained the wallet and made `Setup.isSolved()` return `true`.

Instance addresses, the player private key, cookie, RPC endpoint and transaction identifiers were removed from this public version.

## Other platform-confirmed solves

Night Deposit, Voucher Window, Maintenance Hatch and the late-added Assembly Floor also appeared solved in the final authenticated event state. Their winning transactions and exact flags were not retained, so no technical path is reconstructed here. See [Team solves](team-solves.md#web3).

## Takeaway

Neither Solidity `private` storage, multi-step ownership workflows nor `tx.origin` create a security boundary. Storage is public, every transition needs authorization, and contract callers must be authenticated with `msg.sender` plus explicit trust rules.
