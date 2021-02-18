import asyncio
from contextlib import AsyncExitStack

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import Message, PhotoSize, ReplyKeyboardRemove, ContentTypes
from aiogram.utils.helper import HelperMode

from dialog.avatar_image_work import download_tg_photo, get_userpic, combine_frame_and_photo_v2, img_to_bio
from dialog.base import BaseDialog, message_handler
from localization import BaseLocalization
from lib.depcont import DepContainer
from lib.texts import kbd


class AvatarStates(StatesGroup):
    mode = HelperMode.snake_case  # fixme: no state handle
    MAIN = State()


class AvatarDialog(BaseDialog):
    def __init__(self, loc: BaseLocalization, data: FSMContextProxy, d: DepContainer):
        super().__init__(loc, data, d)
        self._work_lock = asyncio.Lock()

    def menu_kbd(self):
        return kbd([
            self.loc.BUTTON_AVA_FROM_MY_USERPIC,
        ], vert=True)

    @message_handler(state=None)
    async def on_no_state(self, message: Message):
        await self.on_enter(message)

    @message_handler(state=AvatarStates.MAIN)
    async def on_enter(self, message: Message):
        if message.text == self.loc.BUTTON_AVA_FROM_MY_USERPIC:
            await self.handle_avatar_picture(message, self.loc)
        else:
            await AvatarStates.MAIN.set()
            await message.answer(self.loc.TEXT_AVA_WELCOME, reply_markup=self.menu_kbd())

    @message_handler(state=AvatarStates.MAIN, content_types=ContentTypes.PHOTO)
    async def on_picture(self, message: Message):
        await self.handle_avatar_picture(message, self.loc, explicit_picture=message.photo[0])

    async def handle_avatar_picture(self, message: Message, loc: BaseLocalization, explicit_picture: PhotoSize = None):
        async with AsyncExitStack() as stack:
            stack.enter_async_context(self._work_lock)

            # POST A LOADING STICKER
            sticker = await message.answer_sticker(self.loc.LOADING_STICKER,
                                                   disable_notification=True,
                                                   reply_markup=ReplyKeyboardRemove())
            # CLEAN UP IN THE END
            stack.push_async_callback(sticker.delete)

            if explicit_picture is not None:
                user_pic = await download_tg_photo(explicit_picture)
            else:
                user_pic = await get_userpic(message.from_user)

            w, h = user_pic.size
            if not w or not h:
                await message.answer(loc.TEXT_AVA_ERR_INVALID, reply_markup=self.menu_kbd())
                return

            if not ((64 <= w <= 4096) and (64 <= h <= 4096)):
                await message.answer(loc.TEXT_AVA_ERR_SIZE, reply_markup=self.menu_kbd())
                return

            # pic = await combine_frame_and_photo(self.deps.cfg, user_pic)
            pic = await combine_frame_and_photo_v2(self.deps.cfg, user_pic)

            user_id = message.from_user.id
            pic = img_to_bio(pic, name=f'alpha_avatar_{user_id}.png')

            await message.answer_document(pic, caption=loc.TEXT_AVA_READY, reply_markup=self.menu_kbd())
