#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.
""" Pod spec for AMF charm """
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

AMF_PORT = 29518
SCTP_PORT = 38412


def _make_pod_ports() -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "amf", "containerPort": AMF_PORT, "protocol": "TCP"}]


def _make_pod_envconfig(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate pod environment configuration.
    Args:
        config (Dict[str, Any]): configuration information.
        relation_state (Dict[str, Any]): relation state information.
    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    if config["gin_mode"] == "release" or config["gin_mode"] == "debug":
        envconfig = {
            # General configuration
            "ALLOW_ANONYMOUS_LOGIN": "yes",
            "GIN_MODE": config["gin_mode"],
        }
    else:
        raise ValueError("Invalid gin_mode")

    return envconfig


def _make_pod_command() -> List[str]:
    return ["./amf", "-amfcfg", "../config/amfcfg.conf", "&"]


def _make_pod_services(app_name: str):
    return [
        {
            "name": "amf-lb",
            "labels": {"juju-app": app_name},
            "spec": {
                "selector": {"juju-app": app_name},
                "ports": [
                    {
                        "protocol": "SCTP",
                        "port": SCTP_PORT,
                        "targetPort": SCTP_PORT,
                    }
                ],
                "type": "LoadBalancer",
            },
        }
    ]


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

    ports = _make_pod_ports()
    env_config = _make_pod_envconfig(config)
    command = _make_pod_command()
    services = _make_pod_services(app_name)

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
            }
        ],
        "kubernetesResources": {
            "services": services,
        },
    }
