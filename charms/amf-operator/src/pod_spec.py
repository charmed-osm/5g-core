#!/usr/bin/env python3
# Copyright 2020 David Garcia
# See LICENSE file for licensing details.

import logging
from pydantic import BaseModel, constr, PositiveInt
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """Configuration data model."""

    port: PositiveInt
    lb_port: PositiveInt
    gin_mode: constr(regex=r"^(release|anotheroption)$")
    # TODO: Replace another option with the other values possible


# class RelationData(BaseModel):
#     """Relation data model."""


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Args:
        port (int): port to expose.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "amf", "containerPort": config["port"], "protocol": "TCP"}]


def _make_pod_envconfig(
    config: Dict[str, Any],
    # relation_state: Dict[str, Any],
) -> Dict[str, Any]:
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
        "GIN_MODE": config["GIN_MODE"],
    }

    return envconfig


def _make_pod_command() -> List[str]:
    return (["./amf", "-amfcfg", "../config/amfcfg.conf", "&"],)


def _make_pod_services(config: Dict[str, Any], app_name: str):
    return [
        {
            "name": "amf-lb",
            "labels": {"juju-app": app_name},
            "spec": {
                "selector": {"juju-app": app_name},
                "ports": [
                    {
                        "protocol": "SCTP",
                        "port": config["lb_port"],
                        "targetPort": config["lb_port"],
                    }
                ],
                "type": "LoadBalancer",
            },
        }
    ]


def _make_startup_probe() -> Dict[str, Any]:
    """Generate startup probe.

    Returns:
        Dict[str, Any]: startup probe.
    """
    return {
        "exec": {"command": ["/usr/bin/pgrep", "python3"]},
        "initialDelaySeconds": 60,
        "timeoutSeconds": 5,
    }


def _make_readiness_probe() -> Dict[str, Any]:
    """Generate readiness probe.

    Returns:
        Dict[str, Any]: readiness probe.
    """
    return {
        "exec": {
            "command": ["sh", "-c", "osm-pol-healthcheck || exit 1"],
        },
        "periodSeconds": 10,
        "timeoutSeconds": 5,
        "successThreshold": 1,
        "failureThreshold": 3,
    }


def _make_liveness_probe() -> Dict[str, Any]:
    """Generate liveness probe.

    Returns:
        Dict[str, Any]: liveness probe.
    """
    return {
        "exec": {
            "command": ["sh", "-c", "osm-pol-healthcheck || exit 1"],
        },
        "initialDelaySeconds": 45,
        "periodSeconds": 10,
        "timeoutSeconds": 5,
        "successThreshold": 1,
        "failureThreshold": 3,
    }


def _make_busybox_container():
    return (
        {
            "name": "amf-init",
            "image": "busybox:1.28",
            "init": True,
            "command": [
                "sh",
                "-c",
                "until nc -zvw1 nrf-endpoints 29510; do echo waiting; sleep 2; done",
            ],
        },
    )


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, Any],
    # relation_state: Dict[str, Any],
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
    # RelationData(**(relation_state))

    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig(
        config,
        # relation_state,
    )
    command = _make_pod_command()
    services = _make_pod_services(config, app_name)

    busybox_container = _make_busybox_container()
    return {
        "version": 3,
        "containers": [
            busybox_container,
            {
                "name": app_name,
                "imageDetails": image_info,
                "imagePullPolicy": "Always",
                "ports": ports,
                "envConfig": env_config,
                "command": command,
            },
        ],
        "kubernetesResources": {
            "services": services,
        },
    }
