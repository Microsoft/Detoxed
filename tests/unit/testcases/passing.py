"""Tests that (1) extend the Integration Test Base class and (2) produce a passing result"""
from detoxed.integ import IntegTestBase
from detoxed.integ import Pass


class PassingTestCase(IntegTestBase):
    def __init__(self):
        super().__init__('passing test case')

    def test(self):
        return Pass()
