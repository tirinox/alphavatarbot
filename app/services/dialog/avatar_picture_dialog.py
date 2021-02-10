import asyncio
from contextlib import AsyncExitStack
from io import BytesIO

from PIL import Image
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import User, Message, PhotoSize, ReplyKeyboardRemove, ContentTypes
from aiogram.utils.helper import HelperMode

from localization import BaseLocalization
from services.dialog.base import BaseDialog, message_handler
from services.lib.config import Config
from services.lib.depcont import DepContainer
from services.lib.texts import kbd
from services.lib.utils import async_wrap, img_to_bio


async def download_tg_photo(photo: PhotoSize) -> Image.Image:
    photo_raw = BytesIO()
    await photo.download(destination=photo_raw)
    return Image.open(photo_raw)


async def get_userpic(user: User) -> Image.Image:
    pics = await user.get_profile_photos(0, 1)
    if pics.photos and pics.photos[0]:
        first_pic: PhotoSize = pics.photos[0][0]
        return await download_tg_photo(first_pic)


ALPHA_AVA_LOGO_PATH = './data/alpha-logo.png'


def image_square_crop(im):
    width, height = im.size  # Get dimensions

    if width > height:
        new_width, new_height = height, height
    elif width < height:
        new_width, new_height = width, width
    else:
        return im

    left = int((width - new_width) / 2)
    top = int((height - new_height) / 2)
    right = int((width + new_width) / 2)
    bottom = int((height + new_height) / 2)

    # Crop the center of the image
    return im.crop((left, top, right, bottom))


@async_wrap
def combine_frame_and_photo(cfg: Config, photo: Image.Image):
    photo = image_square_crop(photo)

    photo_w, photo_h = photo.size
    logo = Image.open(ALPHA_AVA_LOGO_PATH)

    logo_pos_px = float(cfg.avatar.position.x)
    logo_pos_py = float(cfg.avatar.position.y)
    logo_scale = float(cfg.avatar.scale)
    assert 0 <= logo_pos_px <= 100
    assert 0 <= logo_pos_py <= 100
    assert 1 <= logo_scale <= 200

    logo_size = int(max(photo_w, photo_h) / 100.0 * logo_scale)
    logo_pos_x = int(logo_pos_px * photo_w / 100.0 - logo_size / 2)
    logo_pos_y = int(logo_pos_py * photo_h / 100.0 - logo_size / 2)

    logo = logo.resize((logo_size, logo_size)).convert('RGBA')

    photo.paste(logo, (logo_pos_x, logo_pos_y), mask=logo)

    return photo


class AvatarStates(StatesGroup):
    mode = HelperMode.snake_case
    MAIN = State()


class AvatarDialog(BaseDialog):
    def __init__(self, loc: BaseLocalization, data: FSMContextProxy, d: DepContainer):
        super().__init__(loc, data, d)
        self._work_lock = asyncio.Lock()

    def menu_kbd(self):
        return kbd([
            self.loc.BUTTON_AVA_FROM_MY_USERPIC,
        ], vert=True)

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

            pic = await combine_frame_and_photo(self.deps.cfg, user_pic)

            user_id = message.from_user.id
            pic = img_to_bio(pic, name=f'alpha_avatar_{user_id}.png')

            await message.answer_document(pic, caption=loc.TEXT_AVA_READY, reply_markup=self.menu_kbd())
