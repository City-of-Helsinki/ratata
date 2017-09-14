import curses


def curses_main(stdscr, func, spec, *args, **kwargs):
    stdscr.clear()
    curses.cbreak()
    curses.noecho()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.addstr(0, 0, spec['name'], curses.A_STANDOUT)
    func(spec, stdscr=stdscr, *args, **kwargs)
    stdscr.getkey()


def curses_benchmarking_reporting(results, stdscr):
    i = 0
    for name, values in results['requests'].items():
        passed_amount = len(values['passed'])
        failed_amount = len(values['failed'])
        if passed_amount:
            avg_time_passed = sum(map(lambda x: x[1].microseconds / 1000.0, values['passed'])) / passed_amount
        else:
            avg_time_passed = 0
        if failed_amount:
            avg_time_failed = sum(map(lambda x: x[1].microseconds / 1000.0, values['failed'])) / failed_amount
        else:
            avg_time_failed = 0
        row = i + 3
        stdscr.addstr(row, 0, name, curses.color_pair(1))
        stdscr.addstr(row, int(curses.COLS / 3 * 1),
                      "{} (avg time {:.2f}ms)".format(passed_amount, avg_time_passed),
                      curses.color_pair(3))
        stdscr.addstr(row, int(curses.COLS / 3 * 2),
                      "{} (avg time {:.2f}ms)".format(failed_amount, avg_time_failed),
                      curses.color_pair(2))
        i += 2
    stdscr.refresh()


def curses_benchmarking_summary(results, stdscr):
    passed_amount = 0
    failed_amount = 0
    times = []
    for name, values in results['requests'].items():
        passed_amount += len(values['passed'])
        failed_amount += len(values['failed'])
        times += map(lambda x: x[1].microseconds / 1000, values['passed'])
        times += map(lambda x: x[1].microseconds / 1000, values['failed'])
    avg_time = sum(times) / len(times)
    summary = "{} requests passed, {} failed, average time {:.2f}ms".format(passed_amount, failed_amount, avg_time)
    stdscr.addstr(curses.LINES - 2, 0, summary, curses.color_pair(3) | curses.A_STANDOUT)
    stdscr.addstr(curses.LINES - 1, 0, "Press any key to quit", curses.color_pair(3))
