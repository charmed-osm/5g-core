# Copyright 2020 Ubuntu
# See LICENSE file for licensing details.
""" test script for pod spec.py """

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
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports(dictport)
        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command"""

        expected_result = ["./free5gc-upfd", "-f", "../config/upfcfg.yaml", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_services(self) -> NoReturn:
        """Teting make pod envconfig configuration."""
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
        # pylint:disable=W0212
        pod_services = pod_spec._make_pod_services(appname)
        self.assertEqual(expected_result, pod_services)

    def test_make_pod_custom_resource_definitions(self) -> NoReturn:
        """Teting make pod privilege"""
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
        # pylint:disable=W0212
        pod_custom_resource_definitions = (
            pod_spec._make_pod_custom_resource_definitions()
        )
        self.assertEqual(expected_result, pod_custom_resource_definitions)

    def test_make_pod_custom_resources(self) -> NoReturn:
        """Testing make pod customResources"""
        expected_result = {
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
        }
        # pylint:disable=W0212
        pod_custom_resources = pod_spec._make_pod_custom_resources()
        self.assertEqual(expected_result, pod_custom_resources)

    def test_make_pod_podannotations(self) -> NoReturn:
        """Testing make pod privilege"""
        # pylint:disable=line-too-long
        networks = '[\n{\n"name" : "n6-network",\n"interface": "eth1",\n"ips": ["192.168.1.215"]\n}]'  # noqa
        expected_result = {
            "annotations": {"k8s.v1.cni.cncf.io/networks": networks},
            "securityContext": {"runAsUser": 0000, "runAsGroup": 0000},
        }
        # pylint:disable=W0212
        pod_podannotations = pod_spec._make_pod_podannotations()
        self.assertDictEqual(expected_result, pod_podannotations)

    def test_make_pod_privilege(self) -> NoReturn:
        """Teting make pod privilege"""
        expected_result = {
            "securityContext": {"privileged": True},
        }
        # pylint:disable=W0212
        pod_privilege = pod_spec._make_pod_privilege()
        self.assertDictEqual(expected_result, pod_privilege)

    def test_make_pod_spec(self) -> NoReturn:
        """Testing make pod spec"""
        image_info = {"upstream-source": "localhost:32000/free5gc-upf-1:1.0"}
        config = {
            "gtp_port": 9999,
        }
        app_name = "upf1"

        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
