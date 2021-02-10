from aiogram import filters
from aiogram.types import *

from services.dialog.avatar_picture_dialog import AvatarDialog
from services.dialog.base import BaseDialog, message_handler


class MainMenuDialog(BaseDialog):
    @message_handler(commands='start,lang', state='*')
    async def entry_point(self, message: Message):
        await AvatarDialog(self.loc, self.data, self.deps).on_enter(message)

    @message_handler(commands='help', state='*')
    async def cmd_help(self, message: Message):
        await message.answer(self.loc.help_message(),
                             disable_web_page_preview=True,
                             disable_notification=True)

    @message_handler(filters.RegexpCommandsFilter(regexp_commands=[r'/.*']), state='*')
    async def on_unknown_command(self, message: Message):
        await message.answer(self.loc.unknown_command(), disable_notification=True)
