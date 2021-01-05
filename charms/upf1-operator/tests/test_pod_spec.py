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

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig configuration."""
        expected_result = {
            "UE_RANGE": "60.60.0.0/24",
            "STATIC_IP": "192.168.70.15",
        }
        ue_range = {"ue_range": "60.60.0.0/24"}
        ipadd = {"natapp_ip": "192.168.70.15"}
        pod_envconfig = pod_spec._make_pod_envconfig(ue_range, ipadd)
        self.assertDictEqual(expected_result, pod_envconfig)

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

    def test_make_pod_podannotations(self) -> NoReturn:
        """Testing make pod annotations."""
        expected_result = {
            "annotations": {
                "k8s.v1.cni.cncf.io/networks": '[\n{\n"name" : "n6-network",'
                '\n"interface": "eth1",\n"ips": []\n}\n]'
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

    def test_validate_relation(self) -> NoReturn:
        """Testing relation data scenario."""
        relation_state = {"natapp_ip": "xvz"}
        with self.assertRaises(ValueError):
            pod_spec._validate_relation_state(relation_state)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec."""
        image_info = {"upstream-source": "localhost:32000/free5gc-upf1:1.0"}
        config = {
            "gtp_port": 9999,
        }
        app_name = "upf1"
        relation_state = {"natapp_ip": "192.168.70.15"}

        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name, relation_state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
