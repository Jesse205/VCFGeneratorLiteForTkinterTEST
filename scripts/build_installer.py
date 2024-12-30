import os
import subprocess
import sys

from scripts.utils import get_bits, get_machine
from vcf_generator import __version__ as app_version


def find_iscc_in_path():
    """尝试从系统PATH环境变量中找到iscc.exe的路径"""
    for path in os.environ["PATH"].split(os.pathsep):
        iscc_path = os.path.join(path, "iscc.exe")
        if os.path.isfile(iscc_path):
            return iscc_path
    return None


def main():
    bits = get_bits()
    if bits != 64:
        print(f"Only 64 bit python is supported. Current version is {bits}.", file=sys.stderr)
        exit(1)
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    output_name = f"VCFGenerator_v{app_version}_py{py_version}_{get_machine()}_{bits}bit_setup"
    iscc_path = find_iscc_in_path()
    if iscc_path is None:
        iscc_path = r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe'

    result = subprocess.run([iscc_path, f"/F{output_name}", os.path.abspath('setup.iss')], shell=True)
    if result.returncode != 0:
        print("Build failed.", file=sys.stderr)
        exit(result.returncode)
