#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi
# See LICENSE file for licensing details.

import logging
from pydantic import BaseModel, validator
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """Configuration data model."""

    port: int = 2152

    @validator("port")
    def validate_gtp_port(cls, value: int) -> Any:
        if value == 2152:
            return value
        raise ValueError("Invalid port number")

    port_tcp: int = 80

    @validator("port_tcp")
    def validate_tcp_port(cls, value: int) -> Any:
        if value == 80:
            return value
        raise ValueError("Invalid port number")


def _make_pod_ports(config: ConfigData) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "upf1", "containerPort": config["port"], "protocol": "UDP"}]


def _make_pod_command() -> List[str]:
    return ["./free5gc-upfd", "-f", "../config/upfcfg.yaml", "&"]


def _make_pod_services(config: ConfigData, app_name: str):
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
                        "port": config["port_tcp"],
                        "targetPort": config["port_tcp"],
                    }
                ],
                "type": "ClusterIP",
            },
        }
    ]


def _make_pod_customResourceDefinitions():
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


def _make_pod_customResources():
    """Generate Network attachment definitions.
    Args:
        config (Dict[str, Any]): configuration information.
    Returns:
        Dict[str, Any]: pod network attachment definitions.
    """
    customResources = {
        "network-attachment-definitions.k8s.cni.cncf.io": [
            {
                "apiVersion": "k8s.cni.cncf.io/v1",
                "kind": "NetworkAttachmentDefinition",
                "metadata": {"name": "n6-network"},
                "spec": {
                    "config": '{\n"cniVersion": "0.3.1",\n"name": "n6-network",\n"type": "macvlan",\n"master": "ens3",\n"mode": "bridge",\n"ipam": {\n"type": "host-local",\n"subnet": "192.168.0.0/16",\n"rangeStart": "192.168.1.100",\n"rangeEnd": "192.168.1.250",\n"gateway": "192.168.1.1"\n}\n}'  # noqa
                },
            }
        ]
    }
    return customResources


def _make_pod_podannotations() -> Dict[str, Any]:
    """Generate Pod Annotations.
    Returns:
        Dict[str, Any]: pod Annotations.
    """
    networks = '[\n{\n"name" : "n6-network",\n"interface": "eth1",\n"ips": ["192.168.1.215"]\n}]'
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
    services = _make_pod_services(config, app_name)
    kubernetes = _make_pod_privilege()
    customResourceDefinitions = _make_pod_customResourceDefinitions()
    customResources = _make_pod_customResources()
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
            "customResourceDefinitions": customResourceDefinitions,
            "customResources": customResources,
            "pod": podannotations,
        },
    }
