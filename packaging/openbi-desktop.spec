# PyInstaller spec for OpenBI Desktop.
# Build with: pyinstaller packaging/openbi-desktop.spec --noconfirm

from pathlib import Path

# Repo root (spec lives in packaging/, so go up one level).
ROOT = Path(SPECPATH).parent

block_cipher = None

a = Analysis(
    [str(ROOT / "src" / "openbi_desktop" / "__main__.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[
        # Ship icons and any other non-Python resources.
        (str(ROOT / "src" / "openbi_desktop" / "resources"),
         "openbi_desktop/resources"),
    ],
    hiddenimports=[
        # PySide6 sometimes needs these explicitly declared.
        "PySide6.QtCharts",
        "PySide6.QtSvg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim size — we don't use these Qt modules.
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineQuick",
        "PySide6.QtQuick",
        "PySide6.QtQml",
        "PySide6.Qt3DCore",
        "PySide6.QtMultimedia",
        "PySide6.QtDesigner",
        "PySide6.QtTest",
    ],
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
    name="openbi-desktop",
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
    icon=str(ROOT / "src" / "openbi_desktop" / "resources"
             / "icons" / "hicolor" / "256x256" / "apps" / "openbi-desktop.png"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="openbi-desktop",
)
