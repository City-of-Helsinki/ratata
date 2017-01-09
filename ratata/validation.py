import colorama
import re


def validate_request_result(result, url, request_spec, spec):
    if request_spec.get('response'):
        errors = []
        for key, val in request_spec['response'].items():
            try:
                validate_row(key, val, result, url, spec)
            except AssertionError as e:
                errors += [e]
        return errors
    else:
        print(colorama.Fore.YELLOW + "  No validation required for %s" % request_spec['name'] +
              colorama.Style.RESET_ALL)


def validate_row(key, val, result, url, spec):
    if key == 'code':
        assert result.status_code == int(val), \
            "Required status code {0} does not match returned {1}".format(val, result.status_code)
    if key == 'type':
        t = val
        if t.upper() == 'JSON':
            t = 'application/json'
        elif t.upper() == 'HTML':
            t = 'text/html'
        elif t.upper() == 'TEXT':
            t = 'text/plain'
        ct = result.headers['content-type']
        assert ct == t, "Required content type '{0}' does not match returned '{1}'".format(ct, t)
    if key == 'contains':
        needle = val
        assert result.text.find(needle) != -1, \
            ("Required text '{0}' not found in response".format(needle), result.text)
    if key == 'regex':
        pattern = val
        assert re.match(pattern, result.text), (
            "Regular expression {0} does not match response". format(pattern), result.text
        )
    if key == 'function':
        func_name = val
        func = getattr(spec['module'], func_name)
        assert func(url, result) != False, ("Function {0} says response is not valid".format(func_name), result.text)

