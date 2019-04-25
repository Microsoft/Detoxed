"""Tests that (1) extend the Integration Test Base class and (2) produce an exception"""
from detoxed.integ import IntegTestBase


class ExceptionTestCase(IntegTestBase):
    def __init__(self):
        super().__init__('exception test case')

    def test(self):
        raise Exception('I errored out!')
