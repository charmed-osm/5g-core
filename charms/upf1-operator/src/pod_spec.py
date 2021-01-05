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
"""Pod spec for UPF charm"""

import logging
from typing import Any, Dict, List
from IPy import IP

logger = logging.getLogger(__name__)

TCP_PORT = 80
UPF_PORT = 2152
UE_RANGE = "60.60.0.0/24"


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Args:
        config(Dict[str, Any]): pod ports.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "upf1", "containerPort": config["gtp_port"], "protocol": "UDP"}]


def _make_pod_command() -> List[str]:
    """Generate pod command.

    Returns:
        List[str]:pod command.
    """
    return ["./upf_start.sh", "&"]


def _make_pod_envconfig(
    config: Dict[str, Any], relation_state: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate pod environment configuration.

    Args:
        config (Dict[str, Any]): configuration information.
        relation_state (Dict[str, Any]): relation state information.

    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    return {
        # General configuration
        "UE_RANGE": config["ue_range"],
        "STATIC_IP": relation_state["natapp_ip"],
    }


def _make_pod_services(app_name: str):
    """Generate pod service details.

    Returns:
        app_name(str):pod service details.
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


def _make_pod_podannotations() -> Dict[str, Any]:
    """Generate Pod Annotations.

    Returns:
        Dict[str, Any]: pod Annotations.
    """
    annot = {
        "annotations": {
            "k8s.v1.cni.cncf.io/networks": '[\n{\n"name" : "n6-network",'
            '\n"interface": "eth1",\n"ips": []\n}\n]'
        },
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


def _validate_config(config: Dict[str, Any]):
    """Validate config data.

    Args:
        config (Dict[str, Any]): configuration information.
    """
    if config.get("gtp_port") != UPF_PORT:
        raise ValueError("Invalid upf gtp port")
    if config.get("ue_range") != UE_RANGE:
        raise ValueError("Invalid upf ue range")


def _validate_relation_state(relation_state: Dict[str, Any]):
    """Validate relation data.

    Args:
        relation (Dict[str, Any]): relation state information.
    """
    natapp_ip = relation_state.get("natapp_ip")
    if not IP(natapp_ip):
        raise ValueError("Value error in natapp ip")


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, str],
    app_name: str,
    relation_state: Dict[str, Any],
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
    _validate_relation_state(relation_state)
    ports = _make_pod_ports(config)
    command = _make_pod_command()
    env_config = _make_pod_envconfig(config, relation_state)
    services = _make_pod_services(app_name)
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
                "envConfig": env_config,
                "command": command,
                "kubernetes": kubernetes,
            }
        ],
        "kubernetesResources": {
            "services": services,
            "pod": podannotations,
        },
    }
