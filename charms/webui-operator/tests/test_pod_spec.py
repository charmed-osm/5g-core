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
""" test script for pod spec.py """
from typing import NoReturn
import unittest

import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 5000

        expected_result = [
            {
                "name": "webui",
                "containerPort": port,
                "protocol": "TCP",
            }
        ]
        pod_ports = pod_spec._make_pod_ports()

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Teting make pod envconfig configuration."""

        expected_result = {
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "GIN_MODE": "release",
            "MONGODB_URI": "mongodb://mongodb:27017",
        }
        mode = {"gin_mode": "release"}
        relation_state = {"mongodb_uri": "mongodb://mongodb:27017"}
        pod_envconfig = pod_spec._make_pod_envconfig(mode, relation_state)
        self.assertDictEqual(expected_result, pod_envconfig)

    def test_make_pod_command(self) -> NoReturn:
        """Teting make pod command."""

        expected_result = ["./webui_start.sh", "&"]
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_validate_config(self) -> NoReturn:
        """Testing config data scenario."""
        config = {"gin_mode": "xyz"}
        with self.assertRaises(ValueError):
            pod_spec._validate_config(config)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec."""
        image_info = {"upstream-source": "localhost:32000/free5gc-webui:1.0"}
        config = {"gin_mode": 12345}
        app_name = "webui"
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)
