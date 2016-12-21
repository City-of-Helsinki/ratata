from urllib.parse import urlencode

import colorama
import re
import requests

INITIAL_REQUEST_HEADERS = {'user-agent': 'ratata/0.2'}


def send_request(url, request_spec, spec):
    headers = INITIAL_REQUEST_HEADERS.copy()
    headers.update(request_spec.get('headers', {}))
    if request_spec.get('method') and request_spec['method'].lower() == 'post':
        params = request_spec.get('params', {})
        for k, v in params.items():
            params[k] = __handle_dynamic_parameters(v, url, spec['module'])
        print("  POST:", url, request_spec.get('params'))
        ret = requests.post(url, data=params, headers=headers)
    else:
        print("  GET:", url)
        ret = requests.get(url, headers=headers)
    return ret


def build_url(url, request_spec, spec):
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
    if request_spec.get('params') and request_spec.get('method', 'get').lower() == 'get':
        params = request_spec['params']
        for k, v in params.items():
            params[k] = __handle_dynamic_parameters(v, url, spec['module'])
        params = urlencode(tuple(params.items()))
        url += '?' + params

    return url


def __handle_dynamic_parameters(v, url, module):
    if v.startswith('{%'):
        func_name = re.match(r'\{%\s*([\w_]+)\s*%\}', v).groups()[0]
        func = getattr(module, func_name)
        new_value = func(url)
        return new_value
    return v