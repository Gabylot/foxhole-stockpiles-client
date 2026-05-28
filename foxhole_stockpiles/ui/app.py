"""Main application window for the Foxhole Stockpiles Client."""

import threading
from datetime import datetime
from typing import Any

import ttkbootstrap as tb
from httpx import Client, Timeout
from ttkbootstrap.constants import (
    BOTH,
    DISABLED,
    END,
    LEFT,
    LIGHT,
    NO,
    NORMAL,
    RIGHT,
    VERTICAL,
    WORD,
    YES,
    X,
    Y,
)

from foxhole_stockpiles.core.config import settings
from foxhole_stockpiles.i18n import get_translator, t
from foxhole_stockpiles.ui.settings_window import SettingsWindow


class App(tb.Window):  # type: ignore[misc]
    """Main application window."""

    def __init__(
        self, title: str, width: int = 400, height: int = 600, theme: str = "darkly"
    ) -> None:
        """Initialize the main application window.

        Args:
            title: Window title
            width: Window width in pixels
            height: Window height in pixels
            theme: ttkbootstrap theme name
        """
        if width < 0:
            raise ValueError("Width must be a valid positive integer")

        if height < 0:
            raise ValueError("Height must be a valid positive integer")

        super().__init__(
            themename=theme,
            title=title,
            minsize=(width, height),
            resizable=(False, False),
        )

        # Initialize translator with configured language
        get_translator(settings.language)

        self.create_widgets()

        self.mainloop()

    def create_widgets(self) -> None:
        """Create the widgets for the window."""
        # Menu
        self.menubar = tb.Menu(self)
        self.config(menu=self.menubar)

        self.settings_menu = tb.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=t("app.menu.settings"), menu=self.settings_menu)
        self.settings_menu.add_command(label=t("app.menu.configure"), command=self.command_settings)

        # Main Frame
        main_frame = tb.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)

        buttons_frame = tb.Frame(main_frame)
        buttons_frame.pack(fill=X, expand=NO)

        self.process_button = tb.Button(
            buttons_frame,
            text="Process SAV",
            command=self.command_process_sav,
            bootstyle=LIGHT,
        )
        self.process_button.pack(side=LEFT, padx=5)

        # Disable button if SAV config is not complete
        if not settings.sav.is_configured():
            self.process_button.configure(state=DISABLED)

        # Text Area with Scrollbar
        text_frame = tb.Frame(main_frame)
        text_frame.pack(fill=BOTH, expand=YES)

        self._text_area = tb.Text(text_frame, wrap=WORD, height=10)
        self._text_area.pack(side=LEFT, fill=BOTH, expand=YES, pady=10)

        scrollbar = tb.Scrollbar(text_frame, orient=VERTICAL, command=self._text_area.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        self._text_area.configure(yscrollcommand=scrollbar.set)

    # Menu Commands
    def command_settings(self) -> None:
        """'Settings' callback. Opens the settings configuration window."""
        settings_window = SettingsWindow(parent=self)
        saved = settings_window.show()

        if saved:
            self.message(message=t("app.message.settings_saved"))
            # Re-evaluate button state based on new settings
            if settings.sav.is_configured():
                self.process_button.configure(state=NORMAL)
            else:
                self.process_button.configure(state=DISABLED)

    def command_process_sav(self) -> None:
        """Parse the SAV file and submit all stockpiles."""
        self.message("SAV: Parsing file...")
        threading.Thread(target=self._process_and_submit).start()

    def _process_and_submit(self) -> None:
        """Parse the SAV file and submit stockpiles (runs in background thread)."""
        sav = settings.sav
        stockpiles = sav.parse()

        if stockpiles is None:
            self.message("SAV: Failed to parse file.")
            return

        filtered = sav.filter_stockpiles(stockpiles)

        if not filtered:
            self.message("SAV: No matching stockpiles found.")
            return

        self.message(f"SAV: Found {len(filtered)} stockpile(s), submitting...")
        self._submit(filtered)

    def _submit(self, stockpiles: list) -> None:
        """POST stockpiles to the SAV endpoint."""
        sav = settings.sav
        timeout = Timeout(10.0, read=60.0)

        with Client(
            headers={"X-API-TOKEN": sav.token, "Accept": "application/json"},
            verify=False,
            timeout=timeout,
        ) as client:
            try:
                response = client.post(
                    url=sav.endpoint,
                    json={"stockpiles": stockpiles},
                )
            except Exception as ex:
                self.message(f"SAV: Error sending data: {ex}")
                return

            try:
                results = response.json()
                if not isinstance(results, list):
                    results = [results]
                for r in results:
                    self.message(f"SAV: {r.get('message', r)}")
            except Exception:
                self.message(f"SAV: Unexpected response: {response.text}")

    def message(self, message: str) -> None:
        """Add a message to the text area.

        Args:
            message: Message to add
        """
        current_time = datetime.now().strftime("%H:%M:%S")
        self._text_area.insert(END, f"[{current_time}] {message}\n")
        self._text_area.see(END)