#!/usr/bin/env python3
# Copyright 2020 canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.
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


class ConfigurePodEvent(EventBase):
    """Configure Pod event"""


class PublishNrfEvent(EventBase):
    """Publish NRF event"""


class NrfEvents(CharmEvents):
    """Nrf Events"""

    configure_pod = EventSource(ConfigurePodEvent)
    publish_nrf_info = EventSource(PublishNrfEvent)


class NrfCharm(CharmBase):
    """ NRF charm events class definition """

    state = StoredState()
    on = NrfEvents()

    def __init__(self, *args):
        super().__init__(*args)
        # Internal state initialization
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.start, self.configure_pod)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.upgrade_charm, self.configure_pod)

        # Registering custom internal events
        self.framework.observe(self.on.configure_pod, self.configure_pod)
        self.framework.observe(self.on.publish_nrf_info, self.publish_nrf_info)

        # Registering required relation changed events
        self.framework.observe(
            self.on.mongodb_relation_changed, self._on_mongodb_relation_changed
        )

        # Registering required relation departed events
        self.framework.observe(
            self.on.mongodb_relation_departed, self._on_mongodb_relation_departed
        )

        # -- initialize states --
        self.state.set_default(mongodb_host=None)
        self.state.set_default(mongodb_uri=None)

    def publish_nrf_info(self, event: EventBase) -> NoReturn:
        """Publishes NRF information
        relation.7
        Args:
        event (EventBase): NRF relation event .
        """
        # if event.unit is None:
        # return
        # if self.unit.status != ActiveStatus("ready"):
        # return
        logging.info(event)
        if not self.unit.is_leader():
            return
        relation_id = self.model.relations.__getitem__("nrf")
        for i in relation_id:
            relation = self.model.get_relation("nrf", i.id)
            logging.info("NRF Provides")
            logging.info(self.model.app.name)
            relation.data[self.model.app]["hostname"] = self.model.app.name

    def _on_mongodb_relation_changed(self, event: EventBase) -> NoReturn:
        """Reads information about the MongoDB relation.
        Args:
             event (EventBase): MongoDB relation event.
        """
        if event.app not in event.relation.data:
            return
        # data_loc = event.unit if event.unit else event.app
        mongodb_host = event.relation.data[event.app].get("hostname")
        mongodb_uri = event.relation.data[event.app].get("mongodb_uri")
        logging.info("NRF Requires from MongoDB")
        logging.info(mongodb_host)
        logging.info(mongodb_uri)
        if (
            mongodb_host  # noqa
            and mongodb_uri  # noqa
            # pylint:disable=line-too-long
            and (self.state.mongodb_host != mongodb_host or self.state.mongodb_uri != mongodb_uri)  # noqa
        ):
            self.state.mongodb_host = mongodb_host
            self.state.mongodb_uri = mongodb_uri
            self.on.configure_pod.emit()

    def _on_mongodb_relation_departed(self, event: EventBase) -> NoReturn:
        """Clears data from MongoDB relation.
        Args:
            event (EventBase): MongoDB relation event.
        """
        logging.info(event)
        self.state.mongodb_host = None
        self.state.mongodb_uri = None
        self.on.configure_pod.emit()

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

    def configure_pod(self, event: EventBase) -> NoReturn:
        """Assemble the pod spec and apply it, if possible.
        Args:
            event (EventBase): Hook or Relation event that started the
                               function.
        """
        logging.info(event)
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

        pod_spec = make_pod_spec(
            image_info,
            self.model.config,
            self.relation_state,
            self.model.app.name,
        )

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")
        self.on.publish_nrf_info.emit()


if __name__ == "__main__":
    main(NrfCharm)
