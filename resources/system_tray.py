"""
Windows System Tray Icon for Huntarr-2
"""
import os
import sys
import webbrowser
import threading

try:
    import pystray
    from PIL import Image
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


def get_icon_path():
    """Get the path to the icon file."""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return os.path.join(sys._MEIPASS, 'frontend', 'static', 'logo', 'huntarr.ico')
    else:
        # Running from source
        return os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'logo', 'huntarr.ico')


def open_browser():
    """Open Huntarr in browser."""
    webbrowser.open('http://127.0.0.1:9705')


def quit_app(icon):
    """Quit the application."""
    icon.stop()
    os._exit(0)


def create_tray_icon(stop_event=None):
    """Create and run the system tray icon."""
    if not TRAY_AVAILABLE:
        print("System tray not available (pystray/PIL not installed)")
        return None
    
    icon_path = get_icon_path()
    
    try:
        image = Image.open(icon_path)
    except Exception as e:
        print(f"Could not load icon: {e}")
        # Create a simple colored icon as fallback
        image = Image.new('RGB', (64, 64), color=(66, 133, 244))
    
    menu = pystray.Menu(
        pystray.MenuItem('Open Huntarr-2', lambda: open_browser(), default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Quit', quit_app)
    )
    
    icon = pystray.Icon(
        'Huntarr-2',
        image,
        'Huntarr-2',
        menu
    )
    
    return icon


def run_tray():
    """Run the system tray in a separate thread."""
    icon = create_tray_icon()
    if icon:
        icon.run()


if __name__ == '__main__':
    run_tray()
