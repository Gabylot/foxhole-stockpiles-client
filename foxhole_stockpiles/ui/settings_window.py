"""Settings window for configuring the SAV watcher."""

import threading
import tkinter.filedialog as fd
from typing import Any

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, BOTTOM, LEFT, LIGHT, PRIMARY, RIGHT, SECONDARY, YES, X

from foxhole_stockpiles.core.config import settings
from foxhole_stockpiles.i18n import get_available_languages, get_translator, t
from foxhole_stockpiles.models.keypress import KeyPress


class SettingsWindow(tb.Toplevel):  # type: ignore[misc]
    """Settings dialog window for SAV watcher configuration."""

    def __init__(self, parent: Any) -> None:
        """Create settings window.

        Args:
            parent: Parent window
        """
        super().__init__(parent, minsize=(600, 400), resizable=(False, False))
        self.title(t("settings.title"))
        self.grab_set()  # Make the window modal
        self.result = False  # Track if settings were saved

        # Center the window on the parent window
        self.transient(parent)
        self.update_idletasks()

        # Get parent window position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Get this window size
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2

        # Set the window position
        self.geometry(f"+{x}+{y}")

        self.create_widgets()

    def create_widgets(self) -> None:
        """Create the widgets for the window."""
        main_frame = tb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # Create notebook for tabs
        notebook = tb.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=YES)

        # Keybind tab
        keybind_frame = tb.Frame(notebook, padding=10)
        notebook.add(keybind_frame, text=t("settings.tab.keybind"))
        self.create_keybind_tab(keybind_frame)

        # SAV tab
        sav_frame = tb.Frame(notebook, padding=10)
        notebook.add(sav_frame, text=t("settings.tab.sav"))
        self.create_sav_tab(sav_frame)

        # Language tab
        language_frame = tb.Frame(notebook, padding=10)
        notebook.add(language_frame, text=t("settings.tab.language"))
        self.create_language_tab(language_frame)

        # Buttons at bottom
        button_frame = tb.Frame(main_frame, padding=(0, 10, 0, 0))
        button_frame.pack(fill=X, side=BOTTOM)

        cancel_button = tb.Button(
            button_frame,
            text=t("settings.button.cancel"),
            command=self.on_cancel,
            bootstyle=SECONDARY,
        )
        cancel_button.pack(side=RIGHT, padx=5)

        save_button = tb.Button(
            button_frame,
            text=t("settings.button.save"),
            command=self.on_save,
            bootstyle=PRIMARY,
        )
        save_button.pack(side=RIGHT, padx=5)

    def create_keybind_tab(self, parent: Any) -> None:
        """Create keybind configuration tab.

        Args:
            parent: Parent frame
        """
        tb.Label(parent, text=t("settings.keybind.title"), font=("", 12, "bold")).pack(
            anchor="w", pady=(0, 10)
        )

        # Keybind entry
        keybind_frame = tb.Frame(parent)
        keybind_frame.pack(fill=X, pady=5)

        tb.Label(keybind_frame, text=t("settings.keybind.label_key"), width=22).pack(side=LEFT)
        self.keybind_var = tb.StringVar(
            value=settings.keybind.key
            if settings.keybind.key
            else t("settings.keybind.no_key_defined")
        )
        tb.Entry(keybind_frame, textvariable=self.keybind_var, state="readonly").pack(
            side=LEFT, fill=X, expand=YES, padx=(0, 10)
        )
        change_button = tb.Button(
            keybind_frame, text=t("settings.button.change"), command=self.change_keybind
        )
        change_button.pack(side=LEFT)

        tb.Label(
            parent,
            text=t("settings.keybind.hint"),
            font=("", 9),
        ).pack(anchor="w", pady=(5, 0))

    def create_sav_tab(self, parent: Any) -> None:
        """Create SAV configuration tab.

        Args:
            parent: Parent frame
        """
        tb.Label(parent, text=t("settings.sav.title"), font=("", 12, "bold")).pack(
            anchor="w", pady=(0, 10)
        )

        # SAV file path
        sav_file_frame = tb.Frame(parent)
        sav_file_frame.pack(fill=X, pady=5)
        tb.Label(sav_file_frame, text=t("settings.sav.label_sav_file"), width=26).pack(side=LEFT)
        self.sav_file_var = tb.StringVar(value=settings.sav.sav_file or "")
        tb.Entry(sav_file_frame, textvariable=self.sav_file_var).pack(side=LEFT, fill=X, expand=YES)
        tb.Button(
            sav_file_frame,
            text="Auto Detect",
            command=self._auto_detect_sav_file,
            bootstyle=LIGHT,
        ).pack(side=LEFT, padx=(5, 0))
        tb.Button(
            sav_file_frame,
            text="Browse...",
            command=self._browse_sav_file,
            bootstyle=SECONDARY,
        ).pack(side=LEFT, padx=(5, 0))

        # Auto-detect SAV file on first open if not configured
        if not settings.sav.sav_file:
            self._auto_detect_sav_file()

        # fs-sav executable path
        exe_frame = tb.Frame(parent)
        exe_frame.pack(fill=X, pady=5)
        tb.Label(exe_frame, text=t("settings.sav.label_fs_sav_exe"), width=26).pack(side=LEFT)
        self.fs_sav_exe_var = tb.StringVar(value=settings.sav.fs_sav_exe or "")
        tb.Entry(exe_frame, textvariable=self.fs_sav_exe_var).pack(side=LEFT, fill=X, expand=YES)
        tb.Button(
            exe_frame,
            text="Browse...",
            command=self._browse_fs_sav_exe,
            bootstyle=SECONDARY,
        ).pack(side=LEFT, padx=(5, 0))

        # Separator
        tb.Separator(parent, orient="horizontal").pack(fill=X, pady=20)

        # Submission section
        tb.Label(parent, text=t("settings.sav.submission_title"), font=("", 12, "bold")).pack(
            anchor="w", pady=(0, 10)
        )

        # Endpoint
        endpoint_frame = tb.Frame(parent)
        endpoint_frame.pack(fill=X, pady=5)
        tb.Label(endpoint_frame, text=t("settings.sav.label_endpoint"), width=26).pack(side=LEFT)
        self.endpoint_var = tb.StringVar(value=settings.sav.endpoint or "")
        tb.Entry(endpoint_frame, textvariable=self.endpoint_var).pack(side=LEFT, fill=X, expand=YES)

        # API Token
        token_frame = tb.Frame(parent)
        token_frame.pack(fill=X, pady=5)
        tb.Label(token_frame, text=t("settings.sav.label_token"), width=26).pack(side=LEFT)
        self.token_var = tb.StringVar(value=settings.sav.token or "")
        tb.Entry(token_frame, textvariable=self.token_var, show="*").pack(
            side=LEFT, fill=X, expand=YES
        )

    def create_language_tab(self, parent: Any) -> None:
        """Create language configuration tab.

        Args:
            parent: Parent frame
        """
        tb.Label(parent, text=t("settings.language.title"), font=("", 12, "bold")).pack(
            anchor="w", pady=(0, 10)
        )

        tb.Label(
            parent,
            text=t("settings.language.hint"),
            font=("", 9),
        ).pack(anchor="w", pady=(0, 20))

        # Language selection
        lang_frame = tb.Frame(parent)
        lang_frame.pack(fill=X, pady=5)
        tb.Label(lang_frame, text=t("settings.language.label_language"), width=22).pack(side=LEFT)

        # Get available languages dynamically
        available_languages = get_available_languages()
        language_names = [name for _, name in available_languages]
        language_codes = {name: code for code, name in available_languages}

        # Find current language name
        current_lang_code = settings.language
        current_lang_name = next(
            (name for code, name in available_languages if code == current_lang_code), "English"
        )

        self.language_var = tb.StringVar(value=current_lang_name)
        self.language_codes = language_codes

        lang_combo = tb.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=language_names,
            state="readonly",
        )
        lang_combo.pack(side=LEFT, fill=X, expand=YES)

    def change_keybind(self) -> None:
        """Change keybind callback. Opens a thread to capture a new keybind."""
        self.keybind_var.set(t("settings.keybind.waiting"))
        threading.Thread(target=self.read_keybind).start()

    def read_keybind(self) -> None:
        """Waits for a new key combination and updates the keybind field."""
        k = KeyPress()
        key = k.read_key()

        if not key:
            self.keybind_var.set(t("settings.keybind.no_key_defined"))
            return

        try:
            # Validate the key can be used as a global hotkey
            k.prepare_for_global_hotkey(key)
            self.keybind_var.set(key)
        except ValueError:
            self.keybind_var.set(t("settings.keybind.invalid_key") + f" {key}")

    def _auto_detect_sav_file(self) -> None:
        """Auto-detect the Foxhole MapData.sav file in the default save location."""
        path = settings.sav.auto_detect_sav_file()
        if path:
            self.sav_file_var.set(path)

    def _browse_sav_file(self) -> None:
        """Open a file dialog to select the .sav file."""
        path = fd.askopenfilename(
            title="Select SAV File",
            filetypes=[("SAV files", "*.sav"), ("All files", "*.*")],
            parent=self,
        )
        if path:
            self.sav_file_var.set(path)

    def _browse_fs_sav_exe(self) -> None:
        """Open a file dialog to select the fs-sav executable."""
        path = fd.askopenfilename(
            title="Select fs-sav Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
            parent=self,
        )
        if path:
            self.fs_sav_exe_var.set(path)

    def on_save(self) -> None:
        """Handle save button click."""
        # Save keybind
        keybind_value = self.keybind_var.get()
        no_key_msg = t("settings.keybind.no_key_defined")
        invalid_key_msg = t("settings.keybind.invalid_key")
        waiting_msg = t("settings.keybind.waiting")

        if (
            keybind_value
            and keybind_value != no_key_msg
            and not keybind_value.startswith(invalid_key_msg)
            and keybind_value != waiting_msg
        ):
            settings.keybind.key = keybind_value
        else:
            settings.keybind.key = None

        # Save SAV settings
        settings.sav.sav_file = self.sav_file_var.get() or None
        settings.sav.fs_sav_exe = self.fs_sav_exe_var.get() or None
        settings.sav.endpoint = self.endpoint_var.get() or None
        settings.sav.token = self.token_var.get() or None

        # Save language settings
        language_name = self.language_var.get()
        language_code = self.language_codes.get(language_name, "en")
        settings.language = language_code

        # Update translator with new language
        get_translator(language_code)

        # Save to file
        settings.save()

        self.result = True
        self.destroy()

    def on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = False
        self.destroy()

    def show(self) -> bool:
        """Show the settings window and return whether settings were saved.

        Returns:
            bool: True if settings were saved, False if cancelled
        """
        self.wait_window()
        return self.result