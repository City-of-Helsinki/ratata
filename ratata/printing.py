import colorama

colorama.init()


def print_start(definition_file, spec):
    print(colorama.Fore.GREEN)
    print(text_start(definition_file, spec))
    print(colorama.Style.RESET_ALL)


def text_start(definition_file, spec):
    return "Looking into spec: " + spec['name'] + "\nfrom: " + definition_file


def print_summary(results):
    print()
    summary = "{0} requests passed, {1} failed".format(results['passed'], results['failed'])
    print(colorama.Style.BRIGHT + "=====" + summary + "=====" + colorama.Style.RESET_ALL)
    print()


def print_benchmarking_summary(results):
    print()
    summary = "{0} requests passed, {1} failed".format(results['passed'], results['failed'])
    print(colorama.Style.BRIGHT + "=====" + summary + "=====" + colorama.Style.RESET_ALL)
    print()


def print_request_start(request_spec):
    print(request_start_text(request_spec))


def request_start_text(request_spec):
    return colorama.Fore.YELLOW + "  " + request_spec['name'] + colorama.Style.RESET_ALL


def request_text(request_spec, results):
    return request_start_text(request_spec) + 'S' * len(results['passed']) + 'F' * len(results['failed'])


def print_request_end(request_spec):
    print()


def print_success(result):
    print(colorama.Fore.GREEN + "  " + "PASS (%.2fms)" % (result.elapsed.microseconds / 1000.0) +
          colorama.Style.RESET_ALL)


def print_fail_with_exception(e):
    print(colorama.Fore.RED + "  " + "FAIL (with exception):" + colorama.Style.RESET_ALL)
    print("    " + e.args[0])


def print_fail_with_errors(result, errors, verbose=False):
    print(
        colorama.Fore.RED + "  " + "FAIL (%.2fms)" % (result.elapsed.microseconds / 1000.0) + colorama.Style.RESET_ALL)
    for e in errors:
        err = e.args[0] if type(e.args[0]) == str else e.args[0][0]
        print("     - " + err)
        if verbose and type(e.args[0]) == tuple:
            print("       Server returned: '{0}'".format(e.args[0][1]))
