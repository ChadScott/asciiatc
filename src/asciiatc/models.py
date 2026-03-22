from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VerticalTrend(Enum):
    CLIMBING = "climbing"
    DESCENDING = "descending"
    LEVEL = "level"


@dataclass(frozen=True, slots=True)
class AirportConfig:
    icao: str
    name: str
    lat: float
    lon: float


@dataclass(slots=True)
class Aircraft:
    hex: str
    callsign: str | None = None
    registration: str | None = None
    aircraft_type: str | None = None
    lat: float | None = None
    lon: float | None = None
    alt_baro: int | None = None
    alt_geom: int | None = None
    ground_speed: float | None = None
    track: float | None = None
    vertical_rate: int | None = None
    on_ground: bool = False
    last_seen: float = 0.0
    squawk: str | None = None
    emergency: str | None = None
    category: str | None = None
    nav_altitude_mcp: int | None = None
    nav_heading: float | None = None
    nav_modes: list[str] | None = None
    nav_qnh: float | None = None
    true_heading: float | None = None
    rssi: float | None = None
    messages: int | None = None
    distance: float | None = None
    direction: float | None = None
    data_source: str | None = None
    alert: bool = False
    spi: bool = False

    @property
    def vertical_trend(self) -> VerticalTrend:
        if self.vertical_rate is None or abs(self.vertical_rate) < 200:
            return VerticalTrend.LEVEL
        return VerticalTrend.CLIMBING if self.vertical_rate > 0 else VerticalTrend.DESCENDING

    @property
    def trend_indicator(self) -> str:
        match self.vertical_trend:
            case VerticalTrend.CLIMBING:
                return "\u2191"
            case VerticalTrend.DESCENDING:
                return "\u2193"
            case VerticalTrend.LEVEL:
                return "-"

    @property
    def info_tag_lines(self) -> list[str]:
        """Build a multi-line info tag card.

        Line 1: callsign + registration (identity)
        Line 2: aircraft type + altitude/trend + ground speed (state)
        """
        line1_parts: list[str] = []
        if self.callsign:
            line1_parts.append(self.callsign)
        if self.registration:
            line1_parts.append(self.registration)

        line2_parts: list[str] = []
        if self.aircraft_type:
            line2_parts.append(self.aircraft_type)
        if self.alt_baro is not None:
            alt_display = f"{self.alt_baro // 100:03d}"
            line2_parts.append(f"{alt_display}{self.trend_indicator}")
        if self.ground_speed is not None:
            line2_parts.append(f"{int(self.ground_speed)}kt")

        lines: list[str] = []
        if line1_parts:
            lines.append(" ".join(line1_parts))
        if line2_parts:
            lines.append(" ".join(line2_parts))
        return lines
