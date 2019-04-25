"""Simple test definition that produces a passing result."""
from detoxed.integ import IntegTestBase
from detoxed.integ import Pass


class PassingTestCase(IntegTestBase):
    """Trivial test case."""

    def __init__(self):
        super().__init__('passing test case')

    def setup(self):
        print('inside: setup()')

    def teardown(self):
        print('inside: teardown()')

    def test(self):
        print('inside: test()')
        return Pass()
