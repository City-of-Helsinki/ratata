from urllib.parse import urlencode

import colorama
import re
import requests


def send_request(url, request):
    if request.get('method') and request['method'].lower() == 'post':
        print("  ==> post request", url)
        ret = requests.post(url, data=request.get('params', {}))
    else:
        print("  ==> get request", url)
        ret = requests.get(url)
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
        params = urlencode(tuple(request_spec['params'].items()))
        url += '?' + params

    return url
