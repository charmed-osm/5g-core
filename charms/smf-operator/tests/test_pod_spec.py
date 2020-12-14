""" test script for pod spec.py """
from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 29502

        expected_result = [
            {
                "name": "smf",
                "containerPort": port,
                "protocol": "TCP",
            }
        ]
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports()

        self.assertListEqual(expected_result, pod_ports)

    def test_check_data(self) -> NoReturn:
        """Testing check data."""
        expected_result = True
        config = {"gin_mode": "release"}
        relation = {"upf_host": "127.0.0.1"}
        # pylint:disable=W0212
        check_data = pod_spec._check_data(config, relation)
        self.assertEqual(expected_result, check_data)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig configuration."""
        expected_result = {
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "GIN_MODE": "release",
            "IPADDR1": "127.0.0.1",
        }
        mode = {"gin_mode": "release"}
        ipadd = {"upf_host": "127.0.0.1"}
        # pylint:disable=W0212
        pod_envconfig = pod_spec._make_pod_envconfig(mode, ipadd)
        self.assertDictEqual(expected_result, pod_envconfig)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""
        expected_result = ["./ipscript.sh", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "localhost:32000/free5gc-smf:1.0"}
        config = {
            "gin_mode": "release",
        }
        app_name = "smf"
        relation_state = {"upf_host": "127.0.0.500"}

        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, relation_state, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
