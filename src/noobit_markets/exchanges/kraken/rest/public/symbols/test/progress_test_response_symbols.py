import os
from pathlib import Path
import json
import typing

import pytest
import yaml
from pyrsistent import pmap

from noobit_markets.definitions import ROOT_PATH, APP_PATH
from noobit_markets.base.request import *
from noobit_markets.exchanges.kraken.rest.base import *
from noobit_markets.exchanges.kraken.rest.public.symbols.response import *


rel_path = "tests/cassettes/test_symbols/test_symbols.yaml"
full_path = os.path.join(ROOT_PATH, rel_path)


@pytest.fixture
def load_yaml():
    with open(full_path) as y:
        rec = yaml.safe_load(y)
        return rec

def test_get_response_status_code(load_yaml):

    for interaction in load_yaml["interactions"]:
        req = interaction["request"]
        resp = interaction["response"]
        assert resp["status_code"] == 200


def test_get_error_content(load_yaml):

    for interaction in load_yaml["interactions"]:
        req = interaction["request"]
        resp = interaction["response"]
        assert isinstance(get_error_content(resp), frozenset)
        #! we need to manually change <response[content]> to response[_content] in yaml file
        assert isinstance(json.loads(resp["_content"])["error"], list)
        assert get_error_content(resp) == frozenset(json.loads(resp["_content"])["error"])


def test_get_result_content(load_yaml):

    for interaction in load_yaml["interactions"]:
        req = interaction["request"]
        resp = interaction["response"]
        returned = get_result_content(resp)
        assert isinstance(returned, typing.Mapping)
        expected = pmap(json.loads(resp["_content"])["result"])
        assert isinstance(expected, typing.Mapping)

        assert returned == expected


def test_validate_result_content(load_yaml):

    for interaction in load_yaml["interactions"]:
        req = interaction["request"]
        resp = interaction["response"]
        result_content = pmap(json.loads(resp["_content"])["result"])
        filtered_result_content = filter_result_content_symbols(result_content)
        returned = validate_raw_result_content_symbols(filtered_result_content)
        assert isinstance(returned, Ok)
        assert isinstance(returned.value, KrakenResponseSymbols)