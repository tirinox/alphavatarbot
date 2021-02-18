import asyncio

from localization import LocalizationManager
from main import App
from models.models import PriceReport, CoinPriceInfo, DefiPulseEntry, PriceATH


class TestApp(App):
    async def _run_background_jobs(self):
        loc_man: LocalizationManager = self.deps.loc_man
        p = PriceReport(price_and_cap=CoinPriceInfo(1.2, 100032232, +6.1, 0.000001234, 150.66, -0.1),
                        defipulse=DefiPulseEntry('?', 'Ethereum', 45, 'Alpha Homora', 16565981, 0.6),
                        price_ath=PriceATH(), is_ath=False)
        text = loc_man.default.notification_text_price_update(p)

        user_lang_map = self.deps.broadcaster.telegram_chats_from_config(self.deps.loc_man)
        await self.deps.broadcaster.broadcast(user_lang_map.keys(), text)
        await asyncio.sleep(1.0)
        await self.deps.dp.stop_polling()


if __name__ == '__main__':
    TestApp().run_bot()
