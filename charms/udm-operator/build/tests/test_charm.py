# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import UdmCharm


class TestCharm(unittest.TestCase):
    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(UdmCharm)
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
                    "name": "udm",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "udm",
                            "containerPort": 29503,
                            "protocol": "TCP",
                        }
                    ],
                    "envConfig": {
                        "ALLOW_ANONYMOUS_LOGIN": "yes",
                        "GIN_MODE": "release",
                    },
                    "command": ["./udm", "-udmcfg", "../config/udmcfg.conf", "&"],
                }
            ],
        }

        self.harness.charm.on.start.emit()
        # Check if nrf,db is initialized
        self.assertIsNone(self.harness.charm.state.nrf_host)

        # Initializing the nrf relation
        nrf_relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(nrf_relation_id, "nrf/0")
        self.harness.update_relation_data(nrf_relation_id, "nrf", {"hostname": "nrf"})

        # Checking if nrf,db data is stored
        self.assertEqual(self.harness.charm.state.nrf_host, "nrf")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, kubernetesResources = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_nrf_app_relation_changed(self) -> NoReturn:
        """Test to see if kafka relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.nrf_host)

        relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(relation_id, "nrf/0")
        self.harness.update_relation_data(relation_id, "nrf", {"hostname": "nrf"})

        self.assertEqual(self.harness.charm.state.nrf_host, "nrf")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )
