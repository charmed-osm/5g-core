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
"""UPF test script for charm.py"""

import unittest

# from unittest.mock import Mock
from typing import NoReturn

from ops.model import BlockedStatus
from ops.testing import Harness
from charm import Upf1Charm


class TestCharm(unittest.TestCase):
    """Test script for checking relations"""

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(Upf1Charm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_start_without_relations(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.config_changed.emit()

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_start_with_relations(self) -> NoReturn:
        """Test installation with any relation."""
        annot = {
            "annotations": {
                "k8s.v1.cni.cncf.io/networks": '[\n{\n"name" : "n6-network",'
                '\n"interface": "eth1",\n"ips": []\n}\n]'
            },
            "securityContext": {"runAsUser": 0000, "runAsGroup": 0000},
        }
        service = [{
            "name": "upf-e",
            "labels": {"juju-app": "upf1"},
            "spec": {
                "selector": {"juju-app": "upf1"},
                "ports": [{"protocol": "TCP", "port": 80, "targetPort": 80}],
                "type": "ClusterIP",
            },
        }]

        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "upf1",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "upf1",
                            "containerPort": 2152,
                            "protocol": "UDP",
                        }
                    ],
                    "envConfig": {
                        "UE_RANGE": "60.60.0.0/24",
                        "STATIC_IP": "192.168.70.15",
                    },
                    "command": ["./upf_start.sh", "&"],
                    "kubernetes": {"securityContext": {"privileged": True}},
                }
            ],
            "kubernetesResources": {
                "services": service,
                "pod": annot,
            },
        }
        # Check if natapp is initialized
        self.assertIsNone(self.harness.charm.state.natapp_ip)
        self.assertIsNone(self.harness.charm.state.natapp_host)

        # Initializing the natapp relation
        natapp_relation_id = self.harness.add_relation("natapp", "natapp")
        self.harness.add_relation_unit(natapp_relation_id, "natapp/0")
        self.harness.update_relation_data(
            natapp_relation_id,
            "natapp",
            {"hostname": "natapp", "static_ip": "192.168.70.15"},
        )
        # Checking if natapp data is stored
        self.assertEqual(self.harness.charm.state.natapp_ip, "192.168.70.15")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_config_change(self) -> NoReturn:
        """Test installation without any relation."""

        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "upf1",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {"name": "upf1", "containerPort": 2152, "protocol": "UDP"}
                    ],
                    "envConfig": {
                        "UE_RANGE": "60.60.0.0/24",
                        "STATIC_IP": "192.168.70.15",
                    },
                    "command": ["./upf_start.sh", "&"],
                    "kubernetes": {"securityContext": {"privileged": True}},
                }
            ],
            "kubernetesResources": {
                "pod": {
                    "annotations": {
                        "k8s.v1.cni.cncf.io/networks": '[\n{\n"name" : "n6-network",'
                        '\n"interface": "eth1",\n"ips": []\n}\n]'
                    },
                    "securityContext": {"runAsUser": 0, "runAsGroup": 0},
                },
                "services": [
                    {
                        "name": "upf-e",
                        "labels": {"juju-app": "upf1"},
                        "spec": {
                            "selector": {"juju-app": "upf1"},
                            "ports": [
                                {"protocol": "TCP", "port": 80, "targetPort": 80}
                            ],
                            "type": "ClusterIP",
                        },
                    }
                ],
            },
        }

        # Check if nrf,upf is initialized
        self.assertIsNone(self.harness.charm.state.natapp_ip)

        # Initializing the nrf relation
        natapp_relation_id = self.harness.add_relation("natapp", "natapp")
        self.harness.add_relation_unit(natapp_relation_id, "natapp/0")
        self.harness.update_relation_data(
            natapp_relation_id,
            "natapp",
            {"hostname": "natapp", "static_ip": "192.168.70.15"},
        )

        # Checking if nrf,upf data is stored
        self.assertEqual(self.harness.charm.state.natapp_ip, "192.168.70.15")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_natapp_app_relation_changed(self) -> NoReturn:
        """Test to see if upf app relation is updated."""
        self.harness.charm.on.config_changed.emit()

        self.assertIsNone(self.harness.charm.state.natapp_ip)

        # Initializing the upf relation
        natapp_relation_id = self.harness.add_relation("natapp", "upf")
        self.harness.add_relation_unit(natapp_relation_id, "natapp/0")
        relation_data = {"static_ip": "192.168.70.15"}
        self.harness.update_relation_data(natapp_relation_id, "natapp/0", relation_data)

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_publish_upf_info(self) -> NoReturn:
        """Test to see if upf relation is updated."""
        expected_result = {
            "private_address": "127.1.1.1",
        }
        relation_id = self.harness.add_relation("upf", "smf")
        relation_data = {"private_address": "127.1.1.1"}
        self.harness.update_relation_data(relation_id, "upf1", relation_data)
        relation_data = self.harness.get_relation_data(relation_id, "upf1")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main()
