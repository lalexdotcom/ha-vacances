"""Config flow for the vacances integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import selector
from homeassistant.util import slugify

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("zone"): selector(
            {"select": {"options": ["Zone A", "Zone B", "Zone C"], "mode": "dropdown"}}
        ),
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


# async def get_zones() -> list[str]:
#     """Fetch the available zones from the education API."""
#     async with (
#         aiohttp.ClientSession() as session,
#         session.get(
#             "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?group_by=zones&order_by=zones&limit=100"
#         ) as response,
#     ):
#         return sorted(
#             [x["zones"] for x in (await response.json())["results"]],
#             key=lambda s: "1" if s.startswith("Zone") else "2",
#         )


# async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
#     """Validate the user input allows us to connect.

#     Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
#     """
#     # TODO validate the data can be used to set up a connection.

#     # If your PyPI package is not built with async, pass your methods
#     # to the executor:
#     # await hass.async_add_executor_job(
#     #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
#     # )

#     hub = PlaceholderHub(data[CONF_HOST])

#     if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
#         raise InvalidAuth

#     # If you cannot connect:
#     # throw CannotConnect
#     # If the authentication is wrong:
#     # InvalidAuth

#     # Return info that you want to store in the config entry.
#     return {"title": "Name of the device"}


class VacancesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for vacances."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(slugify(user_input["zone"]))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Vacances {user_input['zone']}",
                data={"zone": user_input["zone"]},
            )

        async with (
            aiohttp.ClientSession() as session,
            session.get(
                "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?group_by=zones&order_by=zones&limit=100"
            ) as response,
        ):
            zones = sorted(
                [x["zones"] for x in (await response.json())["results"]],
                key=lambda s: "1" if s.startswith("Zone") else "2",
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("zone"): selector(
                        {
                            "select": {
                                "options": zones,
                                "mode": "dropdown",
                            }
                        }
                    ),
                }
            ),
            errors=errors,
        )
