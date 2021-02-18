from jobs.defipulse_job import DefiPulseFetcher, DefiPulsePersistance
from main import App

IS_LOAD_SCENARIO = True


class TestApp(App):
    async def _run_background_jobs(self):
        if IS_LOAD_SCENARIO:
            await self._load_scenario()
        else:
            await self._save_scenario()

    async def _load_scenario(self):
        defipulse_saver = DefiPulsePersistance(self.deps)
        items = await defipulse_saver.get_last_state()
        alpha = DefiPulseFetcher.find_alpha(items)
        print(alpha)

    async def _save_scenario(self):
        fetcher_defipulse = DefiPulseFetcher(self.deps)
        defipulse_saver = DefiPulsePersistance(self.deps)
        fetcher_defipulse.subscribe(defipulse_saver)
        await fetcher_defipulse.run()
        await self.deps.dp.stop_polling()


if __name__ == '__main__':
    TestApp().run_bot()
