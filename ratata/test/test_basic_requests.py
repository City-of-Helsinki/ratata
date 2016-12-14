import pprint
import sys

import ratata
from .http_test_server import run as start_testing_server, quit as stop_testing_server


def test_basic_requests():
    start_testing_server()
    ratata.main('./parks.yaml')
    stop_testing_server()
