# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.

import unittest
# from unittest.mock import Mock
from typing import NoReturn
# from ops.model import BlockedStatus
from ops.testing import Harness
from charm import Upf1Charm


class TestCharm(unittest.TestCase):

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(Upf1Charm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_start_without_relations(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()

        # Verifying status
        # self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)

    def test_publish_upf_info(self) -> NoReturn:
        """Test to see if upf relation is updated."""
        self.harness.charm.on.start.emit()
        expected_result = {
            "private_address": "upf",
        }
        relation_id = self.harness.add_relation("upf", "natapp")
        self.harness.add_relation_unit(relation_id, "natapp/0")
        relation_data = self.harness.get_relation_data(relation_id, "upf1")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main()
