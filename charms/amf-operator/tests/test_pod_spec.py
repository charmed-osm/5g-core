""" test script for pod spec.py """
from typing import NoReturn
import unittest

import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 29518

        expected_result = [
            {
                "name": "amf",
                "containerPort": port,
                "protocol": "TCP",
            }
        ]
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports()

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Teting make pod envconfig configuration."""

        expected_result = {
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "GIN_MODE": "release",
        }
        mode = {"gin_mode": "release"}
        # pylint:disable=W0212
        pod_envconfig = pod_spec._make_pod_envconfig(mode)
        self.assertDictEqual(expected_result, pod_envconfig)

    def test_make_pod_command(self) -> NoReturn:
        """Teting make pod command."""

        expected_result = ["./amf", "-amfcfg", "../config/amfcfg.conf", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_services(self) -> NoReturn:
        """Teting make pod services."""
        sctp_port = 38412
        expected_result = [
            {
                "name": "amf-lb",
                "labels": {"juju-app": "amf"},
                "spec": {
                    "selector": {"juju-app": "amf"},
                    "ports": [
                        {
                            "protocol": "SCTP",
                            "port": sctp_port,
                            "targetPort": sctp_port,
                        }
                    ],
                    "type": "LoadBalancer",
                },
            }
        ]
        # pylint:disable=W0212
        pod_services = pod_spec._make_pod_services("amf")
        self.assertEqual(expected_result, pod_services)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec"""
        image_info = {"upstream-source": "localhost:32000/free5gc-amf:1.0"}
        config = {
            "gin_mode": "12345",
        }
        app_name = "amf"
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
