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
""" Pod spec for UPF charm """

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

TCP_PORT = 80


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    if config["gtp_port"] == 2152:
        return [
            {"name": "upf1", "containerPort": config["gtp_port"], "protocol": "UDP"}
        ]
    raise ValueError("Invlaid gtp port number")


def _make_pod_command() -> List[str]:
    return ["./free5gc-upfd", "-f", "../config/upfcfg.yaml", "&"]


def _make_pod_services(app_name: str):
    """Generate pod service details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod service details.
    """
    return [
        {
            "name": "upf-e",
            "labels": {"juju-app": app_name},
            "spec": {
                "selector": {"juju-app": app_name},
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": TCP_PORT,
                        "targetPort": TCP_PORT,
                    }
                ],
                "type": "ClusterIP",
            },
        }
    ]


def _make_pod_custom_resource_definitions():
    return [
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


def _make_pod_custom_resources():
    """Generate Network attachment definitions.
    Args:
        config (Dict[str, Any]): configuration information.
    Returns:
        Dict[str, Any]: pod network attachment definitions.
    """
    custom_resources = {
        "network-attachment-definitions.k8s.cni.cncf.io": [
            {
                "apiVersion": "k8s.cni.cncf.io/v1",
                "kind": "NetworkAttachmentDefinition",
                "metadata": {"name": "n6-network"},
                "spec": {
                    "config": {
                        "cniVersion": "0.3.1",
                        "name": "n6-network",
                        "type": "macvlan",
                        "master": "ens3",
                        "mode": "bridge",
                        "ipam": {
                            "type": "host-local",
                            "subnet": "192.168.0.0/16",
                            "rangeStart": "192.168.1.100",
                            "rangeEnd": "192.168.1.250",
                            "gateway": "192.168.1.1",
                        },
                    }  # noqa
                },
            }
        ]
    }
    return custom_resources


def _make_pod_podannotations() -> Dict[str, Any]:
    """Generate Pod Annotations.
    Returns:
        Dict[str, Any]: pod Annotations.
    """
    networks = '[{"name" : "n6-network","interface": "eth1","ips": ["192.168.1.215"]}]'
    annot = {
        "annotations": {"k8s.v1.cni.cncf.io/networks": networks},
        "securityContext": {"runAsUser": 0000, "runAsGroup": 0000},
    }

    return annot


def _make_pod_privilege() -> Dict[str, Any]:
    """Generate pod privileges.
    Returns:
        Dict[str, Any]: pod privilege.
    """
    privil = {"securityContext": {"privileged": True}}
    return privil


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, str],
    app_name: str,
) -> Dict[str, Any]:
    """Generate the pod spec information.
    Args:
        image_info (Dict[str, str]): Object provided by
                                     OCIImageResource("image").fetch().
        config (Dict[str, Any]): Configuration information.
        relation_state (Dict[str, Any]): Relation state information.
        app_name (str, optional): Application name. Defaults to "pol".
        port (int, optional): Port for the container. Defaults to 80.
    Returns:
        Dict[str, Any]: Pod spec dictionary for the charm.
    """
    if not image_info:
        return None

    ports = _make_pod_ports(config)
    command = _make_pod_command()
    services = _make_pod_services(app_name)
    kubernetes = _make_pod_privilege()
    custom_resource_definitions = _make_pod_custom_resource_definitions()
    custom_resources = _make_pod_custom_resources()
    podannotations = _make_pod_podannotations()
    return {
        "version": 3,
        "containers": [
            {
                "name": app_name,
                "imageDetails": image_info,
                "imagePullPolicy": "Always",
                "ports": ports,
                "command": command,
                "kubernetes": kubernetes,
            }
        ],
        "kubernetesResources": {
            "services": services,
            "customResourceDefinitions": custom_resource_definitions,
            "customResources": custom_resources,
            "pod": podannotations,
        },
    }
