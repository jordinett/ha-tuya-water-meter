"""Sensor platform for Tuya Water Meter."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tuya Water Meter sensors dynamically from Coordinator data."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Iterem tots els dispositius detectats per l'API de l'usuari
    for device_id, device_data in coordinator.data.items():
        device_name = device_data.get("name", f"Tuya Device {device_id}")
        status_list = device_data.get("status", [])

        # Creem una entitat per cada codi (DP Code) que té el dispositiu a Tuya Developer
        for status in status_list:
            dp_code = status.get("code")
            if dp_code:
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
    """Sensor dinàmic que representa un datapoint concret del portal Tuya Developer."""

    def __init__(self, coordinator, device_id, device_name, dp_code):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._dp_code = dp_code

        # Propietats bàsiques de l'entitat de Home Assistant
        self._attr_has_entity_name = True
        self._attr_name = dp_code.replace("_", " ").title()
        self._attr_unique_id = f"tuya_{device_id}_{dp_code}"

        # Assignem icones bàsiques depenent de paraules clau habituals de Tuya
        self._assign_metadata()

    def _assign_metadata(self):
        """Assigna metadades segons el nom de la variable de Tuya."""
        code_lower = self._dp_code.lower()
        if "flux" in code_lower or "consumption" in code_lower or "volume" in code_lower:
            self._attr_icon = "mdi:water"
        elif "battery" in code_lower or "residual" in code_lower:
            self._attr_icon = "mdi:battery"
            self._attr_native_unit_of_measurement = "%"
        elif "flow" in code_lower or "speed" in code_lower:
            self._attr_icon = "mdi:water-speed"
        else:
            self._attr_icon = "mdi:eye"

    @property
    def device_info(self):
        """Enllaça aquesta entitat a un dispositiu unificat dins de Home Assistant."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Tuya Custom",
        }

    @property
    def native_value(self):
        """Retorna el valor actual extret de les dades emmagatzemades al coordinator."""
        device_data = self.coordinator.data.get(self._device_id)
        if not device_data:
            return None

        status_list = device_data.get("status", [])
        for status in status_list:
            if status.get("code") == self._dp_code:
                return status.get("value")
        return None
