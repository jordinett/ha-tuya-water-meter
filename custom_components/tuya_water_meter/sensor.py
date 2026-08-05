"""Sensor platform for Tuya Water Meter."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

EXCLUDED_DP_CODES = ("fault", "switch_code", "valve_status", "switch", "switch_1")

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tuya Water Meter sensors dynamically from Coordinator data."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id, device_data in coordinator.data.items():
        device_name = device_data.get("name", f"Tuya Device {device_id}")
        status_list = device_data.get("status", [])

        for status in status_list:
            dp_code = status.get("code")
            if dp_code and dp_code not in EXCLUDED_DP_CODES:
                entities.append(
                    TuyaCloudDynamicSensor(
                        coordinator=coordinator,
                        device_id=device_id,
                        device_name=device_name,
                        dp_code=dp_code,
                    )
                )

    async_add_entities(entities)


class TuyaCloudDynamicSensor(CoordinatorEntity, SensorEntity):
    """Sensor dinàmic per a dades globals de Tuya Developer."""

    def __init__(self, coordinator, device_id, device_name, dp_code):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._dp_code = dp_code

        self._attr_has_entity_name = True
        self._attr_unique_id = f"tuya_{device_id}_{dp_code}"
        self._attr_name = dp_code.replace("_", " ").title()

        self._assign_metadata()

    def _assign_metadata(self):
        """Assigna metadades (unitats, icones, classes) segons el DP exacte."""
        if self._dp_code == "water_use_data":
            self._attr_name = "Total Water Consumption"
            self._attr_device_class = SensorDeviceClass.WATER
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_native_unit_of_measurement = "m³"
            self._attr_icon = "mdi:water"
            
        elif self._dp_code == "voltage_current":
            self._attr_name = "Battery Voltage"
            self._attr_device_class = SensorDeviceClass.VOLTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = "V"
            
        else:
            self._attr_icon = "mdi:eye"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Tuya Custom",
        }

    @property
    def native_value(self):
        device_data = self.coordinator.data.get(self._device_id)
        if not device_data:
            return None

        status_list = device_data.get("status", [])
        for status in status_list:
            if status.get("code") == self._dp_code:
                val = status.get("value")
                if val is not None:
                    try:
                        if self._dp_code == "water_use_data":
                            return float(val) / 1000.0
                        if self._dp_code == "voltage_current":
                            return float(val) / 100.0
                    except (ValueError, TypeError):
                        pass
                return val
        return None
