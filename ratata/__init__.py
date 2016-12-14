import os
import re
import importlib
import sys

import yaml
import requests
import colorama

colorama.init()


def main(definition_file):
    if not definition_file.startswith('/'):
        definition_file = os.path.join(os.getcwd(), definition_file)
    with open(definition_file) as f:
        spec = yaml.load(f.read())
    print(definition_file)
    spec['module'] = find_possible_support_module(definition_file)
    handle_spec(spec)
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


def handle_spec(spec):
    assert spec.get('name'), "Spec %s is missing name" % spec
    print(colorama.Fore.GREEN +
          "Looking into spec: " + spec['name'] + colorama.Style.RESET_ALL)
    assert spec.get('address'), "Spec %s is missing address attribute" % spec['name']
    for request in spec['requests']:
        handle_request(request, spec)


def handle_request(request_spec, spec):
    assert request_spec.get('name'), "Request %s is missing name attribute" % request_spec
    print(colorama.Fore.YELLOW + request_spec['name'] + colorama.Style.RESET_ALL)
    assert request_spec.get('path'), "Request %s is missing path attribute" % request_spec['name']
    url = "{0}{1}".format(spec['address'], request_spec['path'])
    url = build_url(url, spec)
    result = send_request(url, request_spec)
    validation_result = validate_request_result(result, url, request_spec, spec)


def send_request(url, request):
    if request.get('method') and request['method'].lower() == 'post':
        raise "foo"
    else:
        print("  ==> get request", url)
        ret = requests.get(url)
        return ret


def validate_request_result(result, url, request_spec, spec):
    if request_spec.get('response'):
        if request_spec['response'].get('code'):
            assert result.status_code == int(request_spec['response']['code'])
        if request_spec['response'].get('type'):
            t = request_spec['response'].get('type')
            if t.upper() == 'JSON':
                t = 'application/json'
            elif t.upper() == 'HTML':
                t = 'text/html'
            elif t.upper() == 'TEXT':
                t = 'text/plain'
            ct = result.headers['content-type']
            assert ct == t, "Content type {0} matches {1}".format(ct, t)
        if request_spec['response'].get('contains'):
            needle = request_spec['response']['contains']
            assert result.text.find(needle) != -1, "Text {0} not found in response {1}".format(needle, result.text)
        if request_spec['response'].get('regex'):
            pattern = request_spec['response']['regex']
            assert re.match(pattern, result.text), "Regular expression {0} does not match response {1}".\
                format(pattern, result.text)
        if request_spec['response'].get('function'):
            func_name = request_spec['response']['function']
            func = getattr(spec['module'], func_name)
            assert func(url, result), "Function {0} says response for {1} is not valid".format(
                func_name, request_spec['name'])
    else:
        print(colorama.Fore.YELLOW + "  No validation required for %s" % request_spec['name'] +
              colorama.Style.RESET_ALL)



def build_url(url, spec):
    """
    Build the url by finding {% func_name %} patterns in the URL, calling the
    functions and replacing the patterns with the return values
    """
    match = re.match(r'.*(\{%\s*[\w_]+\s*%\}).*', url)
    if match:
        if not spec.get('module'):
            print(colorama.Fore.RED + "No support module found for solving %s" % url + colorama.Style.RESET_ALL)
            return url
        for func_wrapping in match.groups():
            func_name = re.match(r'\{%\s*([\w_]+)\s*%\}', func_wrapping).groups()[0]
            func = getattr(spec['module'], func_name)
            if not func:
                print(colorama.Fore.RED + "Function %s not found in module %s" % (func_name, spec['module']) +
                      colorama.Style.RESET_ALL)
            else:
                ret_val = func(url)
                url = url.replace(func_wrapping, str(ret_val), 1)
    return url
