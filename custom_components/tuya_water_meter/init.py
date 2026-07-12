from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Tuya Water Meter integration."""
    return True
