import asyncio

from main import App


class TestApp(App):
    async def _run_background_jobs(self):
        user_lang_map = self.deps.broadcaster.telegram_chats_from_config(self.deps.loc_man)
        await self.deps.broadcaster.broadcast(user_lang_map.keys(), 'test message')
        await asyncio.sleep(1.0)
        await self.deps.dp.stop_polling()


if __name__ == '__main__':
    TestApp().run_bot()
