

class TracerouteResult:
    def __init__(self, hop_number: int, ip_address: str | None, rtts: list[float | str]) -> None:
        self._hop_number = hop_number
        self._ip_address = ip_address
        self._rtts = rtts

    def __str__(self) -> str:
        if self._ip_address is None:
            return f"{self._hop_number:2d}  *"
        else:
            rtt_str_list = []
            for r in self._rtts:
                if r is None:
                    rtt_str_list.append("*")
                else:
                    rtt_str_list.append(f"{r:.3f} ms")
            return f"{self._hop_number:2d}  {self._ip_address:<15}  " + "  ".join(rtt_str_list)