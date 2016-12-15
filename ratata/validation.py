import colorama
import re


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
            assert ct == t, "Required content type '{0}' matches given '{1}'".format(ct, t)
        if request_spec['response'].get('contains'):
            needle = request_spec['response']['contains']
            assert result.text.find(needle) != -1, "Required text '{0}' not found in response '{1}'".format(needle, result.text)
        if request_spec['response'].get('regex'):
            pattern = request_spec['response']['regex']
            assert re.match(pattern, result.text), "Regular expression {0} does not match response {1}". \
                format(pattern, result.text)
        if request_spec['response'].get('function'):
            func_name = request_spec['response']['function']
            func = getattr(spec['module'], func_name)
            assert func(url, result), "Function {0} says response for {1} is not valid".format(
                func_name, request_spec['name'])
    else:
        print(colorama.Fore.YELLOW + "  No validation required for %s" % request_spec['name'] +
              colorama.Style.RESET_ALL)

