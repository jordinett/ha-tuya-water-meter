"""Config flow for Tuya Water Meter."""

from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TuyaCloudApi, TuyaCloudApiError
from .const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, DOMAIN


class TuyaWaterMeterConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for Tuya Water Meter."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ):
        """Handle the initial setup step."""

        errors = {}

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)

                api = TuyaCloudApi(
                    session=session,
                    client_id=user_input[CONF_CLIENT_ID],
                    client_secret=user_input[CONF_CLIENT_SECRET],
                )

                token_data = await api.async_get_token()

            except (TuyaCloudApiError, aiohttp.ClientError):
                errors["base"] = "cannot_connect"

            else:
                return self.async_create_entry(
                    title="Tuya Water Meter",
                    data={
                        CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                        CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
                        "uid": token_data.get("uid"),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_SECRET): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
