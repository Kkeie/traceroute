#!/usr/bin/env python3
import platform
import socket
import sys
import time

from scapy.layers.inet import IP, ICMP, TCP, conf
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest
from scapy.sendrecv import sr1

from tracerouteResult import TracerouteResult
from settings import *


class MainTraceroute:
    def __init__(self, settings: TracerouteSettings) -> None:
        self.settings = settings
        self._target_host = settings.target_host
        self._max_ttl = settings.max_ttl
        self._num_probes = settings.num_probes
        self._timeout = settings.timeout
        self._interval = settings.interval
        self._packet_size = settings.packet_size
        self._port = settings.port
        self._resolve_dns = settings.resolve_dns
        self._use_ipv6 = settings.use_ipv6
        self._use_tcp = settings.use_tcp
        conf.verb = 2

        try:
            if self._use_ipv6:
                addr_info = socket.getaddrinfo(self._target_host, self._port, socket.AF_INET6, socket.SOCK_STREAM)
                self._target_addr = addr_info[0][4][0]
                self._ip_proto = IPv6
            else:
                addr_info = socket.getaddrinfo(self._target_host, self._port, socket.AF_INET, socket.SOCK_STREAM)
                self._target_addr = addr_info[0][4][0]
                self._ip_proto = IP
        except socket.gaierror as e:
            print(f"Не удалось разрешить хост '{self._target_host}': {e}")
            sys.exit(1)

    def run(self) -> None:
        ip_mode = IpMode.IPV6 if self._use_ipv6 else IpMode.IPV4
        protocol = Protocol.TCP if self._use_tcp else Protocol.ICMP
        print(
            f"Traceroute to {self._target_host} ({self._target_addr}), {self._max_ttl} hops max, {ip_mode}, {protocol}")

        for ttl in range(1, self._max_ttl + 1):
            hop_results: list[float | None] = []
            current_hop_ip: str | None = None

            for probe in range(1, self._num_probes + 1):
                if self._use_ipv6:
                    if self._use_tcp:
                        pkt = self._ip_proto(dst=self._target_addr, hlim=ttl) / TCP(dport=self._port, flags='S') / (
                                "X" * self._packet_size)
                    else:
                        pkt = self._ip_proto(dst=self._target_addr, hlim=ttl) / ICMPv6EchoRequest() / (
                                "X" * self._packet_size)
                else:
                    if self._use_tcp:
                        pkt = self._ip_proto(dst=self._target_addr, ttl=ttl) / TCP(dport=self._port, flags='S') / (
                                "X" * self._packet_size)
                    else:
                        pkt = self._ip_proto(dst=self._target_addr, ttl=ttl) / ICMP() / ("X" * self._packet_size)

                send_time = time.time()
                try:
                    # Отправляем пакет и ожидаем ответ
                    reply = sr1(pkt, verbose=0, timeout=self._timeout)
                except PermissionError:
                    print("Operation not permitted. Are you running as Administrator/root?")
                    sys.exit(1)
                except Exception as e:
                    print(f"Error sending packet: {e}")
                    sys.exit(1)

                rtt = None
                if reply:
                    rtt = (time.time() - send_time) * 1000  # RTT в миллисекундах
                    current_hop_ip = reply.src
                hop_results.append(rtt)

                time.sleep(self._interval)

            # Разрешение DNS-имен, если включено
            if current_hop_ip and self._resolve_dns:
                try:
                    hostname = socket.gethostbyaddr(current_hop_ip)[0]
                except socket.herror:
                    hostname = current_hop_ip
            else:
                hostname = current_hop_ip if current_hop_ip else "*"

            # Создание объекта результата трассировки
            result = TracerouteResult(ttl, hostname, hop_results)
            print(result)

            # Проверка, достигли ли мы целевого хоста
            if current_hop_ip == self._target_addr:
                break

        print("Trace complete.")

