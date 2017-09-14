#!/usr/bin/env python3
import sys
import argparse

# This is required for issue combining py3.6 & gevent & SSL
# see e.g. https://github.com/kennethreitz/grequests/issues/116
# note: won't work even with this
# from gevent.monkey import patch_select
# patch_select(aggressive=True)

from ratata import run_spec, benchmark_spec
from ratata.integrations import send_slack_message, send_email_message


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('spec_file', help="a YAML file containing API-specifications to test")
    parser.add_argument("-v", "--verbose", help="be more verbose", action="store_true")
    parser.add_argument("-a", "--address", help="test against the server in this http address (overrides spec)")
    parser.add_argument("--only-fail", help="Send messages only when a test has failed", action="store_true")
    parser.add_argument("--slack-token", help="Auth token for Slack (see Authentication "
                                              "https://api.slack.com/docs/oauth-test-tokens)")
    parser.add_argument("--slack-channel", help="send the final results to this slack channel (requires the token)")
    parser.add_argument("--email-to", help="send the final results to this email (requires the smtp argument)")
    parser.add_argument("--email-smtp", help="the smtp server to use for email sending")
    parser.add_argument("--email-smtp-login", help="username and password for the smtp server in the form USER:PASS")

    parser.add_argument("--benchmark", help="Drive all request in the spec file times N in parallel and count durations",
                        type=int)
    parser.add_argument("--no-curses", help="Don't use the curses-based UI with benchmarking, just print results",
                        action="store_true")
    return parser.parse_args()


def validate_args(args):
    if args.slack_channel or args.slack_token:
        if not (args.slack_channel and args.slack_token):
            print("Slack support requires both channel and token")
            sys.exit(1)
    if args.email_to or args.email_smtp:
        if not (args.email_smtp and args.email_to):
            print("Email requires both recipient and smtp server")
            sys.exit(1)


def send_messages(args, results):
    if args.slack_channel:
        send_slack_message(args, results)

    if args.email_to:
        send_email_message(args, results)


if __name__ == '__main__':
    args = get_args()
    validate_args(args)
    if args.benchmark:
        results = benchmark_spec(args.spec_file, args.benchmark, args.address, args.verbose, not args.no_curses)
    else:
        results = run_spec(args.spec_file, args.address, args.verbose)

    if args.only_fail:
        if results['failed'] > 0:
            send_messages(args, results)
    else:
        send_messages(args, results)
