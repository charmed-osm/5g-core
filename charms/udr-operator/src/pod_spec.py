#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.

import logging
from pydantic import BaseModel, constr, validator
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """Configuration data model."""

    port: int = 29504

    @validator("port")
    def validate_port(cls, value: int) -> Any:
        if value == 29504:  # <- Here is condition checking your format.
            return value
        raise ValueError("Invalid port number")

    db_uri: constr(regex=r"^(mongodb://db/free5gc)$")  # noqa
    gin_mode: constr(regex=r"^(release|debug)$")  # noqa


def _make_pod_ports(config: ConfigData) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        port (int): port to expose.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "udr", "containerPort": config["port"], "protocol": "TCP"}]


def _make_pod_envconfig(config: ConfigData) -> Dict[str, Any]:
    """Generate pod environment configuration.
    Args:
        config (Dict[str, Any]): configuration information.
        relation_state (Dict[str, Any]): relation state information.
    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    envconfig = {
        # General configuration
        "ALLOW_ANONYMOUS_LOGIN": "yes",
        "GIN_MODE": config["gin_mode"],
        "DB_URI": config["db_uri"],
    }

    return envconfig


def _make_pod_command() -> List[str]:
    return ["./udr", "-udrcfg", "../config/udrcfg.conf", "&"]


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
    env_config = _make_pod_envconfig(config)
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
