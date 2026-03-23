# asciiatc

A terminal-based air traffic control radar display that shows live aircraft using ADS-B data.

## What it does

asciiatc renders a real-time radar scope in your terminal, centered on an airport or custom coordinates. It pulls live aircraft positions from the [adsb.lol](https://adsb.lol) API and displays them with callsigns, altitudes, and ground speeds. Range rings provide distance reference, and a detail panel shows extended information for selected aircraft.

## Installation

Requires Python 3.11+.

### With uv (recommended)

```bash
uv run asciiatc
```

This installs dependencies and runs the app in one step.

### With pip

```bash
pip install .
asciiatc
```

## Usage

```
asciiatc [-a ICAO] [-r RANGE] [--lat LAT --lon LON] [--no-rings] [--no-ground]
```

| Flag | Description |
|------|-------------|
| `-a`, `--airport` | ICAO airport code (default: KSFO). Available: KATL, EDDF, EGLL, KDEN, KDFW, KJFK, KLAX, KMIA, KORD, KSEA, KSFO, LFPG, OMDB, RJTT, VHHH, WSSS |
| `-r`, `--range` | Radar range in nautical miles (default: 30) |
| `--lat`, `--lon` | Custom center coordinates (must specify both) |
| `--no-rings` | Start with range rings hidden |
| `--no-ground` | Start with ground traffic hidden |

### Examples

```bash
asciiatc -a KJFK              # JFK Airport, 30nm range
asciiatc -a EGLL -r 50        # Heathrow, 50nm range
asciiatc -a RJTT -r 40        # Tokyo Haneda, 40nm range
asciiatc -a OMDB              # Dubai Intl, 30nm range
asciiatc --lat 51.47 --lon -0.45 -r 100  # Custom location
```

## Keybindings

| Key | Action |
|-----|--------|
| `+` / `-` | Zoom in / out (10nm steps) |
| `r` | Toggle range rings |
| `g` | Toggle ground traffic |
| `/` | Search aircraft |
| `Tab` | Autocomplete search (longest common prefix) |
| `Esc` | Close detail panel / search |
| `q` | Quit |
