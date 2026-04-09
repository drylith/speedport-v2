from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from speedport import Speedport, PortForwarding

from .const import DOMAIN
from .device import SpeedportEntity, get_coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up entry."""

    speedport: Speedport = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SpeedportWifiSwitch(hass, speedport),
            SpeedportGuestWifiSwitch(hass, speedport),
            SpeedportOfficeWifiSwitch(hass, speedport),
        ]
    )

    coordinator = get_coordinator(hass, speedport)
    known_pf_ids: set[str] = set()

    @callback
    def _async_handle_port_forwarding_update() -> None:
        current_pfs = {pf.id: pf for pf in coordinator.port_forwardings}
        current_ids = set(current_pfs.keys())

        new_ids = current_ids - known_pf_ids
        if new_ids:
            async_add_entities(
                [SpeedportPortForwardingSwitch(hass, speedport, current_pfs[pf_id]) for pf_id in new_ids]
            )
            known_pf_ids.update(new_ids)

        removed_ids = known_pf_ids - current_ids
        if removed_ids:
            registry = er.async_get(hass)
            for pf_id in removed_ids:
                entity_id = registry.async_get_entity_id(
                    "switch", DOMAIN, f"port_forwarding_{pf_id}"
                )
                if entity_id:
                    registry.async_remove(entity_id)
            known_pf_ids.difference_update(removed_ids)

    entry.async_on_unload(coordinator.async_add_listener(_async_handle_port_forwarding_update))
    _async_handle_port_forwarding_update()


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
    def __init__(self, hass: HomeAssistant, speedport: Speedport, port_forwarding: PortForwarding) -> None:
        super().__init__(hass, speedport)
        self._port_forwarding_id: str = port_forwarding.id
        self._attr_icon = "mdi:transit-connection-variant"
        self._attr_name = f"pfw_{port_forwarding.name}"
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
