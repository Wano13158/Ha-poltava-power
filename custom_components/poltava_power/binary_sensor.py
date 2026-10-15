"""Binary sensor platform for Poltava Power Outages integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import PoltavaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Poltava Power binary sensor entities."""
    coordinator: PoltavaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PoltavaPowerBinarySensor(coordinator)])


class PoltavaPowerBinarySensor(
    CoordinatorEntity[PoltavaDataUpdateCoordinator], BinarySensorEntity
):
    """Binary sensor representing scheduled power availability."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_attribution = ATTRIBUTION
    _attr_translation_key = "scheduled_power"
    _attr_name = "Світло за графіком"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.queue = coordinator.queue
        self._attr_unique_id = f"poltava_power_{self.queue}_power_scheduled"

    @property
    def is_on(self) -> bool:
        """Return True if power is scheduled to be available, False if outage."""
        return self.coordinator.data.is_power_on

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        return "mdi:lightning-bolt" if self.is_on else "mdi:lightning-bolt-outline"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"poltava_power_{self.queue}")},
            name=f"Полтава (Черга {self.queue})",
            manufacturer="АТ 'ПОЛТАВАОБЛЕНЕРГО'",
            model=f"ГПВ Черга {self.queue}",
            sw_version="1.1.0",
            configuration_url="https://www.poe.pl.ua/disconnection/power-outages/",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        data = self.coordinator.data
        return {
            "queue": self.queue,
            "status_text": data.current_state_text,
            "is_outage": data.is_outage,
            "is_maybe_outage": data.is_maybe_outage,
            "current_slot": data.current_slot,
            "next_outage": (
                data.next_outage_start.isoformat() if data.next_outage_start else None
            ),
            "next_restore": (
                data.next_restore.isoformat() if data.next_restore else None
            ),
        }
