"""Simple test that produces a failing result."""
from detoxed.integ import IntegTestBase
from detoxed.integ import Fail


class FailingTestCase(IntegTestBase):
    """Trivial test case."""

    def __init__(self):
        super().__init__('failing test case')

    def setup(self):
        print('inside: setup()')

    def teardown(self):
        print('inside: teardown()')

    def test(self):
        print('inside: test()')
        return Fail('Intentionally failing test')
