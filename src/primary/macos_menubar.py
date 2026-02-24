"""
macOS Menu Bar for Huntarr-2
Backwards-compatible wrapper around unified desktop_tray module.
"""
from src.primary.desktop_tray import run_tray, run_menubar, is_available, open_browser

# Re-export for backwards compatibility
__all__ = ['run_menubar', 'run_tray', 'is_available', 'open_browser']

# Default port constant for backwards compatibility
DEFAULT_PORT = 9705
