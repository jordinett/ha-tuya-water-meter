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

# Llista de codis habituals que utilitza Tuya per a la vàlvula
VALVE_DP_CODES = ("switch_code", "valve_status", "switch", "switch_1")

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya Water Meter switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    switches = []
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
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{device_id}_valve"
        self._attr_name = "Vàlvula d'Aigua"
        self._attr_icon = "mdi:pipe-valve"

    @property
    def device_info(self):
        """Vinculem l'entitat directament al dispositiu principal."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_data.get("name", f"Tuya Device {self._device_id}"),
            "manufacturer": "Tuya Custom",
        }

    def _get_dp_code(self) -> str:
        """Trobem el codi DP actiu per a la vàlvula."""
        device_data = self.coordinator.data.get(self._device_id, {})
        for dp in device_data.get("status", []):
            code = dp.get("code")
            if code in VALVE_DP_CODES:
                return code
        return "switch_code"

    @property
    def is_on(self) -> bool:
        """Return true if the valve is open (on)."""
        device_data = self.coordinator.data.get(self._device_id)
        if not device_data:
            return False

        dp_code = self._get_dp_code()
        for dp in device_data.get("status", []):
            if dp.get("code") == dp_code:
                return bool(dp.get("value"))
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Open the valve."""
        dp_code = self._get_dp_code()
        success = await self.coordinator.api.async_send_command(
            self._device_id, [{"code": dp_code, "value": True}]
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Close the valve."""
        dp_code = self._get_dp_code()
        success = await self.coordinator.api.async_send_command(
            self._device_id, [{"code": dp_code, "value": False}]
        )
        if success:
            await self.coordinator.async_request_refresh()
