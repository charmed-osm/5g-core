# Copyright 2020 canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.

import unittest
# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import NrfCharm


class TestCharm(unittest.TestCase):
    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(NrfCharm)
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
                    "name": "nrf",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [{
                        "name": "nrf",
                        "containerPort": 29510,
                        "protocol": "TCP",
                    }],
                    "envConfig": {
                        "ALLOW_ANONYMOUS_LOGIN": "yes",
                        "DB_URI": "mongodb://db/free5gc",
                        "GIN_MODE": "release",
                    },
                    "command": ["./nrf", "-nrfcfg", "../config/nrfcfg.conf", "&"],
                }
            ],
        }
        self.harness.charm.on.start.emit()
        # Check if nrf is initialized
        self.assertIsNone(self.harness.charm.state.db_host)

        # Initializing the nrf relation
        nrf_relation_id = self.harness.add_relation("db", "db")
        self.harness.add_relation_unit(nrf_relation_id, "db/0")
        self.harness.update_relation_data(
            nrf_relation_id, "db", {"hostname": "db"}
        )

        # Checking if nrf data is stored
        self.assertEqual(self.harness.charm.state.db_host, "db")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_db_app_relation_changed(self) -> NoReturn:
        """Test to see if kafka relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.db_host)

        relation_id = self.harness.add_relation("db", "db")
        self.harness.add_relation_unit(relation_id, "db/0")
        self.harness.update_relation_data(
            relation_id, "db", {"hostname": "db"}
        )

        self.assertEqual(self.harness.charm.state.db_host, "db")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_publish_nrf_info(self) -> NoReturn:
        """Test to see if nrf relation is updated."""
        expected_result = {
            "hostname": "nrf",
        }
        self.harness.charm.on.start.emit()
        relation_id = self.harness.add_relation("nrf", "amf")
        self.harness.add_relation_unit(relation_id, "amf/0")
        relation_data = self.harness.get_relation_data(relation_id, "nrf")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main()