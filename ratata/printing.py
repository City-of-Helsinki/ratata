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
    passed_amount = 0
    failed_amount = 0
    times = []
    for name, values in results['requests'].items():
        passed_amount += len(values['passed'])
        failed_amount += len(values['failed'])
        times += map(lambda x: x[1].microseconds / 1000, values['passed'])
        times += map(lambda x: x[1].microseconds / 1000, values['failed'])
        print(colorama.Fore.YELLOW + "  " + name + colorama.Style.RESET_ALL)
        print("  passed: {}, failed {}".format(passed_amount, failed_amount))

    avg_time = sum(times) / len(times)
    summary = "{} requests passed, {} failed, average time {:.2f}ms".format(passed_amount, failed_amount, avg_time)
    print()
    print(colorama.Style.BRIGHT + "=====" + summary + "=====" + colorama.Style.RESET_ALL)
    print()


def print_request_start(request_spec):
    print(request_start_text(request_spec))


def request_start_text(request_spec):
    return colorama.Fore.YELLOW + "  " + request_spec['name'] + colorama.Style.RESET_ALL


def print_request_end(request_spec):
    print()


def print_success(result):
    print(colorama.Fore.GREEN + "  " + "PASS {} ({:.2f}ms)".format(result.status_code, result.elapsed.microseconds / 1000.0) +
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
