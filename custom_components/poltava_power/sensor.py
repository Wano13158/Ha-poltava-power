"""Sensor platform for Poltava Power Outages integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    DOMAIN,
    STATE_MAYBE_OFF,
    STATE_POWER_OFF,
    STATE_POWER_ON,
)
from .coordinator import PoltavaDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Poltava Power Outages sensor entities."""
    coordinator: PoltavaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            PoltavaCurrentStatusSensor(coordinator),
            PoltavaNextOutageSensor(coordinator),
            PoltavaNextRestoreSensor(coordinator),
            PoltavaTodayScheduleSensor(coordinator),
            PoltavaTomorrowScheduleSensor(coordinator),
            PoltavaLastUpdatedSensor(coordinator),
        ]
    )


class PoltavaBaseSensor(CoordinatorEntity[PoltavaDataUpdateCoordinator], SensorEntity):
    """Base class for Poltava Power sensors."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the base sensor."""
        super().__init__(coordinator)
        self.queue = coordinator.queue

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"poltava_power_{self.queue}")},
            name=f"Полтаваобленерго (Черга {self.queue})",
            manufacturer="АТ 'ПОЛТАВАОБЛЕНЕРГО'",
            model=f"ГПВ Графік відключень (Черга {self.queue})",
            sw_version="1.0.0",
            configuration_url="https://www.poe.pl.ua/disconnection/power-outages/",
        )


class PoltavaCurrentStatusSensor(PoltavaBaseSensor):
    """Sensor for current electricity schedule status."""

    _attr_translation_key = "current_status"

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"poltava_power_{self.queue}_current_status"
        self._attr_name = f"Поточний стан (Черга {self.queue})"

    @property
    def native_value(self) -> str:
        """Return current status text."""
        return self.coordinator.data.current_state_text

    @property
    def icon(self) -> str:
        """Return dynamic icon based on status."""
        state = self.coordinator.data.current_state
        if state == STATE_POWER_OFF:
            return "mdi:power-plug-off"
        if state == STATE_MAYBE_OFF:
            return "mdi:help-circle-outline"
        return "mdi:power-plug"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed state attributes."""
        data = self.coordinator.data
        return {
            "queue": self.queue,
            "status_code": data.current_state,
            "is_outage": data.is_outage,
            "is_power_on": data.is_power_on,
            "is_maybe_outage": data.is_maybe_outage,
            "current_slot": data.current_slot,
            "current_slot_raw": data.current_slot_raw,
            "today_outages": data.today_outages_text,
            "today_possible": data.today_possible_text,
            "tomorrow_outages": data.tomorrow_outages_text,
            "tomorrow_possible": data.tomorrow_possible_text,
            "last_updated_oblenergo": data.last_updated_oblenergo,
            "hourly_today": data.hourly_today,
            "hourly_tomorrow": data.hourly_tomorrow,
        }


class PoltavaNextOutageSensor(PoltavaBaseSensor):
    """Sensor for next scheduled outage timestamp."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-alert-outline"
    _attr_translation_key = "next_outage"

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"poltava_power_{self.queue}_next_outage"
        self._attr_name = f"Наступне відключення (Черга {self.queue})"

    @property
    def native_value(self) -> datetime | None:
        """Return timestamp of the next outage start."""
        return self.coordinator.data.next_outage_start

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return attributes about the next outage."""
        start = self.coordinator.data.next_outage_start
        end = self.coordinator.data.next_outage_end
        attrs: dict[str, Any] = {"queue": self.queue}
        if start:
            attrs["start_time"] = start.strftime("%H:%M")
            attrs["start_date"] = start.strftime("%Y-%m-%d")
        if end:
            attrs["end_time"] = end.strftime("%H:%M")
        if start and end:
            duration_mins = int((end - start).total_seconds() / 60)
            attrs["duration_minutes"] = duration_mins
        return attrs


class PoltavaNextRestoreSensor(PoltavaBaseSensor):
    """Sensor for when power is scheduled to return."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-check-outline"
    _attr_translation_key = "next_restore"

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"poltava_power_{self.queue}_next_restore"
        self._attr_name = f"Увімкнення світла (Черга {self.queue})"

    @property
    def native_value(self) -> datetime | None:
        """Return timestamp of next power restore."""
        return self.coordinator.data.next_restore

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return attributes about power restoration."""
        restore = self.coordinator.data.next_restore
        attrs: dict[str, Any] = {"queue": self.queue}
        if restore:
            attrs["restore_time"] = restore.strftime("%H:%M")
            attrs["restore_date"] = restore.strftime("%Y-%m-%d")
        return attrs


class PoltavaTodayScheduleSensor(PoltavaBaseSensor):
    """Sensor for today's summary outage schedule."""

    _attr_icon = "mdi:calendar-today"
    _attr_translation_key = "today_schedule"

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"poltava_power_{self.queue}_today_schedule"
        self._attr_name = f"Графік на сьогодні (Черга {self.queue})"

    @property
    def native_value(self) -> str:
        """Return formatted string with today's outages."""
        return self.coordinator.data.today_outages_text

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional schedule attributes."""
        data = self.coordinator.data
        return {
            "queue": self.queue,
            "possible_outages": data.today_possible_text,
            "outage_intervals": [
                {
                    "start": iv.start.strftime("%H:%M"),
                    "end": iv.end.strftime("%H:%M"),
                    "state": iv.state,
                }
                for iv in data.intervals_today
                if iv.state != "on"
            ],
        }


class PoltavaTomorrowScheduleSensor(PoltavaBaseSensor):
    """Sensor for tomorrow's summary outage schedule."""

    _attr_icon = "mdi:calendar-arrow-right"
    _attr_translation_key = "tomorrow_schedule"

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"poltava_power_{self.queue}_tomorrow_schedule"
        self._attr_name = f"Графік на завтра (Черга {self.queue})"

    @property
    def native_value(self) -> str:
        """Return formatted string with tomorrow's outages."""
        return self.coordinator.data.tomorrow_outages_text

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional schedule attributes."""
        data = self.coordinator.data
        return {
            "queue": self.queue,
            "possible_outages": data.tomorrow_possible_text,
            "outage_intervals": [
                {
                    "start": iv.start.strftime("%H:%M"),
                    "end": iv.end.strftime("%H:%M"),
                    "state": iv.state,
                }
                for iv in data.intervals_tomorrow
                if iv.state != "on"
            ],
        }


class PoltavaLastUpdatedSensor(PoltavaBaseSensor):
    """Sensor indicating when the oblenergo schedule was last updated."""

    _attr_icon = "mdi:update"
    _attr_translation_key = "last_update"

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"poltava_power_{self.queue}_last_update"
        self._attr_name = f"Останнє оновлення графіка (Черга {self.queue})"

    @property
    def native_value(self) -> str:
        """Return oblenergo update string."""
        return (
            self.coordinator.data.last_updated_oblenergo
            or self.coordinator.data.last_updated_raw
            or "Невідомо"
        )
