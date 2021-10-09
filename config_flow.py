"""Config flow for Cisco Business Dashboard integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import ciscobusinessdashboard

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client
from aiohttp import ClientResponseError, ClientConnectorError

from .const import (
    DOMAIN,
    CONF_SECRET,
    CONF_PORT,
    CONF_KEYID,
    CONF_DASHBOARD,
    CONF_ORGANISATION,
)


_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DASHBOARD): str,
        vol.Optional(CONF_PORT, default="443"): str,
        vol.Optional(CONF_KEYID): str,
        vol.Optional(CONF_SECRET): str,
        vol.Optional(CONF_ORGANISATION, default="Default"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    dashboard = data[CONF_DASHBOARD]
    port = data[CONF_PORT]
    keyid = data.get(CONF_KEYID)
    secret = data.get(CONF_SECRET)
    clientid = None
    appname = data[CONF_DASHBOARD]

    _LOGGER.debug("Connecting to %s:%s over HTTPS", dashboard, port)
    token = ciscobusinessdashboard.getToken(keyid, secret, clientid, appname)

    resp = await aiohttp_client.async_get_clientsession(hass).get(
        "https://%s:%s/api/v2/orgs" % (dashboard, port),
        headers={"Authorization": "Bearer %s" % token},
    )

    # Return info that you want to store in the config entry.
    return resp


class CiscoBDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jochem Ex."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(user_input.get(CONF_DASHBOARD))
            self._abort_if_unique_id_configured()

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except ClientResponseError:
            errors["base"] = "cannot_connect"
        except ClientConnectorError:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            if info.status == 200:
                return self.async_create_entry(
                    title=user_input[CONF_DASHBOARD], data=user_input
                )
            if info.status == 401:
                _LOGGER.warning("401")
                errors["base"] = "unauthorized"
            if info.status == 404:
                _LOGGER.warning("404")
                errors["base"] = "wronghost"

        _LOGGER.warning(info)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
