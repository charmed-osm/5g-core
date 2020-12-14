#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.
""" Defining amf charm events """
import logging

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


class PublishAmfEvent(EventBase):
    """Configure Pod event"""


class AmfEvents(CharmEvents):
    """AMF Events"""

    configure_pod = EventSource(ConfigurePodEvent)
    publish_amf_info = EventSource(PublishAmfEvent)


class AmfCharm(CharmBase):
    """ AMF charm events class definition """

    state = StoredState()
    on = AmfEvents()

    def __init__(self, *args) -> NoReturn:
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
        self.framework.observe(self.on.publish_amf_info, self.publish_amf_info)

        # Registering required relation changed events
        self.framework.observe(
            self.on.nrf_relation_changed, self._on_nrf_relation_changed
        )

        # Registering required relation departed events
        self.framework.observe(
            self.on.nrf_relation_departed, self._on_nrf_relation_departed
        )

        # -- initialize states --
        self.state.set_default(nrf_host=None)

    def publish_amf_info(self, event: EventBase) -> NoReturn:
        """Publishes AMF information
          relation.7
        Args:
             event (EventBase): AMF relation event .
        """
        logging.info(event)
        if not self.unit.is_leader():
            return
        relation_id = self.model.relations.__getitem__("amf")
        for i in relation_id:
            relation = self.model.get_relation("amf", i.id)
            logging.info("AMF Provides")
            logging.info(self.model.app.name)
            relation.data[self.model.app]["hostname"] = self.model.app.name

    def _on_nrf_relation_changed(self, event: EventBase) -> NoReturn:
        """Reads information about the NRF relation.
        Args:
           event (EventBase): NRF relation event.
        """
        if event.app not in event.relation.data:
            return
        # data_loc = event.unit if event.unit else event.app

        nrf_host = event.relation.data[event.app].get("hostname")
        logging.info("AMF Requires From NRF")
        logging.info(nrf_host)
        if nrf_host and self.state.nrf_host != nrf_host:
            self.state.nrf_host = nrf_host
            self.on.configure_pod.emit()

    def _on_nrf_relation_departed(self, event: EventBase) -> NoReturn:
        """Clears data from NRF relation.

        Args:
            event (EventBase): NRF relation event.
        """
        logging.info(event)
        self.state.nrf_host = None
        self.on.configure_pod.emit()

    def _missing_relations(self) -> str:
        """Checks if there missing relations.

        Returns:
            str: string with missing relations
        """
        data_status = {"nrf": self.state.nrf_host}
        missing_relations = [k for k, v in data_status.items() if not v]
        return ", ".join(missing_relations)

    @property
    def relation_state(self) -> Dict[str, Any]:
        """Collects relation state configuration for pod spec assembly.

        Returns:
            Dict[str, Any]: relation state information.
        """
        relation_state = {"nrf_host": self.state.nrf_host}

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
            self.model.app.name,
        )

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")
        self.on.publish_amf_info.emit()


if __name__ == "__main__":
    main(AmfCharm)
