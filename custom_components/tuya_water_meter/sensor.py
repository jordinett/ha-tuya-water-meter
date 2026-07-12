"""Sensor platform for Tuya Water Meter."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""

    async_add_entities(
        [
            TuyaWaterMeterTestSensor(),
        ]
    )


class TuyaWaterMeterTestSensor(SensorEntity):
    """Temporary test sensor."""

    _attr_name = "Tuya Water Meter Test"
    _attr_unique_id = "tuya_water_meter_test"
    _attr_native_value = "Working"
