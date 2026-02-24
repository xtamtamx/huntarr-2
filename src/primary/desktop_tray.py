"""
Unified Desktop System Tray for Huntarr-2
Supports macOS (rumps) and Windows (pystray)
"""
import os
import sys
import webbrowser
import threading
import logging

logger = logging.getLogger("Huntarr-2.Tray")

DEFAULT_PORT = 9705
APP_NAME = "Huntarr-2"

# Detect platform and available libraries
PLATFORM = sys.platform
MACOS = PLATFORM == 'darwin'
WINDOWS = PLATFORM == 'win32'

# Try to import platform-specific libraries
_rumps = None
_pystray = None
_PIL = None

if MACOS:
    try:
        import rumps
        _rumps = rumps
    except ImportError:
        logger.debug("rumps not available")

if WINDOWS:
    try:
        import pystray
        from PIL import Image
        _pystray = pystray
        _PIL = Image
    except ImportError:
        logger.debug("pystray/PIL not available")


def get_icon_path():
    """Get the path to the app icon."""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        base = sys._MEIPASS
    else:
        # Running from source
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Try different icon formats
    for ext in ['icns', 'ico', 'png']:
        path = os.path.join(base, 'frontend', 'static', 'logo', f'huntarr.{ext}')
        if os.path.exists(path):
            return path
    
    # Fallback to any icon in logo folder
    logo_dir = os.path.join(base, 'frontend', 'static', 'logo')
    if os.path.isdir(logo_dir):
        for f in os.listdir(logo_dir):
            if f.endswith(('.icns', '.ico', '.png')):
                return os.path.join(logo_dir, f)
    
    return None


def get_port():
    """Get the configured port."""
    return int(os.environ.get('HUNTARR_PORT', DEFAULT_PORT))


def open_browser(port=None):
    """Open Huntarr in the default browser."""
    port = port or get_port()
    url = f'http://127.0.0.1:{port}'
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")


def is_available():
    """Check if system tray is available on this platform."""
    if MACOS:
        return _rumps is not None
    elif WINDOWS:
        return _pystray is not None and _PIL is not None
    return False


# =============================================================================
# macOS Implementation (rumps)
# =============================================================================

class MacOSTray:
    """macOS system tray using rumps."""
    
    def __init__(self, port=DEFAULT_PORT):
        if not _rumps:
            raise RuntimeError("rumps not available")
        self.port = port
        self.app = None
    
    def _get_open_at_login(self):
        """Check if app is set to open at login."""
        try:
            import subprocess
            result = subprocess.run(
                ['osascript', '-e', 
                 f'tell application "System Events" to get the name of every login item'],
                capture_output=True, text=True
            )
            return APP_NAME in result.stdout
        except Exception:
            return False
    
    def _set_open_at_login(self, enabled):
        """Set whether app opens at login."""
        try:
            import subprocess
            if enabled:
                app_path = os.path.dirname(os.path.dirname(sys.executable))
                if app_path.endswith('.app'):
                    subprocess.run([
                        'osascript', '-e',
                        f'tell application "System Events" to make login item at end with properties {{path:"{app_path}", hidden:false}}'
                    ])
            else:
                subprocess.run([
                    'osascript', '-e',
                    f'tell application "System Events" to delete login item "{APP_NAME}"'
                ])
        except Exception as e:
            logger.error(f"Failed to set login item: {e}")
    
    def run(self):
        """Run the macOS menu bar app."""
        icon_path = get_icon_path()
        
        @_rumps.clicked(f"Open {APP_NAME}")
        def open_app(_):
            open_browser(self.port)
        
        @_rumps.clicked("Open at Login")
        def toggle_login(sender):
            new_state = not sender.state
            self._set_open_at_login(new_state)
            sender.state = new_state
        
        @_rumps.clicked("Quit")
        def quit_app(_):
            _rumps.quit_application()
        
        self.app = _rumps.App(
            APP_NAME,
            icon=icon_path,
            menu=[
                f"Open {APP_NAME}",
                _rumps.MenuItem("Open at Login", callback=toggle_login),
                None,  # Separator
                "Quit"
            ]
        )
        
        # Set initial state for "Open at Login"
        for item in self.app.menu.values():
            if hasattr(item, 'title') and item.title == "Open at Login":
                item.state = self._get_open_at_login()
                break
        
        self.app.run()


# =============================================================================
# Windows Implementation (pystray)
# =============================================================================

class WindowsTray:
    """Windows system tray using pystray."""
    
    def __init__(self, port=DEFAULT_PORT):
        if not _pystray or not _PIL:
            raise RuntimeError("pystray/PIL not available")
        self.port = port
        self.icon = None
    
    def _load_icon(self):
        """Load the tray icon image."""
        icon_path = get_icon_path()
        if icon_path:
            try:
                return _PIL.open(icon_path)
            except Exception as e:
                logger.error(f"Failed to load icon: {e}")
        
        # Fallback: create a simple colored icon
        return _PIL.new('RGB', (64, 64), color=(66, 133, 244))
    
    def _quit(self, icon):
        """Quit the application."""
        icon.stop()
        os._exit(0)
    
    def run(self):
        """Run the Windows system tray."""
        image = self._load_icon()
        
        menu = _pystray.Menu(
            _pystray.MenuItem(f'Open {APP_NAME}', lambda: open_browser(self.port), default=True),
            _pystray.Menu.SEPARATOR,
            _pystray.MenuItem('Quit', self._quit)
        )
        
        self.icon = _pystray.Icon(APP_NAME, image, APP_NAME, menu)
        self.icon.run()


# =============================================================================
# Unified Interface
# =============================================================================

def create_tray(port=DEFAULT_PORT):
    """Create the appropriate tray for the current platform."""
    if MACOS and _rumps:
        return MacOSTray(port)
    elif WINDOWS and _pystray:
        return WindowsTray(port)
    else:
        raise RuntimeError(f"No system tray available for platform: {PLATFORM}")


def run_tray(port=DEFAULT_PORT):
    """Run the system tray (blocking)."""
    tray = create_tray(port)
    tray.run()


def run_tray_background(port=DEFAULT_PORT):
    """Run the system tray in a background thread."""
    thread = threading.Thread(target=run_tray, args=(port,), daemon=True)
    thread.start()
    return thread


# For backwards compatibility
def run_menubar(port=DEFAULT_PORT):
    """Alias for run_tray (macOS compatibility)."""
    run_tray(port)
