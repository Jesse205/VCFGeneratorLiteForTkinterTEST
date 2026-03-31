import importlib.metadata
import sys

from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

from vcf_generator_lite.__version__ import __version__ as app_version
from vcf_generator_lite.constants import APP_COPYRIGHT

sys.path.insert(0, "")

from scripts.build_app import get_windows_file_info_version

app_metadata = importlib.metadata.metadata("vcf_generator_lite")
app_author = app_metadata.get("Author")

app_exe_version = get_windows_file_info_version(app_version)

a = Analysis(
    ["./src/vcf_generator_lite/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[("./src/vcf_generator_lite/resources/", "vcf_generator_lite/resources")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="vcf-generator-lite",
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
    icon=["./assets/images/icon.ico"],
    version=VSVersionInfo(
        # For more details about fixed file info 'ffi' see:
        # http://msdn.microsoft.com/en-us/library/ms646997.aspx
        ffi=FixedFileInfo(
            # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
            # Set not needed items to zero 0. Must always contain 4 elements.
            filevers=app_exe_version,
            prodvers=app_exe_version,
            # Contains a bitmask that specifies the valid bits 'flags'r
            mask=0x3F,
            # Contains a bitmask that specifies the Boolean attributes of the file.
            flags=0x0,
            # The operating system for which this file was designed.
            # 0x4 - NT and there is no need to change it.
            OS=0x40004,
            # The general type of file.
            # 0x1 - the file is an application.
            fileType=0x1,
            # The function of the file.
            # 0x0 - the function is not defined for this fileType
            subtype=0x0,
            # Creation date and time stamp.
            date=(0, 0),
        ),
        kids=[
            # TODO: 本地化
            StringFileInfo(
                [
                    StringTable(
                        "040904B0",
                        [
                            StringStruct("CompanyName", app_author),
                            StringStruct("FileVersion", app_version),
                            StringStruct("InternalName", "VCF Generator Lite"),
                            StringStruct("LegalCopyright", APP_COPYRIGHT),
                            StringStruct("OriginalFilename", "vcf-generator-lite.exe"),
                            StringStruct("ProductName", "VCF Generator Lite"),
                            StringStruct("ProductVersion", app_version),
                        ],
                    ),
                ]
            ),
            # https://learn.microsoft.com/zh-cn/windows/win32/menurc/varfileinfo-block
            VarFileInfo([VarStruct("Translation", [0x0804, 1200, 0x0409, 1200])]),
        ],
    ),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="vcf_generator_lite",
)
