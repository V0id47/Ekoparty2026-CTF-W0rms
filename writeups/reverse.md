# Reverse — 13/13

The Reverse set repeatedly used a small ELF wrapper that found a `HIKB` trailer in `/proc/self/exe`, unpacked another ELF into a `memfd` and launched it with `fexecve`. The inner checkers combined real logic with anti-debug branches and convincing decoys.

## Common workflow

1. Break immediately before `fexecve` and dump the referenced file descriptor.
2. Analyze the inner ELF, not only the wrapper.
3. Neutralize or observe environment checks such as `TracerPid`, parent process names, `LD_PRELOAD` and integrity gates.
4. Stop immediately before the final hash/comparison and inspect the authentic input buffer.
5. Validate with the original wrapper before requesting a fresh ticket.

For the HTTP challenges, the common redemption flow was:

```python
proof = sha256(secret.hex().encode()).hexdigest()
ticket = GET("/ticket")["ticket"]
token = sha256(f"{ticket}:{proof}".encode()).hexdigest()
POST("/flag", json={"ticket": ticket, "token": token})
```

## Sealed Sample

- **Points:** 100
- **Flag:** `HIK_REV_CARCARA_6d2fba7deaabec88aae324dda250c39b`
- **Artifact SHA-256:** `c9100d941a39219d81d374eff64f4dd9c80c561d22d47c19c9f419df313d2057`

The wrapper extracted an inner ELF through `memfd`. The real 32-byte secret was present at `rsp+0xa0` immediately before the hash at offset `0x40140f`:

```text
f6c56bde9f594ea864f4cc625c0e10b155b03cbe3245f905f76680966987e9ea
```

## The Checker

- **Points:** 200
- **Flag:** `HIK_REV_INNER_VM_682822e7fa42ee02a20078cd34e2a338`
- **Artifact SHA-256:** `44e3c5c7cce4e50a48c06ba923ee4a8733b2c2a7413b4275e5377342db8a00cb`

The inner binary implemented a small VM. Reconstructing every opcode was unnecessary: the correct secret was exposed at the second hash site.

```text
719827bde8af49c44d6c6d97487dab19859eb07fdfc9b113e509fb56757dcf17
```

## Butterfly Effect

- **Points:** 250
- **Flag:** `HIK_BUTTERFLY_EFFECT_e555fdfcf33e97a369ae397de0413a8f`
- **Artifact SHA-256:** `2802d409ac6254c1b769dc375ca4a808d12b02076811bd5890c01a531c90723e`
- **Solver:** [`../solvers/butterfly_effect.py`](../solvers/butterfly_effect.py)

The service supplied five 128-bit IDs and requested twelve 32-bit pulses per round. The checker used four invertible state transforms and checkpoints after pulses 3, 6 and 9, plus a final target at 12. Because every multiplication constant was odd, it had an inverse modulo `2^32`. Zeroes were used for unconstrained positions; each checkpoint pulse was calculated by inverting the active transform.

## Forked Path

- **Points:** 300
- **Flag:** `HIK_REV_PHANTOM_f6e23061c3539262e83bb6994f29e8d5`
- **Artifact SHA-256:** `aa5435d2b08c600ded0621665c0de4a2b2cc0d0eb0348ea1f6ca79c0e4fb0d0f`

Anti-debug and environment checks diverted execution to a false secret. Patching only the branches into the decoy exposed the clean path:

```text
adacce46a45062ba11fc623456aeb4aaf2e9866cf8dbcffe5d95590d3696ac9f
```

## Many Rooms

- **Points:** 300
- **Flag:** `HIK_REV_FLATLAND_da76bb711cc563de34a3febda26e7c1c`
- **Artifact SHA-256:** `60ac4abae70f40a2b876b5821eab250bbcc4543120979639e04fcac083c17f2d`

The inner checker flattened control flow into a state machine. Following the real transitions and inspecting the final comparison buffer recovered:

```text
bb50482d24411591fcb40c9e3c56324eb7ae8fedf0024af636d5773ed43ca3b9
```

## Impossible License

- **Points:** 300
- **Flag:** `HIK_ALMOST_IMPOSSIBLE_75521f4db5d9bfc28ffa972b0fae2dc8`
- **Artifact SHA-256:** `5ac337e8fd2a48260f6c7036720d379a095989e8703030e28dcd5d2e776322fd`
- **Solver:** [`../solvers/impossible_license.py`](../solvers/impossible_license.py)

An opaque predicate always selected the first of two checkers; the second was a decoy. The real checker applied eight rounds of bias addition, multiplication by odd constants, rotation, an invertible 8×8 matrix and a permutation. The keygen reversed those operations in the opposite order and answered five live rounds.

## Linked Blocks

- **Points:** 350
- **Flag:** `HIK_REV_INTEGRITY_a06f7f4f41ed24de38b5209e3672275a`
- **Artifact SHA-256:** `db4482880144ce2e77c21e667df2cbe3404fa8d16161201c9ee4b517ae9ffc80`

After bypassing the integrity-aware decoy path, the genuine pre-hash secret was:

```text
9900440601a9a1679bdd8a6c4dafe03977e172821a7bbfad2092f4f8093c9aad
```

## Missing Labels

- **Points:** 350
- **Flag:** `HIK_REV_GHOST_b194dd43fec29d261958d62645a7258f`
- **Artifact SHA-256:** `2f517b5c8e9a9c23fee56f4b00b4c6176abef03c5de3602b3ad8177d0781e663`

The environment branches selected fake data whenever analysis was detected. Forcing the clean branch produced:

```text
3005150bdb097a5aa13357844b2eb183b121fadfae4cfa91468ec2f9af9ccaf6
```

## Virtual Notary

- **Points:** 400
- **Flag:** `HIK_VM_MACHINES_ARE_HARD_9fd7b12da040d4254602b9ce3218e8da`
- **Artifact SHA-256:** `cd66e88cedca4782bf332eb6393eed9dc91412cab607f46e80dad9117286ce08`
- **Solver:** [`../solvers/virtual_notary.py`](../solvers/virtual_notary.py)

The service provided five license IDs and required eight-word serials. The binary decrypted a 154-instruction program for a 16-register VM. Each instruction was eight bytes and supported ID/serial loads, constants, arithmetic, rotations, bitwise operations and comparisons. The solver interpreted this bytecode symbolically with Z3 bit-vectors and solved the eight comparison constraints for every round.

Install the public solver dependency with `python3 -m pip install -r ../requirements.txt` from this directory, or from the repository root with `python3 -m pip install -r requirements.txt`.

## Wrapped Sample

- **Points:** 400
- **Flag:** `HIK_REV_NESTED_1ba5d4c223689741d710de2c57194c8e`
- **Artifact SHA-256:** `16fe809576c64e2054a46352a55452eebfade1d9fa828b86344c7eab052fec6c`

Intercepting `fexecve` yielded the final checker. Its debugger, integrity and `LD_PRELOAD` tests created a decoy; the clean pre-hash buffer contained:

```text
e78de774b2468c7d2f0cfab47ae3d5445ca175002cbe7b277c912b248b1022e1
```

## Clock Watch

- **Points:** 400
- **Flag:** `HIK_REV_BROKEN_TIME_0baa7ba0c14a0f468b018e1f4ccc35ac`
- **Artifact SHA-256:** `f6632cc5cf1a0f4e26b53456cab96d839ef7ee7432db688eedb5d6db0d1f57f3`

The anti-analysis routine checked `TracerPid`, parent names, tool names and integrity. Temporarily forcing it to return zero exposed the authentic hash input:

```text
61506bd3579b890a9397e67d59965ab5117c36a41dcddeb83126db3191ad36a7
```

## Last Sample

- **Points:** 400
- **Flag:** `HIK_REV_MAZE_1936974997aaf7df71df7b0f82ff19cf`
- **Artifact SHA-256:** `cbc3c352ac89326bf62bef2fca7b9d623b0d3a94e611f63b3a68c422ee41276d`

The final verifier combined the `MAZE`, `FLAT`, `TFVM` and `ICHN` formats from earlier challenges. Instead of rebuilding all four, execution was stopped after the checker reconstructed the final value:

```text
e6453a3c167eb3a14419a7acea3e64a90a1dd8f2847ccac3fdc096017411905b
```

## Twin Checkers

- **Points:** 450
- **Flag:** `HIK_REV_TWO_FACED_2feacb1ac356ec9179938d619540004a`
- **Artifact SHA-256:** `05f83db6aaa25fd2376a6a05b0f39147cf42b49582c74c33072834318c211815`

The detected and clean environments used different buffers. Forcing the authentic path and stopping before the final hash recovered:

```text
8449a5056d72a7156b3043c436fc0ae1a7b9debd794c7751644477560da34af3
```

## Main lesson

Do not automatically turn reverse engineering into full decompilation. When the program must eventually materialize a secret to compare or hash it, a carefully chosen dynamic observation point can be both faster and more reliable—provided the clean path and the decoy path are distinguished first.
