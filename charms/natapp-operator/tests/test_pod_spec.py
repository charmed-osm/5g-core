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
import json

import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 9999

        expected_result = [
            {
                "name": "natapp",
                "containerPort": port,
                "protocol": "UDP",
            }
        ]
        portdict = {
            "natapp_port": 9999,
        }
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

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
        config = {
            "pdn_subnet": "192.168.0.0/16",
            "pdn_ip_range_start": "192.168.1.100",
            "pdn_ip_range_end": "192.168.1.250",
            "pdn_gateway_ip": "192.168.1.1",
            "master_interface": "ens3",
        }
        pdn_subnet = "192.168.0.0/16"
        pdn_ip_range_start = "192.168.1.100"
        pdn_ip_range_end = "192.168.1.250"
        pdn_gateway_ip = "192.168.1.1"
        pod_custom_resources = pod_spec._make_pod_custom_resources(config)
        ipam_body = {
            "type": "host-local",
            "subnet": pdn_subnet,
            "rangeStart": pdn_ip_range_start,
            "rangeEnd": pdn_ip_range_end,
            "gateway": pdn_gateway_ip,
        }
        master_interface = "ens3"
        config_body = {
            "cniVersion": "0.3.1",
            "name": "n6-network",
            "type": "macvlan",
            "master": master_interface,
            "mode": "bridge",
            "ipam": ipam_body,
        }

        expected_result = {
            "network-attachment-definitions.k8s.cni.cncf.io": [
                {
                    "apiVersion": "k8s.cni.cncf.io/v1",
                    "kind": "NetworkAttachmentDefinition",
                    "metadata": {"name": "n6-network"},
                    "spec": {"config": json.dumps(config_body)},
                }
            ]
        }
        self.assertDictEqual(expected_result, pod_custom_resources)

    def test_make_pod_podannotations(self) -> NoReturn:
        """Testing make pod envconfig configuration."""
        config = {"static_ip": "192.168.1.216"}
        config_data = "192.168.1.216"
        second_interface = [
            {"name": "n6-network", "interface": "eth1", "ips": [config_data]}
        ]

        expected_result = {
            "annotations": {"k8s.v1.cni.cncf.io/networks": json.dumps(second_interface)}
        }

        pod_annotation = pod_spec._make_pod_podannotations(config)
        self.assertDictEqual(expected_result, pod_annotation)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./start.sh", "&"]
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_(self) -> NoReturn:
        """Testing make pod envconfig configuration."""

        expected_result = {"securityContext": {"privileged": True}}
        pod_privilege = pod_spec._make_pod_privilege()
        self.assertDictEqual(expected_result, pod_privilege)

    def test_validate_config(self) -> NoReturn:
        """Testing config data scenario."""
        config = {
            "natapp_port": -2,
            "master_interface": 234,
        }
        with self.assertRaises(ValueError):
            pod_spec._validate_config(config)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec."""
        image_info = {"upstream-source": "localhost:32000/free5gc-natapp:1.0"}
        config = {
            "natapp_port": -2,
            "master_interface": 234,
        }
        app_name = "natapp"
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)
