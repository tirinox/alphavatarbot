from typing import List

from jobs.base import BaseFetcher
from lib.depcont import DepContainer

from models.models import DefiPulseEntry


class DefiPulseFetcher(BaseFetcher):
    URL_DEFI_PULSE_PROJECTS = 'https://data-api.defipulse.com/api/v1/defipulse/api/GetProjects?api-key={api_key}'
    ALPHA_NAME = 'Alpha Homora'

    def __init__(self, deps: DepContainer, sleep_period=60):
        super().__init__(deps, sleep_period)
        self._defipulse_api_key = deps.cfg.data_source.defi_pulse.api_token

    async def fetch(self):
        return self._fetch_defipulse()

    async def _fetch_defipulse(self):
        url = self.URL_DEFI_PULSE_PROJECTS.format(api_key=self._defipulse_api_key)
        async with self.deps.session.get(url) as reps:
            response_j = await reps.json()
            return self.parse_defipulse(response_j)

    @staticmethod
    def parse_defipulse(response):
        return [DefiPulseEntry.from_json(item) for item in response]

    @staticmethod
    def find_alpha(items: List[DefiPulseEntry]):
        return next((item for item in items if item.name == DefiPulseFetcher.ALPHA_NAME), None)
