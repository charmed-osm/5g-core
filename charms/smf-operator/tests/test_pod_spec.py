#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##
"""test script for pod spec.py"""
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
        pod_ports = pod_spec._make_pod_ports()

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig configuration."""
        expected_result = {
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "GIN_MODE": "release",
            "IPADDR1": "127.0.0.1",
            "NRF_HOST": "nrf",
        }
        mode = {"gin_mode": "release"}
        relation = {"upf_host": "127.0.0.1", "nrf_host": "nrf"}
        pod_envconfig = pod_spec._make_pod_envconfig(mode, relation)
        self.assertDictEqual(expected_result, pod_envconfig)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""
        expected_result = ["./ipscript.sh", "&"]
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_validate_config(self) -> NoReturn:
        """Testing config data scenario."""
        config = {"gin_mode": "xyz"}
        with self.assertRaises(ValueError):
            pod_spec._validate_config(config)

    def test_validate_relation(self) -> NoReturn:
        """Testing relation data scenario."""
        relation_state = {"upf_host": "xyz", "nrf_host": None}
        with self.assertRaises(ValueError):
            pod_spec._validate_relation_state(relation_state)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec."""
        image_info = {"upstream-source": "localhost:32000/free5gc-smf:1.0"}
        config = {
            "gin_mode": "release",
        }
        app_name = "smf"
        relation_state = {"upf_host": "127.0.0.500", "nrf_host": None}

        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, relation_state, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
