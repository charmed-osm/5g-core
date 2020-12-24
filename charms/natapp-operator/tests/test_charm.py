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
"""NatApp test script for charm.py"""

import unittest
from typing import NoReturn

from ops.testing import Harness
from ops.model import BlockedStatus

from charm import NatappCharm

# from ops.model import BlockedStatus


class TestCharm(unittest.TestCase):
    """Test script for checking relations"""

    def setUp(self) -> NoReturn:
        """Test setup."""
        self.harness = Harness(NatappCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_start_without_relations(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for")
        )

    def test_on_start_with_relations(self) -> NoReturn:
        """Test installation with any relation."""
        self.harness.charm.on.start.emit()
        annot = {
            "annotations": {
                "k8s.v1.cni.cncf.io/networks": '[\n{\n"name" : "n6-network",'
                '\n"interface": "eth1",\n"ips": ["192.168.1.216"]\n}\n]'
            }
        }
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "natapp",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "natapp",
                            "containerPort": 2601,
                            "protocol": "UDP",
                        }
                    ],
                    "command": ["./start.sh", "&"],
                    "kubernetes": {"securityContext": {"privileged": True}},
                }
            ],
            "kubernetesResources": {"pod": annot},
        }
        # Check if nrf is initialized
        self.assertIsNone(self.harness.charm.state.upf_host)

        # Initializing the nrf relation
        upf_relation_id = self.harness.add_relation("upf", "upf")
        self.harness.add_relation_unit(upf_relation_id, "upf/0")
        self.harness.update_relation_data(
            upf_relation_id, "upf/0", {"private_address": "upf"}
        )

        # Checking if nrf data is stored
        self.assertEqual(self.harness.charm.state.upf_host, "upf")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_upf_app_relation_changed(self) -> NoReturn:
        """Test to see if upf relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.upf_host)

        upf_relation_id = self.harness.add_relation("upf", "upf")
        self.harness.add_relation_unit(upf_relation_id, "upf/0")
        self.harness.update_relation_data(
            upf_relation_id, "upf/0", {"private_address": "upf"}
        )

        self.assertEqual(self.harness.charm.state.upf_host, "upf")
        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )


if __name__ == "__main__":
    unittest.main()
