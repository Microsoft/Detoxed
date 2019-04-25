"""Tests that (1) extend the Integration Test Base class and (2) produce a failing result"""
from detoxed.integ import Fail
from detoxed.integ import IntegTestBase


class FailingTestCase(IntegTestBase):
    def __init__(self):
        super().__init__('failing test case')

    def test(self):
        return Fail("I failed!")
