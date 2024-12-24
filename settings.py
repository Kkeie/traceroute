#!/usr/bin/env python3
from pydantic import Field
from pydantic_settings import BaseSettings
import enum


class TracerouteSettings(BaseSettings):
    target_host: str = Field(..., description="Целевой хост или IP-адрес для трассировки.")
    max_ttl: int = Field(30, ge=1, le=255, description="Максимальное количество хопов (TTL).")
    num_probes: int = Field(3, ge=1, le=10, description="Количество запросов на каждый хоп.")
    timeout: float = Field(2.0, ge=0.1, le=10.0, description="Таймаут ожидания ответа (секунды).")
    interval: float = Field(0.5, ge=0.0, le=5.0, description="Интервал между запросами (секунды).")
    port: int = Field(80, ge=1, le=65535, description="TCP-порт для трассировки (при использовании TCP).")
    resolve_dns: bool = Field(False, description="Разрешать IP-адреса в DNS-имена.")
    use_ipv6: bool = Field(False, description="Использовать IPv6 вместо IPv4.")
    use_tcp: bool = Field(False, description="Использовать TCP SYN вместо ICMP.")
    packet_size: int = Field(64, ge=1, le=65535, description="Размер пакета в байтах.")

    class Config:
        env_prefix = 'TRACEROUTE_'
        env_file = '.env'
        env_file_encoding = 'utf-8'


class IpMode(enum.StrEnum):
    IPV4 = "IPv4"
    IPV6 = "IPv6"


class Protocol(enum.StrEnum):
    ICMP = "ICMP"
    TCP = "TCP SYN"
