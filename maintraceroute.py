import platform
import socket
import struct
import sys
import time

import select

from icmpPacketBuilder import IcmpPacketBuilder
from tracerouteResult import TracerouteResult

class MainTraceroute:
    """
    Class implementing traceroute functionality.
    """

    def __init__(
        self,
        target_host: str,
        max_ttl: int = 30,
        num_probes: int = 3,
        timeout: float = 2.0,
        interval: float = 0.5,
        packet_size: int = 40
    ) -> None:
        self._target_host = target_host
        self._max_ttl = max_ttl
        self._num_probes = num_probes
        self._timeout = timeout
        self._interval = interval
        self._packet_size = packet_size

        # Resolve target address
        try:
            self._target_addr = socket.gethostbyname(self._target_host)
        except socket.gaierror as e:
            print(f"Failed to resolve host '{self._target_host}': {e}")
            sys.exit(1)

    def run(self) -> None:
        print(f"traceroute to {self._target_host} ({self._target_addr}), {self._max_ttl} hops max")

        icmp_proto = socket.getprotobyname("icmp")
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto)
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto)
        recv_socket.settimeout(self._timeout)

        pid = int(time.time() * 1000) & 0xFFFF

        current_os = platform.system()

        for ttl in range(1, self._max_ttl + 1):
            # Установка TTL с учётом платформы
            if current_os == "Windows":
                ttl_bytes = struct.pack('B', ttl)
            else:
                ttl_bytes = struct.pack('I', ttl)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl_bytes)

            hop_rtts: list[float | None] = []
            current_hop_ip: str | None = None

            for probe in range(self._num_probes):
                sequence_number = ttl * 256 + probe
                icmp_packet = IcmpPacketBuilder.build_echo_request(
                    packet_id=pid,
                    sequence_number=sequence_number,
                    packet_size=self._packet_size
                )

                start_time = time.time()
                try:
                    send_socket.sendto(icmp_packet, (self._target_addr, 0))
                except PermissionError:
                    print("Operation not permitted. Are you running as Administrator?")
                    sys.exit(1)

                response_ip, rtt = self._receive_response(recv_socket, pid, sequence_number, start_time)
                if response_ip:
                    current_hop_ip = response_ip
                hop_rtts.append(rtt)

                time.sleep(self._interval)

            result = TracerouteResult(ttl, current_hop_ip, hop_rtts)
            print(result)
            if current_hop_ip == self._target_addr:
                break

        send_socket.close()
        recv_socket.close()

    def _receive_response(
        self,
        recv_socket: socket.socket,
        pid: int,
        sequence_number: int,
        send_time: float
    ) -> tuple[str | None, float | None]:
        time_left = self._timeout
        current_os = platform.system()
        while True:
            start_select = time.time()
            ready = select.select([recv_socket], [], [], time_left)
            how_long_in_select = time.time() - start_select

            if ready[0] == []:
                # Timeout
                return None, None

            time_received = time.time()
            try:
                received_packet, addr = recv_socket.recvfrom(2048)
            except socket.timeout:
                return None, None

            # Parse outer IP header (assuming no IP options)
            # IP header is the first 20 bytes
            outer_ip_header = received_packet[:20]
            outer_icmp_header = received_packet[20:28]
            if len(outer_icmp_header) < 8:
                return None, None

            icmp_type, icmp_code, icmp_chksum, icmp_pkt_id, icmp_seq = struct.unpack("!BBHHH", outer_icmp_header)

            if icmp_type == 0 and icmp_pkt_id == pid and icmp_seq == sequence_number:
                # Echo reply matches our packet
                rtt = (time_received - send_time) * 1000.0
                return addr[0], rtt
            elif icmp_type == 11:
                inner_ip_header_offset = 28
                inner_ip_header = received_packet[inner_ip_header_offset:inner_ip_header_offset + 20]
                if len(inner_ip_header) < 20:
                    return None, None

                inner_version_ihl = inner_ip_header[0]
                inner_ihl = inner_version_ihl & 0x0F
                inner_ip_header_len = inner_ihl * 4
                inner_icmp_offset = inner_ip_header_offset + inner_ip_header_len
                inner_icmp_header = received_packet[inner_icmp_offset:inner_icmp_offset + 8]
                if len(inner_icmp_header) < 8:
                    return None, None

                inner_type, inner_code, inner_chksum, inner_id, inner_seq = struct.unpack("!BBHHH", inner_icmp_header)

                if inner_id == pid and inner_seq == sequence_number:
                    rtt = (time_received - send_time) * 1000.0
                    return addr[0], rtt

            time_left = time_left - how_long_in_select
            if time_left <= 0:
                return None, None

