# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Add apprise data files
datas = [
    ('frontend', 'frontend'),
    ('version.txt', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
    ('src', 'src'),
    ('resources', 'resources'),
]

# Add apprise data files
try:
    import apprise
    apprise_path = os.path.dirname(apprise.__file__)
    apprise_attachment_path = os.path.join(apprise_path, 'attachment')
    apprise_plugins_path = os.path.join(apprise_path, 'plugins')
    apprise_config_path = os.path.join(apprise_path, 'config')
    
    if os.path.exists(apprise_attachment_path):
        datas.append((apprise_attachment_path, 'apprise/attachment'))
    if os.path.exists(apprise_plugins_path):
        datas.append((apprise_plugins_path, 'apprise/plugins'))
    if os.path.exists(apprise_config_path):
        datas.append((apprise_config_path, 'apprise/config'))
except ImportError:
    print("Warning: apprise not found, skipping apprise data files")

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'flask',
        'flask.json',
        'requests',
        'waitress',
        'bcrypt',
        'qrcode',
        'PIL',
        'pyotp',
        'qrcode.image.pil',
        'routes',
        'main',
        'pystray',
        'PIL.Image',
        'apprise',
        'apprise.common',
        'apprise.conversion',
        'apprise.decorators',
        'apprise.locale',
        'apprise.logger',
        'apprise.manager',
        'apprise.utils',
        'apprise.URLBase',
        'apprise.AppriseAsset',
        'apprise.AppriseAttachment',
        'apprise.AppriseConfig',
        'apprise.cli',
        'apprise.config',
        'apprise.attachment',
        'apprise.plugins',
        'markdown',
        'yaml',
        'cryptography',
        'win32api',
        'win32con',
        'win32gui',
        'pywintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Huntarr-2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='frontend/static/logo/huntarr.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Huntarr-2',
)
