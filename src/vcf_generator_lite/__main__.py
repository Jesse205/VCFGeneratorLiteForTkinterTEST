import logging
import sys

from vcf_generator_lite import constants
from vcf_generator_lite.window.main import create_main_window
from vcf_generator_lite.util.display import enable_dpi_aware


def main():
    log_level = logging.DEBUG if __debug__ else logging.INFO
    logging.basicConfig(level=log_level, stream=sys.stdout)

    enable_dpi_aware()

    logging.info("Starting VCF Generator...")

    print(f"💡Tip: The source code is hosted at {constants.URL_SOURCE}")
    main_window, _ = create_main_window()
    main_window.mainloop()



if __name__ == "__main__":
    main()
