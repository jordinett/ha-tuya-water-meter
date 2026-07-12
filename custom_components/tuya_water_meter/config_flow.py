"""Config flow for Tuya Water Meter."""

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


class TuyaWaterMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Water Meter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration step."""

        if user_input is not None:
            return self.async_create_entry(
                title="Tuya Water Meter",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=None,
        )
