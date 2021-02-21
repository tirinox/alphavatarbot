import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher, executor
from aiogram.types import *

from jobs.defipulse_job import DefiPulseFetcher, DefiPulseKeeper
from jobs.price_job import PriceFetcher, PriceHandler
from lib.broadcast import Broadcaster
from localization import LocalizationManager
from dialog import init_dialogs
from lib.config import Config
from lib.db import DB
from lib.depcont import DepContainer


class App:
    def __init__(self):
        d = self.deps = DepContainer()
        d.cfg = Config()

        log_level = d.cfg.get('log_level', logging.INFO)
        logging.basicConfig(
            level=logging.getLevelName(log_level),
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        logging.info('-' * 100)
        logging.info(f"Log level: {log_level}")

        d.loop = asyncio.get_event_loop()
        d.db = DB(d.loop)

    def create_bot_stuff(self):
        d = self.deps

        d.bot = Bot(token=d.cfg.telegram.bot.token, parse_mode=ParseMode.HTML)
        d.dp = Dispatcher(d.bot, loop=d.loop)
        d.loc_man = LocalizationManager()
        d.broadcaster = Broadcaster(d)

        init_dialogs(d)

    async def connect_chat_storage(self):
        if self.deps.dp:
            self.deps.dp.storage = await self.deps.db.get_storage()

    async def _run_background_jobs(self):
        defipulse_fetcher = DefiPulseFetcher(self.deps)
        self.deps.defipulse = defipulse_saver = DefiPulseKeeper(self.deps)
        defipulse_fetcher.subscribe(defipulse_saver)

        price_fetcher = PriceFetcher(self.deps)
        price_fetcher.startup_sleep = 3.0
        price_handler = PriceHandler(self.deps)
        price_fetcher.subscribe(price_handler)

        await asyncio.gather(*(task.run() for task in [
            defipulse_fetcher,   # fixme: not to spend credits
            price_fetcher
        ]))

    async def on_startup(self, _=None):
        await self.connect_chat_storage()

        self.deps.session = aiohttp.ClientSession()

        asyncio.create_task(self._run_background_jobs())

    async def on_shutdown(self, _):
        await self.deps.session.close()

    def run_bot(self):
        self.create_bot_stuff()
        executor.start_polling(self.deps.dp, skip_updates=True, on_startup=self.on_startup,
                               on_shutdown=self.on_shutdown)


if __name__ == '__main__':
    App().run_bot()
