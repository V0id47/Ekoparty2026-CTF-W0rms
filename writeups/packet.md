# Packet / Network

The captures included deliberate prompt-injection strings in headers and payloads. They were treated as hostile packet data, never as analysis instructions.

## Night Shift

- **Points:** 100
- **Flag:** `HIK_PACKET_BASIC_a17b8d11800c826c22dc09aca15ee97d`

The service generated an ephemeral PCAP. Most HTTP traffic was noise. The relevant flow targeted TCP port `4444`: one client completed the `HELLO` / `WHO` exchange, sent 81-byte binary frames and emitted `id=vlan10-night` by UDP. The validator expected the source and destination endpoint in this exact form:

```text
<SOURCE_IP>:<DESTINATION_IP>:4444
```

The important step was correlating protocol behavior across TCP and UDP rather than trusting readable headers.

## Side Door

- **Points:** 250
- **Flag:** `HIK_PACKET_SCAN_def07827464867d32d2d58334f159ceb`

The capture showed one origin performing a port-knocking sequence against three consecutive high ports. Immediately afterwards, the same origin received a SYN-ACK on a nonstandard SSH-like port, completed the connection and transmitted a `4 + 96` byte length-prefixed record. A second scanner generated plausible noise but never completed both the knock and the follow-up exchange.

The accepted flag was retained, but the exact ephemeral `(sid, answer, pcap)` tuple from the winning session was not. We therefore do not invent a proof formula beyond the evidence preserved during the event.

## Helpdesk

- **Points:** 300
- **Flag:** `HIK_PACKET_SESSION_8e683d5a042c1513c06302183a52d416`

The advanced Packet services bound answers to the current capture and session:

```python
proof = sha256_hex(sid + ":" + answer + ":" + sha256_hex(pcap))
```

The accepted flag was preserved; the winning PCAP and ephemeral `sid` were not. This writeup intentionally distinguishes the confirmed flag from session material that cannot be reproduced after shutdown.

## Operational lesson

For rotating capture services, archive these four items atomically before attempting derivations:

```text
timestamp + sid + raw PCAP + server response
```

Mixing ranges, frames or identifiers from adjacent cycles can preserve valid lengths while silently creating a false object.

