from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from speedport import Speedport

from .const import DOMAIN
from .device import SpeedportEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up entry."""

    speedport: Speedport = hass.data[DOMAIN][entry.entry_id]
    entities: list = [
        SpeedportWifiSwitch(hass, speedport),
        SpeedportGuestWifiSwitch(hass, speedport),
        SpeedportOfficeWifiSwitch(hass, speedport),
    ]

    try:
        port_forwardings = await speedport.port_forwardings
        for pf in port_forwardings:
            entities.append(SpeedportPortForwardingSwitch(hass, speedport, pf))
    except Exception:
        _LOGGER.warning("Failed to fetch port forwardings", exc_info=True)

    async_add_entities(entities)


class SpeedportWifiSwitch(SwitchEntity, SpeedportEntity):
    _attr_is_on: bool | None = False

    def __init__(self, hass: HomeAssistant, speedport: Speedport) -> None:
        super().__init__(hass, speedport)
        self._speedport: Speedport = speedport
        self._attr_icon = "mdi:wifi"
        self._attr_name = f"WLAN {speedport.wlan_ssid}"
        self._attr_unique_id = "wifi"

    @property
    def is_on(self) -> bool | None:
        return self._speedport.wlan_active

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on switch."""
        await self._speedport.wifi_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off switch."""
        await self._speedport.wifi_off()


class SpeedportGuestWifiSwitch(SwitchEntity, SpeedportEntity):
    _attr_is_on: bool | None = False

    def __init__(self, hass: HomeAssistant, speedport: Speedport) -> None:
        super().__init__(hass, speedport)
        self._speedport: Speedport = speedport
        self._attr_icon = "mdi:wifi"
        self._attr_name = f"WLAN {speedport.wlan_guest_ssid}"
        self._attr_unique_id = "wifi_guest"

    @property
    def is_on(self) -> bool | None:
        return self._speedport.wlan_guest_active

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on switch."""
        await self._speedport.wifi_guest_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off switch."""
        await self._speedport.wifi_guest_off()


class SpeedportOfficeWifiSwitch(SwitchEntity, SpeedportEntity):
    _attr_is_on: bool | None = False

    def __init__(self, hass: HomeAssistant, speedport: Speedport) -> None:
        super().__init__(hass, speedport)
        self._speedport: Speedport = speedport
        self._attr_icon = "mdi:wifi"
        self._attr_name = f"WLAN {speedport.wlan_office_ssid}"
        self._attr_unique_id = "wifi_office"

    @property
    def is_on(self) -> bool | None:
        return self._speedport.wlan_office_ssid

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on switch."""
        await self._speedport.wifi_office_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off switch."""
        await self._speedport.wifi_office_off()


class SpeedportPortForwardingSwitch(SwitchEntity, SpeedportEntity):
    def __init__(self, hass: HomeAssistant, speedport: Speedport, port_forwarding) -> None:
        super().__init__(hass, speedport)
        self._port_forwarding_id: str = port_forwarding.id
        self._attr_icon = "mdi:transit-connection-variant"
        self._attr_name = f"Port Forwarding {port_forwarding.name}"
        self._attr_unique_id = f"port_forwarding_{port_forwarding.id}"

    @property
    def is_on(self) -> bool | None:
        for pf in self._coordinator.port_forwardings:
            if pf.id == self._port_forwarding_id:
                return pf.active
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on switch."""
        await self._speedport.set_port_forwarding(self._port_forwarding_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off switch."""
        await self._speedport.set_port_forwarding(self._port_forwarding_id, False)
