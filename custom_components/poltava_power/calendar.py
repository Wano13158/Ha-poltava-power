"""Calendar platform for Poltava Power Outages integration."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import ATTRIBUTION, DOMAIN
from .coordinator import PoltavaDataUpdateCoordinator, PoltavaInterval


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Poltava Power calendar entity."""
    coordinator: PoltavaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PoltavaCalendarEntity(coordinator)])


class PoltavaCalendarEntity(
    CoordinatorEntity[PoltavaDataUpdateCoordinator], CalendarEntity
):
    """Calendar entity displaying scheduled power outages."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_translation_key = "calendar"

    def __init__(self, coordinator: PoltavaDataUpdateCoordinator) -> None:
        """Initialize the calendar entity."""
        super().__init__(coordinator)
        self.queue = coordinator.queue
        self._attr_unique_id = f"poltava_power_{self.queue}_calendar"
        self._attr_name = f"Календар відключень (Черга {self.queue})"

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

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next or current upcoming calendar event."""
        now = dt_util.now()
        intervals = self.coordinator.data.all_outage_intervals

        # Check if currently inside an outage event
        for iv in intervals:
            if iv.start <= now < iv.end:
                return self._create_calendar_event(iv)

        # Otherwise find next upcoming outage event
        for iv in intervals:
            if iv.start > now:
                return self._create_calendar_event(iv)

        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events in the requested date range."""
        events: list[CalendarEvent] = []
        intervals = self.coordinator.data.all_outage_intervals

        for iv in intervals:
            # Overlap check
            if iv.end > start_date and iv.start < end_date:
                events.append(self._create_calendar_event(iv))

        return events

    def _create_calendar_event(self, iv: PoltavaInterval) -> CalendarEvent:
        """Convert a PoltavaInterval into a Home Assistant CalendarEvent."""
        if iv.state == "off":
            prefix = "🔴 Відключення"
        elif iv.state == "maybe":
            prefix = "🟡 Можливе відключення"
        else:
            prefix = "🟢 Світло є"

        summary = f"{prefix} (Черга {self.queue})"
        desc = (
            f"Полтаваобленерго ГПВ: {summary}.\n"
            f"Період: {iv.start.strftime('%H:%M')} — {iv.end.strftime('%H:%M')} "
            f"({iv.start.strftime('%d.%m.%Y')})"
        )

        return CalendarEvent(
            start=iv.start,
            end=iv.end,
            summary=summary,
            description=desc,
            location=f"Полтавська обл., Черга {self.queue}",
        )
