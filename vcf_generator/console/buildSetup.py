import os
import sys
from vcf_generator import __version__ as app_version
import subprocess

from vcf_generator.console.utils import get_bits, get_machine
from vcf_generator.util import logger


def main():
    bits = get_bits()
    if bits != 64:
        logger.error(f"Only 64 bit python is supported. Current version is {bits}")
        return
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    output_name = f"VCFGenerator_v{app_version}_py{py_version}_{get_machine()}_{bits}_setup"
    iss_path = os.path.abspath('setup.iss')
    iscc = r'C:\Program Files (x86)\Inno Setup 6\scripts\ISCC.lnk'
    subprocess.run([iscc, f"/F{output_name}", iss_path], shell=True)
