# Detoxed

## About

[![Build Status](https://travis-ci.org/Microsoft/Detoxed.svg?branch=master)](https://travis-ci.org/Microsoft/Detoxed/)
[![codecov](https://codecov.io/gh/Microsoft/Detoxed/branch/master/graph/badge.svg)](https://codecov.io/gh/Microsoft/Detoxed)
[![PyPI version](https://badge.fury.io/py/detoxed.svg)](https://badge.fury.io/py/detoxed)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/detoxed.svg)](https://pypi.org/project/detoxed/)
[![PyPI - License](https://img.shields.io/pypi/l/detoxed.svg)](https://pypi.org/project/detoxed/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/detoxed.svg)](https://pypi.org/project/detoxed/)

`Detoxed` is an integration test harness that makes it easy to run a suite of integration tests in Python. It is easy to integrate into a CD pipeline and is currently being used to verify the correctness of Azure IoT Deployments in `Dev` and `QA` stages. It is easy to host in any CD pipelines that allow execution of user-defined scripts as part of a deployment.

`Detoxed` can be used in a CD pipeline to:

- Run integration test suite after a deployment to target stages
- Run sanity (*is it up?*) tests after deploying to production stages
- Trigger rollback of failed deployment

## Installation

`Detoxed` currently supports Python versions `3.4`, `3.5`, `3.6` and `3.7`. It can be installed by running `pip install detoxed`.

## Samples

`Detoxed` ships with a dockerized sample showing both passing and failing tests. The sample shows the following use cases:

- Invoking `Detoxed` as a CLI through `bash`
- Invoking `Detoxed` as a Python library.

To run the samples, follow these steps:

```bash
# clone the repo
git clone https://github.com/Microsoft/Detoxed.git
# enter the Detoxed directory
cd Detoxed/
# ensure Docker is running
docker --version
# build the project
docker build . -t detoxed
# run the samples
docker run detoxed
```

## Basic Usage

A common case for using `Detoxed` is to execute integration tests following the deployment of deployment either locally or to a cloud provisioned resource. Here is a simple integration test that will test if an application's HTTP endpoint is up and running:

```python
# assume module name is 'tests.integration.suite'
import requests
from os import getenv
from detoxed.integ import IntegTestBase, Fail, Pass, TestResult


class SimpleOutboundConnectionTestCase(IntegTestBase):
    def __init__(self):
        """Initialize test with a name of your choice."""
        super().__init__('Application responds to HTTP GET')

    # optional method to execute test setup...
    # def setup(self):
    #     ...

    # optional method to execute test teardown...
    # def teardown(self):
    #     ...

    def test(self) -> TestResult:
        """Test logic here. Should return Pass() or Fail('<failure message>')"""
        try:
            status_code = requests.get(getenv('APP_HTTP_ENDPOINT')).status_code
            if status_code == 200:
                return Pass()
            return Fail('status code expected to be 200 but was {}'.format(status_code))
        except Exception as ex:
            return Fail('failed to execute HTTP GET: {}'.format(ex))

# More tests can live in this module or other module.
```

### Running Integ Tests Locally

Here is how you would invoke this integration test locally using `Detoxed`:

```bash
export APP_HTTP_ENDPOINT="..."
export TEST_MODULES="tests.integration.suite" # add any number of modules here...
python3 -m detoxed $TEST_MODULES
```

This will produce the following logs:

```bash
importing module: tests.integration.suite
STARTING: 'Application responds to HTTP GET'
✓ PASSED: 'Application responds to HTTP GET'
# logs for any additional tests will be here...
✓ PASSED: 'Integration Test Suite'
```

### Running Integ Tests through deployment pipeline in Azure Dev Ops

Here is how you would invoke this integration test from an Azure Dev Ops Pipeline (steps for other CD technologies would be similar):

- Create a variable group linked to your release stage. It should include the following variables:
  - `TEST_MODULES`: modules where your integration test classes live
  - Any test-specific environment variables. In the example test above, this would be `APP_HTTP_ENDPOINT`
- Create a script step that runs the test harness:

```bash
python3 -m pip install detoxed
# install other modules as needed, perhaps from requirements.txt
python3 -m detoxed $TEST_MODULES
```

![ADO Setup](./.README.images/test_configure_ado.PNG)

## Advanced Usage

### Configuring Deployment Conditions

The test harness will accept an optional parameter that specifies a deployment condition. This condition defines a criteria that must be met in order for the tests to run along with a timeout that specifies how long to wait for the condition to pass. The default condition will immediately be met and will not block test execution. This behavior can be overriden by creating the test harness in python using a deployment condition that matches this interface:

```python
class DeploymentCondition(ABC):
    """Represents a deployment condition that should block the tests from running until met."""

    @abstractmethod
    def is_met(self) -> bool:
        """True if the condition is met, False otherwise."""

    @abstractmethod
    def timeout(self) -> int:
        """Timeout for contition to be met."""
```

### Azure IoT Edge Deployment Condition

A common case for using `Detoxed` is to execute integration tests following the deployment of an IoT application. Integration tests need to be run *after* the IoT Deployment is applied to the target devices. However the IoT Deployment is considered complete after it is applied to the IoT Hub itself. It may be quite some time until it is applied to the IoT devices. A built in deployment condition to handle this case ships with `Detoxed`.

```python
from detoxed.conditions import IoTDeploymentFinishedCondition
from detoxed.integ import IntegTestRunner


TEST_MODULES = [
    # your test modules here...
]

condition = IoTDeploymentFinishedCondition(
    timeout=300,                            # seconds to wait for deployment to finish
    iot_hub='my-iot-hub-qa',                # iot hub name
    deployment_id=102,                      # iot deployment ID
    device_query="tags.environment='qa'")   # iot device query to enumerate targeted devices

test_harness = IntegTestRunner(TEST_MODULES, condition)
passed = test_harness.run()
```

**Notes about `IoTDeploymentFinishedCondition`**: `IoTDeploymentFinishedCondition` currently has a hard dependency on the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest) and the [Azure IoT CLI Extension](https://github.com/Azure/azure-iot-cli-extension). `az login` must be executed for `IoTDeploymentFinishedCondition` to work properly. This can be accomplished in Azure Dev Ops by running the integration test using an `Azure CLI Task` with the `Use Global Configuration` option set to `True`.

## Pending development work

- Enable parallel test execution

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

For additional guidance, refer to the project-specific [contributing guidelines](./.github/CONTRIBUTING.md) as well as the [pull request template](./.github/PULL_REQUEST_TEMPLATE.md)
