# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.
""" MongoDB test script for charm.py """

import unittest
from typing import NoReturn
from ops.testing import Harness
from ops.model import BlockedStatus

from charm import MongodbCharm


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(MongodbCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_configure_pod(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()

        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "mongodb",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "mongodb",
                            "containerPort": 27017,
                            "protocol": "TCP",
                        }
                    ],
                    "command": [
                        "mongod",
                        "--bind_ip",
                        "mongodb-endpoints",
                        "--port",
                        "27017",
                    ],
                }
            ],
        }

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_publish_mongodb_info(self) -> NoReturn:
        """Test to see if mongodb relation is updated."""
        expected_result = {
            "hostname": "mongodb",
            "mongodb_uri": "mongodb://mongodb/free5gc",
        }
        self.harness.charm.on.start.emit()
        relation_id = self.harness.add_relation("mongodb", "nrf")
        self.harness.add_relation_unit(relation_id, "nrf/0")
        relation_data = self.harness.get_relation_data(relation_id, "mongodb")
        print("relation_data", relation_data)
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main()
