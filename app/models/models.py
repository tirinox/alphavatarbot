from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DefiPulseEntry:
    category: str = ''
    chain: str = ''
    id: int = 0
    name: str = 'no_name'
    tlv_usd: float = 0.0
    tlv_usd_relative_1d: float = 0.0

    @classmethod
    def parse(cls, j):
        tlv_usd = j.get('value', {}).get('tvl', {}).get('USD', {})
        return cls(
            category=j.get('category', ''),
            chain=j.get('chain', ''),
            id=int(j.get('id', 0)),
            name=j.get('name', ''),
            tlv_usd=float(tlv_usd.get('value', 0.0)),
            tlv_usd_relative_1d=float(tlv_usd.get('relative_1d', 0.0))
        )

    @property
    def rank(self):
        return self.id + 1


@dataclass
class CoinPriceInfo:
    usd: float = 0.0
    usd_market_cap: float = 0.0
    usd_24h_change: float = 0.0
    btc: float = 0.0
    btc_market_cap: float = 0.0
    btc_24h_change: float = 0.0
    rank: int = 0


REAL_REGISTERED_ATH = 2.93
REAL_REGISTERED_ATH_DATE = 1612367085


@dataclass
class PriceATH:
    ath_date: int = REAL_REGISTERED_ATH_DATE
    ath_price: float = REAL_REGISTERED_ATH

    def is_new_ath(self, price):
        return price and float(price) > 0 and float(price) > self.ath_price


@dataclass
class PriceHistoricalTriplet:
    price_1h: float = 0.0
    price_24h: float = 0.0
    price_7d: float = 0.0


@dataclass_json
@dataclass
class PriceReport:
    price_and_cap: CoinPriceInfo
    price_change: PriceHistoricalTriplet
    defipulse: DefiPulseEntry
    price_ath: PriceATH
    is_ath: bool = False
