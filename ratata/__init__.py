import os
import importlib
import sys

import requests
import yaml
import colorama

from .validation import validate_request_result
from .request_handling import build_url, send_request


colorama.init()


def run_spec(definition_file, override_server=None, verbose=False):
    """ Main entry point. Opens the given specification file path and starts cracking. """
    print()
    if not definition_file.startswith('/'):
        definition_file = os.path.join(os.getcwd(), definition_file)
    with open(definition_file) as f:
        spec = yaml.load(f.read())
    spec['module'] = find_possible_support_module(definition_file)
    assert spec.get('name'), "Spec %s is missing name" % spec
    print(colorama.Fore.GREEN +
          "Looking into spec: " + spec['name'] + colorama.Style.RESET_ALL)
    print("from:", definition_file)
    print()
    if override_server:
        spec['address'] = override_server
    else:
        assert spec.get('address'), "Spec %s is missing address attribute" % spec['name']
    passed = 0
    failed = 0
    for request in spec['requests']:
        try:
            errors = handle_request_spec(request, spec)
            if not errors:
                print(colorama.Fore.GREEN + "  " + "PASS!" + colorama.Style.RESET_ALL)
                passed += 1
            else:
                print(colorama.Fore.RED + "  " + "FAIL:" + colorama.Style.RESET_ALL)
                failed += 1
                for e in errors:
                    err = e.args[0] if type(e.args[0]) == str else e.args[0][0]
                    print("     - " + err)
                    if verbose and type(e.args[0]) == tuple:
                        print("       Server returned: '{0}'".format(e.args[0][1]))
        except AssertionError as e:
            print(colorama.Fore.RED + "  " + "FAIL:" + colorama.Style.RESET_ALL)
            print("    " + e.args[0])
            failed += 1
        print()
    print(colorama.Style.BRIGHT + "==== {0} requests passed, {1} failed ====".format(passed, failed) +
          colorama.Style.RESET_ALL)
    print()
    return spec


def handle_request_spec(request_spec, spec):
    assert request_spec.get('name'), "Request %s is missing name attribute" % request_spec
    print(colorama.Fore.YELLOW + "  " + request_spec['name'], colorama.Style.RESET_ALL)
    assert request_spec.get('path'), "Request %s is missing path attribute" % request_spec['name']
    url = "{0}{1}".format(spec['address'], request_spec['path'])
    url = build_url(url, request_spec, spec)
    try:
        result = send_request(url, request_spec, spec)
        return validate_request_result(result, url, request_spec, spec)
    except requests.exceptions.ConnectionError as e:
        print(colorama.Fore.RED + "  Connection to '{0}' was refused".format(url) + colorama.Style.RESET_ALL)


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


