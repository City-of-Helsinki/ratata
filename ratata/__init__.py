import os
import importlib
import sys

import yaml
import colorama

from .validation import validate_request_result
from .request_handling import build_url, send_request


colorama.init()


def run_spec(definition_file):
    if not definition_file.startswith('/'):
        definition_file = os.path.join(os.getcwd(), definition_file)
    with open(definition_file) as f:
        spec = yaml.load(f.read())
    spec['module'] = find_possible_support_module(definition_file)
    assert spec.get('name'), "Spec %s is missing name" % spec
    print(colorama.Fore.GREEN +
          "Looking into spec: " + spec['name'] + colorama.Style.RESET_ALL)
    assert spec.get('address'), "Spec %s is missing address attribute" % spec['name']
    for request in spec['requests']:
        handle_request_spec(request, spec)
    return spec


def handle_request_spec(request_spec, spec):
    assert request_spec.get('name'), "Request %s is missing name attribute" % request_spec
    print(colorama.Fore.YELLOW + request_spec['name'] + colorama.Style.RESET_ALL)
    assert request_spec.get('path'), "Request %s is missing path attribute" % request_spec['name']
    url = "{0}{1}".format(spec['address'], request_spec['path'])
    url = build_url(url, request_spec, spec)
    result = send_request(url, request_spec)
    return validate_request_result(result, url, request_spec, spec)


def find_possible_support_module(definition_file):
    possible_module_name = definition_file.rsplit('.', 1)[0]
    # need to append to sys.path first because relative imports would require
    # an anchor package, which is not available
    sys.path.append(os.path.dirname(possible_module_name))
    try:
        module = importlib.import_module(os.path.basename(possible_module_name))
        return module
    except ImportError as e:
        print("Could not import the module ", possible_module_name, e)
    return None


