import asyncio

from jobs.base import BaseFetcher, INotified
from lib.datetime import parse_timespan_to_seconds
from lib.depcont import DepContainer
from models.models import CoinPriceInfo


class PriceFetcher(BaseFetcher):
    ALPHA_GECKO_NAME = 'alpha-finance'
    COIN_RANK_GECKO = "https://api.coingecko.com/api/v3/coins/{coin}?" \
                      "localization=false&tickers=false&market_data=false&" \
                      "community_data=false&developer_data=false&sparkline=false"

    COIN_PRICE_GECKO = "https://api.coingecko.com/api/v3/simple/price?" \
                       "ids={coin}&vs_currencies=usd%2Cbtc&include_market_cap=true&include_24hr_change=true"

    def __init__(self, deps: DepContainer):
        cfg = deps.cfg.data_source.coin_gecko
        super().__init__(deps, parse_timespan_to_seconds(cfg.fetch_period))

    async def fetch(self) -> CoinPriceInfo:
        rank, price_data = await asyncio.gather(self._fetch_rank(), self._fetch_price())
        price_data.rank = rank
        return price_data

    async def _fetch_price(self):
        url = self.COIN_PRICE_GECKO.format(coin=self.ALPHA_GECKO_NAME)
        async with self.deps.session.get(url) as reps:
            response_j = await reps.json()
            result = CoinPriceInfo(**response_j.get(self.ALPHA_GECKO_NAME, {}))
            return result

    async def _fetch_rank(self) -> int:
        url = self.COIN_RANK_GECKO.format(coin=self.ALPHA_GECKO_NAME)
        async with self.deps.session.get(url) as reps:
            response_j = await reps.json()
            return int(response_j.get('market_cap_rank', 0))


class PriceHandler(INotified):
    def __init__(self, deps: DepContainer):
        self.deps = deps

    async def on_data(self, sender, data):
        rank, price_data = data
        print(f'rank = {rank}, data = {price_data}')