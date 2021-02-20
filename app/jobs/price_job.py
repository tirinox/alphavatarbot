import asyncio
import datetime
from collections import namedtuple
from typing import List

from jobs.base import BaseFetcher, INotified
from jobs.defipulse_job import DefiPulseKeeper
from lib.cooldown import Cooldown, OnceADay
from lib.datetime import parse_timespan_to_seconds, now_ts, HOUR, MINUTE, DAY, delay_to_next_hour_minute, parse_time, \
    is_time_to_do
from lib.depcont import DepContainer
from lib.texts import MessageType
from lib.utils import circular_shuffled_iterator
from localization import LocalizationManager
from models.models import CoinPriceInfo, PriceReport, PriceHistoricalTriplet, DefiPulseEntry, PriceATH

PriceAndDate = namedtuple('PriceAndDate', ('timestamp', 'price'))


class PriceFetcher(BaseFetcher):
    ALPHA_GECKO_NAME = 'alpha-finance'
    COIN_RANK_GECKO = "https://api.coingecko.com/api/v3/coins/{coin}?" \
                      "localization=false&tickers=false&market_data=false&" \
                      "community_data=false&developer_data=false&sparkline=false"

    COIN_PRICE_GECKO = "https://api.coingecko.com/api/v3/simple/price?" \
                       "ids={coin}&vs_currencies=usd%2Cbtc&include_market_cap=true&include_24hr_change=true"

    COIN_PRICE_HISTORY_GECKO = "https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range?" \
                               "vs_currency=usd&from={t_from}&to={t_to}"

    def __init__(self, deps: DepContainer):
        cfg = deps.cfg.data_source.coin_gecko
        super().__init__(deps, parse_timespan_to_seconds(cfg.fetch_period))

    async def fetch(self) -> PriceReport:
        now = now_ts()
        rank, price_data, p_1h, p_24h, p_7d = await asyncio.gather(
            self._fetch_rank(),
            self._fetch_price(),
            self._fetch_price_history(t_from=now - HOUR - MINUTE * 5, t_to=now - HOUR + MINUTE * 5),
            self._fetch_price_history(t_from=now - DAY - MINUTE * 15, t_to=now - DAY + MINUTE * 15),
            self._fetch_price_history(t_from=now - DAY * 7 - HOUR, t_to=now - DAY * 7 + HOUR),
        )
        price_data: CoinPriceInfo
        price_data.rank = rank

        return PriceReport(
            price_and_cap=price_data,
            price_change=PriceHistoricalTriplet(
                price_7d=p_7d[0].price,
                price_24h=p_24h[0].price,
                price_1h=p_1h[0].price
            ),
            defipulse=DefiPulseEntry(),
            price_ath=PriceATH(),
            is_ath=False
        )

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

    async def _fetch_price_history(self, t_from, t_to) -> List[PriceAndDate]:
        url = self.COIN_PRICE_HISTORY_GECKO.format(coin=self.ALPHA_GECKO_NAME, t_from=t_from, t_to=t_to)
        async with self.deps.session.get(url) as reps:
            response_j = await reps.json()
            prices = response_j.get('prices', [])
            return [PriceAndDate(*p) for p in prices]


class PriceHandler(INotified):
    KEY_ATH = 'alpha:price:ath'

    def __init__(self, deps: DepContainer):
        self.deps = deps
        self.cfg = deps.cfg.notifications.price
        self.stickers = self.cfg.ath.stickers
        self.ath_sticker_iter = circular_shuffled_iterator(self.stickers)
        self.daily_once = OnceADay(self.deps.db, 'PriceDaily')

    async def get_prev_ath(self) -> PriceATH:
        try:
            await self.deps.db.get_redis()
            ath_str = await self.deps.db.redis.get(self.KEY_ATH)
            if ath_str is None:
                return PriceATH()
            else:
                return PriceATH.from_json(ath_str)
        except (TypeError, ValueError, AttributeError):
            return PriceATH()

    async def reset_ath(self):
        await self.deps.db.redis.delete(self.KEY_ATH)

    async def update_ath(self, price):
        last_ath = await self.get_prev_ath()
        if price and price > 0 and last_ath.is_new_ath(price):
            await self.deps.db.get_redis()
            await self.deps.db.redis.set(self.KEY_ATH, PriceATH(
                int(now_ts()), price
            ).to_json())
            return True
        return False

    async def send_ath_sticker(self):
        if self.ath_sticker_iter:
            sticker = next(self.ath_sticker_iter)
            user_lang_map = self.deps.broadcaster.telegram_chats_from_config(self.deps.loc_man)
            await self.deps.broadcaster.broadcast(user_lang_map.keys(), sticker, message_type=MessageType.STICKER)

    async def send_notification(self, p: PriceReport):
        loc_man: LocalizationManager = self.deps.loc_man
        text = loc_man.default.notification_text_price_update(p)
        user_lang_map = self.deps.broadcaster.telegram_chats_from_config(self.deps.loc_man)
        await self.deps.broadcaster.broadcast(user_lang_map.keys(), text)
        if p.is_ath:
            await self.send_ath_sticker()

    def _is_it_time_for_daily_message(self):
        h, m = parse_time(self.cfg.time_of_day)
        return is_time_to_do(h, m)

    async def on_data(self, sender, p: PriceReport):
        d: DefiPulseKeeper = self.deps.defipulse

        # p.price_and_cap.usd = 2.98  # todo: for ATH debugging

        p.defipulse = await d.get_last_state()
        p.price_ath = await self.get_prev_ath()
        p.is_ath = (await self.update_ath(p.price_and_cap.usd))

        if p.is_ath:
            await self.send_notification(p)
        elif self._is_it_time_for_daily_message():
            if await self.daily_once.can_do():
                await self.send_notification(p)
                await self.daily_once.write_today()
