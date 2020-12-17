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
""" UPF test script for charm.py """

import unittest

# from unittest.mock import Mock
from typing import NoReturn

from ops.model import BlockedStatus
from ops.testing import Harness
from charm import Upf1Charm


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(Upf1Charm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_config_change(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "upf1",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {"name": "upf1", "containerPort": 2152, "protocol": "UDP"}
                    ],
                    "command": ["./free5gc-upfd", "-f", "../config/upfcfg.yaml", "&"],
                    "kubernetes": {"securityContext": {"privileged": True}},
                }
            ],
            "kubernetesResources": {
                "services": [
                    {
                        "name": "upf-e",
                        "labels": {"juju-app": "upf1"},
                        "spec": {
                            "selector": {"juju-app": "upf1"},
                            "ports": [
                                {"protocol": "TCP", "port": 80, "targetPort": 80}
                            ],
                            "type": "ClusterIP",
                        },
                    }
                ],
                "customResourceDefinitions": [
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
                            "versions": [
                                {"name": "v1", "served": True, "storage": True}
                            ],
                        },
                    }
                ],
                "customResources": {
                    "network-attachment-definitions.k8s.cni.cncf.io": [
                        {
                            "apiVersion": "k8s.cni.cncf.io/v1",
                            "kind": "NetworkAttachmentDefinition",
                            "metadata": {"name": "n6-network"},
                            "spec": {
                                # pylint:disable=line-too-long
                                "config": '{\n"cniVersion": "0.3.1",\n"name": "n6-network",\n"type": "macvlan",\n"master": "ens3",\n"mode": "bridge",\n"ipam": {\n"type": "host-local",\n"subnet": "192.168.0.0/16",\n"rangeStart": "192.168.1.100",\n"rangeEnd": "192.168.1.250",\n"gateway": "192.168.1.1"\n}\n}'  # noqa
                            },
                        }
                    ]
                },
                "pod": {
                    "annotations": {
                        # pylint:disable=line-too-long
                        "k8s.v1.cni.cncf.io/networks": '[\n{\n"name" : "n6-network",\n"interface": "eth1",\n"ips": ["192.168.1.215"]\n}]'  # noqa
                    },
                    "securityContext": {"runAsUser": 0, "runAsGroup": 0},
                },
            },
        }
        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

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
