"""Config flow for Poltava Power Outages integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_QUEUE,
    CONF_UPDATE_INTERVAL,
    CONF_INCLUDE_POSSIBLE,
    CONF_DATA_URL,
    DEFAULT_QUEUE,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_INCLUDE_POSSIBLE,
    DEFAULT_DATA_URL,
    QUEUES,
)

_LOGGER = logging.getLogger(__name__)


class PoltavaPowerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Poltava Power Outages."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            queue = user_input[CONF_QUEUE]
            await self.async_set_unique_id(f"{DOMAIN}_{queue}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Полтаваобленерго (Черга {queue})",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_QUEUE, default=DEFAULT_QUEUE): vol.In(QUEUES),
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=2, max=60)),
                vol.Optional(
                    CONF_INCLUDE_POSSIBLE, default=DEFAULT_INCLUDE_POSSIBLE
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return PoltavaPowerOptionsFlowHandler(config_entry)


class PoltavaPowerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Poltava Power Outages."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_queue = self.config_entry.options.get(
            CONF_QUEUE, self.config_entry.data.get(CONF_QUEUE, DEFAULT_QUEUE)
        )
        current_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        )
        current_possible = self.config_entry.options.get(
            CONF_INCLUDE_POSSIBLE,
            self.config_entry.data.get(CONF_INCLUDE_POSSIBLE, DEFAULT_INCLUDE_POSSIBLE),
        )
        current_url = self.config_entry.options.get(
            CONF_DATA_URL,
            self.config_entry.data.get(CONF_DATA_URL, DEFAULT_DATA_URL),
        )

        options_schema = vol.Schema(
            {
                vol.Required(CONF_QUEUE, default=current_queue): vol.In(QUEUES),
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=current_interval
                ): vol.All(vol.Coerce(int), vol.Range(min=2, max=60)),
                vol.Optional(
                    CONF_INCLUDE_POSSIBLE, default=current_possible
                ): bool,
                vol.Optional(
                    CONF_DATA_URL, default=current_url
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
