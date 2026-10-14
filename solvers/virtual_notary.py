#!/usr/bin/env python3
import base64
import re
import socket
import struct

import z3


HOST = "127.0.0.1"
PORT = 31337
PROGRAM_B64 = "Eg4AAAAAAAASBwEAAAAAABUODgcAAAAAEgcCAAAAAAAVDg4HAAAAABIHAwAAAAAAFQ4OBwAAAAAQBwAAoXi51BUODgcAAAAAEgEAAAAAAAAQAgAAnHW9TRUBAQIAAAAAEQAAAAAAAAAVAAABAAAAABcAAAAXAAAAEAIAAJNakRcWAAACAAAAABIDAQAAAAAAFwMDAB4AAAATAAADAAAAABUOAA4AAAAAEgQAAAAAAAAQBQAAT3tXKhYEBAUAAAAAEAYAAMbiguMVBAQGAAAAABsOBAAAAAAAEgEBAAAAAAAQAgAA0cD1lBUBAQIAAAAAEQABAAAAAAAVAAABAAAAABcAAAAVAAAAEAIAAIMgR7oWAAACAAAAABIDAgAAAAAAFwMDAB4AAAATAAADAAAAABUOAA4AAAAAEgQBAAAAAAAQBQAAQyxJ/RYEBAUAAAAAEAYAAHcTuPAVBAQGAAAAABsOBAAAAAAAEgECAAAAAAAQAgAAAxaMshUBAQIAAAAAEQACAAAAAAAVAAABAAAAABcAAAAbAAAAEAIAAPntULMWAAACAAAAABIDAwAAAAAAFwMDABsAAAATAAADAAAAABUOAA4AAAAAEgQCAAAAAAAQBQAAb8r79RYEBAUAAAAAEAYAAPAAi/wVBAQGAAAAABsOBAAAAAAAEgEDAAAAAAAQAgAAbTpMAxUBAQIAAAAAEQADAAAAAAAVAAABAAAAABcAAAALAAAAEAIAAHMrsk4WAAACAAAAABIDAAAAAAAAFwMDAA4AAAATAAADAAAAABUOAA4AAAAAEgQDAAAAAAAQBQAAf/kHFRYEBAUAAAAAEAYAAAwUmjsVBAQGAAAAABsOBAAAAAAAEgEAAAAAAAAQAgAA//kOtBUBAQIAAAAAEQAEAAAAAAAVAAABAAAAABcAAAAYAAAAEAIAAE3w480WAAACAAAAABIDAQAAAAAAFwMDAAUAAAATAAADAAAAABUOAA4AAAAAEgQAAAAAAAAQBQAAHfdk7RYEBAUAAAAAEAYAAIF08dkVBAQGAAAAABsOBAAAAAAAEgEBAAAAAAAQAgAAz+qFBRUBAQIAAAAAEQAFAAAAAAAVAAABAAAAABcAAAAEAAAAEAIAAHXcs78WAAACAAAAABIDAgAAAAAAFwMDABYAAAATAAADAAAAABUOAA4AAAAAEgQBAAAAAAAQBQAAs0qHpBYEBAUAAAAAEAYAAK6lMOMVBAQGAAAAABsOBAAAAAAAEgECAAAAAAAQAgAApwgyCxUBAQIAAAAAEQAGAAAAAAAVAAABAAAAABcAAAABAAAAEAIAACcO5ZsWAAACAAAAABIDAwAAAAAAFwMDAAEAAAATAAADAAAAABUOAA4AAAAAEgQCAAAAAAAQBQAAI5REWRYEBAUAAAAAEAYAAEa1XJ0VBAQGAAAAABsOBAAAAAAAEgEDAAAAAAAQAgAAvJ8TyBUBAQIAAAAAEQAHAAAAAAAVAAABAAAAABcAAAALAAAAEAIAAA9dbA0WAAACAAAAABIDAAAAAAAAFwMDAAsAAAATAAADAAAAABUOAA4AAAAAEgQDAAAAAAAQBQAAmW0+cBYEBAUAAAAAEAYAAJ9Qc9YVBAQGAAAAABsOBAAAAAAAHwAAAAAAAAA="
PROGRAM = base64.b64decode(PROGRAM_B64)


def keygen(identifier: str) -> str:
    product = [
        z3.BitVecVal(int(identifier[i : i + 8], 16), 32)
        for i in range(0, 32, 8)
    ]
    serial = [z3.BitVec(f"s{i}", 32) for i in range(8)]
    regs = [z3.BitVecVal(0, 32) for _ in range(16)]
    solver = z3.Solver()

    for offset in range(0, len(PROGRAM), 8):
        op, dst, left, right, imm = struct.unpack_from("<BBBBI", PROGRAM, offset)
        dst &= 0xF
        left &= 0xF
        right &= 0xF

        if op == 0x10:
            regs[dst] = z3.BitVecVal(imm, 32)
        elif op == 0x11:
            regs[dst] = serial[left & 7]
        elif op == 0x12:
            regs[dst] = product[left & 3]
        elif op == 0x13:
            regs[dst] = regs[right] + regs[left]
        elif op == 0x14:
            regs[dst] = regs[left] - regs[right]
        elif op == 0x15:
            regs[dst] = regs[right] ^ regs[left]
        elif op == 0x16:
            regs[dst] = regs[right] * regs[left]
        elif op == 0x17:
            regs[dst] = z3.RotateLeft(regs[left], imm & 31)
        elif op == 0x18:
            regs[dst] = z3.RotateRight(regs[left], imm & 31)
        elif op == 0x19:
            regs[dst] = regs[right] & regs[left]
        elif op == 0x1A:
            regs[dst] = regs[right] | regs[left]
        elif op == 0x1B:
            solver.add(regs[dst] == regs[left])
        elif op == 0x1F:
            break
        else:
            raise ValueError(f"unknown opcode {op:#x} at {offset:#x}")

    if solver.check() != z3.sat:
        raise RuntimeError("unsatisfiable license")
    model = solver.model()
    return "-".join(
        f"{model.eval(word, model_completion=True).as_long():08X}" for word in serial
    )


def main() -> None:
    with socket.create_connection((HOST, PORT)) as sock:
        stream = sock.makefile("rwb", buffering=0)
        while line := stream.readline():
            text = line.decode(errors="replace")
            print(text, end="")
            match = re.search(r"LICENSE_ID ([0-9A-F]{32})", text)
            if match:
                answer = keygen(match.group(1))
                print(answer)
                stream.write((answer + "\n").encode())


if __name__ == "__main__":
    main()
