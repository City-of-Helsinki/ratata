import os
import re
import importlib
import sys

import yaml
import requests
import colorama

colorama.init()


def main(definition_file):
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


def handle_request(request, spec):
    assert request.get('name'), "Request %s is missing name attribute" % request
    print(colorama.Fore.YELLOW + request['name'] + colorama.Style.RESET_ALL)
    assert request.get('path'), "Request %s is missing path attribute" % request['name']
    url = "{0}{1}".format(spec['address'], request['path'])
    url = build_url(url, spec)
    if request.get('method') and request['method'].lower() == 'post':
        pass
    else:
        do_get_request(url)


def do_get_request(url):
    print("  ==> get request", url)
    ret = requests.get(url)
    return ret


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
