# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
from kivy.tools.packaging.pyinstaller_hooks import (
    get_deps_minimal,
    hookspath,
    runtime_hooks,
)
from kivy_deps import sdl2, glew

deps = get_deps_minimal(audio=None, camera=None, spelling=None, video=None)
deps["hiddenimports"].append("win32timezone")

block_cipher = None


a = Analysis(
    ["idleon_saver\\gui\\main.py"],
    pathex=["C:\\Users\\desophos\\Dropbox\\Code\\Python\\idleon\\Idleon Saver"],
    datas=[
        ("idleon_saver/scripts/*.js", "idleon_saver/scripts"),
        ("idleon-data/maps/*.json", "idleon-data/maps"),
    ],
    hookspath=hookspath(),
    hooksconfig={},
    runtime_hooks=runtime_hooks(),
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    **deps
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    Tree("idleon_saver\\gui\\"),
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name="IdleonSaver",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
