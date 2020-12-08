#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi canonical@tataelxsi.onmicrosoft.com
# See LICENSE file for licensing details.

import logging

from ops.charm import CharmBase, CharmEvents
from ops.main import main
from ops.framework import StoredState, EventBase, EventSource
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus

from oci_image import OCIImageResource, OCIImageResourceError

from pydantic import ValidationError
from typing import NoReturn

from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class ConfigurePodEvent(EventBase):
    """Configure Pod event"""
    pass


class PcfEvents(CharmEvents):
    """PCF Events"""
    configure_pod = EventSource(ConfigurePodEvent)


logger = logging.getLogger(__name__)


class PcfCharm(CharmBase):
    state = StoredState()
    on = PcfEvents()

    def __init__(self, *args):
        super().__init__(*args)
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.start, self.configure_pod)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.upgrade_charm, self.configure_pod)

        # Registering custom internal events
        self.framework.observe(self.on.configure_pod, self.configure_pod)

        # Registering required relation changed events
        # self.framework.observe(self.on.amf_relation_changed, self._on_amf_relation_changed)

        # Registering required relation departed events
        # self.framework.observe(self.on.amf_relation_departed, self._on_amf_relation_departed)

        # -- initialize states --
        # self.state.set_default(amf_host=None)

    def configure_pod(self, event: EventBase) -> NoReturn:
        """Assemble the pod spec and apply it, if possible.
        Args:
            event (EventBase): Hook or Relation event that started the
                               function.
        """
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
    main(PcfCharm)
