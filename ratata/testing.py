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
    results = {'passed': [], 'failed': [], 'time': datetime.datetime.now(), 'name': spec['name'], 'return_values': {}}
    for request_spec in spec['requests']:
        try:
            request, url = handle_request_spec(request_spec, spec, results)
            print_request_start(request_spec)
            request_results = grequests.map((request,))
            result = request_results[0]
            if verbose:
                print("  URL: {}".format(url))
                print("  Returns: {}".format(result.content))
            results['return_values'][request_spec['name']] = result
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
    if 'module' in spec:
        module_path = spec['module']
        if not module_path.startswith('/'):
            module_path = os.path.join(os.path.dirname(definition_file), module_path)
        spec['module'] = get_support_module(module_path)
    else:
        possible_module_name = definition_file.rsplit('.', 1)[0]
        if os.path.exists(possible_module_name + '.py'):
            spec['module'] = get_support_module(possible_module_name)
    assert spec.get('name'), "Spec %s is missing name" % spec
    if override_server:
        spec['address'] = override_server
    else:
        assert spec.get('address'), "Spec %s is missing address attribute" % spec['name']
    return spec


def get_support_module(module_name):
    # need to append to sys.path first because relative imports would require
    # an anchor package, which is not available
    sys.path.append(os.path.dirname(module_name))
    try:
        module = importlib.import_module(os.path.basename(module_name))
        return module
    except ImportError as e:
        print(colorama.Fore.RED + "Could not import the module: " + module_name + colorama.Style.RESET_ALL)
    return None


def handle_request_spec(request_spec, spec, test_run_results=None):
    assert request_spec.get('name'), "Request %s is missing name attribute" % request_spec
    assert request_spec.get('path'), "Request %s is missing path attribute" % request_spec['name']
    prev_results = test_run_results['return_values'] if test_run_results else {}
    url = "{0}{1}".format(spec['address'], request_spec['path'])
    url = build_url(url, request_spec, spec, prev_results)
    try:
        # result = send_request(url, request_spec, spec)
        request = build_request(url, request_spec, spec, prev_results)
        return request, url
    except requests.exceptions.ConnectionError as e:
        print(colorama.Fore.RED + "  Connection to '{0}' was refused".format(url) + colorama.Style.RESET_ALL)
