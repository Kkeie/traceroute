#!/usr/bin/env python3
from maintraceroute import MainTraceroute
import sys

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python traceroute.py <host> [max_ttl] [num_probes] [timeout] [interval] [packet_size]")
        sys.exit(1)

    target_host = sys.argv[1]
    max_ttl = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    num_probes = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
    interval = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
    packet_size = int(sys.argv[6]) if len(sys.argv) > 6 else 40

    tracer = MainTraceroute(
        target_host=target_host,
        max_ttl=max_ttl,
        num_probes=num_probes,
        timeout=timeout,
        interval=interval,
        packet_size=packet_size
    )
    tracer.run()


if __name__ == "__main__":
    main()
