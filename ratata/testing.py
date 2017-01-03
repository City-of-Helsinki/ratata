import os
import importlib
import sys

import datetime
import requests
import grequests
import yaml
import colorama

from ratata.printing import print_fail_with_errors, print_fail_with_exception, print_success, print_request_start, \
    print_start, print_request_end
from .validation import validate_request_result
from .request_handling import build_url, build_request


def run_spec(definition_file, override_server=None, verbose=False):
    """ Main entry point. Opens the given specification file path and starts cracking. """
    spec = load_spec_and_env(definition_file, override_server)
    print_start(definition_file, spec)
    results = {'passed': [], 'failed': [], 'time': datetime.datetime.now(), 'name': spec['name']}
    for request_spec in spec['requests']:
        try:
            request, url = handle_request_spec(request_spec, spec)
            print_request_start(request_spec)
            request_results = grequests.map((request,))
            result = request_results[0]
            errors = validate_request_result(result, url, request_spec, spec)
            if not errors:
                print_success(result)
                results['passed'].append((request_spec['name'], result.elapsed))
            else:
                print_fail_with_errors(result, errors, verbose)
                results['failed'].append((request_spec['name'], result.elapsed))
        except AssertionError as e:
            print_fail_with_exception(e)
            results['failed'].append((request_spec['name'], None))
        print_request_end(request_spec)
    return results


def load_spec_and_env(definition_file, override_server):
    if not definition_file.startswith('/'):
        definition_file = os.path.join(os.getcwd(), definition_file)
    with open(definition_file) as f:
        spec = yaml.load(f.read())
    spec['module'] = find_possible_support_module(definition_file)
    assert spec.get('name'), "Spec %s is missing name" % spec
    if override_server:
        spec['address'] = override_server
    else:
        assert spec.get('address'), "Spec %s is missing address attribute" % spec['name']
    return spec


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


def handle_request_spec(request_spec, spec):
    assert request_spec.get('name'), "Request %s is missing name attribute" % request_spec
    assert request_spec.get('path'), "Request %s is missing path attribute" % request_spec['name']
    url = "{0}{1}".format(spec['address'], request_spec['path'])
    url = build_url(url, request_spec, spec)
    try:
        # result = send_request(url, request_spec, spec)
        request = build_request(url, request_spec, spec)
        return request, url
    except requests.exceptions.ConnectionError as e:
        print(colorama.Fore.RED + "  Connection to '{0}' was refused".format(url) + colorama.Style.RESET_ALL)
