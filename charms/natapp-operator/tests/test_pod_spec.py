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
                "name": "natapp",
                "containerPort": port,
                "protocol": "UDP",
            }
        ]
        portdict = {
            "port": 9999,
        }
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_podannotations(self) -> NoReturn:
        """Testing make pod envconfig configuration."""

        networks = '[\n{\n"name" : "n6-network",\n"interface": "eth1",\n"ips": ["192.168.1.216"]\n}]' # noqa
        expected_result = {
            "annotations": {"k8s.v1.cni.cncf.io/networks": networks}
        }
        pod_annotation = pod_spec._make_pod_podannotations()
        self.assertDictEqual(expected_result, pod_annotation)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./nat", "eth1", "eth0", "169.254.1.1"]
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_(self) -> NoReturn:
        """Testing make pod envconfig configuration."""

        expected_result = {"securityContext": {"privileged": True}}
        pod_privilege = pod_spec._make_pod_privilege()
        self.assertDictEqual(expected_result, pod_privilege)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "10.45.5.100:4200/canonical/natapp:dev2.0"}
        config = {
            "port": -2,
        }
        app_name = "natapp"
        with self.assertRaises(ValidationError):
            pod_spec.make_pod_spec(image_info, config, app_name)
