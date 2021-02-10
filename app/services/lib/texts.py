import itertools
from dataclasses import dataclass
from enum import Enum

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class MessageType(Enum):
    TEXT = 'text'
    STICKER = 'sticker'
    PHOTO = 'photo'


@dataclass
class BoardMessage:
    text: str
    message_type: MessageType = MessageType.TEXT
    photo: str = None

    @classmethod
    def make_photo(cls, photo, caption=''):
        return cls(caption, MessageType.PHOTO, photo)


def bold(text):
    return f"<b>{text}</b>"


def link(url, text):
    return f'<a href="{url}">{text}</a>'


def code(text):
    return f"<code>{text}</code>"


def ital(text):
    return f"<i>{text}</i>"


def pre(text):
    return f"<pre>{text}</pre>"


def progressbar(x, total, symbol_width=10):
    if total <= 0:
        s = 0
    else:
        s = int(round(symbol_width * x / total))
    s = max(0, s)
    s = min(symbol_width, s)
    return '▰' * s + '▱' * (symbol_width - s)


def grouper(n, iterable):
    args = [iter(iterable)] * n
    return ([e for e in t if e is not None] for t in itertools.zip_longest(*args))


def kbd(buttons, resize=True, vert=False, one_time=False, inline=False, row_width=3):
    if isinstance(buttons, str):
        buttons = [[buttons]]
    elif isinstance(buttons, (list, tuple, set)):
        if all(isinstance(b, str) for b in buttons):
            if vert:
                buttons = [[b] for b in buttons]
            else:
                buttons = [buttons]

    buttons = [
        [KeyboardButton(b) for b in row] for row in buttons
    ]
    return ReplyKeyboardMarkup(buttons,
                               resize_keyboard=resize,
                               one_time_keyboard=one_time,
                               row_width=row_width)
