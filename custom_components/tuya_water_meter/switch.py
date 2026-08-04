"""Switch platform for Tuya Water Meter."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Tuya Water Meter switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    switches = []
    for device in coordinator.data:
        # Crea el switch per a cada dispositiu
        switches.append(TuyaValveSwitch(coordinator, device))
        
    async_add_entities(switches)

class TuyaValveSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of the Tuya Valve Switch."""

    def __init__(self, coordinator, device):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"{device['id']}_valve"
        self._attr_name = "Vàlvula d'Aigua"
        self._attr_icon = "mdi:pipe-valve"
        # Substitueix 'switch' pel codi exacte del Data Point de la vàlvula a Tuya (ex: 'valve_state')
        self._dp_code = "switch" 

    @property
    def is_on(self) -> bool:
        """Return true if the valve is open (on)."""
        # Llegim la llista d'estats per veure si està oberta o tancada
        for status in self.coordinator.data:
            if status["id"] == self._device["id"]:
                for dp in status.get("status", []):
                    if dp["code"] == self._dp_code:
                        return bool(dp["value"])
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """Open the valve."""
        success = await self.coordinator.api.async_send_command(
            self._device["id"], [{"code": self._dp_code, "value": True}]
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Close the valve."""
        success = await self.coordinator.api.async_send_command(
            self._device["id"], [{"code": self._dp_code, "value": False}]
        )
        if success:
            await self.coordinator.async_request_refresh()
