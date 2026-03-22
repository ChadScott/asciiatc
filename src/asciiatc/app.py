from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Input, Static
from textual import work

from asciiatc.adsb_client import ADSBClient
from asciiatc.config import (
    AIRPORTS,
    API_POLL_INTERVAL,
    DEFAULT_AIRPORT,
    DEFAULT_RANGE_NM,
)
from asciiatc.detail_widget import DetailPanel
from asciiatc.radar_widget import RadarDisplay


class AsciiATCApp(App):
    """Terminal-based live radar display."""

    TITLE = "asciiatc"

    CSS = """
    Screen {
        background: black;
    }
    #main-area {
        width: 1fr;
        height: 1fr;
    }
    #main-area RadarDisplay {
        width: 1fr;
        height: 1fr;
    }
    #detail {
        width: 32;
        height: 1fr;
        display: none;
    }
    #detail.visible {
        display: block;
    }
    #search {
        dock: bottom;
        display: none;
    }
    #search.visible {
        display: block;
    }
    #status-bar {
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", show=False, priority=True),
        Binding("plus,equal", "zoom_in", "Zoom In", key_display="+"),
        Binding("minus", "zoom_out", "Zoom Out", key_display="-"),
        Binding("g", "toggle_rings", "Rings"),
        Binding("G", "toggle_ground", "Ground"),
        Binding("slash", "start_search", "/Search", key_display="/"),
        Binding("escape", "dismiss", "Close", show=False, priority=True),
    ]

    def __init__(
        self,
        airport_icao: str = DEFAULT_AIRPORT,
        range_nm: int = DEFAULT_RANGE_NM,
        show_rings: bool = True,
        show_ground: bool = True,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self._airport = AIRPORTS.get(
            airport_icao.upper(),
            AIRPORTS[DEFAULT_AIRPORT],
        )
        self._range_nm = range_nm
        self._show_rings = show_rings
        self._show_ground = show_ground
        self._client = ADSBClient()
        self._aircraft_count = 0
        self._selected_hex: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-area"):
            yield RadarDisplay(id="radar")
            yield DetailPanel(id="detail")
        yield Input(id="search", placeholder="Search callsign or tail...", disabled=True)
        yield Static(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        radar = self.query_one(RadarDisplay)
        radar.airport = self._airport
        radar.range_nm = self._range_nm
        radar.show_rings = self._show_rings
        radar.show_ground = self._show_ground
        self.set_interval(API_POLL_INTERVAL, self._poll_adsb)
        self._poll_adsb()

    @work(exclusive=True)
    async def _poll_adsb(self) -> None:
        try:
            aircraft = await self._client.fetch_aircraft(
                self._airport, self._range_nm
            )
            self._aircraft_count = len(aircraft)
            radar = self.query_one(RadarDisplay)
            radar.aircraft_data = aircraft

            # Update detail panel if a flight is selected
            if self._selected_hex:
                detail = self.query_one(DetailPanel)
                match = next(
                    (a for a in aircraft if a.hex == self._selected_hex), None
                )
                detail.aircraft = match

            self._update_status_bar()
        except Exception as exc:
            self._update_status_bar(error=str(exc))

    def _update_status_bar(self, error: str | None = None) -> None:
        status = self.query_one("#status-bar", Static)
        if error:
            status.update(
                f" {self._airport.icao} | Range: {self._range_nm}nm | Error: {error}"
            )
        else:
            status.update(
                f" {self._airport.icao} | Range: {self._range_nm}nm | "
                f"Tracking: {self._aircraft_count} aircraft"
            )

    # --- Search ---

    def action_start_search(self) -> None:
        search = self.query_one("#search", Input)
        search.disabled = False
        search.add_class("visible")
        search.value = ""
        search.focus()

    def _close_search(self) -> None:
        search = self.query_one("#search", Input)
        search.remove_class("visible")
        search.disabled = True
        search.value = ""
        self.query_one(RadarDisplay).search_query = ""

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search":
            self.query_one(RadarDisplay).search_query = event.value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "search":
            return
        query = event.value.strip()
        if not query:
            return

        # Find matching aircraft
        radar = self.query_one(RadarDisplay)
        q = query.upper()
        matches = [
            ac
            for ac in radar.aircraft_data
            if q in (ac.callsign or "").upper()
            or q in (ac.registration or "").upper()
        ]

        if len(matches) == 1:
            self._selected_hex = matches[0].hex
            detail = self.query_one(DetailPanel)
            detail.aircraft = matches[0]
            detail.add_class("visible")
            self._close_search()
        else:
            self.bell()

    def action_dismiss(self) -> None:
        """Handle Escape: close search first, then detail panel."""
        search = self.query_one("#search", Input)
        if search.has_class("visible"):
            self._close_search()
            return

        detail = self.query_one(DetailPanel)
        if detail.has_class("visible"):
            detail.remove_class("visible")
            detail.aircraft = None
            self._selected_hex = None
            return

    # --- Zoom / Range ---

    def action_zoom_in(self) -> None:
        if self._range_nm > 10:
            self._range_nm -= 10
            self.query_one(RadarDisplay).range_nm = self._range_nm
            self._update_status_bar()

    def action_zoom_out(self) -> None:
        if self._range_nm < 250:
            self._range_nm += 10
            self.query_one(RadarDisplay).range_nm = self._range_nm
            self._update_status_bar()

    def action_toggle_rings(self) -> None:
        radar = self.query_one(RadarDisplay)
        radar.show_rings = not radar.show_rings

    def action_toggle_ground(self) -> None:
        radar = self.query_one(RadarDisplay)
        radar.show_ground = not radar.show_ground

    async def on_unmount(self) -> None:
        await self._client.close()
