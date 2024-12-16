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
