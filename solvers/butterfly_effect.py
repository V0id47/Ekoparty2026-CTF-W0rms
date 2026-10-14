#!/usr/bin/env python3
import re
import socket
import sys

MASK = 0xFFFFFFFF
C = [
    0x2D2AFE11, 0x3B6A02FF, 0x0B82F90F, 0x3157079D,
    15, 1, 28, 22, 0xE6FBA04F, 9, 3, 0xBDA924DB,
    20, 0x2860F229, 12, 3, 3, 6, 9,
]


def rol(value: int, count: int) -> int:
    count &= 31
    if not count:
        return value & MASK
    return ((value << count) | (value >> (32 - count))) & MASK


def ror(value: int, count: int) -> int:
    return rol(value, 32 - (count & 31))


def sequence_for(id_hex: str) -> str:
    words = [int(id_hex[i:i + 8], 16) for i in range(0, 32, 8)]
    multipliers = C[:4]
    inverses = [pow(value, -1, 1 << 32) for value in multipliers]
    checkpoints = {C[16]: 0, C[17]: 1, C[18]: 2}

    current = words[0]
    side = words[2]
    state = words[1] & 3
    final_target = rol(words[0] ^ words[1] ^ words[2] ^ words[3], C[12]) ^ C[13]
    result = []

    for position in range(1, C[14] + 1):
        if position in checkpoints:
            index = checkpoints[position]
            target = (
                (index + 1) * words[1]
                + rol(words[3] ^ words[0], (index + 1) * C[10])
                + C[11]
            ) & MASK
        elif position == C[14]:
            target = final_target
        else:
            target = None

        if target is None:
            pulse = 0
        elif state == 0:
            pulse = (((target ^ side) - current) & MASK) * inverses[0] & MASK
        elif state == 1:
            pulse = (current ^ ror((target - side) & MASK, C[5])) * inverses[1] & MASK
        elif state == 2:
            pulse = ((target - (current ^ side)) & MASK) * inverses[2] & MASK
        else:
            pulse = ((ror(target ^ side, C[7]) - current) & MASK) * inverses[3] & MASK

        if state == 0:
            updated = ((current + pulse * C[0]) & MASK) ^ side
        elif state == 1:
            updated = (rol(current ^ (pulse * C[1] & MASK), C[5]) + side) & MASK
        elif state == 2:
            updated = ((current ^ side) + pulse * C[2]) & MASK
        else:
            updated = rol((current + pulse * C[3]) & MASK, C[7]) ^ side

        state = (state + 1 + (pulse & 1) + (current >> 31)) & 3
        side = (rol(side, C[9]) + C[8]) & MASK
        current = updated & MASK
        result.append(pulse)

    return "-".join(f"{value:08X}" for value in result)


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 31337
    with socket.create_connection((host, port), timeout=15) as sock:
        stream = sock.makefile("rwb", buffering=0)
        while line := stream.readline():
            text = line.decode(errors="replace")
            print(text, end="")
            match = re.search(r"ID ([0-9A-F]{32})", text)
            if match:
                answer = sequence_for(match.group(1))
                print(answer)
                stream.write((answer + "\n").encode())


if __name__ == "__main__":
    main()
