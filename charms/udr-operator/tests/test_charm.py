# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.
""" UDR test script for charm.py """

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import UdrCharm


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """
    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(UdrCharm)
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
                    "name": "udr",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "udr",
                            "containerPort": 29504,
                            "protocol": "TCP",
                        }
                    ],
                    "envConfig": {
                        "ALLOW_ANONYMOUS_LOGIN": "yes",
                        "GIN_MODE": "release",
                        "MONGODB_URI": "mongodb://mongodb/free5gc",
                    },
                    "command": ["./udr", "-udrcfg", "../config/udrcfg.conf", "&"],
                }
            ],
        }

        self.harness.charm.on.start.emit()
        # Check if nrf,mongodb is initialized
        self.assertIsNone(self.harness.charm.state.nrf_host)
        self.assertIsNone(self.harness.charm.state.mongodb_host)
        self.assertIsNone(self.harness.charm.state.mongodb_uri)

        # Initializing the nrf relation
        nrf_relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(nrf_relation_id, "nrf/0")
        self.harness.update_relation_data(nrf_relation_id, "nrf", {"hostname": "nrf"})

        # Initializing the mongodb relation
        mongodb_relation_id = self.harness.add_relation("mongodb", "mongodb")
        self.harness.add_relation_unit(mongodb_relation_id, "mongodb/0")
        self.harness.update_relation_data(
            # pylint:disable=line-too-long
            mongodb_relation_id, "mongodb", {"hostname": "mongodb", "mongodb_uri": "mongodb://mongodb/free5gc"} # noqa
        )

        # Checking if nrf,mongodb data is stored
        self.assertEqual(self.harness.charm.state.nrf_host, "nrf")
        self.assertEqual(self.harness.charm.state.mongodb_host, "mongodb")
        self.assertEqual(self.harness.charm.state.mongodb_uri, "mongodb://mongodb/free5gc")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_mongodb_relation_changed(self) -> NoReturn:
        """Test to see if kafka relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.mongodb_host)

        relation_id = self.harness.add_relation("mongodb", "mongodb")
        self.harness.add_relation_unit(relation_id, "mongodb/0")
        self.harness.update_relation_data(relation_id, "mongodb", {"hostname": "mongodb"})

        self.assertNotEqual(self.harness.charm.state.mongodb_host, "mongodb")

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
        self.harness.update_relation_data(relation_id, "nrf", {"hostname": "nrf"})

        self.assertEqual(self.harness.charm.state.nrf_host, "nrf")

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )
