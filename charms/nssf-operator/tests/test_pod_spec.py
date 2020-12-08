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
                "name": "nssf",
                "containerPort": port,
                "protocol": "TCP",
            }
        ]
        portdict = {
            "port": 9999,
        }
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig configuration."""

        expected_result = {
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "GIN_MODE": "release",
        }
        mode = {"gin_mode": "release"}
        pod_envconfig = pod_spec._make_pod_envconfig(mode)
        self.assertDictEqual(expected_result, pod_envconfig)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./nssf", "-nssfcfg", "../config/nssfcfg.conf", "&"]
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "10.45.5.100:4200/canonical/nssf:dev2.0"}
        config = {
            "port": 29518,
            "gin_mode": "release",
        }
        app_name = "nssf"
        with self.assertRaises(ValidationError):
            pod_spec.make_pod_spec(image_info, config, app_name)