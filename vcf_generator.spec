# -*- mode: python ; coding: utf-8 -*-

# noinspection PyUnresolvedReferences
a = Analysis(
    ['./main.py'],
    pathex=[],
    binaries=[],
    datas=[('./assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure)

# noinspection PyUnresolvedReferences
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='vcf_generator',
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
    icon=['assets/icon.ico'],
    version="file_version_info.txt" if os.path.exists("file_version_info.txt") else None,
)

# noinspection PyUnresolvedReferences
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='vcf_generator',
    icon=['assets/icon.ico']
)
