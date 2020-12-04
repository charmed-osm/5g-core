# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.

import unittest
# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import AmfCharm


class TestCharm(unittest.TestCase):
    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(AmfCharm)
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
        # Check if nrf is initialized
        self.assertIsNone(self.harness.charm.state.nrf_host)

        # Initializing the nrf relation
        nrf_relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(nrf_relation_id, "nrf/0")
        self.harness.update_relation_data(
            nrf_relation_id, "nrf/0", {"hostname": "nrf"}
        )

        # Checking if nrf data is stored
        # self.assertEqual(self.harness.charm.state.nrf_host, "nrf")

        # Verifying status
        # self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # pod_spec, kubernetesResources = self.harness.get_pod_spec()
        # self.assertDictEqual(expected_result, pod_spec)

    def test_on_nrf_unit_relation_changed(self) -> NoReturn:
        """Test to see if kafka relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.nrf_host)

        relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(relation_id, "nrf/0")
        self.harness.update_relation_data(
            relation_id, "nrf/0", {"host": "nrf"}
        )

        # self.assertEqual(self.harness.charm.state.nrf_host, "nrf")

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_nrf_app_relation_changed(self) -> NoReturn:
        """Test to see if kafka relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.nrf_host)

        relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(relation_id, "nrf/0")
        self.harness.update_relation_data(
            relation_id, "nrf/0", {"host": "nrf"}
        )

        # self.assertEqual(self.harness.charm.state.nrf_host, "nrf")

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )


if __name__ == "__main__":
    unittest.main()
