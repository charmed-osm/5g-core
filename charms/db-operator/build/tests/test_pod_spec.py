# Copyright 2020 Ubuntu
# See LICENSE file for licensing details.

from pydantic import ValidationError
from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 9999
        expected_result = [
            {
                "name": "db",
                "containerPort": port,
                "protocol": "TCP",
            }

        ]
        portdict = {
            "port": 9999,
        }
        pod_ports = pod_spec._make_pod_ports(portdict)
        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command"""

        expected_result = ["mongod", "--bind_ip", "db-endpoints", "--port", "27017"]

        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "10.45.5.100:4200/canonical/core-db:v1.0"}
        config = {
            "port": 9999,
        }
        app_name = "db"

        with self.assertRaises(ValidationError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
