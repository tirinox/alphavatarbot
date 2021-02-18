from datetime import datetime

from lib.datetime import delay_to_next_hour_minute, DAY, MINUTE, HOUR


def test_time1():
    now_dt = datetime.now().replace(hour=12, minute=45, second=0, microsecond=0)
    assert delay_to_next_hour_minute(12, 44, now=now_dt) == 60
    assert delay_to_next_hour_minute(12, 46, now=now_dt) == DAY - MINUTE


def test_time2():
    now_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    assert delay_to_next_hour_minute(1, 0, now=now_dt) == HOUR * 23
    assert delay_to_next_hour_minute(23, 0, now=now_dt) == HOUR
