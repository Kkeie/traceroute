#!/usr/bin/env python3
import click
from maintraceroute import MainTraceroute
from settings import TracerouteSettings


@click.command()
@click.argument('host')
@click.option('--max-ttl', default=30, show_default=True, type=click.IntRange(1, 255),
              help='Максимальное количество хопов (TTL).')
@click.option('--num-probes', default=3, show_default=True, type=click.IntRange(1, 10),
              help='Количество запросов на каждый хоп.')
@click.option('--timeout', default=2.0, show_default=True, type=click.FloatRange(0.1, 10.0),
              help='Таймаут ожидания ответа (секунды).')
@click.option('--interval', default=0.5, show_default=True, type=click.FloatRange(0.0, 5.0),
              help='Интервал между запросами (секунды).')
@click.option('--port', default=80, show_default=True, type=click.IntRange(1, 65535),
              help='TCP-порт для трассировки (при использовании TCP).')
@click.option('--ipv6', is_flag=True, help='Использовать IPv6 вместо IPv4.')
@click.option('--resolve-dns', is_flag=True, help='Разрешать IP-адреса в DNS-имена.')
@click.option('--tcp', is_flag=True, help='Использовать TCP SYN вместо ICMP.')
def traceroute(host, max_ttl, num_probes, timeout, interval, port, ipv6, resolve_dns, tcp) -> None:
    settings = TracerouteSettings(
        target_host=host,
        max_ttl=max_ttl,
        num_probes=num_probes,
        timeout=timeout,
        interval=interval,
        port=port,
        resolve_dns=resolve_dns,
        use_ipv6=ipv6,
        use_tcp=tcp,
        packet_size=64  # Добавлено значение по умолчанию
    )
    tracer = MainTraceroute(settings)
    tracer.run()


if __name__ == "__main__":
    traceroute()
