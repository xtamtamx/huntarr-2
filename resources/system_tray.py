"""
Windows System Tray for Huntarr-2
Backwards-compatible wrapper around unified desktop_tray module.
"""
import sys
import os

# Add parent to path for imports when running standalone
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.primary.desktop_tray import run_tray, create_tray, is_available, open_browser

# Re-export for backwards compatibility
__all__ = ['run_tray', 'create_tray', 'is_available', 'open_browser']


def get_icon_path():
    """Backwards-compatible alias."""
    from src.primary.desktop_tray import get_icon_path as _get_icon_path
    return _get_icon_path()


def quit_app(icon):
    """Backwards-compatible alias."""
    icon.stop()
    os._exit(0)


def create_tray_icon(stop_event=None):
    """Backwards-compatible alias."""
    return create_tray()


if __name__ == '__main__':
    run_tray()
