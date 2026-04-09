"""The Speedport integration."""

import asyncio
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from speedport import Speedport

from .config_flow import OptionsFlowHandler
from .const import DOMAIN
from .device import get_coordinator

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

PLATFORMS_WITH_IP_DEVICES: list[Platform] = PLATFORMS + [Platform.DEVICE_TRACKER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Speedport from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    speedport = await Speedport(
        host=entry.data["host"],
        password=entry.data["password"],
        https=entry.data["https"],
        session=aiohttp_client.async_get_clientsession(hass),
        pause_time=entry.options.get("pause_time", 5),
    ).create()
    hass.data[DOMAIN][entry.entry_id] = speedport
    hass.data[DOMAIN]["coordinators"] = {}
    await asyncio.gather(*[speedport.update_status(), speedport.update_ip_data()])

    entry.async_on_unload(entry.add_update_listener(update_listener))

    platforms = PLATFORMS_WITH_IP_DEVICES if entry.data.get("add_ip_devices", True) else PLATFORMS
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    coordinator = get_coordinator(hass, speedport)
    coordinator.update_interval = timedelta(seconds=entry.options.get("polling_rate", 30))

    return True


async def update_listener(hass, entry):
    """Handle options update."""
    speedport: Speedport = hass.data[DOMAIN][entry.entry_id]
    speedport.set_pause_time(entry.options.get("pause_time", 5))
    coordinator = get_coordinator(hass, speedport)
    coordinator.update_interval = timedelta(seconds=entry.options.get("polling_rate", 30))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    platforms = PLATFORMS_WITH_IP_DEVICES if entry.data.get("add_ip_devices", True) else PLATFORMS
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms):
        speedport = hass.data[DOMAIN].pop(entry.entry_id)
        await speedport.close()

    return unload_ok
