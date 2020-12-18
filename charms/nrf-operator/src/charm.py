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
""" Defining nrf charm events """

import logging

# import yaml
# import json
from typing import Any, Dict, NoReturn
from ops.charm import CharmBase, CharmEvents
from ops.main import main
from ops.framework import StoredState, EventBase, EventSource
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus

from oci_image import OCIImageResource, OCIImageResourceError

from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class NrfCharm(CharmBase):
    """ NRF charm events class definition """

    state = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        # Internal state initialization
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.config_changed, self.configure_pod)

        # Registering required relation changed events
        self.framework.observe(
            self.on.mongodb_relation_changed,
            self._on_mongodb_relation_changed,
        )

        # Registering required relation broken events
        self.framework.observe(
            self.on.mongodb_relation_broken,
            self._on_mongodb_relation_broken,
        )

        # Registering provides relation events
        self.framework.observe(self.on.nrf_relation_joined, self.publish_nrf_info)

        # -- initialize states --
        self.state.set_default(mongodb_host=None, mongodb_uri=None)

    def publish_nrf_info(self, event: EventBase) -> NoReturn:
        """Publishes NRF information relation.
        Args:
        event (EventBase): NRF relation event .
        """
        if self.unit.is_leader():
            event.relation.data[self.model.app]["hostname"] = self.model.app.name

    def _on_mongodb_relation_changed(self, event: EventBase) -> NoReturn:
        """Reads information about the MongoDB relation.
        Args:
             event (EventBase): MongoDB relation event.
        """
        if event.app not in event.relation.data:
            return
        mongodb_host = event.relation.data[event.app].get("hostname")
        mongodb_uri = event.relation.data[event.app].get("mongodb_uri")

        if (
            mongodb_host
            and mongodb_uri
            and (
                self.state.mongodb_host != mongodb_host
                or self.state.mongodb_uri != mongodb_uri
            )
        ):
            self.state.mongodb_host = mongodb_host
            self.state.mongodb_uri = mongodb_uri
            self.configure_pod()

    def _on_mongodb_relation_broken(self, event: EventBase) -> NoReturn:
        """Clears data from MongoDB relation.
        Args:
            event (EventBase): MongoDB relation event.
        """

        self.state.mongodb_host = None
        self.state.mongodb_uri = None
        self.configure_pod()

    def _missing_relations(self) -> str:
        """Checks if there missing relations.

        Returns:
            str: string with missing relations
        """
        data_status = {"mongodb": self.state.mongodb_uri}
        missing_relations = [k for k, v in data_status.items() if not v]
        return ", ".join(missing_relations)

    @property
    def relation_state(self) -> Dict[str, Any]:
        """Collects relation state configuration for pod spec assembly.

        Returns:
            Dict[str, Any]: relation state information.
        """
        relation_state = {
            "mongodb_host": self.state.mongodb_host,
            "mongodb_uri": self.state.mongodb_uri,
        }

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

        # Fetch image information
        try:
            image_info = self.image.fetch()
        except OCIImageResourceError:
            self.unit.status = BlockedStatus("Error fetching image information")
            return

        try:
            pod_spec = make_pod_spec(
                image_info,
                self.model.config,
                self.relation_state,
                self.model.app.name,
            )
        except ValueError as e:
            logger.exception("Config/Relation data validation error")
            self.unit.status = BlockedStatus(str(e))
            return

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")


if __name__ == "__main__":
    main(NrfCharm)
