"""Sensor platform for Cisco Business Dashboard."""
from __future__ import annotations
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import get_coordinator
from .const import ATTRIBUTION

_LOGGER = logging.getLogger(__name__)

SENSORS = {
    "organisation": "mdi:car",
    "networkcount": "mdi:network",
    "devicecount": "mdi:network",
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Defer sensor setup to the shared sensor module."""
    coordinator = await get_coordinator(hass)

    _LOGGER.warning("Async_setup_entry:")
    _LOGGER.warning(coordinator.data)
    entities: list[CiscoBDOrganisationSensor] = []

    _LOGGER.warning("Keys coordinator.data: ")
    _LOGGER.warning(coordinator.data.keys())
    _LOGGER.warning("Keys config_entry.data: ")
    _LOGGER.warning(config_entry.data["organisation"])
    _LOGGER.warning("Keys coordinator.data[default]: ")
    _LOGGER.warning(coordinator.data["Default"])

    #   _LOGGER.warning(coordinator.data['Default']['organisation'])

    for info_type in SENSORS:
        if (
            getattr(coordinator.data[config_entry.data["organisation"]], info_type)
            != ""
        ):
            entities.append(
                CiscoBDOrganisationSensor(
                    coordinator, config_entry.data["organisation"], info_type
                )
            )

    async_add_entities(entities)


class CiscoBDOrganisationSensor(CoordinatorEntity, SensorEntity):
    """Sensor representing CBD Organisation data."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, organisation: str, info_type: str
    ) -> None:
        """Initialize sensor."""
        _LOGGER.warning("Init sensor")
        super().__init__(coordinator)
        self._unique_id = f"{organisation}-{info_type}"
        self._organisation = organisation
        self._info_type = info_type
        self._name = f"{organisation} - {info_type}".replace("_", " ")

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique id of the device."""
        return self._unique_id

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self.coordinator.last_update_success and (
            self._organisation in self.coordinator.data
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return getattr(self.coordinator.data[self._organisation], self._info_type)

    @property
    def icon(self) -> str:
        """Return the icon."""
        return SENSORS[self._info_type]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""
        return "cars"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device attributes."""
        return {ATTR_ATTRIBUTION: ATTRIBUTION}
