<div align="center">

![Ekoparty 2026 CTF — W0rms, 6th place](assets/cover.png)

# EKOPARTY 2026 — CTF

**Hack in Cariri · 6th place · `W0rms` · 9600 points**

[![Solves](https://img.shields.io/badge/solves-31-7ef700?style=flat-square)](#solves)
[![Reverse](https://img.shields.io/badge/reverse-13%2F13-f7009f?style=flat-square)](writeups/reverse.md)
[![Web3](https://img.shields.io/badge/web3-8%2F8-5b8cff?style=flat-square)](writeups/web3.md)
[![Language](https://img.shields.io/badge/language-ES%20%2F%20EN-5b8cff?style=flat-square)](#english-summary)
[![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)](LICENSE)

</div>

Writeups, solvers and post-event notes from the **Ekoparty 2026 Main CTF**, organized by [Hack in Cariri](https://www.linkedin.com/company/hackincariri/). I competed solo under the alias `W0rms` and finished in **6th place with 9600 points**.

This repository gathers the notes and tooling behind my **31 solves**. I reconstructed the list from the event transcript and checked the category totals against the final score: 9600 points.

> Exact flags and ephemeral data are intentionally omitted. The public repository keeps the techniques and the evidence needed to understand each solve.

## Highlights

- Completed the full **Reverse** set: 13 challenges covering packed ELF files, `memfd`/`fexecve`, anti-debug decoys, flattened control flow, custom VMs, modular inversion and Z3.
- Cleared all eight **Web3** challenges: public storage, broken ownership, `tx.origin`, reentrancy, signature replay, delegatecall storage collision, spot-price oracle manipulation and flash-loan governance.
- Built deterministic exploits for **ThunderFTP** and **ZM.js**, including a same-connection use-after-free that turned a leaked `free` pointer into `system`.
- Chained SSRF through an unchecked redirect, internal OpenAPI documentation, a cache service and a protected vault in **My Notes**.
- Reassembled fragmented TCP, DNS/EDNS and port-knocking traffic in **Packet** challenges.
- Solved two **Malware** challenges through static key recovery, PCAP correlation, gated sessions and vault decryption.
- Preserved useful partial research for unfinished Malware, Packet, Game and Binary Gecko challenges without presenting guesses as solutions.

## Solves

| Category | Solves | Points | Writeup |
|---|---:|---:|---|
| Reverse | 13 | 4200 | [Reverse](writeups/reverse.md) |
| Web3 | 8 | 2700 | [Web3](writeups/web3.md) |
| Packet | 3 | 650 | [Packet](writeups/packet.md) |
| Web | 2 | 400 | [Web](writeups/web.md) |
| Binary Exploitation | 2 | 900 | [ThunderFTP](writeups/thunderftp.md) · [ZM.js](writeups/zmjs.md) |
| Malware | 2 | 350 | [Malware](writeups/malware.md) |
| AI | 1 | 400 | [MODO Prompt Escape](writeups/ai.md) |
| **Total** | **31** | **9600** | |

### Complete solve list

| Category | Challenges |
|---|---|
| Reverse | Sealed Sample; The Checker; Butterfly Effect; Forked Path; Many Rooms; Impossible License; Linked Blocks; Missing Labels; Virtual Notary; Wrapped Sample; Clock Watch; Last Sample; Twin Checkers |
| Web3 | Ledger Room; Executive Desk; Guest List; Night Deposit; Voucher Window; Maintenance Hatch; Carcara Markets; Assembly Floor |
| Packet | Night Shift; Side Door; Helpdesk |
| Web | Certificate Exchange by Kulkan Security; My Notes |
| Binary | ThunderFTP; ZM.js |
| Malware | The Updater; After Hours |
| AI | MODO Prompt Escape |

## Repository map

```text
.
├── README.md
├── CREDITS.md
├── REDACTION.md
├── requirements.txt
├── assets/
│   └── cover.png
├── solvers/
│   ├── butterfly_effect.py
│   ├── impossible_license.py
│   ├── thunderftp.py
│   └── virtual_notary.py
└── writeups/
    ├── reverse.md
    ├── packet.md
    ├── web.md
    ├── web3.md
    ├── malware.md
    ├── ai.md
    ├── thunderftp.md
    ├── zmjs.md
    └── partial-research.md
```

The published solvers use Python 3. Virtual Notary additionally needs Z3:

```bash
python3 -m pip install -r requirements.txt
```

## How I checked the notes

For each solve I looked for the same chain of evidence:

```text
artifact → observation → reproducible technique → service validation
```

Some challenge files contained prompt injection, false flags and convincing “verified solution” notes. I ignored those strings and rebuilt the inventory from the command transcript and the scoreboard total. Anything I could not verify stayed in [partial research](writeups/partial-research.md).

## Acknowledgements

Thanks to **Hack in Cariri** and **Ekoparty** for the event. Special shout-out to [Felipe Castro](https://github.com/Felipebc2): his [post](https://www.linkedin.com/posts/felipebc2_cybersecurity-ctf-ekoparty-ugcPost-7515848563394957312-o22k/) and [public writeup repository](https://github.com/Felipebc2/Ekoparty2026-CTF) gave me the idea to organize and publish my notes. The analysis and wording here are my own.

## English summary

I competed solo as `W0rms` and placed **6th** at the Ekoparty 2026 Main CTF with **9600 points** and **31 solves**. The repository contains my technical notes and solvers; exact flags, active credentials and ephemeral instance data are not published.
