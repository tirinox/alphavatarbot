from io import BytesIO

from PIL import Image
from aiogram.types import PhotoSize, User

from services.lib.config import Config
from services.lib.utils import async_wrap


def img_to_bio(image, name):
    bio = BytesIO()
    bio.name = name
    image.save(bio, 'PNG')
    bio.seek(0)
    return bio


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
ALPHA_FULL_BG_PATH = './data/alpha-avatar-v3.png'


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


@async_wrap
def combine_frame_and_photo_v2(cfg: Config, photo: Image.Image):
    photo = image_square_crop(photo)

    photo_w, photo_h = photo.size
    logo = Image.open(ALPHA_FULL_BG_PATH)

    logo = logo.resize((photo_w, photo_w)).convert('RGBA')

    photo.paste(logo, (0, 0), mask=logo)

    return photo
