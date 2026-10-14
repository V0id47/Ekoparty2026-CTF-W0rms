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

## Takeaway

Neither Solidity `private` storage nor multi-step ownership workflows create a security boundary. Storage is public, and every transition needs authorization—not just the final privileged action.

