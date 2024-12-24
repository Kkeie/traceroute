#!/usr/bin/env python3

class TracerouteResult:
    def __init__(self, ttl: int, host: str, rtts: list[float | None]) -> None:
        self.ttl = ttl
        self.host = host
        self.rtts = rtts

    def __str__(self) -> str:
        rtt_strs = []
        for rtt in self.rtts:
            if rtt is None:
                rtt_strs.append("*")
            else:
                rtt_strs.append(f"{rtt:.2f} ms")
        return f"{self.ttl}\t{self.host}\t" + "\t".join(rtt_strs)
