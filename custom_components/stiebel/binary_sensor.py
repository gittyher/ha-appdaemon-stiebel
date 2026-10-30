"""Binäre Sensoren des Devices "Stiebel" (Bool-Datenpunkte der Wärmepumpe).

Werden per `stiebel.set_value` (key = unique_id, value "on"/"off") gesetzt.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_SIGNALS, DOMAIN, EVENT_VALUE
from .sensor import member_device_info

DEVICE_CLASS_MAP: dict[str, BinarySensorDeviceClass] = {
    "lock": BinarySensorDeviceClass.LOCK,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Erzeugt die binären Datenpunkt-Entities."""
    store: dict[str, Any] = hass.data[DOMAIN]
    async_add_entities(StiebelBinarySensor(spec, store) for spec in BINARY_SIGNALS)


class StiebelBinarySensor(BinarySensorEntity):
    """Ein Bool-Datenpunkt (on/off); bis zum ersten Wert "unknown"."""

    _attr_should_poll = False

    def __init__(self, spec: dict[str, str], store: dict[str, Any]) -> None:
        self._spec = spec
        self._store = store
        self._attr_name = spec["name"]
        self._attr_unique_id = spec["key"]
        self._attr_device_info = member_device_info(spec["member"])
        if spec.get("device_class"):
            self._attr_device_class = DEVICE_CLASS_MAP[spec["device_class"]]
        if spec.get("icon"):
            self._attr_icon = spec["icon"]

    async def async_added_to_hass(self) -> None:
        self._handle_value(None)
        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_VALUE, self._handle_value)
        )

    @callback
    def _handle_value(self, _event: Event | None) -> None:
        value = self._store["values"].get(self._spec["key"])
        if value in ("on", "off"):
            self._attr_is_on = value == "on"
            self.async_write_ha_state()
