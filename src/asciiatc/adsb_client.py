from __future__ import annotations

import httpx

from asciiatc.config import ADSB_API_BASE, MAX_AIRCRAFT_AGE
from asciiatc.models import Aircraft, AirportConfig


class ADSBClient:
    """Async client for the ADSB.lol API."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=ADSB_API_BASE,
            timeout=10.0,
            headers={"Accept": "application/json"},
        )

    async def fetch_aircraft(
        self, airport: AirportConfig, range_nm: int
    ) -> list[Aircraft]:
        url = f"/v2/lat/{airport.lat}/lon/{airport.lon}/dist/{range_nm}"
        response = await self._client.get(url)
        response.raise_for_status()
        data = response.json()

        aircraft_list: list[Aircraft] = []
        for ac in data.get("ac", []):
            lat = ac.get("lat")
            lon = ac.get("lon")
            if lat is None or lon is None:
                continue

            alt_baro = ac.get("alt_baro")
            on_ground = False
            if alt_baro == "ground":
                alt_baro = 0
                on_ground = True
            elif isinstance(alt_baro, str):
                alt_baro = None

            emergency = ac.get("emergency")
            if emergency == "none":
                emergency = None

            aircraft_list.append(
                Aircraft(
                    hex=ac.get("hex", ""),
                    callsign=ac.get("flight", "").strip() or None,
                    registration=ac.get("r") or None,
                    aircraft_type=ac.get("t") or None,
                    lat=lat,
                    lon=lon,
                    alt_baro=alt_baro,
                    alt_geom=ac.get("alt_geom"),
                    ground_speed=ac.get("gs"),
                    track=ac.get("track"),
                    vertical_rate=ac.get("baro_rate") or ac.get("geom_rate"),
                    on_ground=on_ground,
                    last_seen=ac.get("seen_pos", 0.0) or 0.0,
                    squawk=ac.get("squawk"),
                    emergency=emergency,
                    category=ac.get("category"),
                    nav_altitude_mcp=ac.get("nav_altitude_mcp"),
                    nav_heading=ac.get("nav_heading"),
                    nav_modes=ac.get("nav_modes"),
                    nav_qnh=ac.get("nav_qnh"),
                    true_heading=ac.get("true_heading"),
                    rssi=ac.get("rssi"),
                    messages=ac.get("messages"),
                    distance=ac.get("dst"),
                    direction=ac.get("dir"),
                    data_source=ac.get("type"),
                    alert=bool(ac.get("alert", 0)),
                    spi=bool(ac.get("spi", 0)),
                )
            )

        return [a for a in aircraft_list if a.last_seen < MAX_AIRCRAFT_AGE]

    async def close(self) -> None:
        await self._client.aclose()
