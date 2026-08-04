  """The Tuya Water Meter integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TuyaCloudApi, TuyaCloudApiError
from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_REGION, CONF_UID

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[str] = ["sensor", "binary_sensor", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tuya Water Meter from a config entry."""
    session = async_get_clientsession(hass)
    
    api = TuyaCloudApi(
        session=session,
        client_id=entry.data[CONF_CLIENT_ID],
        client_secret=entry.data[CONF_CLIENT_SECRET],
        region=entry.data[CONF_REGION],
    )

    async def async_update_data():
        """Actualitza les dades des de l'API de Tuya i filtra per categoria."""
        try:
            # Forcem refresc/obtenció del token i baixem dispositius
            await api.async_get_token()
            devices = await api.async_get_user_devices(entry.data[CONF_UID])
            
            # FILTRE CLAU: Només ens quedem amb els dispositius de la categoria "znsb"
            filtered_devices = {}
            for device in devices:
                if device.get("category") == "znsb":
                    filtered_devices[device["id"]] = device
                    _LOGGER.debug("Comptador d'aigua trobat: %s", device.get("name"))
                else:
                    _LOGGER.debug("Ignorant el dispositiu %s (Categoria: %s)", device.get("name"), device.get("category"))
                    
            return filtered_devices
            
        except TuyaCloudApiError as err:
            raise UpdateFailed(f"Error connectant amb Tuya: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Tuya Water Meter Devices (ZNSB)",
        update_method=async_update_data,
        # Interval d'1 hora per optimitzar les peticions al cloud
        update_interval=timedelta(hours=1),
    )

    # Forcem la primera descàrrega de dades en arrencar
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
