import json
import unittest
from typing import List
from unittest.mock import MagicMock
from unittest.mock import call

from detoxed.conditions import CommandRunner
from detoxed.conditions import DefaultDeploymentCondition
from detoxed.conditions import IoTDeploymentFinishedCondition


def make_cli_side_effect_for_counts(counts: List[int]) -> List[str]:
    return [json.dumps([{'_count': i}]) for i in counts]


class TestDeploymentConditions(unittest.TestCase):

    def test_default_condition(self) -> None:
        condition = DefaultDeploymentCondition()
        self.assertTrue(condition.is_met())
        self.assertEqual(0, condition.timeout())

    def test_iot_deployment_condition_timeout(self) -> None:
        condition = IoTDeploymentFinishedCondition(
            timeout=5,
            iot_hub='iot_hub',
            deployment_id='deployment_id',
            device_query='device_query')

        self.assertEqual(5, condition.timeout())

    def test_iot_deployment_condition_not_met_for_zero_counts(self) -> None:
        cmd_mock = MagicMock()
        cmd_mock.run.side_effect = make_cli_side_effect_for_counts([0, 0])

        condition = IoTDeploymentFinishedCondition(
            timeout=5,
            iot_hub='iot_hub',
            deployment_id='deployment_id',
            device_query='device_query',
            command_runner=cmd_mock)

        self.assertFalse(condition.is_met())

    def test_iot_deployment_condition_not_met_for_differing_counts(self) -> None:
        cmd_mock = MagicMock()
        cmd_mock.run.side_effect = make_cli_side_effect_for_counts([1, 2])

        condition = IoTDeploymentFinishedCondition(
            timeout=5,
            iot_hub='iot_hub',
            deployment_id='deployment_id',
            device_query='device_query',
            command_runner=cmd_mock)

        self.assertFalse(condition.is_met())

    def test_iot_deployment_condition_met_for_same_positive_counts(self) -> None:
        cmd_mock = MagicMock()
        cmd_mock.run.side_effect = make_cli_side_effect_for_counts([2, 2])

        condition = IoTDeploymentFinishedCondition(
            timeout=5,
            iot_hub='iot_hub',
            deployment_id='deployment_id',
            device_query='device_query',
            command_runner=cmd_mock)

        self.assertTrue(condition.is_met())

    def test_iot_deployment_condition_runs_correct_commands(self) -> None:
        cmd_mock = MagicMock()
        condition = IoTDeploymentFinishedCondition(
            timeout=5,
            iot_hub='iot_hub',
            deployment_id='deployment_id',
            device_query='device_query',
            command_runner=cmd_mock)

        condition.is_met()

        expected_command_format = 'az iot hub query -n "{0}" -q "{1}" -o json'
        expected_targeted_count_format = (
            "select count() as _count from devices "
            "where capabilities.iotEdge = true and {0}")
        expected_successful_count_format = (
            "select count() as _count from devices.modules "
            r"where moduleId = '\$edgeAgent' and configurations.[[{0}]].status = 'Applied' "
            r"and properties.desired.\$version = properties.reported.lastDesiredVersion and "
            "properties.reported.lastDesiredStatus.code = 200")

        self.assertEqual(2, cmd_mock.run.call_count)
        self.assertEqual(
            cmd_mock.run.call_args_list,
            [
                call(expected_command_format.format(
                    'iot_hub',
                    expected_targeted_count_format.format('device_query'))),
                call(expected_command_format.format(
                    'iot_hub',
                    expected_successful_count_format.format('deployment_id'))),
            ]
        )

    def test_command_runner(self):
        cmd_runner = CommandRunner()
        self.assertIsNone(cmd_runner.run('not a real command'))
        self.assertGreater(len(cmd_runner.run('ls -lah')), 0)
