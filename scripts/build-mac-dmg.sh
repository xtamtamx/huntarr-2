#!/bin/bash
set -e

# Build Huntarr-2 macOS DMG
# Requires: Python 3.12+, pip, create-dmg (brew install create-dmg)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"
VERSION=$(cat "$PROJECT_DIR/version.txt")
APP_NAME="Huntarr-2"

echo "🔨 Building $APP_NAME v$VERSION for macOS..."

cd "$PROJECT_DIR"

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

if ! command -v create-dmg &> /dev/null; then
    echo "📦 Installing create-dmg..."
    brew install create-dmg
fi

# Create and activate virtual environment
VENV_DIR="$PROJECT_DIR/.venv-build"
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller rumps pyobjc-framework-ServiceManagement

# Create app launcher
echo "📝 Creating app launcher..."
cat > app_launcher.py << 'LAUNCHER_EOF'
#!/usr/bin/env python3
import os
import sys
import logging
import json
import time
from datetime import datetime

# Setup paths
bundle_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
if hasattr(sys, "_MEIPASS"):
    bundle_dir = sys._MEIPASS

app_name = "Huntarr-2"
home = os.path.expanduser("~")
config_dir = os.path.join(home, "Library", "Application Support", app_name, "config")
log_dir = os.path.join(config_dir, "logs")

# Create directories
for d in [config_dir, log_dir,
          os.path.join(config_dir, "settings"),
          os.path.join(config_dir, "stateful"),
          os.path.join(config_dir, "user"),
          os.path.join(config_dir, "scheduler")]:
    os.makedirs(d, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "huntarr.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Huntarr-2")

# Set environment
os.environ["HUNTARR_CONFIG_DIR"] = config_dir
os.environ["FLASK_ENV"] = "production"

try:
    # Change to bundle directory
    if hasattr(sys, "_MEIPASS"):
        os.chdir(sys._MEIPASS)
    
    sys.path.insert(0, os.getcwd())
    import main
    
    # Open browser after delay
    def open_browser():
        time.sleep(3)
        try:
            import webbrowser
            webbrowser.open('http://127.0.0.1:9705')
        except Exception:
            pass
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # On macOS, run with menu bar
    if sys.platform == 'darwin':
        server_thread = threading.Thread(target=main.main, daemon=False)
        server_thread.start()
        try:
            from src.primary.macos_menubar import run_menubar
            run_menubar()
        finally:
            server_thread.join(timeout=10)
    else:
        main.main()
        
except Exception as e:
    logger.exception(f"Fatal error: {e}")
    with open(os.path.join(log_dir, "huntarr_error.log"), "a") as f:
        f.write(f"\n[{datetime.now().isoformat()}] FATAL: {e}\n")
LAUNCHER_EOF

# Create runtime hook
mkdir -p hooks
cat > hooks/runtime_hook.py << 'HOOK_EOF'
import os
import sys
os.environ["FLASK_ENV"] = "production"
home = os.path.expanduser("~")
config_dir = os.path.join(home, "Library", "Application Support", "Huntarr-2", "config")
os.environ["HUNTARR_CONFIG_DIR"] = config_dir
HOOK_EOF

# Create icon
echo "🎨 Creating app icon..."
mkdir -p icon.iconset
for size in 16 32 64 128 256 512; do
    src="frontend/static/logo/${size}.png"
    if [ -f "$src" ]; then
        cp "$src" "icon.iconset/icon_${size}x${size}.png"
    fi
done
# Create @2x variants
[ -f icon.iconset/icon_32x32.png ] && cp icon.iconset/icon_32x32.png icon.iconset/icon_16x16@2x.png
[ -f icon.iconset/icon_64x64.png ] && cp icon.iconset/icon_64x64.png icon.iconset/icon_32x32@2x.png
[ -f icon.iconset/icon_256x256.png ] && cp icon.iconset/icon_256x256.png icon.iconset/icon_128x128@2x.png
[ -f icon.iconset/icon_512x512.png ] && cp icon.iconset/icon_512x512.png icon.iconset/icon_256x256@2x.png

iconutil -c icns icon.iconset -o app_icon.icns 2>/dev/null || cp /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericApplicationIcon.icns app_icon.icns

# Create PyInstaller spec
echo "📝 Creating PyInstaller spec..."
cat > Huntarr2.spec << SPECEOF
# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

if sys.platform == 'darwin':
    try:
        from PyInstaller.building.api import BUNDLE
    except ImportError:
        try:
            from PyInstaller.building.osx import BUNDLE
        except ImportError:
            from PyInstaller.utils.osx import BUNDLE

a = Analysis(
    ['app_launcher.py'],
    pathex=['.'],
    datas=[
        ('frontend', 'frontend'),
        ('version.txt', '.'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'flask', 'flask.json', 'requests', 'waitress', 'bcrypt',
        'qrcode', 'PIL', 'pyotp', 'rumps', 'Foundation', 'AppKit',
        'ServiceManagement', 'objc', 'apprise', 'markdown', 'yaml',
    ],
    hookspath=['hooks'],
    runtime_hooks=['hooks/runtime_hook.py'],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='Huntarr-2',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='app_icon.icns',
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, name='Huntarr-2',
)

app = BUNDLE(
    coll,
    name='Huntarr-2.app',
    icon='app_icon.icns',
    bundle_identifier='io.huntarr2.app',
    info_plist={
        'CFBundleShortVersionString': '$VERSION',
        'CFBundleVersion': '$VERSION',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,
    },
)
SPECEOF

# Build with PyInstaller
echo "🔨 Building app with PyInstaller..."
python3 -m PyInstaller Huntarr2.spec --clean --noconfirm

# Check if app was built
if [ ! -d "$DIST_DIR/Huntarr-2.app" ]; then
    echo "❌ Build failed - app not created"
    exit 1
fi

echo "✅ App built: $DIST_DIR/Huntarr-2.app"

# Create DMG
echo "💿 Creating DMG..."
DMG_NAME="Huntarr-2-${VERSION}-mac.dmg"

# Remove old DMG if exists
rm -f "$PROJECT_DIR/$DMG_NAME"

create-dmg \
    --volname "Huntarr-2" \
    --volicon "app_icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "Huntarr-2.app" 150 185 \
    --app-drop-link 450 185 \
    --hide-extension "Huntarr-2.app" \
    "$PROJECT_DIR/$DMG_NAME" \
    "$DIST_DIR/Huntarr-2.app"

echo ""
echo "✅ DMG created: $PROJECT_DIR/$DMG_NAME"
echo ""
echo "To install:"
echo "  1. Open the DMG"
echo "  2. Drag Huntarr-2 to Applications"
echo "  3. If macOS blocks it, go to System Settings → Privacy & Security → Allow"
