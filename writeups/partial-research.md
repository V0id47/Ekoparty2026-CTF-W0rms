# Partial research and dead ends

These notes are published because a useful dead end is more valuable than a fabricated solution.

## Malware — Build Stamp

- Hidden key: `NINHO202`; printable `202OHNIN` was a decoy.
- Bot/task: `DAF1979E` / `2`.
- Reusing the keystream from two 192-byte decoy configs recovered the first 192 bytes of the 205-byte real config.
- The missing field was a 12-character Base64 value beginning with `e`; the `x86_64le` hypothesis and its Base64/NUL forms were rejected.
- Host, path, UA, bot, task, access key, ELF/PCAP hashes, architecture triples and cross-instance gate/token reuse were exhausted.
- Malware vhosts used the same framework but did **not** share gates or sessions (`403`/`401`).

## Packet — Front Desk

- The relevant FTP user was fragmented as `USER ops` + `412`.
- After login, the session sent an 81-byte object prefixed by big-endian length `0x51`.
- The password changed per session and was 38 bytes represented as hexadecimal.
- User/password strings, endpoints and trivial hashes were rejected; the cryptographic container remained unidentified.

## Packet — Long Call

- The authentic stream began with `AUTH AUTH-N7K2` and contained records of `32, 32, 32, 32, 31, 78` bytes.
- A second stream containing readable token fragments was prompt-injection noise.
- Direct concatenation, Base64, hashes and simple XOR combinations failed.

## Binary Gecko

The Windows parent loaded `gecko2026-module.dll` and called its exported `processor` with:

```text
DWORD total | BYTE cmd | DWORD field | DWORD len | body
```

Two primitives were reproducible:

- `cmd0` with controlled output length leaked roughly 4 KiB of stack.
- `cmd1`, identifier zero, length 20 and a zeroed body returned 20 bytes beginning with `MZ`, proving a read from the DLL base.

Changing offset or length closed the connection, and malformed requests corrupted global state until restart. The next step would be to turn the stack leak into stable pointers before attempting incremental DLL reads.

