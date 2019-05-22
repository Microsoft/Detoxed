"""Sample code for the package."""
from typing import List
from detoxed.conditions import DefaultDeploymentCondition
from detoxed.integ import DeploymentCondition
from detoxed.integ import IntegTestRunner

# The modules holding the passing test cases.
PASSING_TEST_MODULES = [
    'samplepy.tests.passing'
]

# The modules holding the failing test cases.
FAILING_TEST_MODULES = [
    'samplepy.tests.failing'
]


def run_test_cases_and_assert_outcome(
        test_cases: List[str],
        expected_pass_count: int,
        expected_fail_count: int,
        expected_overall_result: bool,
        deployment_condition: DeploymentCondition = DefaultDeploymentCondition()) -> None:
    """Run tests and assert pass/fail metrics."""

    test_runner = IntegTestRunner(test_cases, deployment_condition)
    results = test_runner.run()
    print('Number of tests run: {}'.format(test_runner.failed_count + test_runner.passed_count))
    print('Number of tests passed: {}'.format(test_runner.passed_count))
    print('Number of tests failed: {}'.format(test_runner.failed_count))

    assert test_runner.passed_count == expected_pass_count
    assert test_runner.failed_count == expected_fail_count
    assert results == expected_overall_result


if __name__ == '__main__':

    # run the passing test cases
    run_test_cases_and_assert_outcome(
        test_cases=PASSING_TEST_MODULES,
        expected_pass_count=1,
        expected_fail_count=0,
        expected_overall_result=True)

    # run the failing test cases
    run_test_cases_and_assert_outcome(
        test_cases=FAILING_TEST_MODULES,
        expected_pass_count=0,
        expected_fail_count=1,
        expected_overall_result=False)
