import asyncio

import pytest

from lib.config import Config
from lib.db import DB
from lib.depcont import DepContainer


@pytest.fixture
def dep_cont() -> DepContainer:
    d = DepContainer()
    d.cfg = Config()
    d.loop = asyncio.get_event_loop()
    d.db = DB(d.loop)
    return d
