from __future__ import annotations

from asciiatc.models import AirportConfig

AIRPORTS: dict[str, AirportConfig] = {
    "KSFO": AirportConfig(icao="KSFO", name="San Francisco Intl", lat=37.6188, lon=-122.3754),
    "KLAX": AirportConfig(icao="KLAX", name="Los Angeles Intl", lat=33.9425, lon=-118.4081),
    "KJFK": AirportConfig(icao="KJFK", name="John F Kennedy Intl", lat=40.6413, lon=-73.7781),
    "KORD": AirportConfig(icao="KORD", name="Chicago O'Hare Intl", lat=41.9742, lon=-87.9073),
    "KATL": AirportConfig(icao="KATL", name="Hartsfield-Jackson Atlanta Intl", lat=33.6407, lon=-84.4277),
    "EGLL": AirportConfig(icao="EGLL", name="London Heathrow", lat=51.4700, lon=-0.4543),
    "KDFW": AirportConfig(icao="KDFW", name="Dallas/Fort Worth Intl", lat=32.8998, lon=-97.0403),
    "KDEN": AirportConfig(icao="KDEN", name="Denver Intl", lat=39.8561, lon=-104.6737),
    "KMIA": AirportConfig(icao="KMIA", name="Miami Intl", lat=25.7959, lon=-80.2870),
    "KSEA": AirportConfig(icao="KSEA", name="Seattle-Tacoma Intl", lat=47.4502, lon=-122.3088),
    "RJTT": AirportConfig(icao="RJTT", name="Tokyo Haneda", lat=35.5494, lon=139.7798),
    "LFPG": AirportConfig(icao="LFPG", name="Paris Charles de Gaulle", lat=49.0097, lon=2.5479),
    "EDDF": AirportConfig(icao="EDDF", name="Frankfurt am Main", lat=50.0379, lon=8.5622),
    "OMDB": AirportConfig(icao="OMDB", name="Dubai Intl", lat=25.2532, lon=55.3657),
    "WSSS": AirportConfig(icao="WSSS", name="Singapore Changi", lat=1.3644, lon=103.9915),
    "VHHH": AirportConfig(icao="VHHH", name="Hong Kong Intl", lat=22.3080, lon=113.9185),
}

DEFAULT_AIRPORT = "KSFO"
DEFAULT_RANGE_NM = 30
API_POLL_INTERVAL = 5.0
CHAR_ASPECT_RATIO = 2.0
MAX_AIRCRAFT_AGE = 60.0

ADSB_API_BASE = "https://api.adsb.lol"
