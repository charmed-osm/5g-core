#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##
"""NatApp test script for charm.py"""

import unittest
import json
from typing import NoReturn

from ops.testing import Harness
from ops.model import BlockedStatus

from charm import NatappCharm

# from ops.model import BlockedStatus


class TestCharm(unittest.TestCase):
    """Test script for checking relations"""

    def setUp(self) -> NoReturn:
        """Test setup."""
        self.harness = Harness(NatappCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_configure_change(self) -> NoReturn:
        """Test installation with any relation."""
        self.harness.charm.on.config_changed.emit()
        config_data = "192.168.1.216"
        second_interface = [
            {"name": "n6-network", "interface": "eth1", "ips": [config_data]}
        ]

        annot = {
            "annotations": {"k8s.v1.cni.cncf.io/networks": json.dumps(second_interface)}
        }
        custom_resource_def = [
            {
                "name": "network-attachment-definitions.k8s.cni.cncf.io",
                "spec": {
                    "group": "k8s.cni.cncf.io",
                    "scope": "Namespaced",
                    "names": {
                        "kind": "NetworkAttachmentDefinition",
                        "singular": "network-attachment-definition",
                        "plural": "network-attachment-definitions",
                    },
                    "versions": [{"name": "v1", "served": True, "storage": True}],
                },
            }
        ]
        pdn_subnet = "192.168.0.0/16"
        pdn_ip_range_start = "192.168.1.100"
        pdn_ip_range_end = "192.168.1.250"
        pdn_gateway_ip = "192.168.1.1"
        ipam_body = {
            "type": "host-local",
            "subnet": pdn_subnet,
            "rangeStart": pdn_ip_range_start,
            "rangeEnd": pdn_ip_range_end,
            "gateway": pdn_gateway_ip,
        }
        config_body = {
            "cniVersion": "0.3.1",
            "name": "n6-network",
            "type": "macvlan",
            "master": "ens3",
            "mode": "bridge",
            "ipam": ipam_body,
        }

        custom_resource = {
            "network-attachment-definitions.k8s.cni.cncf.io": [
                {
                    "apiVersion": "k8s.cni.cncf.io/v1",
                    "kind": "NetworkAttachmentDefinition",
                    "metadata": {"name": "n6-network"},
                    "spec": {"config": json.dumps(config_body)},
                }
            ]
        }

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
            "kubernetesResources": {
                "customResourceDefinitions": custom_resource_def,
                "customResources": custom_resource,
                "pod": annot,
            },
        }

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_publish_natapp_info(self) -> NoReturn:
        """Test to see if upf relation is updated."""
        expected_result = {
            "hostname": "natapp",
            "static_ip": "192.168.70.15",
        }
        relation_id = self.harness.add_relation("natapp", "upf1")
        self.harness.add_relation_unit(relation_id, "upf1/0")
        relation_data = {"hostname": "natapp", "static_ip": "192.168.70.15"}
        self.harness.update_relation_data(relation_id, "natapp", relation_data)
        relation_data = self.harness.get_relation_data(relation_id, "natapp")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main()
