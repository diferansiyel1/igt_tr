# -*- mode: python ; coding: utf-8 -*-
# Iowa Gambling Task v3.0 - PyInstaller Spec File

import sys

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pandas',
        'numpy',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'seaborn',
        'scipy',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PySide6', 'PySide2', 'PyQt5', 'psychopy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IGT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='IGT.app',
        icon=None,
        bundle_identifier='com.mcbu.igt',
        info_plist={
            'CFBundleName': 'Iowa Gambling Task',
            'CFBundleDisplayName': 'IGT v3.0',
            'CFBundleVersion': '3.0.0',
            'CFBundleShortVersionString': '3.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
        },
    )

