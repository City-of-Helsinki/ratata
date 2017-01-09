import random
import datetime
import grequests

from ratata.curses_printing import curses_benchmarking_reporting, curses_main, curses_benchmarking_summary
from .printing import print_fail_with_exception, text_start, print_benchmarking_summary
from .validation import validate_request_result
from .testing import load_spec_and_env, handle_request_spec


def benchmark_spec(definition_file, multiply_by=1, override_server=None, verbose=False, curses=True):
    spec = load_spec_and_env(definition_file, override_server)
    if curses:
        import curses
        return curses.wrapper(curses_main, _do, spec, multiply_by, verbose, curses)
    else:
        print(text_start(definition_file, spec))
        return _do(spec, multiply_by, verbose, False)


def _do(spec, multiply_by=1, verbose=False, curses=True, stdscr=None):
    results = {'requests': {}, 'time': datetime.datetime.now(), 'name': spec['name']}
    reqs = []

    for request_spec in spec['requests']:
        if request_spec.get('method', 'GET') != 'GET':
            print("Ignoring {} for benchmarking as it is not GET".format(request_spec['name']))
            continue
        if request_spec['name'] not in results['requests']:
            results['requests'][request_spec['name']] = {'passed': [], 'failed': []}
        try:
            for i in range(multiply_by):
                request, url = handle_request_spec(request_spec, spec)
                reqs.append((request, url))
        except AssertionError as e:
            print_fail_with_exception(e)
            results['requests'][request_spec['name']]['failed'].append((request_spec['name'], None))

    plain_reqs = list(map(lambda x: x[0], reqs))
    random.shuffle(plain_reqs)
    request_results = grequests.imap(plain_reqs)
    for res in request_results:
        request_spec_name = res.request.headers['X-ratata-id']
        request_spec = next(x for x in spec['requests'] if x['name'] == request_spec_name)
        errors = validate_request_result(res, res.request.url, request_spec, spec)
        if not errors:
            results['requests'][request_spec['name']]['passed'].append((request_spec_name, res.elapsed))
        else:
            results['requests'][request_spec['name']]['failed'].append((request_spec_name, res.elapsed))

        if curses:
            curses_benchmarking_reporting(results, stdscr)

    if curses:
        curses_benchmarking_summary(results, stdscr)
    else:
        print_benchmarking_summary(results)

    return results
