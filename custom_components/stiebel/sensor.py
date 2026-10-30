"""Sensoren des Devices "Stiebel": Health, Skript-Version + Datenpunkte.

Die Werte kommen per Push von der Stiebel-App (AppDaemon, eigene Instanz
appdaemon-stiebel) über die Services set_health / set_value; das
Entity-Polling ist deaktiviert. Health/Version liegen am Hauptgerät,
die Datenpunkte an den Untergeräten je CAN-Member (Konventionen wie
bullitt/ha-stiebel-control).
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNKNOWN, EntityCategory
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    EVENT_REPORT,
    EVENT_VALUE,
    MAIN_DEVICE_ID,
    MAIN_DEVICE_NAME,
    MANUFACTURER,
    MEMBER_DEVICES,
    SIGNALS,
    UNIQUE_ID,
)
from .health_state import STATE_OFFLINE, HealthState

DEVICE_CLASS_MAP: dict[str, SensorDeviceClass] = {
    "temperature": SensorDeviceClass.TEMPERATURE,
    "humidity": SensorDeviceClass.HUMIDITY,
    "pressure": SensorDeviceClass.PRESSURE,
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    "duration": SensorDeviceClass.DURATION,
    "power_factor": SensorDeviceClass.POWER_FACTOR,
}


def main_device_info() -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, MAIN_DEVICE_ID)},
        name=MAIN_DEVICE_NAME,
        manufacturer=MANUFACTURER,
    )


def member_device_info(member: str) -> DeviceInfo:
    device_id, device_name = MEMBER_DEVICES[member]
    return DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer=MANUFACTURER,
        via_device=(DOMAIN, MAIN_DEVICE_ID),
    )


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Erzeugt Health-, Versions- und Datenpunkt-Entities."""
    store: dict[str, Any] = hass.data[DOMAIN]
    entities: list[SensorEntity] = [
        StiebelHealthSensor(store["state"]),
        StiebelVersionSensor(store),
    ]
    for spec in SIGNALS:
        entities.append(StiebelSignalSensor(spec, store))
    async_add_entities(entities)


class StiebelHealthSensor(SensorEntity):
    """Stiebel-Prozess-Status: ok | error | offline (kein frischer Report)."""

    _attr_has_entity_name = True
    _attr_translation_key = "health"
    _attr_unique_id = f"{UNIQUE_ID}_health"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:heart-pulse"
    _attr_should_poll = False

    def __init__(self, state: HealthState) -> None:
        self._state_store = state
        self._attr_native_value = STATE_OFFLINE
        self._attr_extra_state_attributes = {
            "last_report": None,
            "last_report_sent": None,
        }
        self._attr_device_info = main_device_info()

    async def async_added_to_hass(self) -> None:
        # Initialen Zustand (ggf. bereits empfangene Reports) einspielen
        self._handle_report(None)
        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_REPORT, self._handle_report)
        )

    @callback
    def _handle_report(self, _event: Event | None) -> None:
        self._attr_native_value = self._state_store.current()
        report = self._state_store.last_report
        sent_at = self._state_store.last_report_sent_at
        self._attr_extra_state_attributes = {
            # Empfangszeit auf HA (UTC) – Basis der Stale-Erkennung,
            # ISO-String für Templates/Automations
            "last_report": report.isoformat() if report else None,
            # Sendezeit des Reporters (AppDaemon-Server, UTC)
            "last_report_sent": sent_at.isoformat() if sent_at else None,
        }
        self.async_write_ha_state()


class StiebelVersionSensor(SensorEntity):
    """Zentrale Skript-Version des auf dem AppDaemon-Server laufenden Scripts.

    Wird vom Script mit jedem Report gemeldet (Service-Feld `version`);
    bis zum ersten Report "unknown". Die Version wird beim Deploy automatisch
    aus der Commit-Distance abgeleitet (install/derive_version.sh).
    """

    _attr_has_entity_name = True
    _attr_translation_key = "script_version"
    _attr_unique_id = f"{UNIQUE_ID}_script_version"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:tag-text"
    _attr_should_poll = False

    def __init__(self, store: dict[str, Any]) -> None:
        self._store = store
        self._attr_native_value = STATE_UNKNOWN
        self._attr_device_info = main_device_info()

    async def async_added_to_hass(self) -> None:
        # Initialen Wert (ggf. bereits empfangene Version) einspielen
        self._handle_report(None)
        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_REPORT, self._handle_report)
        )

    @callback
    def _handle_report(self, _event: Event | None) -> None:
        version = self._store.get("version")
        self._attr_native_value = version if version is not None else STATE_UNKNOWN
        self.async_write_ha_state()


class StiebelSignalSensor(SensorEntity):
    """Ein Datenpunkt der Wärmepumpe (Anzeigename exakt nach bullitt).

    Der Wert wird per `stiebel.set_value` (Feld `key` = unique_id) gesetzt;
    bis zum ersten Wert bleibt die Entity "unknown".
    """

    _attr_should_poll = False

    def __init__(self, spec: dict[str, str], store: dict[str, Any]) -> None:
        self._spec = spec
        self._store = store
        self._attr_name = spec["name"]
        self._attr_unique_id = spec["key"]
        self._attr_device_info = member_device_info(spec["member"])
        if spec.get("device_class"):
            self._attr_device_class = DEVICE_CLASS_MAP[spec["device_class"]]
        if spec.get("unit"):
            self._attr_native_unit_of_measurement = spec["unit"]
        if spec.get("state_class"):
            self._attr_state_class = spec["state_class"]
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
        if value is not None:
            self._attr_native_value = value
            self.async_write_ha_state()
