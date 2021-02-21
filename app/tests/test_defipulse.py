import json
import os

import pytest

from jobs.defipulse_job import DefiPulseFetcher, DefiPulseKeeper


@pytest.fixture
def defipulse_example_json():
    print(os.getcwd())
    with open('app/data/GetProjects_example_defipulse.json', 'r') as f:
        return json.load(f)


def test_parsedefi_pulse(defipulse_example_json):
    alpha_defi = DefiPulseKeeper.find_alpha(DefiPulseFetcher.parse_defipulse(defipulse_example_json))
    assert alpha_defi.id == 49
    assert alpha_defi.name == DefiPulseFetcher.ALPHA_NAME
    assert alpha_defi.tlv_usd == 1023102498.0
    assert alpha_defi.tlv_usd_relative_1d == -7.57
