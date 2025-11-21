"""The vacances integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from config.custom_components.vacances.binary_sensor import VacanceBinarySensor
from config.custom_components.vacances.coordinator import VacancesCoordinator
from config.custom_components.vacances.sensor import VacanceSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, STORAGE_PATH

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations

# type New_NameConfigEntry = ConfigEntry[MyApi]  # noqa: F821
_LOGGER = logging.getLogger(__name__)

ZONES = []


async def async_setup(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up the vacances component."""
    _LOGGER.info(
        "Initializing %s integration with plaforms: %s with config: %s",
        DOMAIN,
        PLATFORMS,
        config,
    )
    return True


@dataclass
class VacancesData:
    """Adguard data type."""

    zone: str


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up vacances from a config entry."""

    _LOGGER.info(
        "Setting up vacances entry: %s (%s)", config_entry.title, config_entry.data
    )

    coordinator = VacancesCoordinator(hass, config_entry)
    config_entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    await coordinator.async_refresh()

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
