"""Switch platform for Tuya Water Meter."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya Water Meter switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    switches = []
    # CORRECCIÓ: Llegim com a diccionari (items)
    for device_id, device_data in coordinator.data.items():
        switches.append(TuyaValveSwitch(coordinator, device_id, device_data))
        
    async_add_entities(switches)

class TuyaValveSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of the Tuya Valve Switch."""

    def __init__(self, coordinator, device_id, device_data) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_data = device_data
        self._attr_unique_id = f"{device_id}_valve"
        self._attr_name = "Vàlvula d'Aigua"
        self._attr_icon = "mdi:pipe-valve"
        self._dp_code = "switch_code" 

    @property
    def is_on(self) -> bool:
        """Return true if the valve is open (on)."""
        # CORRECCIÓ: Busquem directament la ID dins el diccionari del coordinator
        device_data = self.coordinator.data.get(self._device_id)
        if not device_data:
            return False

        for dp in device_data.get("status", []):
            if dp.get("code") == self._dp_code:
                return bool(dp.get("value"))
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Open the valve."""
        success = await self.coordinator.api.async_send_command(
            self._device_id, [{"code": self._dp_code, "value": True}]
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Close the valve."""
        success = await self.coordinator.api.async_send_command(
            self._device_id, [{"code": self._dp_code, "value": False}]
        )
        if success:
            await self.coordinator.async_request_refresh()
