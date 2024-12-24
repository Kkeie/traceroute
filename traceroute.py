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
              help='Таймаут ожидания ответа на каждый запрос (секунды).')
@click.option('--interval', default=0.5, show_default=True, type=click.FloatRange(0.0, 5.0),
              help='Интервал между запросами на один хоп (секунды).')
@click.option('--packet-size', default=40, show_default=True, type=click.IntRange(8, 1500),
              help='Размер полезной нагрузки ICMP-пакета (байты).')
def traceroute(host, max_ttl, num_probes, timeout, interval, packet_size):
    settings = TracerouteSettings(
        target_host=host,
        max_ttl=max_ttl,
        num_probes=num_probes,
        timeout=timeout,
        interval=interval,
        packet_size=packet_size
    )

    tracer = MainTraceroute(settings=settings)
    tracer.run()


if __name__ == "__main__":
    traceroute()
