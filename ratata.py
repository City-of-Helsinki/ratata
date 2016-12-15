import sys
import argparse

from ratata import run_spec


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('spec_file', help="a YAML file containing API-specifications to test")
    parser.add_argument("-v", "--verbose", help="be more verbose", action="store_true")
    parser.add_argument("-s", "--server", help="test against this server (overrides spec)")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    run_spec(args.spec_file, args.server, args.verbose)

