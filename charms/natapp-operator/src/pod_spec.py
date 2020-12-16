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
""" Pod spec for NatApp charm """

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    if config["natapp_port"] > 0:
        return [
            {
                "name": "natapp",
                "containerPort": config["natapp_port"],
                "protocol": "UDP",
            }
        ]
    raise ValueError("Invalid port number")


def _make_pod_command() -> List[str]:
    return ["./start.sh", "&"]


def _make_pod_podannotations() -> Dict[str, Any]:
    """Generate Pod Annotations.
    Returns:
        Dict[str, Any]: pod Annotations.
    """
    networks = '[{"name" : "n6-network","interface": "eth1","ips": ["192.168.1.216"]}]'
    annot = {"annotations": {"k8s.v1.cni.cncf.io/networks": networks}}

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
    config: Dict[str, Any],
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
    kubernetes = _make_pod_privilege()
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
            "pod": podannotations,
        },
    }
