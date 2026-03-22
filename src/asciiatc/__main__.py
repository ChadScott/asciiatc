from __future__ import annotations

import argparse
import sys

from asciiatc.app import AsciiATCApp
from asciiatc.config import AIRPORTS, DEFAULT_AIRPORT, DEFAULT_RANGE_NM


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="asciiatc",
        description="Terminal-based live radar display for aircraft",
    )
    parser.add_argument(
        "-a",
        "--airport",
        default=DEFAULT_AIRPORT,
        help=(
            f"ICAO airport code (default: {DEFAULT_AIRPORT}). "
            f"Known: {', '.join(sorted(AIRPORTS.keys()))}"
        ),
    )
    parser.add_argument(
        "-r",
        "--range",
        type=int,
        default=DEFAULT_RANGE_NM,
        help=f"Radar range in nautical miles (default: {DEFAULT_RANGE_NM})",
    )
    parser.add_argument(
        "--no-rings",
        action="store_true",
        default=False,
        help="Disable range rings (toggle at runtime with 'g')",
    )
    parser.add_argument(
        "--no-ground",
        action="store_true",
        default=False,
        help="Hide ground aircraft and vehicles (toggle at runtime with 'G')",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=None,
        help="Custom center latitude (overrides airport)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=None,
        help="Custom center longitude (overrides airport)",
    )
    args = parser.parse_args()

    if args.lat is not None and args.lon is not None:
        from asciiatc.models import AirportConfig

        custom = AirportConfig(
            icao="CUSTOM",
            name="Custom Location",
            lat=args.lat,
            lon=args.lon,
        )
        AIRPORTS["CUSTOM"] = custom
        args.airport = "CUSTOM"
    elif args.lat is not None or args.lon is not None:
        print("Error: --lat and --lon must be used together", file=sys.stderr)
        sys.exit(1)

    app = AsciiATCApp(
        airport_icao=args.airport,
        range_nm=args.range,
        show_rings=not args.no_rings,
        show_ground=not args.no_ground,
    )
    app.run()


if __name__ == "__main__":
    main()
