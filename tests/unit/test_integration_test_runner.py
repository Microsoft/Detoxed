import unittest

from detoxed.integ import IntegTestRunner

PASSING = ['tests.unit.testcases.passing']
FAILING = ['tests.unit.testcases.failing']
EXCEPTIONED = ['tests.unit.testcases.exceptioned']


class TestIntegTestRunner(unittest.TestCase):

    def test_passing_tests_produce_passing_result(self) -> None:
        runner = IntegTestRunner(PASSING, 1, '', '', '')
        self.assertTrue(
            runner.run(wait_for_deployment=False),
            'passing tests should produce a passing result'
        )
        self.assertEqual(1, runner.passed_count, 'passed count is wrong')
        self.assertEqual(0, runner.failed_count, 'failed count is wrong')

    def test_failing_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner(FAILING, 1, '', '', '')
        self.assertFalse(
            runner.run(wait_for_deployment=False),
            'failing tests should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(1, runner.failed_count, 'failed count is wrong')

    def test_exception_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner(EXCEPTIONED, 1, '', '', '')
        self.assertFalse(
            runner.run(wait_for_deployment=False),
            'exceptioned tests should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(1, runner.failed_count, 'failed count is wrong')

    def test_passing_and_failing_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner(PASSING + FAILING, 1, '', '', '')
        self.assertFalse(
            runner.run(wait_for_deployment=False),
            'passing tests with failing tests should produce a failing result'
        )
        self.assertEqual(1, runner.passed_count, 'passed count is wrong')
        self.assertEqual(1, runner.failed_count, 'failed count is wrong')

    def test_passing_test_with_deployment_timeout_produce_failing_result(self) -> None:
        runner = IntegTestRunner(PASSING, 1, '', '', '')
        self.assertFalse(
            runner.run(wait_for_deployment=True),
            'passing tests with failing tests should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(0, runner.failed_count, 'failed count is wrong')

    def test_no_tests_produce_failing_result(self) -> None:
        runner = IntegTestRunner([], 1, '', '', '')
        self.assertFalse(
            runner.run(wait_for_deployment=True),
            'no test scenario should produce a failing result'
        )
        self.assertEqual(0, runner.passed_count, 'passed count is wrong')
        self.assertEqual(0, runner.failed_count, 'failed count is wrong')
