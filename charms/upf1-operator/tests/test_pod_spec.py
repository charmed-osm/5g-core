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
"""test script for pod spec.py"""

from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 2152
        expected_result = [
            {
                "name": "upf1",
                "containerPort": port,
                "protocol": "UDP",
            }
        ]
        dictport = {"gtp_port": 2152}
        pod_ports = pod_spec._make_pod_ports(dictport)
        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./upf_start.sh", "&"]
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_services(self) -> NoReturn:
        """Teting make pod services."""
        appname = "upf1"
        expected_result = [
            {
                "name": "upf-e",
                "labels": {"juju-app": appname},
                "spec": {
                    "selector": {"juju-app": appname},
                    "ports": [
                        {
                            "protocol": "TCP",
                            "port": 80,
                            "targetPort": 80,
                        }
                    ],
                    "type": "ClusterIP",
                },
            }
        ]
        pod_services = pod_spec._make_pod_services(appname)
        self.assertEqual(expected_result, pod_services)

    def test_make_pod_custom_resource_definitions(self) -> NoReturn:
        """Teting make pod custom resource definitions."""
        expected_result = [
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
        pod_custom_resource_definitions = (
            pod_spec._make_pod_custom_resource_definitions()
        )
        self.assertEqual(expected_result, pod_custom_resource_definitions)

    def test_make_pod_custom_resources(self) -> NoReturn:
        """Testing make pod customResources."""
        expected_result = {
            "network-attachment-definitions.k8s.cni.cncf.io": [
                {
                    "apiVersion": "k8s.cni.cncf.io/v1",
                    "kind": "NetworkAttachmentDefinition",
                    "metadata": {"name": "n6-network"},
                    "spec": {
                        "config": '{"cniVersion": "0.3.1",'
                        '\n"name": "n6-network",'
                        '\n"type": "macvlan",'
                        '\n"master": "ens3",'
                        '\n"mode": "bridge",'
                        '\n"ipam": {"type": "host-local",'
                        '\n"subnet": "192.168.0.0/16",'
                        '\n"rangeStart": "192.168.1.100",'
                        '\n"rangeEnd": "192.168.1.250",'
                        '\n"gateway": "192.168.1.1"\n}\n}'
                    },
                }
            ]
        }
        pod_custom_resources = pod_spec._make_pod_custom_resources()
        self.assertEqual(expected_result, pod_custom_resources)

    def test_make_pod_podannotations(self) -> NoReturn:
        """Testing make pod annotations."""
        expected_result = {
            "annotations": {
                "k8s.v1.cni.cncf.io/networks": '[\n{\n"name" : "n6-network",'
                '\n"interface": "eth1",\n"ips": ["192.168.1.215"]\n}\n]'
            },
            "securityContext": {"runAsUser": 0000, "runAsGroup": 0000},
        }
        pod_podannotations = pod_spec._make_pod_podannotations()
        self.assertDictEqual(expected_result, pod_podannotations)

    def test_make_pod_privilege(self) -> NoReturn:
        """Teting make pod privilege."""
        expected_result = {
            "securityContext": {"privileged": True},
        }
        pod_privilege = pod_spec._make_pod_privilege()
        self.assertDictEqual(expected_result, pod_privilege)

    def test_validate_config(self) -> NoReturn:
        """Testing validate config."""
        config = {"gtp_port": 1234}
        with self.assertRaises(ValueError):
            pod_spec._validate_config(config)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec."""
        image_info = {"upstream-source": "localhost:32000/free5gc-upf1:1.0"}
        config = {
            "gtp_port": 9999,
        }
        app_name = "upf1"

        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
