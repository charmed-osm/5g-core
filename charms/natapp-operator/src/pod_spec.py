#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi
# See LICENSE file for licensing details.

import logging
from pydantic import BaseModel, PositiveInt
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """Configuration data model."""

    port: PositiveInt


def _make_pod_ports(config: ConfigData) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "natapp", "containerPort": config["port"], "protocol": "UDP"}]


def _make_pod_command() -> List[str]:
    return ["./nat", "eth1", "eth0", "169.254.1.1"]


def _make_pod_podannotations() -> Dict[str, Any]:
    """Generate Pod Annotations.
    Returns:
        Dict[str, Any]: pod Annotations.
    """
    networks = '[\n{\n"name" : "n6-network",\n"interface": "eth1",\n"ips": ["192.168.1.216"]\n}]'
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

    ConfigData(**(config))

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
