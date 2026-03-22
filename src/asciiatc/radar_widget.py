from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget

from asciiatc.config import CHAR_ASPECT_RATIO
from asciiatc.models import Aircraft, AirportConfig
from asciiatc.projection import heading_to_symbol, project_to_screen

# Role keys stored in the grid instead of Style objects
BG = "bg"
RING = "ring"
AIRPORT = "airport"
TARGET = "target"
TAG = "tag"
DIM_TARGET = "dim-target"
DIM_TAG = "dim-tag"


@dataclass
class PlottedTarget:
    aircraft: Aircraft
    col: int
    row: int
    symbol: str
    tag_lines: list[str]


class RadarDisplay(Widget):
    """Radar scope widget that renders aircraft on a character grid."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "radardisplay--bg",
        "radardisplay--ring",
        "radardisplay--airport",
        "radardisplay--target",
        "radardisplay--tag",
        "radardisplay--dim-target",
        "radardisplay--dim-tag",
    }

    DEFAULT_CSS = """
    RadarDisplay {
        & > .radardisplay--bg {
            color: $primary-darken-3;
            background: $surface;
        }
        & > .radardisplay--ring {
            color: $primary-darken-1;
            background: $surface;
        }
        & > .radardisplay--airport {
            color: $warning;
            background: $surface;
            text-style: bold;
        }
        & > .radardisplay--target {
            color: $primary;
            background: $surface;
            text-style: bold;
        }
        & > .radardisplay--tag {
            color: $text;
            background: $surface;
        }
        & > .radardisplay--dim-target {
            color: $primary-darken-2;
            background: $surface;
        }
        & > .radardisplay--dim-tag {
            color: $text-muted;
            background: $surface;
        }
    }
    """

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._aircraft_data: list[Aircraft] = []
        self._airport: AirportConfig | None = None
        self._range_nm: int = 30
        self._show_rings: bool = True
        self._show_ground: bool = True
        self._search_query: str = ""
        self._grid: list[list[tuple[str, str]]] = []

    @property
    def airport(self) -> AirportConfig | None:
        return self._airport

    @airport.setter
    def airport(self, value: AirportConfig | None) -> None:
        self._airport = value
        self._rebuild_grid()
        self.refresh()

    @property
    def range_nm(self) -> int:
        return self._range_nm

    @range_nm.setter
    def range_nm(self, value: int) -> None:
        self._range_nm = value
        self._rebuild_grid()
        self.refresh()

    @property
    def show_rings(self) -> bool:
        return self._show_rings

    @show_rings.setter
    def show_rings(self, value: bool) -> None:
        self._show_rings = value
        self._rebuild_grid()
        self.refresh()

    @property
    def show_ground(self) -> bool:
        return self._show_ground

    @show_ground.setter
    def show_ground(self, value: bool) -> None:
        self._show_ground = value
        self._rebuild_grid()
        self.refresh()

    @property
    def search_query(self) -> str:
        return self._search_query

    @search_query.setter
    def search_query(self, value: str) -> None:
        self._search_query = value
        self._rebuild_grid()
        self.refresh()

    @property
    def aircraft_data(self) -> list[Aircraft]:
        return self._aircraft_data

    @aircraft_data.setter
    def aircraft_data(self, value: list[Aircraft]) -> None:
        self._aircraft_data = value
        self._rebuild_grid()
        self.refresh()

    def on_resize(self) -> None:
        self._rebuild_grid()
        self.refresh()

    def _rebuild_grid(self) -> None:
        w = self.size.width
        h = self.size.height
        if w == 0 or h == 0 or self._airport is None:
            self._grid = []
            return

        grid: list[list[tuple[str, str]]] = [
            [(" ", BG) for _ in range(w)] for _ in range(h)
        ]

        if self._show_rings:
            self._draw_range_rings(grid, w, h)
        self._draw_airport_marker(grid, w, h)
        self._draw_aircraft(grid, w, h)

        self._grid = grid

    def _draw_range_rings(
        self, grid: list[list[tuple[str, str]]], w: int, h: int
    ) -> None:
        cx = w / 2
        cy = h / 2
        ring_interval = 10
        num_rings = self._range_nm // ring_interval

        for ring_i in range(1, num_rings + 1):
            frac = ring_i * ring_interval / self._range_nm
            ry = frac * (h / 2)
            rx = ry * CHAR_ASPECT_RATIO

            steps = max(24, int(max(rx, ry) * 1.2))
            if steps == 0:
                continue
            for step in range(steps):
                angle = 2 * math.pi * step / steps
                col = int(cx + rx * math.cos(angle))
                row = int(cy + ry * math.sin(angle))
                if 0 <= col < w and 0 <= row < h and grid[row][col][0] == " ":
                    grid[row][col] = ("\u00b7", RING)

    def _draw_airport_marker(
        self, grid: list[list[tuple[str, str]]], w: int, h: int
    ) -> None:
        cx, cy = w // 2, h // 2
        if 0 <= cx < w and 0 <= cy < h:
            grid[cy][cx] = ("+", AIRPORT)

        if self._airport is None:
            return
        label = self._airport.icao
        start = cx + 2
        if start + len(label) < w:
            for i, ch in enumerate(label):
                grid[cy][start + i] = (ch, AIRPORT)

    def _matches_query(self, ac: Aircraft) -> bool:
        if not self._search_query:
            return True
        q = self._search_query.upper()
        return (
            q in (ac.callsign or "").upper()
            or q in (ac.registration or "").upper()
        )

    def _draw_aircraft(
        self, grid: list[list[tuple[str, str]]], w: int, h: int
    ) -> None:
        if self._airport is None:
            return

        plotted: list[PlottedTarget] = []
        for ac in self._aircraft_data:
            if ac.lat is None or ac.lon is None:
                continue
            if not self._show_ground and ac.on_ground:
                continue
            result = project_to_screen(
                ac.lat,
                ac.lon,
                self._airport.lat,
                self._airport.lon,
                self._range_nm,
                w,
                h,
            )
            if result is None:
                continue
            col, row = result
            plotted.append(
                PlottedTarget(
                    aircraft=ac,
                    col=col,
                    row=row,
                    symbol=heading_to_symbol(ac.track),
                    tag_lines=ac.info_tag_lines,
                )
            )

        plotted.sort(key=lambda t: t.aircraft.alt_baro or 0, reverse=True)

        # Pre-seed occupied with airport marker cells
        occupied: set[tuple[int, int]] = set()
        cx, cy = w // 2, h // 2
        occupied.add((cy, cx))
        if self._airport is not None:
            label = self._airport.icao
            start = cx + 2
            for i in range(len(label)):
                if 0 <= start + i < w:
                    occupied.add((cy, start + i))

        # First pass: place all target symbols
        for target in plotted:
            r, c = target.row, target.col
            matched = self._matches_query(target.aircraft)
            role = TARGET if matched else DIM_TARGET
            if 0 <= r < h and 0 <= c < w:
                grid[r][c] = (target.symbol, role)
                occupied.add((r, c))

        # Second pass: place multi-line tags (all-or-nothing per tag block)
        for target in plotted:
            lines = target.tag_lines
            if not lines:
                continue

            matched = self._matches_query(target.aircraft)
            role = TAG if matched else DIM_TAG

            r, c = target.row, target.col
            tag_h = len(lines)
            tag_w = max(len(line) for line in lines)

            # Pad lines to uniform width for a rectangular block
            padded = [line.ljust(tag_w) for line in lines]

            # Try placements: above target, below, further above, further below
            offsets = [-(tag_h), 1, -(tag_h + 1), 2]
            for row_offset in offsets:
                top_row = r + row_offset
                if top_row < 0 or top_row + tag_h > h:
                    continue

                tag_col = max(0, min(c - tag_w // 2, w - tag_w))
                if tag_col < 0:
                    continue

                # Check if entire rectangular block is free
                block_free = all(
                    (top_row + row_i, tag_col + col_i) not in occupied
                    for row_i in range(tag_h)
                    for col_i in range(tag_w)
                )
                if not block_free:
                    continue

                # Place the block
                for row_i, line in enumerate(padded):
                    for col_i, ch in enumerate(line):
                        grid_row = top_row + row_i
                        grid_col = tag_col + col_i
                        if 0 <= grid_col < w:
                            grid[grid_row][grid_col] = (ch, role)
                            occupied.add((grid_row, grid_col))
                break

    def _resolve_styles(self) -> dict[str, Style]:
        """Resolve component class styles from the current theme."""
        return {
            BG: self.get_component_rich_style("radardisplay--bg"),
            RING: self.get_component_rich_style("radardisplay--ring"),
            AIRPORT: self.get_component_rich_style("radardisplay--airport"),
            TARGET: self.get_component_rich_style("radardisplay--target"),
            TAG: self.get_component_rich_style("radardisplay--tag"),
            DIM_TARGET: self.get_component_rich_style("radardisplay--dim-target"),
            DIM_TAG: self.get_component_rich_style("radardisplay--dim-tag"),
        }

    def render_line(self, y: int) -> Strip:
        if not self._grid or y >= len(self._grid):
            return Strip.blank(self.size.width)

        styles = self._resolve_styles()
        row = self._grid[y]
        segments = [Segment(ch, styles[role]) for ch, role in row]
        return Strip(segments, self.size.width)
