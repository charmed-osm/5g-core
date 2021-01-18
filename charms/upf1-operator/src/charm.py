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
"""Defining upf charm events"""

import logging
from typing import NoReturn, Dict, Any
from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState, EventBase
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus

from oci_image import OCIImageResource, OCIImageResourceError

from pod_spec import make_pod_spec


logger = logging.getLogger(__name__)


class Upf1Charm(CharmBase):
    """UPF charm events class definition"""

    state = StoredState()

    def __init__(self, *args):
        """UPF charm constructor."""
        super().__init__(*args)
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.config_changed, self.configure_pod)
        # Registering required relation changed events
        self.framework.observe(
            self.on.natapp_relation_changed, self._on_natapp_relation_changed
        )
        self.framework.observe(
            self.on.upf_relation_joined, self.publish_upf_info
        )

        # Registering required relation departed events
        self.framework.observe(
            self.on.natapp_relation_departed, self._on_natapp_relation_departed
        )

        # -- initialize states --
        self.state.set_default(natapp_ip=None)
        self.state.set_default(natapp_host=None)

    def publish_upf_info(self, event: EventBase) -> NoReturn:
        """Publishes UPF IP information for SMF
          relation.7

        Args:
             event (EventBase): upf relation event to update SMF.
        """
        if not self.unit.is_leader():
            return
        try:
            private_ip = self.model.get_binding(event.relation).network.bind_address
            logger.info("UPF ip")
            logger.info(str(private_ip))
            if private_ip:
                logger.info(str(private_ip))
                event.relation.data[self.model.unit]["private_address"] = str(
                    private_ip
                )
            else:
                event.defer()
        except TypeError:
            event.defer()
            self.unit.status = BlockedStatus("Ip not yet fetched")
            return

    def _on_natapp_relation_changed(self, event: EventBase) -> NoReturn:
        """Reads information about the upf relation.

        Args:
           event (EventBase): upf relation event.
        """
        if event.app not in event.relation.data:
            return

        natapp_host = event.relation.data[event.app].get("hostname")
        natapp_ip = event.relation.data[event.app].get("static_ip")
        validate_natapp = natapp_host and natapp_ip
        host_state = self.state.natapp_host != natapp_host
        uri_state = self.state.natapp_ip != natapp_ip
        validate_state = host_state or uri_state
        if validate_natapp and validate_state:
            self.state.natapp_ip = natapp_ip
            self.state.natapp_host = natapp_host
            self.configure_pod()

    def _on_natapp_relation_departed(self, _=None) -> NoReturn:
        """Clears data from UPF relation."""
        self.state.natapp_ip = None
        self.state.natapp_host = None
        self.configure_pod()

    def _missing_relations(self) -> str:
        """Checks if there missing relations.

        Returns:
            str: string with missing relations
        """
        data_status = {"natapp": self.state.natapp_ip}
        missing_relations = [k for k, v in data_status.items() if not v]
        return ", ".join(missing_relations)

    @property
    def relation_state(self) -> Dict[str, Any]:
        """Collects relation state configuration for pod spec assembly.

        Returns:
            Dict[str, Any]: relation state information.
        """
        relation_state = {"natapp_ip": self.state.natapp_ip}

        return relation_state

    def configure_pod(self, _=None) -> NoReturn:
        """Assemble the pod spec and apply it, if possible."""
        missing = self._missing_relations()
        if missing:
            status = "Waiting for {0} relation{1}"
            self.unit.status = BlockedStatus(
                status.format(missing, "s" if "," in missing else "")
            )
            return
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus("ready")
            return

        self.unit.status = MaintenanceStatus("Assembling pod spec")

        # Fetch image information
        try:
            self.unit.status = MaintenanceStatus("Fetching image information")
            image_info = self.image.fetch()
        except OCIImageResourceError:
            self.unit.status = BlockedStatus("Error fetching image information")
            return
        try:
            pod_spec = make_pod_spec(
                image_info,
                self.model.config,
                self.model.app.name,
                self.relation_state,
            )
        except ValueError as exc:
            logger.exception("Config data validation error")
            self.unit.status = BlockedStatus(str(exc))
            return

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")


if __name__ == "__main__":
    main(Upf1Charm)
