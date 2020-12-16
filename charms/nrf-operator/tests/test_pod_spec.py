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
        port = 29510

        expected_result = [
            {
                "name": "nrf",
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
        relation = {"mongodb_uri": "mongodb://mongodb/free5gc"}
        # pylint:disable=W0212
        check_data = pod_spec._check_data(config, relation)
        self.assertEqual(expected_result, check_data)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig configuration."""

        expected_result = {
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "MONGODB_URI": "mongodb://mongodb/free5gc",
            "GIN_MODE": "release",
        }
        mode = {"gin_mode": "release"}
        relation = {
            "mongodb_uri": "mongodb://mongodb/free5gc",
        }
        # pylint:disable=W0212
        pod_envconfig = pod_spec._make_pod_envconfig(mode, relation)
        self.assertDictEqual(expected_result, pod_envconfig)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./nrf", "-nrfcfg", "../config/nrfcfg.conf", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "localhost:32000/free5gc-nrf:1.0"}
        config = {
            "gin_mode": "release",
        }
        app_name = "nrf"
        relation_state = {"mongodb_uri": "norelation_mongodb"}
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, relation_state, app_name)
