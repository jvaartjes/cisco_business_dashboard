"""Sensor platform for Cisco Business Dashboard."""
from __future__ import annotations

import logging
from typing import Any


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)

from . import get_coordinator
from .const import (
    ATTRIBUTION,
    SENSOR_ORG_DEVICECOUNT,
    SENSOR_ORG_NETWORKCOUNT,
    CONF_ORGANISATION,
)

_LOGGER = logging.getLogger(__name__)

# TODO: fix translations locale
SENSORS_ORG = (
    SensorEntityDescription(
        key=SENSOR_ORG_DEVICECOUNT,
        name="Device Count",
        native_unit_of_measurement="devices",
        icon="mdi:network",
    ),
    SensorEntityDescription(
        key=SENSOR_ORG_NETWORKCOUNT,
        name="Network Count",
        native_unit_of_measurement="devices",
        icon="mdi:network",
    ),
)


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
    _LOGGER.warning(config_entry.data[CONF_ORGANISATION])
    _LOGGER.warning("Keys coordinator.data[default]: ")
    _LOGGER.warning(coordinator.data["Default"])

    entities = [
        CiscoBDOrganisationSensor(
            coordinator, description, organisation=config_entry.data[CONF_ORGANISATION]
        )
        for description in SENSORS_ORG
    ]
    async_add_entities(entities)


class CiscoBDOrganisationSensor(CoordinatorEntity, SensorEntity):
    """Sensor representing CBD Organisation data."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
        organisation: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._unique_id = f"{organisation}-{description.key}"
        self._organisation = organisation
        self._name = description.name
        self._attr_icon = description.icon
        self._key = description.key
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        # TODO: fix translation locale
        self._device_name = f"Cisco Business Dashboard Organisation - {organisation}"

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                ("neerslag", "neerslag-device")
            },
            "name": self._device_name,
            "manufacturer": "jvaartjes",
            "model": "CBD",
            "sw_version": "0.1.0",
            "via_device": ("cbd", "abcd"),
        }

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
        return getattr(self.coordinator.data[self._organisation], self._key)

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._attr_icon

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""
        return self._attr_native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device attributes."""
        return {ATTR_ATTRIBUTION: ATTRIBUTION}


class CiscoBDDeviceSensor(CoordinatorEntity, SensorEntity):
    """Sensor representing CBD Organisation data."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
        organisation: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._unique_id = f"{organisation}-{description.key}"
        self._organisation = organisation
        self._name = description.name
        self._attr_icon = description.icon
        self._key = description.key
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        # TODO: fix translation locale
        self._device_name = f"Cisco Business Dashboard Organisation - {organisation}"

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                ("cbd", "cbd-org")
            },
            "name": self._device_name,
            "manufacturer": "jvaartjes",
            "model": "CBD",
            "sw_version": "0.1.0",
            "via_device": ("cbd", "abcd"),
        }

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
        return getattr(self.coordinator.data[self._organisation], self._key)

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._attr_icon

    @property
    def native_unit_of_measurement(self) -> str:
        """Return unit of measurement."""
        return self._attr_native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device attributes."""
        return {ATTR_ATTRIBUTION: ATTRIBUTION}
