from __future__ import annotations

import math

from asciiatc.config import CHAR_ASPECT_RATIO

NM_PER_DEG_LAT = 60.0


def project_to_screen(
    aircraft_lat: float,
    aircraft_lon: float,
    center_lat: float,
    center_lon: float,
    range_nm: float,
    screen_width: int,
    screen_height: int,
) -> tuple[int, int] | None:
    """Project lat/lon to (col, row) using equirectangular projection.

    Returns None if the aircraft is outside the display range.
    """
    delta_lat_nm = (aircraft_lat - center_lat) * NM_PER_DEG_LAT
    cos_lat = math.cos(math.radians(center_lat))
    delta_lon_nm = (aircraft_lon - center_lon) * NM_PER_DEG_LAT * cos_lat

    dist_nm = math.sqrt(delta_lat_nm**2 + delta_lon_nm**2)
    if dist_nm > range_nm:
        return None

    x_norm = delta_lon_nm / range_nm
    y_norm = -delta_lat_nm / range_nm

    half_w = screen_width / 2
    half_h = screen_height / 2

    col = int(half_w + x_norm * half_h * CHAR_ASPECT_RATIO)
    row = int(half_h + y_norm * half_h)

    if 0 <= col < screen_width and 0 <= row < screen_height:
        return (col, row)
    return None


def heading_to_symbol(track: float | None) -> str:
    """Convert heading in degrees to a directional arrow character."""
    if track is None:
        return "\u2666"

    symbols = [
        "\u2191",  # N
        "\u2197",  # NE
        "\u2192",  # E
        "\u2198",  # SE
        "\u2193",  # S
        "\u2199",  # SW
        "\u2190",  # W
        "\u2196",  # NW
    ]
    index = int((track % 360 + 22.5) / 45) % 8
    return symbols[index]
