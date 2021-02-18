import asyncio

from jobs.price_job import PriceFetcher, CoinPriceInfo
from main import App


class TestApp(App):
    async def _run_background_jobs(self):
        pf = PriceFetcher(self.deps)
        rank, price_info = await pf.fetch()
        print(f"rank = {rank}; price info = {price_info}")


if __name__ == '__main__':
    TestApp().run_bot()
