# Speedport Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/hacs-Default-41BDF5.svg)](https://hacs.xyz)
[![GitHub](https://img.shields.io/github/license/drylith/speedport-v2?color=red)](https://github.com/drylith/speedport-v2/blob/main/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/drylith/speedport-v2?color=green&label=release)](https://github.com/drylith/speedport-v2/releases/latest)
[![GitHub pre-release](https://img.shields.io/github/v/release/drylith/speedport-v2?include_prereleases&color=orange&label=pre-release)](https://github.com/drylith/speedport-v2/releases)

Telekom Speedport Integration for Home Assistant based
on [speedport-api](https://github.com/drylith/speedport-api-v2.git).

## Features

- Track presence of connected devices
- Turn on/off wifi (guest/office/normal)
- Reconnect, reboot, wps on
- Sensors (IP-Addresses, Upload/Download, Connection, ...)
- PortForwarding (dynamicly list pfw entities; set active state)

## Supported devices

- Speedport Smart 4

## Installation

**Method 1:** [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=drylith&repository=speedport&category=integration)

**Method 2:** [HACS](https://hacs.xyz/) > Integrations > Add Integration > **Speedport** > Install

**Method 3:** Manually copy `speedport` folder from [latest release](https://github.com/drylith/speedport/releases/latest) to `config/custom_components` folder.

_Restart Home Assistant_

## Configuration

**Method 1**: [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=speedport)

**Method 2**: Settings > Devices & Services > Add Integration > **Speedport**  
_If the integration is not in the list, you need to clear the browser cache._
