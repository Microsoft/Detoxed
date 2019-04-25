"""Entrypoint for integration tests."""

import argparse
import sys
from typing import Any

from .integ import IntegTestRunner


def run_tests(args: Any) -> bool:
    """Run integration tests."""
    return IntegTestRunner(args.test_modules).run()


def get_args() -> Any:
    """Get args from command line input."""
    parser = argparse.ArgumentParser(description='Run Integration Tests')
    parser.add_argument('test_modules', type=str, help='Timeout for IoTEdge deployment in seconds', nargs='+')
    return parser.parse_args()


if __name__ == '__main__':
    sys.exit(not run_tests(get_args()))
