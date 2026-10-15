"""DataUpdateCoordinator for Poltava Power Outages integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from typing import Any
import zoneinfo

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import (
    DOMAIN,
    DEFAULT_DATA_URL,
    DEFAULT_QUEUE,
    IMAGE_BASE_URL,
    QUEUE_IMAGE_FILES,
    IMAGE_ALL_TODAY,
    IMAGE_ALL_TOMORROW,
    STATUS_DESCRIPTIONS,
    STATE_POWER_ON,
    STATE_POWER_OFF,
    STATE_MAYBE_OFF,
)

_LOGGER = logging.getLogger(__name__)

KYIV_TIMEZONE_NAME = "Europe/Kyiv"


@dataclass
class PoltavaInterval:
    """Represents a continuous time interval with a given state."""

    start: datetime
    end: datetime
    state: str  # 'on', 'off', 'maybe'
    description: str


@dataclass
class PoltavaData:
    """Parsed outage schedule data for a specific queue."""

    queue: str
    last_updated_raw: str | None = None
    last_updated_oblenergo: str | None = None
    current_state: str = STATE_POWER_ON
    current_state_text: str = "Світло є"
    is_power_on: bool = True
    is_outage: bool = False
    is_maybe_outage: bool = False
    current_slot: str = "00:00 - 01:00"
    current_slot_raw: str = "yes"
    next_outage_start: datetime | None = None
    next_outage_end: datetime | None = None
    next_outage_state: str = "off"
    next_restore: datetime | None = None
    today_outages_text: str = "Немає відключень"
    today_possible_text: str = "Немає"
    tomorrow_outages_text: str = "Немає даних"
    tomorrow_possible_text: str = "Немає даних"
    intervals_today: list[PoltavaInterval] = field(default_factory=list)
    intervals_tomorrow: list[PoltavaInterval] = field(default_factory=list)
    all_outage_intervals: list[PoltavaInterval] = field(default_factory=list)
    hourly_today: dict[int, str] = field(default_factory=dict)
    hourly_tomorrow: dict[int, str] = field(default_factory=dict)
    queue_image_url: str = ""
    all_today_image_url: str = ""
    all_tomorrow_image_url: str = ""


class PoltavaDataUpdateCoordinator(DataUpdateCoordinator[PoltavaData]):
    """Class to manage fetching Poltava Oblenergo outage data."""

    def __init__(
        self,
        hass: HomeAssistant,
        queue: str = DEFAULT_QUEUE,
        update_interval_minutes: int = 5,
        include_possible: bool = False,
        data_url: str = DEFAULT_DATA_URL,
    ) -> None:
        """Initialize the coordinator."""
        self.queue = queue
        self.include_possible = include_possible
        self.data_url = data_url
        self.session = async_get_clientsession(hass)

        try:
            self._tz = zoneinfo.ZoneInfo(KYIV_TIMEZONE_NAME)
        except Exception:
            self._tz = dt_util.get_time_zone(KYIV_TIMEZONE_NAME) or zoneinfo.ZoneInfo("UTC")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{queue}",
            update_interval=timedelta(minutes=update_interval_minutes),
        )

    async def _async_update_data(self) -> PoltavaData:
        """Fetch data from GitHub data mirror."""
        try:
            headers = {
                "User-Agent": "HomeAssistant-PoltavaPower/1.0",
                "Accept": "application/json",
            }
            async with self.session.get(self.data_url, headers=headers, timeout=15) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Error fetching Poltava outage data: HTTP status {response.status}"
                    )
                raw_json = await response.json(content_type=None)
        except Exception as err:
            raise UpdateFailed(f"Failed to communicate with Poltava outage mirror: {err}") from err

        return self._parse_data(raw_json)

    def _parse_data(self, json_data: dict[str, Any]) -> PoltavaData:
        """Parse the raw JSON data for the configured queue."""
        fact = json_data.get("fact", {})
        fact_data = fact.get("data", {})
        last_updated_raw = json_data.get("lastUpdated")
        last_updated_oblenergo = fact.get("update")

        now = dt_util.now(self._tz)
        queue_key = f"GPV{self.queue}"

        # Sort available day timestamps
        day_keys = sorted(fact_data.keys(), key=lambda x: int(x))
        today_ts = str(fact.get("today", ""))

        all_half_hour_slots: list[tuple[datetime, datetime, str]] = []
        today_hourly: dict[int, str] = {}
        tomorrow_hourly: dict[int, str] = {}

        for day_ts_str in day_keys:
            try:
                day_ts = int(day_ts_str)
                day_dt = datetime.fromtimestamp(day_ts, tz=self._tz)
            except Exception:
                continue

            day_queues = fact_data.get(day_ts_str, {})
            queue_hours = day_queues.get(queue_key, {})

            is_today = day_ts_str == today_ts or (
                day_dt.date() == now.date()
            )
            is_tomorrow = day_dt.date() == (now.date() + timedelta(days=1))

            for h in range(1, 25):
                val = queue_hours.get(str(h), "yes")
                if is_today:
                    today_hourly[h] = val
                elif is_tomorrow:
                    tomorrow_hourly[h] = val

                # Determine 30-minute slots based on Poltavaoblenergo definitions
                if val == "no":
                    s1, s2 = "off", "off"
                elif val == "yes":
                    s1, s2 = "on", "on"
                elif val == "first":
                    s1, s2 = "off", "on"
                elif val == "second":
                    s1, s2 = "on", "off"
                elif val == "mfirst":
                    s1, s2 = "maybe", "on"
                elif val == "msecond":
                    s1, s2 = "off", "maybe"
                else:
                    s1, s2 = "on", "on"

                t1 = day_dt + timedelta(hours=h - 1)
                t2 = t1 + timedelta(minutes=30)
                t3 = t1 + timedelta(hours=1)

                all_half_hour_slots.append((t1, t2, s1))
                all_half_hour_slots.append((t2, t3, s2))

        # Merge contiguous slots into intervals
        merged_intervals: list[PoltavaInterval] = []
        if all_half_hour_slots:
            cur_start, cur_end, cur_state = all_half_hour_slots[0]
            for s_start, s_end, state in all_half_hour_slots[1:]:
                if state == cur_state:
                    cur_end = s_end
                else:
                    desc = self._state_to_text(cur_state)
                    merged_intervals.append(
                        PoltavaInterval(start=cur_start, end=cur_end, state=cur_state, description=desc)
                    )
                    cur_start, cur_end, cur_state = s_start, s_end, state
            desc = self._state_to_text(cur_state)
            merged_intervals.append(
                PoltavaInterval(start=cur_start, end=cur_end, state=cur_state, description=desc)
            )

        # Categorize today vs tomorrow intervals
        today_intervals = [
            iv for iv in merged_intervals if iv.start.date() == now.date()
        ]
        tomorrow_intervals = [
            iv for iv in merged_intervals if iv.start.date() == (now.date() + timedelta(days=1))
        ]
        all_outages = [iv for iv in merged_intervals if iv.state in ("off", "maybe")]

        # Determine current interval & status
        cur_interval = None
        for iv in merged_intervals:
            if iv.start <= now < iv.end:
                cur_interval = iv
                break

        outage_check_states = ("off", "maybe") if self.include_possible else ("off",)

        if cur_interval:
            cur_state_type = cur_interval.state
        else:
            cur_state_type = "on"

        is_outage = cur_state_type in outage_check_states
        is_maybe = cur_state_type == "maybe"
        is_power_on = not is_outage

        if cur_state_type == "off":
            current_state = STATE_POWER_OFF
            current_state_text = "Відключення за графіком"
        elif cur_state_type == "maybe":
            current_state = STATE_MAYBE_OFF
            current_state_text = "Можливе відключення"
        else:
            current_state = STATE_POWER_ON
            current_state_text = "Світло є"

        cur_hour = now.hour
        current_slot = f"{cur_hour:02d}:00 - {cur_hour+1:02d}:00"
        current_slot_raw = today_hourly.get(cur_hour + 1, "yes")

        # Calculate next outage & next restore
        next_outage_start: datetime | None = None
        next_outage_end: datetime | None = None
        next_outage_state: str = "off"
        next_restore: datetime | None = None

        if is_outage and cur_interval:
            # Currently off/maybe: restore is end of current consecutive outage block
            restore_candidate = cur_interval.end
            for iv in merged_intervals:
                if iv.start == restore_candidate and iv.state in outage_check_states:
                    restore_candidate = iv.end
            next_restore = restore_candidate

            # Next outage is the first outage that starts after restore
            for iv in merged_intervals:
                if iv.start >= next_restore and iv.state in ("off", "maybe"):
                    next_outage_start = iv.start
                    next_outage_end = iv.end
                    next_outage_state = iv.state
                    break
        else:
            # Currently on: next event is first upcoming outage or possible outage
            for iv in merged_intervals:
                if iv.start > now and iv.state in ("off", "maybe"):
                    next_outage_start = iv.start
                    next_outage_end = iv.end
                    next_outage_state = iv.state
                    next_restore = iv.end
                    break

        # Generate summary texts (clean time ranges matching the official graphic chart)
        today_outages_text = self._format_intervals_summary(
            [iv for iv in today_intervals if iv.state == "off"]
        )
        today_possible_text = self._format_intervals_summary(
            [iv for iv in today_intervals if iv.state == "maybe"]
        )

        tomorrow_outages_text = self._format_intervals_summary(
            [iv for iv in tomorrow_intervals if iv.state == "off"]
        )
        tomorrow_possible_text = self._format_intervals_summary(
            [iv for iv in tomorrow_intervals if iv.state == "maybe"]
        )

        # Image URLs
        img_name = QUEUE_IMAGE_FILES.get(self.queue, f"gpv-{self.queue.replace('.', '-')}-emergency.png")
        queue_image_url = f"{IMAGE_BASE_URL}{img_name}"
        all_today_image_url = f"{IMAGE_BASE_URL}{IMAGE_ALL_TODAY}"
        all_tomorrow_image_url = f"{IMAGE_BASE_URL}{IMAGE_ALL_TOMORROW}"

        return PoltavaData(
            queue=self.queue,
            last_updated_raw=last_updated_raw,
            last_updated_oblenergo=last_updated_oblenergo,
            current_state=current_state,
            current_state_text=current_state_text,
            is_power_on=is_power_on,
            is_outage=is_outage,
            is_maybe_outage=is_maybe,
            current_slot=current_slot,
            current_slot_raw=current_slot_raw,
            next_outage_start=next_outage_start,
            next_outage_end=next_outage_end,
            next_outage_state=next_outage_state,
            next_restore=next_restore,
            today_outages_text=today_outages_text,
            today_possible_text=today_possible_text,
            tomorrow_outages_text=tomorrow_outages_text,
            tomorrow_possible_text=tomorrow_possible_text,
            intervals_today=today_intervals,
            intervals_tomorrow=tomorrow_intervals,
            all_outage_intervals=all_outages,
            hourly_today=today_hourly,
            hourly_tomorrow=tomorrow_hourly,
            queue_image_url=queue_image_url,
            all_today_image_url=all_today_image_url,
            all_tomorrow_image_url=all_tomorrow_image_url,
        )

    def _state_to_text(self, state: str) -> str:
        """Convert interval state code to descriptive text."""
        if state == "off":
            return f"Відключення світла (Черга {self.queue})"
        if state == "maybe":
            return f"Можливе відключення (Черга {self.queue})"
        return f"Світло є (Черга {self.queue})"

    @staticmethod
    def _format_schedule_full(intervals: list[PoltavaInterval]) -> str:
        """Format intervals including guaranteed and possible outages."""
        outage_ivs = [iv for iv in intervals if iv.state in ("off", "maybe")]
        if not outage_ivs:
            return "Немає відключень"

        has_maybe = any(iv.state == "maybe" for iv in outage_ivs)
        parts = []
        for iv in outage_ivs:
            time_str = f"{iv.start.strftime('%H:%M')} - {iv.end.strftime('%H:%M')}"
            if iv.state == "maybe":
                parts.append(f"{time_str} можливе відключення")
            else:
                if has_maybe:
                    parts.append(f"{time_str} відключення")
                else:
                    parts.append(time_str)
        return ", ".join(parts)

    @staticmethod
    def _format_intervals_summary(intervals: list[PoltavaInterval]) -> str:
        """Format a list of intervals into readable time string."""
        if not intervals:
            return "Немає відключень"
        parts = [f"{iv.start.strftime('%H:%M')} - {iv.end.strftime('%H:%M')}" for iv in intervals]
        return ", ".join(parts)
