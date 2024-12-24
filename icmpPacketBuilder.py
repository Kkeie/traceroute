#!/usr/bin/env python3
import struct


class IcmpPacketBuilder:
    """Class to build ICMP echo request packets (internal use)."""

    @staticmethod
    def _checksum(data: bytes) -> int:
        """
        Compute ICMP checksum.
        """
        total = 0
        length = len(data)
        count = 0
        # Perform 16-bit sums
        while count < (length - 1):
            total += (data[count] << 8) + data[count + 1]
            count += 2
        if length % 2 == 1:
            total += data[-1] << 8
        # Fold 32-bit sum into 16 bits
        while (total >> 16) > 0:
            total = (total & 0xFFFF) + (total >> 16)
        return ~total & 0xFFFF

    @staticmethod
    def build_echo_request(
            packet_id: int,
            sequence_number: int,
            packet_size: int
    ) -> bytes:
        """
        Build an ICMP echo request packet with given packet ID, sequence number, and payload size.
        """
        icmp_type = 8  # Echo request
        icmp_code = 0
        icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, 0, packet_id, sequence_number)
        payload = bytes(packet_size)
        chksum = IcmpPacketBuilder._checksum(icmp_header + payload)
        icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, chksum, packet_id, sequence_number)
        return icmp_header + payload
