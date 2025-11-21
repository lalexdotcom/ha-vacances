"""Calendar platform for a Local Calendar."""

from __future__ import annotations

from datetime import datetime
import logging

from config.custom_components.vacances import VacancesCoordinator
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

PRODID = "-//homeassistant.io//local_calendar 1.0//EN"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the local calendar platform."""
    coordinator = config_entry.runtime_data

    name = f"Vacances {config_entry.data['zone']}"
    entity = VacancesCalendarEntity(coordinator, name, unique_id=config_entry.entry_id)
    async_add_entities([entity], True)


class VacancesCalendarEntity(CoordinatorEntity[VacancesCoordinator], CalendarEntity):
    """A calendar entity backed by a local iCalendar file."""

    _attr_has_entity_name = True
    _attr_supported_features = None

    def __init__(
        self,
        coordinator: VacancesCoordinator,
        name: str,
        unique_id: str,
    ) -> None:
        """Initialize LocalCalendarEntity."""

        super().__init__(coordinator)
        self._event: CalendarEvent | None = None
        self._attr_name = name
        self._attr_unique_id = f"vacances_{unique_id}"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.info("Update from coordinator: %s", self.coordinator.data)
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the entity."""

        def next_event() -> CalendarEvent | None:
            now = dt_util.now()
            events = (
                event
                for event in (
                    self.coordinator.data["holidays"]
                    if self.coordinator.data is not None
                    else []
                )
                if event["end"] >= now
            )
            if event := next(events, None):
                return CalendarEvent(
                    start=event["start"],
                    end=event["end"],
                    summary=f"{event['summary']} - {self.coordinator.zone}",
                    uid=event["uid"],
                )
            return None

        self._event = await self.hass.async_add_executor_job(next_event)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get events in a specific date range."""
        events: list[CalendarEvent] = []
        for event in self.coordinator.data["holidays"]:
            event_start: datetime = event["start"]
            event_end: datetime = event["end"]

            if event_end >= start_date and event_start <= end_date:
                events.append(
                    CalendarEvent(
                        summary=f"{event['summary']} - {self.coordinator.zone}",
                        start=event_start,
                        end=event_end,
                        uid=event["uid"],
                    )
                )

        _LOGGER.info("Found %d events", len(events))
        return events
