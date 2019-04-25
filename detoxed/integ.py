"""Holds integration test suite code for IoTEdge modules."""
import importlib
import logging
import sys
from abc import ABC
from abc import abstractmethod
from time import sleep
from time import time
from typing import Dict
from typing import List
from typing import Optional

from .conditions import DefaultDeploymentCondition
from .conditions import DeploymentCondition

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

if not LOG.handlers:
    LOG.addHandler(logging.StreamHandler(sys.stdout))


class TestResult(ABC):
    """Represents test results."""


class Pass(TestResult):
    """Represents a passed test."""


class Fail(TestResult):
    """Represents a failed test."""
    def __init__(self, message: Optional[str]) -> None:
        self.message = message


class IntegTestBase(ABC):
    """Test runner to execute an integration test."""

    def __init__(self, name: str) -> None:
        self.name = name

    def setup(self) -> None:
        """Hook for tests to run setup that needs to happen prior to the test."""

    @abstractmethod
    def test(self) -> TestResult:
        """Hook for tests to run tests against the functionality under test."""

    def teardown(self) -> None:
        """Hook for tests to run teardown logic that needs to happen after the test."""

    def run(self) -> TestResult:
        """Run the integration test."""
        try:
            LOG.info("STARTING: '%s'", self.name)
            self.setup()
            return self.test()
        except Exception as ex:
            return Fail(str(ex))
        finally:
            self.teardown()


class IntegTestRunner:
    """Runner for integration tests."""

    def __init__(
            self,
            test_modules: List[str],
            deployment_condition: DeploymentCondition = DefaultDeploymentCondition()) -> None:

        self.tests = self._get_test_classes_for_modules(test_modules)
        self.results = {}  # type: Dict[IntegTestBase, TestResult]
        self.deployment_condition = deployment_condition

    def _get_test_classes_for_modules(self, test_modules: List[str]) -> List[IntegTestBase]:
        """dynamically loads and instantiates all subclasses of the integration test base."""

        for test_module in test_modules:
            if test_module not in sys.modules:
                LOG.info('importing module: %s', test_module)
                importlib.import_module(test_module)

        return [
            test_class() for test_class in IntegTestBase.__subclasses__()  # type: ignore
            if getattr(test_class, '__module__', None) in test_modules
        ]

    def run(self) -> bool:
        """Run integration test suite, optionally waiting for the IoT deployment to finish."""
        if not self.tests:
            LOG.error('FAILED: no tests to run!')
            return False

        try:
            self._block_on_deployment_condition()
        except Exception as ex:
            LOG.exception(ex)
            return False

        return self._run_tests()

    def _block_on_deployment_condition(self):
        """
        Block on deployment condition. If the condition is not met within the specified timeout, a
        TimeoutError will be thrown.
        """
        start = time()
        while True:
            if self.deployment_condition.is_met():
                return

            if time() - start < self.deployment_condition.timeout():
                sleep(1)
            else:
                raise TimeoutError(
                    'deployment condition not met within {} seconds'.format(self.deployment_condition.timeout()))

    def _run_tests(self) -> bool:
        self.results = {test: test.run() for test in self.tests}
        all_passed = True
        for test, result in self.results.items():
            if isinstance(result, Pass):
                self._log_passed(test.name)

            if isinstance(result, Fail):
                self._log_failed(test.name, result.message)
                all_passed = False

        if all_passed:
            self._log_passed('Integration Test Suite')
        else:
            self._log_failed('Integration Test Suite', 'Not all tests passed!')

        return all_passed

    def _log_passed(self, name: str):
        LOG.info('%s PASSED: \'%s\'', u'\u2713', name)

    def _log_failed(self, name: str, reason: Optional[str]):
        LOG.error('%s FAILED: \'%s\'. Reason: %s', u'\u2717', name, reason)

    @property
    def passed_count(self) -> int:
        """Count of tests that have passed."""
        return sum(map(lambda result: int(isinstance(result, Pass)), self.results.values()))

    @property
    def failed_count(self) -> int:
        """Count of tests that have failed."""
        return len(self.results) - self.passed_count
