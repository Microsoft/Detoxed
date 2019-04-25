"""Holds integration test suite code for IoTEdge modules."""
import importlib
import json
import logging
import subprocess
import sys
from abc import ABC
from abc import abstractmethod
from time import sleep
from time import time
from typing import Dict
from typing import List
from typing import Optional

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
            deployment_timeout_seconds: int,
            deployment_id: str,
            deployment_condition: str,
            iot_hub: str) -> None:
        self.tests = self._get_test_classes_for_modules(test_modules)
        self.deployment_timeout_seconds = deployment_timeout_seconds
        self.deployment_condition = deployment_condition
        self.iot_hub = iot_hub
        self.deployment_id = deployment_id
        self.results = {}  # type: Dict[IntegTestBase, TestResult]

    def _get_test_classes_for_modules(self, test_modules: List[str]) -> List[IntegTestBase]:
        """dynamically loads and instantiates all subclasses of the integration test base."""

        for test_module in test_modules:
            LOG.info('importing module: %s', test_module)
            importlib.import_module(test_module)
        all_subclasses = [x() for x in IntegTestBase.__subclasses__()]  # type: ignore
        return [x for x in all_subclasses if getattr(x, '__module__', None) in test_modules]

    def run(self, wait_for_deployment=True) -> bool:
        """Run integration test suite, optionally waiting for the IoT deployment to finish."""
        if not self.tests:
            LOG.error('FAILED: no tests to run!')
            return False

        try:
            if wait_for_deployment:
                self._wait_for_deployment_to_finish()
        except TimeoutError as ex:
            LOG.exception(ex)
            return False

        return self._run_tests()

    def _wait_for_deployment_to_finish(self):
        """
        Ensures that the deployment has been applied to all target devices. If this takes too
        long, a timeout exception will be raised
        """
        start = time()
        while True:
            LOG.info('Waiting for deployment to finish...')
            if self._is_deployment_finished():
                return
            sleep(1.0)
            if time() - start > self.deployment_timeout_seconds:
                raise TimeoutError(
                    "Deployment taking longer than {0} seconds...".format(
                        self.deployment_timeout_seconds))

    # uses Azure CLI to determine if the deployment has
    def _is_deployment_finished(self):
        target_device_count_query = (
            "select count() as _count from devices "
            "where capabilities.iotEdge = true and " + self.deployment_condition
        )
        successful_device_count_query = (
            "select count() as _count from devices.modules "
            r"where moduleId = '\$edgeAgent' and configurations.[[{0}]].status = 'Applied' "
            r"and properties.desired.\$version = properties.reported.lastDesiredVersion and "
            "properties.reported.lastDesiredStatus.code = 200"
        ).format(self.deployment_id)

        target_device_count = self._query_for_count(target_device_count_query)
        successful_device_count = self._query_for_count(successful_device_count_query)

        deployment_done = target_device_count == successful_device_count and target_device_count > 0
        LOG.info('target_count=%d, successful_count=%d, deployment_done=%s',
                 target_device_count, successful_device_count, deployment_done)
        return deployment_done

    def _query_for_count(self, query: str) -> int:
        try:
            command = 'az iot hub query -n "{0}" -q "{1}" -o json'.format(self.iot_hub, query)
            LOG.info(command)
            os_response = self._run_os_command(command)
            if os_response:
                parsed_response = json.loads(os_response)
                if not parsed_response:
                    return 0
                return parsed_response[0]['_count']
        except Exception:
            LOG.exception('failed to find count from query')

        return 0

    def _run_os_command(self, command: str) -> Optional[str]:
        LOG.debug('running OS command:\n\t%s', command)
        try:
            result = subprocess.check_output(command, shell=True).decode('utf-8').strip()
            LOG.debug('response from OS command:\n\t%s', result)
            return result
        except KeyboardInterrupt as ex:
            raise ex
        except BaseException:
            LOG.debug('command returned non-zero exit code')
            return None

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
