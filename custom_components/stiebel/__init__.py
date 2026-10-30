"""Stiebel – Device "Stiebel" mit Health- und Skript-Versions-Entity.

Die Entities werden von der App auf dem eigenen AppDaemon-Server
(appdaemon-stiebel) per Service gesetzt:
- stiebel.set_health: Health (mit Stale-Check, ohne frischen Report
  "offline") und die zentrale Skript-Version des Reporters.
- stiebel.set_value: Datenpunkte der Wärmepumpe (key = unique_id der
  Sensor-Entity, value = Anzeigewert).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import event as ha_event
from homeassistant.util import dt as dt_util

from .const import (
    CONF_STALE_TIMEOUT,
    DEFAULT_STALE_TIMEOUT,
    DOMAIN,
    EVENT_REPORT,
    EVENT_VALUE,
    PLATFORMS,
    SERVICE_SET_HEALTH,
    SERVICE_SET_VALUE,
    STALE_CHECK_INTERVAL,
    VALID_STATES,
)
from .health_state import HealthState


def _validate_timestamp(value: Any) -> str:
    """Validiert einen ISO-8601-Zeitstempel (z. B. vom AppDaemon-Server)."""
    if not isinstance(value, str):
        raise vol.Invalid("timestamp muss eine ISO-8601-String sein")
    try:
        datetime.fromisoformat(value)
    except ValueError as err:
        raise vol.Invalid(f"Ungültiger ISO-8601-Zeitstempel: {value!r}") from err
    return value


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Integration wird nur per Config-Entry eingerichtet (UI)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Registriert set_health/set_value und den Stale-Check."""
    state = HealthState(
        timedelta(minutes=entry.data.get(CONF_STALE_TIMEOUT, DEFAULT_STALE_TIMEOUT))
    )
    # "version" = zentrale Skript-Version des Reporters (AppDaemon-Server);
    # wird mit jedem Report aktualisiert und in der Text-Entity angezeigt.
    # "values" = letzte per set_value gemeldete Datenpunkte (key -> Wert).
    store: dict[str, Any] = {
        "state": state,
        "version": None,
        "values": {},
    }
    hass.data[DOMAIN] = store

    async def _handle_set_health(call: ServiceCall) -> None:
        sent_at: datetime | None = None
        if (raw := call.data.get("timestamp")) is not None:
            # Vom Schema bereits validiert (ISO-8601)
            sent_at = datetime.fromisoformat(raw)
        if (version := call.data.get("version")) is not None:
            store["version"] = version
        state.set(call.data["state"], sent_at)
        hass.bus.async_fire(EVENT_REPORT)

    async def _handle_set_value(call: ServiceCall) -> None:
        store["values"][call.data["key"]] = call.data["value"]
        hass.bus.async_fire(EVENT_VALUE)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_HEALTH,
        _handle_set_health,
        schema=vol.Schema(
            {
                vol.Required("state"): vol.In(list(VALID_STATES)),
                vol.Optional("timestamp"): _validate_timestamp,
                vol.Optional("version"): cv.string,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_VALUE,
        _handle_set_value,
        schema=vol.Schema(
            {
                vol.Required("key"): cv.string,
                vol.Required("value"): vol.Any(str, int, float),
            }
        ),
    )

    # Stale-Check: stellt die Entity ohne frischen Report auf "offline" um
    last_published: str | None = None

    # HA ruft die Action mit Local-Time auf; für die Terminierung
    # (point_in_time erwartet UTC) immer fresh UTC-Now verwenden
    async def _check_stale(now: datetime) -> None:
        nonlocal last_published
        current = state.current()
        if current != last_published:
            last_published = current
            hass.bus.async_fire(EVENT_REPORT)
        store["unsub_stale"] = ha_event.async_track_point_in_time(
            hass,
            _check_stale,
            dt_util.utcnow() + timedelta(seconds=STALE_CHECK_INTERVAL),
        )

    store["unsub_stale"] = ha_event.async_track_point_in_time(
        hass, _check_stale, dt_util.utcnow() + timedelta(seconds=STALE_CHECK_INTERVAL)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entfernt Plattformen, Stale-Check und die Services."""
    store = hass.data.get(DOMAIN)
    if store and store.get("unsub_stale"):
        store["unsub_stale"]()
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.pop(DOMAIN, None)
        hass.services.async_remove(DOMAIN, SERVICE_SET_HEALTH)
        hass.services.async_remove(DOMAIN, SERVICE_SET_VALUE)
    return unloaded
