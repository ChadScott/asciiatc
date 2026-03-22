from __future__ import annotations

from typing import ClassVar

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget

from asciiatc.models import Aircraft

PANEL_WIDTH = 32
INNER_WIDTH = PANEL_WIDTH - 2

# Role keys
BORDER = "border"
LABEL = "label"
VALUE = "value"
PANEL_BG = "panel-bg"


class DetailPanel(Widget):
    """Vertical panel showing detailed stats for a selected aircraft."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "detailpanel--border",
        "detailpanel--label",
        "detailpanel--value",
        "detailpanel--bg",
    }

    DEFAULT_CSS = """
    DetailPanel {
        & > .detailpanel--border {
            color: $primary;
            background: $surface;
        }
        & > .detailpanel--label {
            color: $text-muted;
            background: $surface;
        }
        & > .detailpanel--value {
            color: $text;
            background: $surface;
        }
        & > .detailpanel--bg {
            color: $primary;
            background: $surface;
        }
    }
    """

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._aircraft: Aircraft | None = None
        self._lines: list[list[tuple[str, str]]] = []

    @property
    def aircraft(self) -> Aircraft | None:
        return self._aircraft

    @aircraft.setter
    def aircraft(self, value: Aircraft | None) -> None:
        self._aircraft = value
        self._rebuild()
        self.refresh()

    def on_resize(self) -> None:
        self._rebuild()

    def _make_row(
        self, label: str, value: str
    ) -> list[tuple[str, str]]:
        """Build one bordered row: | LABEL  value |"""
        cells: list[tuple[str, str]] = []
        cells.append(("\u2502", BORDER))

        label_text = f" {label}"
        for ch in label_text:
            cells.append((ch, LABEL))

        gap = INNER_WIDTH - len(label_text) - len(value) - 1
        if gap < 1:
            gap = 1
        for _ in range(gap):
            cells.append((" ", PANEL_BG))

        for ch in value:
            cells.append((ch, VALUE))
        cells.append((" ", PANEL_BG))

        cells.append(("\u2502", BORDER))
        return cells

    def _make_border(self, kind: str) -> list[tuple[str, str]]:
        if kind == "top":
            left, right, fill = "\u250c", "\u2510", "\u2500"
        else:
            left, right, fill = "\u2514", "\u2518", "\u2500"
        cells: list[tuple[str, str]] = []
        cells.append((left, BORDER))
        for _ in range(INNER_WIDTH):
            cells.append((fill, BORDER))
        cells.append((right, BORDER))
        return cells

    def _make_empty(self) -> list[tuple[str, str]]:
        cells: list[tuple[str, str]] = []
        cells.append(("\u2502", BORDER))
        for _ in range(INNER_WIDTH):
            cells.append((" ", PANEL_BG))
        cells.append(("\u2502", BORDER))
        return cells

    def _make_divider(self) -> list[tuple[str, str]]:
        cells: list[tuple[str, str]] = []
        cells.append(("\u251c", BORDER))
        for _ in range(INNER_WIDTH):
            cells.append(("\u2500", BORDER))
        cells.append(("\u2524", BORDER))
        return cells

    def _rebuild(self) -> None:
        ac = self._aircraft
        lines: list[list[tuple[str, str]]] = []

        lines.append(self._make_border("top"))

        if ac is None:
            lines.append(self._make_row("", "No selection"))
            lines.append(self._make_border("bottom"))
            self._lines = lines
            return

        # --- Identity ---
        lines.append(self._make_row("CALLSIGN", ac.callsign or "-"))
        lines.append(self._make_row("REG", ac.registration or "-"))
        lines.append(self._make_row("TYPE", ac.aircraft_type or "-"))
        if ac.category:
            lines.append(self._make_row("CATEGORY", ac.category))
        lines.append(self._make_empty())

        # --- Flight state ---
        if ac.alt_baro is not None:
            alt_str = f"{ac.alt_baro:,} ft"
        else:
            alt_str = "-"
        lines.append(self._make_row("ALTITUDE", alt_str))

        if ac.alt_geom is not None:
            lines.append(self._make_row("GEO ALT", f"{ac.alt_geom:,} ft"))

        if ac.vertical_rate is not None:
            vr_str = f"{ac.trend_indicator} {abs(ac.vertical_rate):,} fpm"
        else:
            vr_str = "-"
        lines.append(self._make_row("VERT RATE", vr_str))

        if ac.ground_speed is not None:
            gs_str = f"{int(ac.ground_speed)} kt"
        else:
            gs_str = "-"
        lines.append(self._make_row("GND SPEED", gs_str))

        if ac.track is not None:
            hdg_str = f"{int(ac.track)}\u00b0"
        else:
            hdg_str = "-"
        lines.append(self._make_row("HEADING", hdg_str))

        lines.append(self._make_row("ON GROUND", "Yes" if ac.on_ground else "No"))

        # --- Transponder ---
        lines.append(self._make_divider())
        lines.append(self._make_row("SQUAWK", ac.squawk or "-"))
        if ac.emergency:
            lines.append(self._make_row("EMERGENCY", ac.emergency))
        if ac.alert:
            lines.append(self._make_row("ALERT", "YES"))
        if ac.spi:
            lines.append(self._make_row("IDENT", "YES"))

        # --- Navigation / Autopilot ---
        lines.append(self._make_divider())
        if ac.nav_altitude_mcp is not None:
            lines.append(
                self._make_row("SEL ALT", f"{ac.nav_altitude_mcp:,} ft")
            )
        if ac.nav_heading is not None:
            lines.append(
                self._make_row("SEL HDG", f"{int(ac.nav_heading)}\u00b0")
            )
        if ac.nav_qnh is not None:
            lines.append(
                self._make_row("QNH", f"{ac.nav_qnh:.1f} mb")
            )
        if ac.nav_modes:
            modes_str = " ".join(m.upper() for m in ac.nav_modes)
            if len(modes_str) <= INNER_WIDTH - 2:
                lines.append(self._make_row("NAV", modes_str))
            else:
                lines.append(self._make_row("NAV", ""))
                chunk = ""
                for mode in ac.nav_modes:
                    token = mode.upper()
                    if chunk and len(chunk) + 1 + len(token) > INNER_WIDTH - 3:
                        lines.append(self._make_row("", chunk))
                        chunk = token
                    else:
                        chunk = f"{chunk} {token}" if chunk else token
                if chunk:
                    lines.append(self._make_row("", chunk))

        # --- Position / Signal ---
        lines.append(self._make_divider())
        if ac.lat is not None:
            lines.append(self._make_row("LAT", f"{ac.lat:.4f}"))
        if ac.lon is not None:
            lines.append(self._make_row("LON", f"{ac.lon:.4f}"))
        if ac.distance is not None:
            lines.append(self._make_row("DISTANCE", f"{ac.distance:.1f} nm"))
        if ac.direction is not None:
            lines.append(
                self._make_row("BEARING", f"{int(ac.direction)}\u00b0")
            )

        # --- Technical ---
        lines.append(self._make_divider())
        lines.append(self._make_row("ICAO HEX", ac.hex.upper()))
        if ac.data_source:
            lines.append(self._make_row("SOURCE", ac.data_source))
        if ac.rssi is not None:
            lines.append(self._make_row("RSSI", f"{ac.rssi:.1f} dBFS"))
        if ac.messages is not None:
            lines.append(self._make_row("MESSAGES", f"{ac.messages:,}"))

        lines.append(self._make_border("bottom"))
        self._lines = lines

    def _resolve_styles(self) -> dict[str, Style]:
        return {
            BORDER: self.get_component_rich_style("detailpanel--border"),
            LABEL: self.get_component_rich_style("detailpanel--label"),
            VALUE: self.get_component_rich_style("detailpanel--value"),
            PANEL_BG: self.get_component_rich_style("detailpanel--bg"),
        }

    def render_line(self, y: int) -> Strip:
        if y < len(self._lines):
            styles = self._resolve_styles()
            row = self._lines[y]
            segments = [Segment(ch, styles[role]) for ch, role in row]
            return Strip(segments, PANEL_WIDTH)
        return Strip.blank(PANEL_WIDTH)
