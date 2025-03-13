# -*- mode: python ; coding: utf-8 -*-
import os

resources_dir = './src/vcf_generator_lite/resources/'

resources = []
for root, dirs, files in os.walk("./src/vcf_generator_lite/resources/"):
    for file in files:
        if not file.endswith(".pyc") and not file.endswith(".py"):
            resources.append((os.path.join(root, file), os.path.relpath(root, './src/')))

# noinspection PyUnresolvedReferences
a = Analysis(
    ['./src/vcf_generator_lite/__main__.py'],
    pathex=[],
    binaries=[],
    datas=resources,
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
