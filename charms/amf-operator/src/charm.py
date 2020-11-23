#!/usr/bin/env python3
# Copyright 2020 David Garcia
# See LICENSE file for licensing details.

import logging

from ops.charm import CharmBase, EventBase
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.main import main
from ops.framework import StoredState

from oci_image import OCIImageResource, OCIImageResourceError

from pydantic import ValidationError
from typing import Any, Dict, NoReturn

from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class AmfCharm(CharmBase):
    _stored = StoredState()

    def __init__(self, *args) -> NoReturn:
        """AMF Charm constructor"""
        super().__init__(*args)

        # Internal state initialization
        self._stored.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.start, self.configure_pod)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.upgrade_charm, self.configure_pod)

        # -- initialize states --
        self.state.set_default(installed=False)
        self.state.set_default(configured=False)
        self.state.set_default(started=False)

    # def _missing_relations(self) -> str:
    #     """Checks if there missing relations.

    #     Returns:
    #         str: string with missing relations
    #     """
    #     data_status = {
    #         "kafka": self.state.message_host,
    #         "mongodb": self.state.database_uri,
    #     }

    #     missing_relations = [k for k, v in data_status.items() if not v]

    #     return ", ".join(missing_relations)

    # @property
    # def relation_state(self) -> Dict[str, Any]:
    #     """Collects relation state configuration for pod spec assembly.

    #     Returns:
    #         Dict[str, Any]: relation state information.
    #     """
    #     relation_state = {
    #         "message_host": self.state.message_host,
    #         "message_port": self.state.message_port,
    #         "database_uri": self.state.database_uri,
    #     }

    #     return relation_state

    def configure_pod(self, event: EventBase) -> NoReturn:
        """Assemble the pod spec and apply it, if possible.

        Args:
            event (EventBase): Hook or Relation event that started the
                               function.
        """
        # if missing := self._missing_relations():
        #     self.unit.status = BlockedStatus(
        #         "Waiting for {0} relation{1}".format(
        #             missing, "s" if "," in missing else ""
        #         )
        #     )
        #     return

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
                self.config,
                # self.relation_state,
                self.model.app.name,
            )
        except ValidationError as exc:
            logger.exception("Config/Relation data validation error")
            self.unit.status = BlockedStatus(str(exc))
            return

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")


if __name__ == "__main__":
    main(AmfCharm)
