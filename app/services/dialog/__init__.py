from aiogram.types import ContentTypes, Message

from services.dialog.avatar_picture_dialog import AvatarDialog
from services.dialog.main_menu import MainMenuDialog
from services.lib.depcont import DepContainer


async def sticker_handler(message: Message):
    s = message.sticker
    await message.reply(f'Sticker: {s.emoji}: {s.file_id}')


def init_dialogs(d: DepContainer):
    MainMenuDialog.register(d)

    mm = MainMenuDialog
    AvatarDialog.register(d, mm, mm.entry_point)

    d.dp.register_message_handler(sticker_handler, content_types=ContentTypes.STICKER, state='*')
