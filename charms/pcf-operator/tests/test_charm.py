# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.

import unittest

from ops.testing import Harness
from ops.model import BlockedStatus

from charm import PcfCharm
from typing import NoReturn


class TestCharm(unittest.TestCase):

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(PcfCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_config_changed(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()
        busybox_container = {
            "name": "pcf-init",
            "image": "busybox:1.28",
            "init": True,
            "command": [
                "sh",
                "-c",
                "until(nc -zvw1 nrf-endpoints 29510 && nc -zvw1 amf-endpoints 29518); do echo waiting; sleep 2; done", # noqa
            ],
        }
        expected_result = {
            "version": 3,
            "containers": [
                busybox_container,
                {
                    "name": "pcf",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [{
                        "name": "pcf",
                        "containerPort": 29507,
                        "protocol": "TCP",
                    }],
                    "envConfig": {
                        "ALLOW_ANONYMOUS_LOGIN": "yes",
                        "GIN_MODE": "release",
                    },
                    "command": ["./pcf", "-pcfcfg", "../config/pcfcfg.conf", "&"],
                }
            ],
        }

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(self.harness.charm.unit.status.message.endswith(" relations"))

        pod_spec, kubernetesResources = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)


if __name__ == '__main__':
    unittest.main()
