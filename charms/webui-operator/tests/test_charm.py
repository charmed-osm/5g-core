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
""" WebUI test script for charm.py """

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import WebuiCharm


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(WebuiCharm)
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
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_start_with_relations(self) -> NoReturn:
        """Test installation with any relation."""
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "webui",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "webui",
                            "containerPort": 5000,
                            "protocol": "TCP",
                        }
                    ],
                    "envConfig": {
                        "ALLOW_ANONYMOUS_LOGIN": "yes",
                        "GIN_MODE": "release",
                    },
                    "command": ["./webui", "&"],
                }
            ],
        }

        self.harness.charm.on.start.emit()
        # Check if nrf is initialized
        self.assertIsNone(self.harness.charm.state.mongodb_host)

        # Initializing the nrf relation
        mongodb_relation_id = self.harness.add_relation("mongodb", "mongodb")
        self.harness.add_relation_unit(mongodb_relation_id, "mongodb/0")
        self.harness.update_relation_data(
            mongodb_relation_id, "mongodb", {"hostname": "mongodb"}
        )

        # Checking if nrf data is stored
        self.assertEqual(self.harness.charm.state.mongodb_host, "mongodb")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_mongodb_app_relation_changed(self) -> NoReturn:
        """Test to see if kafka relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.mongodb_host)

        relation_id = self.harness.add_relation("mongodb", "mongodb")
        self.harness.add_relation_unit(relation_id, "mongodb/0")
        self.harness.update_relation_data(
            relation_id, "mongodb", {"hostname": "mongodb"}
        )

        self.assertEqual(self.harness.charm.state.mongodb_host, "mongodb")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )


if __name__ == "__main__":
    unittest.main()
