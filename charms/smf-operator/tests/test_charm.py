# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.
""" SMF test script for charm.py """

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import SmfCharm


class TestCharm(unittest.TestCase):
    """ Test script for checking pod spec and relations """

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(SmfCharm)
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
        """Test installation with relation."""
        self.harness.charm.on.start.emit()
        # Check if nrf,upf is initialized
        self.assertIsNone(self.harness.charm.state.nrf_host)
        self.assertIsNone(self.harness.charm.state.upf_host)

        # Initializing the nrf relation
        nrf_relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(nrf_relation_id, "nrf/0")
        self.harness.update_relation_data(
            nrf_relation_id, "nrf/0", {"hostname": "nrf", "port": 9092}
        )

        # Initializing the upf relation
        upf_relation_id = self.harness.add_relation("upf", "upf")
        self.harness.add_relation_unit(upf_relation_id, "upf/0")
        self.harness.update_relation_data(
            upf_relation_id, "upf/0", {"private_address": "upf", "port": 9090}
        )

        # Checking if nrf,upf data is stored
        # self.assertEqual(self.harness.charm.state.nrf_host, "nrf")
        # self.assertEqual(self.harness.charm.state.upf_host, "upf")

        # Verifying status
        # self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # pod_spec, _ = self.harness.get_pod_spec()
        # self.assertDictEqual(expected_result, pod_spec)

    def test_on_upf_unit_relation_changed(self) -> NoReturn:
        """Test to see if upf relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.upf_host)

        relation_id = self.harness.add_relation("upf", "upf")
        self.harness.add_relation_unit(relation_id, "upf/0")
        self.harness.update_relation_data(relation_id, "upf/0", {"host": "upf"})

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_upf_app_relation_changed(self) -> NoReturn:
        """Test to see if upf app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.upf_host)

        relation_id = self.harness.add_relation("upf", "upf")
        self.harness.add_relation_unit(relation_id, "upf/0")
        self.harness.update_relation_data(relation_id, "upf", {"host": "upf"})

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_nrf_unit_relation_changed(self) -> NoReturn:
        """Test to see if nfr relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.nrf_host)

        relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(relation_id, "nrf/0")
        self.harness.update_relation_data(relation_id, "nrf/0", {"host": "nrf"})

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_nrf_app_relation_changed(self) -> NoReturn:
        """Test to see if nfr relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.nrf_host)

        relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(relation_id, "nrf/0")
        self.harness.update_relation_data(relation_id, "nrf", {"host": "nrf"})

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )


if __name__ == "__main__":
    unittest.main()
