""" test script for pod spec.py """
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
            "natapp_port": 9999,
        }
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_podannotations(self) -> NoReturn:
        """Testing make pod envconfig configuration."""
        # pylint:disable=line-too-long
        networks = '[\n{\n"name" : "n6-network",\n"interface": "eth1",\n"ips": ["192.168.1.216"]\n}]'  # noqa
        expected_result = {"annotations": {"k8s.v1.cni.cncf.io/networks": networks}}
        # pylint:disable=W0212
        pod_annotation = pod_spec._make_pod_podannotations()
        self.assertDictEqual(expected_result, pod_annotation)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./start.sh", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_(self) -> NoReturn:
        """Testing make pod envconfig configuration."""

        expected_result = {"securityContext": {"privileged": True}}
        # pylint:disable=W0212
        pod_privilege = pod_spec._make_pod_privilege()
        self.assertDictEqual(expected_result, pod_privilege)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "localhost:32000/free5gc-natapp:1.0"}
        config = {
            "natapp_port": -2,
        }
        app_name = "natapp"
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)
