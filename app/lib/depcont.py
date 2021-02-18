import asyncio
import typing
from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiohttp import ClientSession


@dataclass
class DepContainer:
    cfg: typing.Optional['Config'] = None
    db: typing.Optional['DB'] = None
    loop: typing.Optional[asyncio.BaseEventLoop] = None

    session: typing.Optional[ClientSession] = None

    bot: typing.Optional['Bot'] = None
    dp: typing.Optional['Dispatcher'] = None
    broadcaster: typing.Optional['Broadcaster'] = None
    loc_man: typing.Optional['LocalizationManager'] = None
