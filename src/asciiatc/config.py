from __future__ import annotations

from asciiatc.models import AirportConfig

AIRPORTS: dict[str, AirportConfig] = {
    "KSFO": AirportConfig(icao="KSFO", name="San Francisco Intl", lat=37.6188, lon=-122.3754),
    "KLAX": AirportConfig(icao="KLAX", name="Los Angeles Intl", lat=33.9425, lon=-118.4081),
    "KJFK": AirportConfig(icao="KJFK", name="John F Kennedy Intl", lat=40.6413, lon=-73.7781),
    "KORD": AirportConfig(icao="KORD", name="Chicago O'Hare Intl", lat=41.9742, lon=-87.9073),
    "KATL": AirportConfig(icao="KATL", name="Hartsfield-Jackson Atlanta Intl", lat=33.6407, lon=-84.4277),
    "EGLL": AirportConfig(icao="EGLL", name="London Heathrow", lat=51.4700, lon=-0.4543),
}

DEFAULT_AIRPORT = "KSFO"
DEFAULT_RANGE_NM = 30
API_POLL_INTERVAL = 5.0
CHAR_ASPECT_RATIO = 2.0
MAX_AIRCRAFT_AGE = 60.0

ADSB_API_BASE = "https://api.adsb.lol"
