"""Deployment conditions for integration tests."""

import json
import logging
import subprocess
import sys
from abc import ABC
from abc import abstractmethod
from typing import Optional

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

if not LOG.handlers:
    LOG.addHandler(logging.StreamHandler(sys.stdout))


class DeploymentCondition(ABC):
    """Represents a deployment condition that should block the tests from running until met."""

    @abstractmethod
    def is_met(self) -> bool:
        """True if the condition is met, False otherwise."""

    @abstractmethod
    def timeout(self) -> int:
        """Timeout for contition to be met."""


class DefaultDeploymentCondition(DeploymentCondition):
    """Default deployment condition that will not block."""

    def is_met(self) -> bool:
        return True

    def timeout(self) -> int:
        return 0


class CommandRunner():
    """Runs OS level command."""

    def run(self, command: str) -> Optional[str]:
        """Run command. Returns None if there was an error."""

        LOG.debug('running OS command:\n%s', command)
        try:
            result = subprocess.check_output(command, shell=True).decode('utf-8').strip()
            LOG.debug('response from OS command:\n\t%s', result)
            return result
        except KeyboardInterrupt as ex:
            raise ex
        except BaseException:
            LOG.debug('command returned non-zero exit code')
            return None


class IoTDeploymentFinishedCondition(DeploymentCondition):
    """
    Deployment condition that will block on Azure IoT deployment.

    Note: this implementation relies on the following:
        - Azure CLI must be installed on the machine
        - `az login` must have been run
    """

    def __init__(
            self,
            timeout: int,
            iot_hub: str,
            deployment_id: str,
            device_query: str,
            command_runner: CommandRunner = CommandRunner()) -> None:
        self._timeout = timeout
        self._iot_hub = iot_hub
        self._deployment_id = deployment_id
        self._device_query = device_query
        self._command_runner = command_runner

    def timeout(self) -> int:
        return self._timeout

    def is_met(self) -> bool:
        targeted_device_count = self._get_targeted_device_count()
        successful_device_count = self._get_successful_device_deployment_count()

        deployment_done = targeted_device_count == successful_device_count and targeted_device_count > 0
        LOG.info('target_count=%d, successful_count=%d, deployment_done=%s',
                 targeted_device_count, successful_device_count, deployment_done)
        return deployment_done

    def _get_targeted_device_count(self) -> int:
        return self._query_for_count((
            "select count() as _count from devices "
            "where capabilities.iotEdge = true and " + self._device_query
        ))

    def _get_successful_device_deployment_count(self) -> int:
        return self._query_for_count((
            "select count() as _count from devices.modules "
            r"where moduleId = '\$edgeAgent' and configurations.[[{0}]].status = 'Applied' "
            r"and properties.desired.\$version = properties.reported.lastDesiredVersion and "
            "properties.reported.lastDesiredStatus.code = 200"
        ).format(self._deployment_id))

    def _query_for_count(self, query: str) -> int:
        try:
            command = 'az iot hub query -n "{0}" -q "{1}" -o json'.format(self._iot_hub, query)
            os_response = self._command_runner.run(command)
            if os_response:
                parsed_response = json.loads(os_response)
                if not parsed_response:
                    return 0
                return parsed_response[0]['_count']
        except Exception:
            LOG.exception('failed to find count from query')

        return 0
