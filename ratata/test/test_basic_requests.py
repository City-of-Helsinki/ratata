import pprint
import sys
import pytest

import ratata
from .http_test_server import run as start_testing_server, quit as stop_testing_server
from .parks_http_test_server import ParksHTTPTestServer


@pytest.fixture
def parks_server():
    t = start_testing_server(ParksHTTPTestServer)
    yield
    stop_testing_server(t)
    return


def test_basic_requests(parks_server):
    ratata.main('ratata/test/parks.yaml')
