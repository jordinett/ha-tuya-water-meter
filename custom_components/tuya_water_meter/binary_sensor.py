"""Binary sensor platform for Tuya Water Meter."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

# Mapeig exacte dels bits d'alerta del comptador
FAULT_MAP = {
    0: ("Battery Alarm", BinarySensorDeviceClass.BATTERY),
    1: ("Magnetism Alarm", BinarySensorDeviceClass.PROBLEM),
    2: ("Switch Gaps Alarm", BinarySensorDeviceClass.PROBLEM),
    3: ("Meter Body Alarm", BinarySensorDeviceClass.PROBLEM),
    4: ("Credit Alarm", BinarySensorDeviceClass.PROBLEM),
    5: ("Arrearage Alarm", BinarySensorDeviceClass.PROBLEM),
    6: ("Abnormal Water Alarm", BinarySensorDeviceClass.MOISTURE),
    7: ("Overflow Alarm", BinarySensorDeviceClass.PROBLEM),
    8: ("Reverse Flow Alarm", BinarySensorDeviceClass.PROBLEM),
    9: ("Low Flow Alarm", BinarySensorDeviceClass.PROBLEM),
    10: ("Low Temp Alarm", BinarySensorDeviceClass.COLD),
    11: ("Overuse Alarm", BinarySensorDeviceClass.PROBLEM),
    12: ("Cover Alarm", BinarySensorDeviceClass.TAMPER),
    13: ("Over Pre Alarm", BinarySensorDeviceClass.PROBLEM),
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tuya Water Meter fault binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id, device_data in coordinator.data.items():
        device_name = device_data.get("name", f"Tuya Device {device_id}")
        status_list = device_data.get("status", [])

        # Busquem el DP 'fault'
        for status in status_list:
            if status.get("code") == "fault":
                # Creem un binary sensor independent per a cada bit
                for bit, (alarm_name, device_class) in FAULT_MAP.items():
                    entities.append(
                        TuyaFaultBinarySensor(
                            coordinator=coordinator,
                            device_id=device_id,
                            device_name=device_name,
                            bit=bit,
                            alarm_name=alarm_name,
                            device_class=device_class,
                        )
                    )
                break # Ja hem processat el fault

    async_add_entities(entities)


class TuyaFaultBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor binari que representa un bit individual d'alerta dins del DP 'fault'."""

    def __init__(self, coordinator, device_id, device_name, bit, alarm_name, device_class):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._bit = bit

        self._attr_has_entity_name = True
        self._attr_name = alarm_name
        self._attr_unique_id = f"tuya_{device_id}_fault_bit_{bit}"
        self._attr_device_class = device_class

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Tuya Custom",
        }

    @property
    def is_on(self) -> bool:
        """Avalua si el bit específic d'aquest sensor està activat dins el valor del 'fault'."""
        device_data = self.coordinator.data.get(self._device_id)
        if not device_data:
            return False

        status_list = device_data.get("status", [])
        for status in status_list:
            if status.get("code") == "fault":
                try:
                    # Agafem l'integer enter de Tuya i comprovem el bit fent bitwise AND
                    fault_val = int(status.get("value", 0))
                    return bool(fault_val & (1 << self._bit))
                except (ValueError, TypeError):
                    return False
        return False
