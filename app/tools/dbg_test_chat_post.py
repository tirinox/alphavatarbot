import asyncio
from datetime import datetime

from jobs.price_job import PriceHandler
from lib.texts import MessageType, code
from localization import LocalizationManager
from main import App
from models.models import PriceReport, CoinPriceInfo, DefiPulseEntry, PriceATH, PriceHistoricalTriplet


class TestApp(App):
    async def _test_send_message(self):
        is_ath = False
        tlv_is_ath = False
        rank_delta = -2
        loc_man: LocalizationManager = self.deps.loc_man
        p = PriceReport(price_and_cap=CoinPriceInfo(1.2, 100032232, +6.1, 0.000001234, 150.66, -0.1, 77),
                        price_change=PriceHistoricalTriplet(1.3, 0.9, 2.5),
                        defipulse=DefiPulseEntry('?', 'Ethereum', 45, 'Alpha Homora', 16565981, 0.6,
                                                 tlv_is_ath=tlv_is_ath, rank_delta=rank_delta),
                        price_ath=PriceATH(int(datetime.now().timestamp() - 2308), ath_price=0.99), is_ath=is_ath)
        text = loc_man.default.notification_text_price_update(p)

        user_lang_map = self.deps.broadcaster.telegram_chats_from_config(self.deps.loc_man)
        await self.deps.broadcaster.broadcast(user_lang_map.keys(), text)

    async def _test_all_stickers(self):
        chat_ids = self.deps.broadcaster.telegram_chats_from_config(self.deps.loc_man).keys()
        ph = PriceHandler(self.deps)
        for sticker in ph.stickers:
            await self.deps.broadcaster.broadcast(chat_ids, sticker, message_type=MessageType.STICKER)
            await asyncio.sleep(1.0)
            await self.deps.broadcaster.broadcast(chat_ids, f'☝️ {code(sticker)}')
            await asyncio.sleep(1.0)

    async def _run_background_jobs(self):
        # await self._test_all_stickers()
        exit(0)


if __name__ == '__main__':
    TestApp().run_bot()
