#!/usr/bin/env python3
from pydantic_settings import BaseSettings
from pydantic import Field


class TracerouteSettings(BaseSettings):
    target_host: str = Field(..., description="Целевой хост или IP-адрес для трассировки.")
    max_ttl: int = Field(30, ge=1, le=255, description="Максимальное количество хопов (TTL).")
    num_probes: int = Field(3, ge=1, le=10, description="Количество запросов на каждый хоп.")
    timeout: float = Field(2.0, ge=0.1, le=10.0, description="Таймаут ожидания ответа на каждый запрос (секунды).")
    interval: float = Field(0.5, ge=0.0, le=5.0, description="Интервал между запросами на один хоп (секунды).")
    packet_size: int = Field(40, ge=8, le=1500, description="Размер полезной нагрузки ICMP-пакета (байты).")

    class Config:
        env_prefix = 'TRACEROUTE_'
        env_file = '.env'
        env_file_encoding = 'utf-8'
