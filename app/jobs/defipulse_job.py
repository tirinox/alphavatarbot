import logging
from typing import List

import aioredis
import typing

from jobs.base import BaseFetcher, INotified
from lib.datetime import parse_timespan_to_seconds
from lib.depcont import DepContainer

from models.models import DefiPulseEntry


class DefiPulseFetcher(BaseFetcher):
    URL_DEFI_PULSE_PROJECTS = 'https://data-api.defipulse.com/api/v1/defipulse/api/GetProjects?api-key={api_key}'
    ALPHA_NAME = 'Alpha Homora'

    def __init__(self, deps: DepContainer):
        cfg = deps.cfg.data_source.defi_pulse
        super().__init__(deps, parse_timespan_to_seconds(cfg.fetch_period))
        self._defipulse_api_key = cfg.api_token

    async def fetch(self):
        return await self._fetch_defipulse()

    async def _fetch_defipulse(self):
        url = self.URL_DEFI_PULSE_PROJECTS.format(api_key=self._defipulse_api_key)
        async with self.deps.session.get(url) as reps:
            response_j = await reps.json()
            return self.parse_defipulse(response_j)

    @staticmethod
    def parse_defipulse(response):
        return [DefiPulseEntry.parse(item) for item in response]


class DefiPulseKeeper(INotified):
    KEY_DEFIPULSE = 'defipulse:alpha:last'
    KEY_TLV_ATH_USD = 'defipulse:alpha:tlv_ath_usd'

    def __init__(self, deps: DepContainer):
        self.deps = deps
        self.logger = logging.getLogger(self.__class__.__name__)

    async def on_data(self, sender, data: List[DefiPulseEntry]):
        alpha: DefiPulseEntry = self.find_alpha(data)
        if not alpha:
            self.logger.error('no alpha found!')
            return

        prev_alpha: DefiPulseEntry = await self.get_last_state()
        if prev_alpha:
            alpha.rank_delta = alpha.rank - prev_alpha.rank

        r: aioredis.Redis = await self.deps.db.get_redis()

        prev_tlv_ath = float((await r.get(self.KEY_TLV_ATH_USD)) or 0.0)
        if alpha.tlv_usd > prev_tlv_ath:
            await r.set(self.KEY_TLV_ATH_USD, alpha.tlv_usd)
            self.logger.info(f'updated TLV ATH ${prev_tlv_ath} -> ${alpha.tlv_usd}')
            alpha.tlv_is_ath = True

        await r.set(self.KEY_DEFIPULSE, alpha.to_json())

    async def get_last_state(self) -> typing.Optional[DefiPulseEntry]:
        r: aioredis.Redis = await self.deps.db.get_redis()
        data = await r.get(self.KEY_DEFIPULSE)
        return DefiPulseEntry.from_json(data) if data else None

    @staticmethod
    def find_alpha(items: List[DefiPulseEntry]):
        return next((item for item in items if item.name == DefiPulseFetcher.ALPHA_NAME), None)
