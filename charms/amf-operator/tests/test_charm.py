# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.
""" AMF test script for charm.py """
import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import AmfCharm


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """

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
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "amf",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "amf",
                            "containerPort": 29518,
                            "protocol": "TCP",
                        }
                    ],
                    "envConfig": {
                        "ALLOW_ANONYMOUS_LOGIN": "yes",
                        "GIN_MODE": "release",
                    },
                    "command": ["./amf", "-amfcfg", "../config/amfcfg.conf", "&"],
                }
            ],
            "kubernetesResources": {
                "services": [
                    {
                        "name": "amf-lb",
                        "labels": {"juju-app": "amf"},
                        "spec": {
                            "selector": {"juju-app": "amf"},
                            "ports": [
                                {
                                    "protocol": "SCTP",
                                    "port": 38412,
                                    "targetPort": 38412,
                                }
                            ],
                            "type": "LoadBalancer",
                        },
                    }
                ],
            },
        }
        # Check if nrf is initialized
        self.assertIsNone(self.harness.charm.state.nrf_host)

        # Initializing the nrf relation
        nrf_relation_id = self.harness.add_relation("nrf", "nrf")
        self.harness.add_relation_unit(nrf_relation_id, "nrf/0")
        self.harness.update_relation_data(nrf_relation_id, "nrf", {"hostname": "nrf"})

        # Checking if nrf data is stored
        self.assertEqual(self.harness.charm.state.nrf_host, "nrf")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_nrf_app_relation_changed(self) -> NoReturn:
        """Test to see if nrf relation is updated."""
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

    def test_publish_amf_info(self) -> NoReturn:
        """Test to see if amf relation is updated."""
        expected_result = {
            "hostname": "amf",
        }

        relation_id = self.harness.add_relation("amf", "pcf")
        self.harness.add_relation_unit(relation_id, "pcf/0")
        self.harness.charm.on.publish_amf_info.emit()
        relation_data = self.harness.get_relation_data(relation_id, "amf")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main()
