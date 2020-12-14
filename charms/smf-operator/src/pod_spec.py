#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi
# See LICENSE file for licensing details.
""" Pod spec for SMF charm """

import logging
from typing import Any, Dict, List
from IPy import IP

logger = logging.getLogger(__name__)


SMF_PORT = 29502


def _make_pod_ports() -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "smf", "containerPort": SMF_PORT, "protocol": "TCP"}]


def _check_data(config: Dict[str, Any], relation_state: Dict[str, Any]) -> bool:
    logging.info(relation_state)
    if config["gin_mode"] != "release" and config["gin_mode"] != "debug":
        raise ValueError("Invalid gin_mode")
    return True


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
    if _check_data(config, relation_state):
        if IP(relation_state["upf_host"]):
            envconfig = {
                # General configuration
                "ALLOW_ANONYMOUS_LOGIN": "yes",
                "GIN_MODE": config["gin_mode"],
                "IPADDR1": relation_state["upf_host"],
            }
    return envconfig


def _make_pod_command() -> List[str]:
    return ["./ipscript.sh", "&"]


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, Any],
    relation_state: Dict[str, Any],
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
    env_config = _make_pod_envconfig(config, relation_state)
    command = _make_pod_command()
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
    }
