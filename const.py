"""Constants for the vacances integration."""

from homeassistant.const import Platform

DOMAIN = "vacances"
PLATFORMS: list[Platform] = [Platform.CALENDAR]
DEVICE_MANUFACTURER = "LALEX"

STORAGE_PATH = ".storage/vacances.{key}.ics"
