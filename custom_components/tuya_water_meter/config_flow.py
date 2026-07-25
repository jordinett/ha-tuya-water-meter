"""Config flow for Tuya Water Meter."""

from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_UID,
    CONF_REGION,
)

_LOGGER = logging.getLogger(__name__)

class TuyaWaterMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Water Meter."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Tuya Developer Cloud",
                data=user_input,
            )

        # Definim el formulari separant bé els elements per evitar errors de sintaxi
        data_schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_CLIENT_SECRET): str,
                vol.Required(CONF_UID): str,
                vol.Required(CONF_REGION, default="eu"): vol.In(
                    {
                        "eu": "Europe (eu)",
                        "us": "America (us)",
                        "cn": "China (cn)",
                        "in": "India (in)",
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
