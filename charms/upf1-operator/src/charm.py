#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi <canonical@tataelxsi.onmicrosoft.com>
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


class Upf1Events(CharmEvents):
    """UPF1 Events"""

    configure_pod = EventSource(ConfigurePodEvent)


class Upf1Charm(CharmBase):
    state = StoredState()
    on = Upf1Events()

    def __init__(self, *args):
        super().__init__(*args)
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.start, self.configure_pod)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.upgrade_charm, self.configure_pod)
        self.framework.observe(self.on.leader_elected, self.configure_pod)
        self.framework.observe(self.on.update_status, self.configure_pod)

        # Registering custom internal events
        self.framework.observe(self.on.configure_pod, self.configure_pod)

        # Registering provided relation events
        self.framework.observe(self.on.upf_relation_changed, self._publish_upf_info)

    def _publish_upf_info(self, event: EventBase) -> NoReturn:
        """Publishes UPF IP information for SMF
          relation.7
        Args:
             event (EventBase): upf relation event to update SMF.
        """
        # if event.unit is None:
        # return

        logging.info("UPF Provides IP")
        print("Entered")
        if self.unit.is_leader():
            private_ip = str(
                self.model.get_binding(event.relation).network.bind_address
            )
            logging.info(private_ip)
            print("Entered ip", private_ip)
            event.relation.data[self.model.app]["private_address"] = private_ip

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
    main(Upf1Charm)
