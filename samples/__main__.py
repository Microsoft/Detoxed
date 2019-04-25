"""Sample code for the package."""
from detoxed.integ import IntegTestRunner

# This should be set to True if run from a release pipeline and False if used for local
# testing. If set to True, the tests won't run until the deployment has been applied to
# all devices matching the deployment condition.
WAIT_FOR_DEPLOYMENT = False

# This is the name of the IoT Hub on which the deployment
# is being executed.
#
# Note: Only obeyed if WAIT_FOR_DEPLOYMENT=True.
IOT_HUB_NAME = '<your IoT Hub Name>'

# This specifies the maximum amount of time that to wait for a deployment to be successfully
# applied to the devices matching the target criterion. If the deployment is not applied
# within this time, the test run will produce a negative (failed) result.
#
# Note: Only obeyed if WAIT_FOR_DEPLOYMENT=True.
DEPLOYMENT_TIMEOUT_SECONDS = 300

# This will be the ID of the deployment.
#
# Note: Only obeyed if WAIT_FOR_DEPLOYMENT=True.
#
# For more information about this, search for the term 'ID' in the following documentation:
#   https://docs.microsoft.com/en-us/azure/iot-edge/how-to-deploy-monitor
DEPLOYMENT_ID = '<deployment id>'

# This will be the deployment condition used in the IoT deployment.
#
# Note: Only obeyed if WAIT_FOR_DEPLOYMENT=True.
#
# For more information
# about this, search for the term 'Target condition' in the following documentation:
#   https://docs.microsoft.com/en-us/azure/iot-edge/how-to-deploy-monitor
DEPLOYMENT_CONDITION = "tags.environment='dev'"

# This specifies the modules to look for tests to run. All tests that exist in these modules
# will be initialized and run by the test runner.
TEST_MODULES = [
    'samples.tests'
]

def run_example() -> None:
    """Run example."""
    test_runner = IntegTestRunner(
        TEST_MODULES,
        DEPLOYMENT_TIMEOUT_SECONDS,
        DEPLOYMENT_ID,
        DEPLOYMENT_CONDITION,
        IOT_HUB_NAME
    )

    results = test_runner.run(wait_for_deployment=WAIT_FOR_DEPLOYMENT)
    print('Number of tests run: {}'.format(test_runner.failed_count + test_runner.passed_count))
    print('Number of tests passed: {}'.format(test_runner.passed_count))
    print('Number of tests failed: {}'.format(test_runner.failed_count))

    assert test_runner.passed_count == 1
    assert test_runner.failed_count == 0
    assert results


if __name__ == '__main__':
    run_example()
