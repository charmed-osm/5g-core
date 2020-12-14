# Copyright 2020 Ubuntu
# See LICENSE file for licensing details.
""" NatApp test script for charm.py """

import unittest
from typing import NoReturn

from ops.testing import Harness
from ops.model import BlockedStatus

from charm import NatappCharm

# from ops.model import BlockedStatus


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """

    def setUp(self) -> NoReturn:
        """Test setup"""
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
        # pylint:disable=line-too-long
        networks = '[\n{\n"name" : "n6-network",\n"interface": "eth1",\n"ips": ["192.168.1.216"]\n}]'  # noqa
        annot = {"annotations": {"k8s.v1.cni.cncf.io/networks": networks}}
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
            upf_relation_id, "upf", {"private_address": "upf"}
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
            upf_relation_id, "upf", {"private_address": "upf"}
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
