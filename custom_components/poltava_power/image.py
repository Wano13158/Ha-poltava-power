"""Image platform for Poltava Power Outages integration."""
from __future__ import annotations

import logging
from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import ATTRIBUTION, DOMAIN
from .coordinator import PoltavaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Poltava Power image entities."""
    coordinator: PoltavaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            PoltavaQueueScheduleImage(coordinator, hass),
            PoltavaSummaryTodayImage(coordinator, hass),
            PoltavaSummaryTomorrowImage(coordinator, hass),
        ]
    )


class PoltavaBaseImage(
    CoordinatorEntity[PoltavaDataUpdateCoordinator], ImageEntity
):
    """Base image entity for Poltava outage schedules."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self, coordinator: PoltavaDataUpdateCoordinator, hass: HomeAssistant
    ) -> None:
        """Initialize the base image entity."""
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self, hass)
        self.queue = coordinator.queue
        self._image_bytes: bytes | None = None
        self._attr_image_last_updated = dt_util.utcnow()

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
    def image_url(self) -> str:
        """Return the URL of the image."""
        raise NotImplementedError

    async def async_image(self) -> bytes | None:
        """Fetch and return image bytes asynchronously."""
        url = self.image_url
        if not url:
            return None

        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    self._image_bytes = await response.read()
                    self._attr_image_last_updated = dt_util.utcnow()
                    return self._image_bytes
                _LOGGER.warning(
                    "Failed to fetch schedule image %s (HTTP %s)", url, response.status
                )
        except Exception as err:
            _LOGGER.warning("Error fetching schedule image %s: %s", url, err)

        return self._image_bytes


class PoltavaQueueScheduleImage(PoltavaBaseImage):
    """Image entity for the specific queue schedule."""

    _attr_translation_key = "queue_schedule_image"

    def __init__(
        self, coordinator: PoltavaDataUpdateCoordinator, hass: HomeAssistant
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, hass)
        self._attr_unique_id = f"poltava_power_{self.queue}_image_queue"
        self._attr_name = f"Графік відключень (Черга {self.queue})"

    @property
    def image_url(self) -> str:
        """Return the URL for the queue schedule image."""
        return self.coordinator.data.queue_image_url


class PoltavaSummaryTodayImage(PoltavaBaseImage):
    """Image entity for the summary schedule of all queues today."""

    _attr_translation_key = "summary_today_image"

    def __init__(
        self, coordinator: PoltavaDataUpdateCoordinator, hass: HomeAssistant
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, hass)
        self._attr_unique_id = f"poltava_power_{self.queue}_image_today"
        self._attr_name = f"Загальний графік на сьогодні (Черга {self.queue})"

    @property
    def image_url(self) -> str:
        """Return the URL for all queues today."""
        return self.coordinator.data.all_today_image_url


class PoltavaSummaryTomorrowImage(PoltavaBaseImage):
    """Image entity for the summary schedule of all queues tomorrow."""

    _attr_translation_key = "summary_tomorrow_image"

    def __init__(
        self, coordinator: PoltavaDataUpdateCoordinator, hass: HomeAssistant
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, hass)
        self._attr_unique_id = f"poltava_power_{self.queue}_image_tomorrow"
        self._attr_name = f"Загальний графік на завтра (Черга {self.queue})"

    @property
    def image_url(self) -> str:
        """Return the URL for all queues tomorrow."""
        return self.coordinator.data.all_tomorrow_image_url
