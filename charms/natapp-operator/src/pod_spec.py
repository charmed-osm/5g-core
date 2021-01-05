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
"""Pod spec for NatApp charm"""

import logging
import json
from typing import Any, Dict, List
from IPy import IP

logger = logging.getLogger(__name__)


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Args:
        config(Dict[str, Any]):pod ports details.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [
        {
            "name": "natapp",
            "containerPort": config["natapp_port"],
            "protocol": "UDP",
        }
    ]


def _make_pod_command() -> List[str]:
    """Generate pod command.

    Returns:
        List[str]:pod command.
    """
    return ["./start.sh", "&"]


def _make_pod_custom_resource_definitions():
    """Generate pod custom resource definitions."""
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


def _make_pod_custom_resources(config: Dict[str, Any]):
    """Generate pod customresources."""
    ipam_body = {
        "type": "host-local",
        "subnet": config["pdn_subnet"],
        "rangeStart": config["pdn_ip_range_start"],
        "rangeEnd": config["pdn_ip_range_end"],
        "gateway": config["pdn_gateway_ip"],
    }
    config_body = {
        "cniVersion": "0.3.1",
        "name": "n6-network",
        "type": "macvlan",
        "master": "ens3",
        "mode": "bridge",
        "ipam": ipam_body,
    }

    custom_resources = {
        "network-attachment-definitions.k8s.cni.cncf.io": [
            {
                "apiVersion": "k8s.cni.cncf.io/v1",
                "kind": "NetworkAttachmentDefinition",
                "metadata": {"name": "n6-network"},
                "spec": {"config": json.dumps(config_body)},
            }
        ]
    }
    return custom_resources


def _make_pod_podannotations(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Pod Annotations.

    Returns:
        Dict[str, Any]: pod Annotations.
    """
    second_interface = [
        {"name": "n6-network", "interface": "eth1", "ips": [config["static_ip"]]}
    ]
    annot = {
        "annotations": {"k8s.v1.cni.cncf.io/networks": json.dumps(second_interface)}
    }

    return annot


def _make_pod_privilege() -> Dict[str, Any]:
    """Generate pod privileges.

    Returns:
        Dict[str, Any]: pod privilege.
    """
    privil = {"securityContext": {"privileged": True}}
    return privil


def _validate_config(config: Dict[str, Any]):
    """Validate config data.

    Args:
        config (Dict[str, Any]): configuration information.
    """
    if not config.get("natapp_port") > 0:
        raise ValueError("Invalid natapp port number")
    pdn_subnet = config.get("pdn_subnet")
    pdn_ip_range_start = config.get("pdn_ip_range_start")
    pdn_ip_range_end = config.get("pdn_ip_range_end")
    pdn_gateway_ip = config.get("pdn_gateway_ip")
    static_ip = config.get("static_ip")
    for pdn_conf in (
        pdn_subnet,
        pdn_ip_range_start,
        pdn_ip_range_end,
        pdn_gateway_ip,
        static_ip,
    ):
        if not IP(pdn_conf):
            raise ValueError("Value error in pdn ip configuration")


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, Any],
    app_name: str,
) -> Dict[str, Any]:
    """Generate the pod spec information.

    Args:
        image_info (Dict[str, str]): Object provided by
                                     OCIImageResource("image").fetch().
        config (Dict[str, Any]): Configuration information.
        app_name (str, optional): Application name. Defaults to "pol".

    Returns:
        Dict[str, Any]: Pod spec dictionary for the charm.
    """
    if not image_info:
        return None

    _validate_config(config)
    ports = _make_pod_ports(config)
    command = _make_pod_command()
    kubernetes = _make_pod_privilege()
    custom_resource_definitions = _make_pod_custom_resource_definitions()
    custom_resources = _make_pod_custom_resources(config)
    podannotations = _make_pod_podannotations(config)
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
            "customResourceDefinitions": custom_resource_definitions,
            "customResources": custom_resources,
            "pod": podannotations,
        },
    }
