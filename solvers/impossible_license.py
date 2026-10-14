#!/usr/bin/env python3
import base64
import re
import socket
import struct


HOST = "127.0.0.1"
PORT = 31337
MOD = 1 << 32
MASK = MOD - 1
CTX_B64 = "+0xoljPDdWdfwhR11/l107kJ2kdfDZWW1VplCYt9JW0EAAAAAwAAABAAAAASAAAABwAAABMAAAAHAAAAGgAAAAoAAAATAAAAGwAAAAIAAAAaAAAABgAAAAQAAAADAAAAPjbM8cF0hV2hH5ShEyIZYvc6osUHYLqTsVovOIQaJ7Mq31UhTDC4vzjc/yctAPRNSDDjTDRQXK9NchYae0iaTPErlQN7UqqKQVGU92vb6OJZKkn/H/E7Qjf+UkzxRjIcHQAAABkAAAAKAAAAEwAAAAUAAAAFAAAABwAAAAsAAACc7ATyGzEng/TyRIOr54sCiEjV0n6KP0zRMVpR+OFkBQIAAAAHAAAAAwAAAAUAAAAAAAAABAAAAAYAAAABAAAAAQAAAPtk0ecYxf7v53f9NcEqEVnStP7YxtarotNuggxrQIzi6vQHDTM1VebYMMfAeOyD/chCENH8uWYP8b0Uu5kI0mYsiSg5PCPC1yWsJhZ9+9IjyovM+HdM2zP7lnDt6EFe7Iq85K9Y4cR/daBa+S7n0GY9hVis9UWlENUPSGkWwBzvtHEBBCAn+qHB7yfAgT3x5rXCII1P/v5mKJE6vR0g4xIfTycfEstFJsK4DKw5QtgK3Fev+Y/u6j+rxXi5oBNXNT2zM6jeCiXMYF9phHqBl8XvMlz4CK6vMiZQ/VqoT/gv+jBZfy2RHnmrLffZ/eWOfqrJ/Gc0nxmSbijF8A=="
CTX = list(struct.unpack("<136I", base64.b64decode(CTX_B64)))


def rol(value: int, count: int) -> int:
    count &= 31
    return ((value << count) | (value >> (32 - count))) & MASK if count else value


def ror(value: int, count: int) -> int:
    count &= 31
    return ((value >> count) | (value << (32 - count))) & MASK if count else value


def matrix_inverse(matrix: list[list[int]]) -> list[list[int]]:
    size = len(matrix)
    augmented = [
        matrix[row][:] + [int(row == col) for col in range(size)]
        for row in range(size)
    ]
    for col in range(size):
        pivot = next(row for row in range(col, size) if augmented[row][col] & 1)
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        inverse = pow(augmented[col][col], -1, MOD)
        augmented[col] = [(value * inverse) & MASK for value in augmented[col]]
        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [
                (augmented[row][i] - factor * augmented[col][i]) & MASK
                for i in range(size * 2)
            ]
    return [row[size:] for row in augmented]


MATRIX = [[CTX[72 + row * 8 + col] for col in range(8)] for row in range(8)]
MATRIX_INV = matrix_inverse(MATRIX)
PERMUTATION = CTX[64:72]


def keygen(identifier: str) -> str:
    product = [int(identifier[i : i + 8], 16) for i in range(0, 32, 8)]

    round_bias = [
        rol(CTX[24 + i] ^ product[i % 4], CTX[16 + i]) for i in range(8)
    ]
    state = [
        (
            rol(product[i % 4], CTX[48 + i])
            + CTX[40 + i] * product[(i + 1) % 4]
        )
        & MASK
        ^ CTX[56 + i]
        for i in range(8)
    ]

    for round_number in range(7, -1, -1):
        matrix_output = [0] * 8
        for i in range(8):
            matrix_output[PERMUTATION[i]] = state[i]

        before_matrix = [
            sum(MATRIX_INV[row][col] * matrix_output[col] for col in range(8))
            & MASK
            for row in range(8)
        ]
        state = [
            (
                ror(before_matrix[i], CTX[8 + i])
                * pow(CTX[i], -1, MOD)
                - CTX[32 + round_number]
                - round_bias[i]
            )
            & MASK
            for i in range(8)
        ]

    return "-".join(f"{word:08X}" for word in state)


def main() -> None:
    with socket.create_connection((HOST, PORT)) as sock:
        stream = sock.makefile("rwb", buffering=0)
        while line := stream.readline():
            text = line.decode(errors="replace")
            print(text, end="")
            match = re.search(r"PRODUCT_ID ([0-9A-F]{32})", text)
            if match:
                serial = keygen(match.group(1))
                print(serial)
                stream.write((serial + "\n").encode())


if __name__ == "__main__":
    main()
