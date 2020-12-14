""" test script for pod spec.py """
from typing import NoReturn
import unittest

import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 29531

        expected_result = [
            {
                "name": "nssf",
                "containerPort": port,
                "protocol": "TCP",
            }
        ]
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports()

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig configuration."""

        expected_result = {
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "GIN_MODE": "release",
        }
        mode = {"gin_mode": "release"}
        # pylint:disable=W0212
        pod_envconfig = pod_spec._make_pod_envconfig(mode)
        self.assertDictEqual(expected_result, pod_envconfig)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./nssf", "-nssfcfg", "../config/nssfcfg.conf", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "localhost:32000/free5gc-nssf:1.0"}
        config = {
            "gin_mode": "notrelease",
        }
        app_name = "nssf"
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)
