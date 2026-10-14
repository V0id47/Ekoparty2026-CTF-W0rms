# ThunderFTP — deterministic ZMmalloc exploitation

- **Category:** Pwn / Binary
- **Status:** solved locally and remotely
- **Binary SHA-256:** `4f7fc518edf99dcaee52942b53da82868849224a9b9e321969e769c4263f8d73`
- **Solver:** [`../solvers/thunderftp.py`](../solvers/thunderftp.py)

The original challenge binary is not redistributed here. Place your own copy at `./ftpsrv` for local testing or pass its path with `--local`.

## Protections

```text
amd64 · Full RELRO · Canary · NX · PIE · IBT/SHSTK declared · stripped
```

There was no need to attack the GOT, stack or libc. The binary contained a `win()` function at PIE offset `0x23c6` that printed the flag.

## Useful protocol surface

```text
PASS <anything>
STAT <offset>
STOR <slot> <requested_size> <transfer_size> + binary data
WRITE <slot> <transfer_size> + binary data
RETR <slot> <size>
DELE <slot>
MKJOB <name>
EXEC
```

## Primitives

1. `STAT 16` returned the ZMmalloc control block's `top` and `end` pointers. The arena was `0x20000` bytes, so `end - 0x20000` revealed its base.
2. `STOR` validated `requested_size` and `transfer_size` separately, allocated the former and copied the latter: a direct heap overflow.
3. ZMmalloc v2.1 followed recycled `next_free` pointers without authentication.
4. A 64-byte-class job stored a callback at `job + 0x18`. The normal callback was at PIE offset `0x1daa`.

## Exploit chain

Let the arena base be `H`. After initial allocations:

```text
slot 0 header H+0x180, data H+0x1a0
slot 1 header H+0x200, data H+0x220
job    header H+0x280, data H+0x2a0
```

Free slot 1 and then slot 0, making the freelist `slot0 -> slot1`. Reallocate slot 0 with a requested size of 64 but transfer 128 bytes. The overflow replaces slot 1's `next_free` pointer with `H+0x280`, the job header.

The next two allocations return slot 1 and then the job itself. The overlapping note can now:

1. `RETR` the normal callback and calculate PIE.
2. `WRITE` `PIE + 0x23c6` over the callback.
3. Trigger `EXEC` and receive the flag.

This is deterministic, single-connection exploitation with no brute force.
