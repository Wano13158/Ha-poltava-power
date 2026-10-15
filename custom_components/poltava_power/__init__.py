"""Poltava Power Outages integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

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
)
from .coordinator import PoltavaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CALENDAR,
    Platform.IMAGE,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Poltava Power Outages from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    queue = entry.options.get(CONF_QUEUE, entry.data.get(CONF_QUEUE, DEFAULT_QUEUE))
    update_interval = entry.options.get(
        CONF_UPDATE_INTERVAL, entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    )
    include_possible = entry.options.get(
        CONF_INCLUDE_POSSIBLE, entry.data.get(CONF_INCLUDE_POSSIBLE, DEFAULT_INCLUDE_POSSIBLE)
    )
    data_url = entry.options.get(
        CONF_DATA_URL, entry.data.get(CONF_DATA_URL, DEFAULT_DATA_URL)
    )

    coordinator = PoltavaDataUpdateCoordinator(
        hass=hass,
        queue=queue,
        update_interval_minutes=update_interval,
        include_possible=include_possible,
        data_url=data_url,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry after options change."""
    await hass.config_entries.async_reload(entry.entry_id)
