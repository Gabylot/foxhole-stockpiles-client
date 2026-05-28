"""Main entry point for the Foxhole Stockpiles Client application.

Run this from the project root (foxhole-stockpiles-client/) with:

    python -m foxhole_stockpiles.main
"""

from foxhole_stockpiles import __version__
from foxhole_stockpiles.ui.app import App


def main() -> None:
    """Launch the Foxhole Stockpiles Client application."""
    window = App(title=f"Foxhole Stockpiles v{__version__}", width=700, height=400)
    window.mainloop()


if __name__ == "__main__":
    main()