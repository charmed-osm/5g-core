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
"""Pod spec for NRF charm"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
NRF_PORT = 29510


def _make_pod_ports() -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "nrf", "containerPort": NRF_PORT, "protocol": "TCP"}]


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
        "ALLOW_ANONYMOUS_LOGIN": "yes",
        "GIN_MODE": config["gin_mode"],
        "MONGODB_URI": relation_state["mongodb_uri"],
        "MONGODB_HOST": relation_state["mongodb_host"],
    }


def _make_pod_command() -> List[str]:
    """Generate pod command.

    Returns:
        List[str]:pod command.
    """
    return ["./nrf_start.sh", "&"]


def _validate_config(config: Dict[str, Any]):
    """Validate config data.

    Args:
        config (Dict[str, Any]): configuration information.
    """
    valid_gin_modes = ["release", "debug"]
    if config.get("gin_mode") not in valid_gin_modes:
        raise ValueError("Invalid gin_mode")


def _validate_relation_state(relation_state: Dict[str, Any]):
    """Validate relation data.

    Args:
        relation (Dict[str, Any]): relation information.
    """
    uri = relation_state.get("mongodb_uri")
    mongodb_host = relation_state.get("mongodb_host")
    uri_state = not uri or not isinstance(uri, str)
    host_state = not uri.startswith("mongodb://") or not mongodb_host
    if uri_state or host_state:
        raise ValueError("Value error in mongodb relations")


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

    Returns:
        Dict[str, Any]: Pod spec dictionary for the charm.
    """
    if not image_info:
        return None

    _validate_config(config)
    _validate_relation_state(relation_state)
    env_config = _make_pod_envconfig(config, relation_state)
    if not env_config:
        raise ValueError("Env config Value Error")
    ports = _make_pod_ports()
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
