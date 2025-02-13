# -*- mode: python ; coding: utf-8 -*-

# noinspection PyUnresolvedReferences
a = Analysis(
    ['./src/vcf_generator_lite/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('./src/vcf_generator_lite/assets', 'vcf_generator_lite/assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2
)

# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure)

# noinspection PyUnresolvedReferences
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='vcf_generator_lite',
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
    icon=['./icon.ico'],
    version="versionfile.txt" if os.path.exists("versionfile.txt") else None,
)

# noinspection PyUnresolvedReferences
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='vcf_generator_lite',
    icon=['./icon.ico']
)
