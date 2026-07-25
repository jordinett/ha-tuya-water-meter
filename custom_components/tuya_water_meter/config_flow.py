"""Config flow for Tuya Water Meter."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

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

        self.hass.logger.warning(
            "TUYA WATER METER TEST: Config flow executed."
        )

        if user_input is not None:
            self.hass.logger.warning(
                "TUYA WATER METER TEST: Submit button pressed."
            )

            return self.async_create_entry(
                title="Tuya Water Meter",
                data={
                    CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                    CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
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
        )
