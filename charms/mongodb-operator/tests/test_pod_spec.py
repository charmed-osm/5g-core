""" Test script for pod spec.py """
# Copyright 2020 Ubuntu
# See LICENSE file for licensing details.

from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 27017
        expected_result = [
            {
                "name": "mongodb",
                "containerPort": port,
                "protocol": "TCP",
            }
        ]
        dictport = {"mongo_port": 27017}
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports(dictport)
        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command"""

        expected_result = [
            "mongod",
            "--bind_ip",
            "mongodb-endpoints",
            "--port",
            "27017",
        ]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "localhost:32000/free5gc-mongo:1.0"} # noqa
        config = {
            "mongo_port": 9999,
        }
        app_name = "mongodb"

        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main()
