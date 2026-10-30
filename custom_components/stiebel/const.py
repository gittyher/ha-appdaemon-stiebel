"""Konstanten für die stiebel-Integration.

Hinweis: `ruff: noqa: E501` – die Signaltabelle unten ist eine kompakte
Datendatei; Zeilenlängen sind dort bewusst länger als 100 Zeichen.
"""

# ruff: noqa: E501

from homeassistant.const import Platform

from .health_state import STATE_ERROR, STATE_OK

CONF_STALE_TIMEOUT = "stale_timeout"  # Minuten ohne Report -> "offline"

DOMAIN = "stiebel"
NAME = "Stiebel"

UNIQUE_ID = "stiebel"
DEFAULT_STALE_TIMEOUT = 5  # Minuten
STALE_CHECK_INTERVAL = 60  # Sekunden

SERVICE_SET_HEALTH = "set_health"
SERVICE_SET_VALUE = "set_value"
EVENT_REPORT = f"{DOMAIN}_report"
EVENT_VALUE = f"{DOMAIN}_value_report"
VALID_STATES = (STATE_OK, STATE_ERROR)

# Gerätestruktur (Konventionen wie bullitt/ha-stiebel-control):
# Hauptgerät + Untergeräte je CAN-Member (via via_device).
MAIN_DEVICE_ID = "stiebel_eltron_wpl13e"
MAIN_DEVICE_NAME = "Stiebel Eltron Wärmepumpe"
MANUFACTURER = "Stiebel Eltron"

# Member -> (Geräte-ID, Anzeigename des Untergeräts)
MEMBER_DEVICES: dict[str, tuple[str, str]] = {
    "KESSEL": ("stiebel_KESSEL", "Kessel"),
    "MANAGER": ("stiebel_MANAGER", "Manager"),
    "HEIZMODUL": ("stiebel_HEIZMODUL", "Heizmodul"),
    "BEDIENMODUL_2": ("stiebel_BEDIENMODUL_2", "Bedienmodul 2"),
}

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

# ---------------------------------------------------------------------------
# Datenpunkte (WPL 13 E, nur Lesen).
# `key` = HA-unique_id (`stiebel_<member>_<signal>`); `name` = Anzeigename
# (bullitt lang_base.h). Muss mit `apps/stiebel/signals.py` synchron bleiben
# (dort Index/Typ/Frequenz).
# ---------------------------------------------------------------------------
_SIGNAL_SPECS: list[tuple[str, str, str, str, str, str, str, str]] = [
    # key, name, member, component, device_class, unit, state_class, icon
    # --- Temperaturen (et_dec_val) ---
    ("stiebel_kessel_kesselsolltemp", "Kessel Soll Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_kessel_speichersolltemp", "Speicher Soll Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_kessel_vorlaufsolltemp", "Vorlauf Soll Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_manager_raumsolltemp_i", "Raum Soll Temperatur I", "MANAGER", "sensor", "temperature", "°C", "measurement", "mdi:home-thermometer"),
    ("stiebel_manager_raumsolltemp_ii", "Raum Soll Temperatur II", "MANAGER", "sensor", "temperature", "°C", "measurement", "mdi:home-thermometer"),
    ("stiebel_manager_raumsolltemp_iii", "Raum Soll Temperatur III", "MANAGER", "sensor", "temperature", "°C", "measurement", "mdi:home-thermometer"),
    ("stiebel_manager_raumsolltemp_nacht", "Raum Soll Temperatur Nacht", "MANAGER", "sensor", "temperature", "°C", "measurement", "mdi:home-thermometer-outline"),
    ("stiebel_kessel_aussentemp", "Außen Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_kessel_sammleristtemp", "Sammler Ist Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_kessel_speicheristtemp", "Speicher Ist Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_kessel_vorlaufisttemp", "Vorlauf Ist Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_bedienmodul_2_raumisttemp", "Raum Ist Temperatur", "BEDIENMODUL_2", "sensor", "temperature", "°C", "measurement", "mdi:home-thermometer"),
    ("stiebel_bedienmodul_2_verstellte_raumsolltemp", "Verstellte Raum Soll Temperatur", "BEDIENMODUL_2", "sensor", "temperature", "°C", "measurement", "mdi:home-thermometer"),
    ("stiebel_kessel_einstell_speichersolltemp", "Einstellung Speicher Soll Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-high"),
    ("stiebel_kessel_ruecklaufisttemp", "Rücklauf Ist Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_kessel_wpvorlaufist", "Wärmepumpe Vorlauf Ist Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-lines"),
    ("stiebel_kessel_hilfskesselsoll", "Hilfskessel Soll Temperatur", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-high"),
    ("stiebel_kessel_einstell_speichersolltemp2", "Einstellung Speicher Soll Temperatur 2", "KESSEL", "sensor", "temperature", "°C", "measurement", "mdi:thermometer-low"),
    # --- Feuchte ---
    ("stiebel_bedienmodul_2_feuchte", "Feuchte", "BEDIENMODUL_2", "sensor", "humidity", "%", "measurement", "mdi:water-percent"),
    # --- Drücke (Kältemittel) ---
    ("stiebel_heizmodul_anzeige_hochdruck", "Anzeige Hochdruck", "HEIZMODUL", "sensor", "pressure", "bar", "measurement", "mdi:gauge"),
    ("stiebel_heizmodul_anzeige_niederdruck", "Anzeige Niederdruck", "HEIZMODUL", "sensor", "pressure", "bar", "measurement", "mdi:gauge"),
    # --- Leistung ---
    ("stiebel_heizmodul_verdichter", "Verdichter", "HEIZMODUL", "sensor", "power", "W", "measurement", "mdi:lightning-bolt"),
    # --- Laufzeiten (et_mil_val -> h) ---
    ("stiebel_heizmodul_lz_verd_1_heizbetrieb", "Laufzeit Verdichter 1 Heizbetrieb", "HEIZMODUL", "sensor", "duration", "h", "total_increasing", "mdi:timer"),
    ("stiebel_heizmodul_lz_verd_2_heizbetrieb", "Laufzeit Verdichter 2 Heizbetrieb", "HEIZMODUL", "sensor", "duration", "h", "total_increasing", "mdi:timer"),
    ("stiebel_heizmodul_lz_verd_1_2_heizbetrieb", "Laufzeit Verdichter 1+2 Heizbetrieb", "HEIZMODUL", "sensor", "duration", "h", "total_increasing", "mdi:timer"),
    ("stiebel_heizmodul_lz_verd_1_kuehlbetrieb", "Laufzeit Verdichter 1 Kühlbetrieb", "HEIZMODUL", "sensor", "duration", "h", "total_increasing", "mdi:timer"),
    ("stiebel_heizmodul_lz_verd_2_kuehlbetrieb", "Laufzeit Verdichter 2 Kühlbetrieb", "HEIZMODUL", "sensor", "duration", "h", "total_increasing", "mdi:timer"),
    ("stiebel_heizmodul_lz_verd_1_2_kuehlbetrieb", "Laufzeit Verdichter 1+2 Kühlbetrieb", "HEIZMODUL", "sensor", "duration", "h", "total_increasing", "mdi:timer"),
    # --- Elektrische Aufnahmeleistung (Zähler) ---
    ("stiebel_heizmodul_el_aufnahmeleistung_ww_tag_wh", "Elektrisch Aufnahmeleistung Warmwasser Tag Wh", "HEIZMODUL", "sensor", "energy", "Wh", "total_increasing", "mdi:flash"),
    ("stiebel_heizmodul_el_aufnahmeleistung_ww_tag_kwh", "Elektrisch Aufnahmeleistung Warmwasser Tag kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:flash"),
    ("stiebel_heizmodul_el_aufnahmeleistung_ww_sum_kwh", "Elektrisch Aufnahmeleistung Warmwasser Summe kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:flash"),
    ("stiebel_heizmodul_el_aufnahmeleistung_ww_sum_mwh", "Elektrisch Aufnahmeleistung Warmwasser Summe MWh", "HEIZMODUL", "sensor", "energy", "MWh", "total_increasing", "mdi:flash"),
    ("stiebel_heizmodul_el_aufnahmeleistung_heiz_tag_wh", "Elektrisch Aufnahmeleistung Heizung Tag Wh", "HEIZMODUL", "sensor", "energy", "Wh", "total_increasing", "mdi:flash"),
    ("stiebel_heizmodul_el_aufnahmeleistung_heiz_tag_kwh", "Elektrisch Aufnahmeleistung Heizung Tag kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:flash"),
    ("stiebel_heizmodul_el_aufnahmeleistung_heiz_sum_kwh", "Elektrisch Aufnahmeleistung Heizung Summe kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:flash"),
    ("stiebel_heizmodul_el_aufnahmeleistung_heiz_sum_mwh", "Elektrisch Aufnahmeleistung Heizung Summe MWh", "HEIZMODUL", "sensor", "energy", "MWh", "total_increasing", "mdi:flash"),
    # --- Wärmeertrag (Zähler) ---
    ("stiebel_heizmodul_waermeertrag_2we_ww_tag_wh", "Wärme Ertrag 2we Warmwasser Tag Wh", "HEIZMODUL", "sensor", "energy", "Wh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_2we_ww_tag_kwh", "Wärme Ertrag 2we Warmwasser Tag kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_2we_ww_sum_kwh", "Wärme Ertrag 2we Warmwasser Summe kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_2we_ww_sum_mwh", "Wärme Ertrag 2we Warmwasser Summe MWh", "HEIZMODUL", "sensor", "energy", "MWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_2we_heiz_tag_wh", "Wärme Ertrag 2we Heizung Tag Wh", "HEIZMODUL", "sensor", "energy", "Wh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_2we_heiz_tag_kwh", "Wärme Ertrag 2we Heizung Tag kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_2we_heiz_sum_kwh", "Wärme Ertrag 2we Heizung Summe kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_2we_heiz_sum_mwh", "Wärme Ertrag 2we Heizung Summe MWh", "HEIZMODUL", "sensor", "energy", "MWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_ww_tag_wh", "Wärme Ertrag Warmwasser Tag Wh", "HEIZMODUL", "sensor", "energy", "Wh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_ww_tag_kwh", "Wärme Ertrag Warmwasser Tag kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_ww_sum_kwh", "Wärme Ertrag Warmwasser Summe kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_ww_sum_mwh", "Wärme Ertrag Warmwasser Summe MWh", "HEIZMODUL", "sensor", "energy", "MWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_heiz_tag_wh", "Wärme Ertrag Heizung Tag Wh", "HEIZMODUL", "sensor", "energy", "Wh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_heiz_tag_kwh", "Wärme Ertrag Heizung Tag kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_heiz_sum_kwh", "Wärme Ertrag Heizung Summe kWh", "HEIZMODUL", "sensor", "energy", "kWh", "total_increasing", "mdi:fire"),
    ("stiebel_heizmodul_waermeertrag_heiz_sum_mwh", "Wärme Ertrag Heizung Summe MWh", "HEIZMODUL", "sensor", "energy", "MWh", "total_increasing", "mdi:fire"),
    # --- COP (berechnet aus den Summenzählern; siehe apps/stiebel/signals.py) ---
    ("stiebel_heizmodul_cop_ww", "COP Warmwasser", "HEIZMODUL", "sensor", "power_factor", "", "measurement", "mdi:gauge"),
    ("stiebel_heizmodul_cop_heizung", "COP Heizung", "HEIZMODUL", "sensor", "power_factor", "", "measurement", "mdi:gauge"),
    ("stiebel_heizmodul_cop_gesamt", "COP Gesamt", "HEIZMODUL", "sensor", "power_factor", "", "measurement", "mdi:gauge"),
    # --- Betriebszustand ---
    ("stiebel_manager_programmschalter", "Programmschalter", "MANAGER", "sensor", "", "", "", "mdi:dip-switch"),
    # --- Einstellungen (lesen) ---
    ("stiebel_manager_heizkurve", "Heizkurve", "MANAGER", "sensor", "", "", "", "mdi:chart-line"),
    ("stiebel_manager_ww_hysterse", "Warmwasser Hysterese", "MANAGER", "sensor", "temperature", "K", "measurement", "mdi:thermometer"),
    ("stiebel_manager_gebaeudeart", "Gebäudeart", "MANAGER", "sensor", "", "", "", "mdi:home"),
    ("stiebel_manager_antilegionellen_zeitpunkt", "Antilegionellen Zeitpunkt", "MANAGER", "sensor", "", "", "", "mdi:clock"),
    # --- Datum / Uhrzeit ---
    ("stiebel_manager_uhrzeit", "Uhrzeit", "MANAGER", "sensor", "", "", "", "mdi:clock-outline"),
    ("stiebel_manager_datum", "Datum", "MANAGER", "sensor", "", "", "", "mdi:calendar"),
    # --- Fehlerliste (neuester Eintrag) ---
    ("stiebel_kessel_fehlerliste", "Fehlerliste", "KESSEL", "sensor", "", "", "", "mdi:alert"),
]

# Binäre Signale (et_bool / et_little_bool).
_BINARY_SPECS: list[tuple[str, str, str, str, str]] = [
    # key, name, member, device_class, icon
    ("stiebel_heizmodul_abtauungaktiv", "Abtauung Aktiv", "HEIZMODUL", "", "mdi:snowflake-melt"),
    ("stiebel_manager_evu_sperre_aktiv", "EVU Sperre Aktiv", "MANAGER", "lock", "mdi:lock"),
    ("stiebel_manager_sommerbetrieb", "Sommerbetrieb-Automatik", "MANAGER", "", "mdi:weather-sunny"),
    ("stiebel_manager_antilegionellen", "Antilegionellen", "MANAGER", "", "mdi:shield-check-outline"),
]

SIGNALS: list[dict[str, str]] = [
    {
        "key": key,
        "name": name,
        "member": member,
        "component": component,
        "device_class": device_class,
        "unit": unit,
        "state_class": state_class,
        "icon": icon,
    }
    for (key, name, member, component, device_class, unit, state_class, icon) in _SIGNAL_SPECS
]

BINARY_SIGNALS: list[dict[str, str]] = [
    {
        "key": key,
        "name": name,
        "member": member,
        "device_class": device_class,
        "icon": icon,
    }
    for (key, name, member, device_class, icon) in _BINARY_SPECS
]
