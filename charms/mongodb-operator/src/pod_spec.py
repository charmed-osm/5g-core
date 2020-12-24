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
"""Pod spec for MongoDB charm"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
MONGO_PORT = 27017


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Args:
        config(Dict[str, Any]):pod ports details.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [
        {
            "name": "mongodb",
            "containerPort": config["mongo_port"],
            "protocol": "TCP",
        }
    ]


def _make_pod_command() -> List[str]:
    """Generate pod command.

    Returns:
        List[str]:pod command.
    """
    return ["mongod", "--bind_ip", "mongodb-endpoints", "--port", "27017"]


def _validate_config(config: Dict[str, Any]):
    """Validate config data.

    Args:
        config (Dict[str, Any]): configuration information.
    """
    if config.get("mongo_port") != MONGO_PORT:
        raise ValueError("Invalid mongodb port number")


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, str],
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

    return {
        "version": 3,
        "containers": [
            {
                "name": app_name,
                "imageDetails": image_info,
                "imagePullPolicy": "Always",
                "ports": ports,
                "command": command,
            }
        ],
    }
