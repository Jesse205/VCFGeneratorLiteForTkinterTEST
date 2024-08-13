# nuitka-project: --enable-plugin=tk-inter
# nuitka-project: --include-data-dir=./vcf_generator/assets=assets
# nuitka-project: --windows-icon-from-ico=./vcf_generator/assets/images/icon.ico
# nuitka-project: --product-name="VCF Generator"
# nuitka-project: --product-version=2.0.1.0
# nuitka-project: --copyright="Copyright (c) 2023-2024 Jesse205"
# nuitka-project: --output-dir=./build
# nuitka-project: --standalone
#
# Debugging options, controlled via environment variable at compile time.
# nuitka-project-if: os.getenv("DEBUG_COMPILATION", "no") == "yes":
#     nuitka-project: --enable-console
# nuitka-project-else:
#     nuitka-project: --disable-console
import constants
import vcf_generator.ui.main
import logging

from util import display

logging.basicConfig(level=logging.INFO)
display.set_process_dpi_aware(display.WinDpiAwareness.PROCESS_SYSTEM_DPI_AWARE)

logging.info("Starting VCF Generator...")

if __name__ == '__main__':
    print(f"Tip: The source code is hosted at {constants.URL_SOURCE}")
    vcf_generator.ui.main.main()
