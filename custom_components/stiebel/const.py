"""Konstanten für die stiebel-Integration."""

from homeassistant.const import Platform

from .health_state import STATE_ERROR, STATE_OK

CONF_STALE_TIMEOUT = "stale_timeout"  # Minuten ohne Report -> "offline"

DOMAIN = "stiebel"
NAME = "Stiebel"

UNIQUE_ID = "stiebel"
DEFAULT_STALE_TIMEOUT = 5  # Minuten
STALE_CHECK_INTERVAL = 60  # Sekunden

SERVICE_SET_HEALTH = "set_health"
EVENT_REPORT = f"{DOMAIN}_report"
VALID_STATES = (STATE_OK, STATE_ERROR)

PLATFORMS = [Platform.SENSOR]
