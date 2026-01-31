from vcf_generator_lite.windows.main.controller import MainController
from vcf_generator_lite.windows.main.window import VCFGeneratorLiteApp


def create_app() -> tuple[VCFGeneratorLiteApp, MainController]:
    main_window = VCFGeneratorLiteApp()
    main_controller = MainController(main_window)
    return main_window, main_controller
