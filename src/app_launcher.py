#!/usr/bin/env python3
"""
Huntarr-2 Desktop Application Launcher
Used by PyInstaller builds on macOS and Windows.
"""
import os
import sys
import logging
import json
import time
import threading
from datetime import datetime

APP_NAME = "Huntarr-2"
DEFAULT_PORT = 9705


def get_config_dir():
    """Get the configuration directory for the current platform."""
    home = os.path.expanduser("~")
    
    if sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/Huntarr-2/config
        return os.path.join(home, "Library", "Application Support", APP_NAME, "config")
    elif sys.platform == 'win32':
        # Windows: %APPDATA%/Huntarr-2/config
        appdata = os.environ.get('APPDATA', os.path.join(home, 'AppData', 'Roaming'))
        return os.path.join(appdata, APP_NAME, "config")
    else:
        # Linux: ~/.config/huntarr-2
        return os.path.join(home, ".config", APP_NAME.lower())


def setup_directories(config_dir):
    """Create necessary directories."""
    dirs = [
        config_dir,
        os.path.join(config_dir, "logs"),
        os.path.join(config_dir, "settings"),
        os.path.join(config_dir, "stateful"),
        os.path.join(config_dir, "user"),
        os.path.join(config_dir, "scheduler"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    return dirs


def setup_logging(log_dir):
    """Configure logging."""
    log_file = os.path.join(log_dir, "huntarr.log")
    error_log = os.path.join(log_dir, "huntarr_error.log")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(APP_NAME)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return logger, error_log


def setup_bundle_environment():
    """Set up environment for PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        bundle_dir = sys._MEIPASS
        os.chdir(bundle_dir)
        sys.path.insert(0, bundle_dir)
        return bundle_dir
    return os.getcwd()


def create_default_configs(config_dir):
    """Create default configuration files if they don't exist."""
    # Default scheduler
    scheduler_file = os.path.join(config_dir, "scheduler", "schedule.json")
    if not os.path.exists(scheduler_file):
        with open(scheduler_file, "w") as f:
            json.dump({
                "global": [],
                "sonarr": [],
                "radarr": [],
                "lidarr": [],
                "readarr": []
            }, f, indent=2)
    
    # Default general settings
    general_file = os.path.join(config_dir, "settings", "general.json")
    if not os.path.exists(general_file):
        with open(general_file, "w") as f:
            json.dump({
                "api_timeout": 120,
                "command_wait_delay": 1,
                "command_wait_attempts": 600,
                "log_level": "DEBUG"
            }, f, indent=2)


def open_browser_delayed(port=DEFAULT_PORT, delay=3):
    """Open browser after a short delay."""
    def _open():
        time.sleep(delay)
        try:
            import webbrowser
            webbrowser.open(f'http://127.0.0.1:{port}')
        except Exception:
            pass
    
    threading.Thread(target=_open, daemon=True).start()


def run_with_tray(main_func, port=DEFAULT_PORT):
    """Run the main app with system tray on supported platforms."""
    if sys.platform == 'darwin':
        # macOS: run server in thread, tray in main thread
        server_thread = threading.Thread(target=main_func, daemon=False)
        server_thread.start()
        
        try:
            from src.primary.desktop_tray import run_tray
            run_tray(port)
        except ImportError:
            server_thread.join()
        finally:
            server_thread.join(timeout=10)
    
    elif sys.platform == 'win32':
        # Windows: run tray in thread, server in main thread
        try:
            from src.primary.desktop_tray import run_tray_background
            run_tray_background(port)
        except ImportError:
            pass
        main_func()
    
    else:
        # Other platforms: just run the server
        main_func()


def main():
    """Main entry point for desktop application."""
    # Set up config directory
    config_dir = get_config_dir()
    setup_directories(config_dir)
    
    # Set up logging
    log_dir = os.path.join(config_dir, "logs")
    logger, error_log = setup_logging(log_dir)
    
    logger.info(f"Starting {APP_NAME}")
    logger.info(f"Config directory: {config_dir}")
    
    try:
        # Set environment
        os.environ["HUNTARR_CONFIG_DIR"] = config_dir
        os.environ["FLASK_ENV"] = "production"
        
        # Set up bundle environment
        bundle_dir = setup_bundle_environment()
        logger.debug(f"Bundle directory: {bundle_dir}")
        
        # Create default configs
        create_default_configs(config_dir)
        
        # Import and run main
        import main as huntarr_main
        
        # Open browser after delay
        open_browser_delayed()
        
        # Run with system tray
        run_with_tray(huntarr_main.main)
        
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        
        # Write to error log
        with open(error_log, "a") as f:
            f.write(f"\n[{datetime.now().isoformat()}] FATAL: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        
        raise


if __name__ == "__main__":
    main()
