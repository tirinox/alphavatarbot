from dataclasses import dataclass


@dataclass
class DefiPulseEntry:
    category: str = ''
    chain: str = ''
    id: int = 0
    name: str = 'no_name'
    tlv_usd: float = 0.0
    tlv_usd_relative_1d: float = 0.0

    @classmethod
    def from_json(cls, j):
        tlv_usd = j.get('value', {}).get('tvl', {}).get('USD', {})
        return cls(
            category=j.get('category', ''),
            chain=j.get('chain', ''),
            id=int(j.get('id', 0)),
            name=j.get('name', ''),
            tlv_usd=float(tlv_usd.get('value', 0.0)),
            tlv_usd_relative_1d=float(tlv_usd.get('relative_1d', 0.0))
        )