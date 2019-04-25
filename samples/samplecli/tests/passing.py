"""Simple test that produces a passing result."""
import requests

from detoxed.integ import IntegTestBase
from detoxed.integ import Fail
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
        """Test connection to https://google.com/."""
        print('inside: test()')
        try:
            response = requests.get('https://google.com/')
            status_code = response.status_code
            print('HTTP GET status_code: {}'.format(status_code))
            if status_code == 200:
                return Pass()
            return Fail('status code expected to be 200 but was {}'.format(status_code))
        except Exception as ex:
            return Fail('failed to execute HTTP GET: {}'.format(ex))
