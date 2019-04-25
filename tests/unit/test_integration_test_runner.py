import unittest

from detoxed.conditions import DefaultDeploymentCondition
from detoxed.conditions import DeploymentCondition
from detoxed.integ import IntegTestRunner

PASSING = ['tests.unit.testcases.passing']
FAILING = ['tests.unit.testcases.failing']
EXCEPTIONED = ['tests.unit.testcases.exceptioned']


class TestIntegTestRunner(unittest.TestCase):

    def test_passing_tests_produce_passing_result(self) -> None:
        runner = IntegTestRunner(PASSING)
        self.assertTrue(
            runner.run(),
            'passing tests should produce a passing result'
        )
        self.assertEqual(1, runner.passed_count, 'passed count is wrong')
        self.assertEqual(0, runner.failed_count, 'failed count is wrong')

    def test_failing_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner(FAILING)
        self.assertFalse(
            runner.run(),
            'failing tests should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(1, runner.failed_count, 'failed count is wrong')

    def test_exception_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner(EXCEPTIONED)
        self.assertFalse(
            runner.run(),
            'exceptioned tests should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(1, runner.failed_count, 'failed count is wrong')

    def test_passing_and_failing_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner(PASSING + FAILING)
        self.assertFalse(
            runner.run(),
            'passing tests with failing tests should produce a failing result'
        )
        self.assertEqual(1, runner.passed_count, 'passed count is wrong')
        self.assertEqual(1, runner.failed_count, 'failed count is wrong')

    def test_default_deployment_condition_is_correct_instance(self) -> None:
        self.assertIsInstance(IntegTestRunner([]).deployment_condition, DefaultDeploymentCondition)

    def test_passing_test_with_deployment_timeout_produce_failing_result(self) -> None:
        class TimeoutDeploymentCondition(DeploymentCondition):
            def timeout(self) -> int:
                return 2

            def is_met(self) -> bool:
                return False

        runner = IntegTestRunner(PASSING, TimeoutDeploymentCondition())
        self.assertFalse(
            runner.run(),
            'passing tests with failing tests should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(0, runner.failed_count, 'failed count is wrong')

    def test_no_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner([])
        self.assertFalse(
            runner.run(),
            'no test scenario should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(0, runner.failed_count, 'failed count is wrong')
