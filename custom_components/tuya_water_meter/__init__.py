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
PLATFORMS: list[str] = ["sensor"]

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
        """Actualitza les dades des de l'API de Tuya."""
        try:
            # Forcem refresc/obtenció del token i baixem dispositius
            await api.async_get_token()
            devices = await api.async_get_user_devices(entry.data[CONF_UID])
            # Retornem un diccionari mapejat per ID de dispositiu per agilitzar la cerca
            return {device["id"]: device for device in devices}
        except TuyaCloudApiError as err:
            raise UpdateFailed(f"Error connectant amb Tuya: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Tuya Cloud Developer Devices",
        update_method=async_update_data,
        update_interval=timedelta(minutes=5),
    )

    # Forcem la primera descàrrega de dades abans de carregar les plataformes
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
