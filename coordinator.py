"""Example integration using DataUpdateCoordinator."""

from datetime import datetime, timedelta
import logging
import urllib.parse

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify
from homeassistant.util.dt import parse_datetime

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


# async def async_setup_entry(
#     hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
# ):
#     """Config entry example."""
#     _LOGGER.info("Setting up vacances coordinator for entry: %s", config_entry)
#     coordinator = VacancesCoordinator(hass, config_entry)

#     await coordinator.async_config_entry_first_refresh()

#     async_add_entities(
#         [
#             VacanceBinarySensor(coordinator, config_entry),
#             VacanceSensor(coordinator, config_entry),
#         ]
#     )


class VacancesCoordinator(DataUpdateCoordinator):
    """Vacances Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize vacances coordinator."""
        _LOGGER.info("Initializing VacancesCoordinator for zone: %s", config_entry.data)
        super().__init__(
            hass,
            _LOGGER,
            name="Vacances Data Coordinator",
            update_interval=timedelta(days=60),  # Update every 30 days
            always_update=True,
        )
        self.zone = config_entry.data["zone"]
        self.uid = config_entry.unique_id

    async def _async_update_data(self):
        """Fetch data from vacances API.

        This is where you would implement the logic to fetch data
        from the vacances API.
        """

        # Placeholder logic; replace with actual API call

        today = datetime.now().date()

        # https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=end_date%20%3E%3D%20date%272025-11-20%27%20and%20end_date%20%3E%20start_date&group_by=description%2Czones%2Cstart_date%2Cend_date%2Cannee_scolaire&order_by=start_date%2Clocation&limit=20&refine=zones%3A%22Zone%20A%22&refine=population%3A%22%C3%89l%C3%A8ves%22&refine=population%3A%22-%22
        url = f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?limit=100&refine={urllib.parse.quote(f'zones:"{self.zone}"')}&where={urllib.parse.quote(f"end_date >= date'{today}' and end_date > start_date")}&timezone={urllib.parse.quote('Europe/Paris')}&refine={urllib.parse.quote(f'population:"-"')}&refine={urllib.parse.quote(f'population:"Élèves"')}&order_by={urllib.parse.quote('start_date,location')}&group_by={urllib.parse.quote('start_date,end_date,description,zones,annee_scolaire')}"

        result = {"holidays": []}

        async with (
            aiohttp.ClientSession() as session,
            session.get(url) as response,
        ):
            data = await response.json()

            result = {
                "holidays": [
                    {
                        "summary": period["description"],
                        "start": parse_datetime(period["start_date"]),
                        "end": parse_datetime(period["end_date"]),
                        "uid": f"{self.uid}-{slugify(period['description'])}-{period['annee_scolaire']}",
                    }
                    for period in data["results"]
                ]
            }

            _LOGGER.info(
                "VacancesCoordinator data for %s from %s is %s", self.zone, url, result
            )

            return result

            # is_holiday = data["total_count"] > 0
            # holiday_name = (
            #     data["results"][0]["description"] if is_holiday else "Écoles ouvertes"
            # )
